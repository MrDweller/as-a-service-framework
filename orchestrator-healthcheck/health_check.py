import time
import requests
import os

RETRY_TIMES = 15
RETRY_TIME_SECONDS = 15

def check_external_resource(sr_address, sr_port, cert_file_path, key_file_path):
    try:
        request = {
            "serviceDefinitionRequirement": "orchestration-service"
        }
        response = requests.post(f"https://{sr_address}:{sr_port}/serviceregistry/query", json=request, cert=(cert_file_path, key_file_path), verify=False)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        serviceQueryData = response.json()["serviceQueryData"][0]

        response = requests.get(f"https://{serviceQueryData['provider']['address']}:{serviceQueryData['provider']['port']}/orchestrator/echo", cert=(cert_file_path, key_file_path), verify=False)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        return True
    except Exception as e:
        print(f"Error checking external resource: {e}")
        return False

if __name__ == "__main__":
    print("Waiting for external resource to be available...")

    amount_retried = 0
    while not check_external_resource(os.environ['SERVICE_REGISTRY_ADDRESS'], os.environ['SERVICE_REGISTRY_PORT'], os.environ['CERT_FILE_PATH'], os.environ['KEY_FILE_PATH']):
        print(f"Orchestrator is unavailable, retrying in {RETRY_TIME_SECONDS}s")

        amount_retried += 1
        if amount_retried == RETRY_TIMES:
            exit(1)
        
        time.sleep(RETRY_TIME_SECONDS)

    print("External resource is ready!")
    exit(0)

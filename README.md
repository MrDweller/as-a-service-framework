# as-a-service framework
Collection of all neccesary modules for the as-a-service framework, in terms of data proccessing. This project is used for starting all modules on one machine, in order to easily show case the system.

The as-a-service framework, provides data sharing functionalities neccesary, in order to ahcive servitization in terms of physical products that require maintanance and repairs. This framework enables the possiblity to analyze sensor data, and if it is found that maintanance is required a workt task is created and a equivalent event is distribute to authorized technicians. Multiple different analytics models can be used to gain different insights for the same product. Similarly multiple technicians can be given events generated for the same product, some events could be given only to a select few technicians and others to multiple.

## Additional systems

The framework could be extended to use a service level agrement system, [fabric-network](https://github.com/nalle631/fabric-network). As well as a web portal, [web-portal](https://github.com/MrDweller/as-a-service-framework-web-portal).

It is recommended to use the [Arrowhead Management Tool](https://www.aitia.ai/products/arrowhead-tools/), for an easy assignment of authorization and orchestration rules in the Arrowhead framework.

## Certificates
The framework uses Arrowhead certificate security, and thus all systems requires server side and client side certificates. All certificates are located in `certificates` directory, and all have the password `123456`. To create a new certificate, use a gide from [https://github.com/eclipse-arrowhead/core-java-spring/wiki/Certificate-Creation](https://github.com/eclipse-arrowhead/core-java-spring/wiki/Certificate-Creation). If the system requires pem certificates instead of `.p12`, you could convert the `.p12` certificate with the shell script `/certificates/pkcs12-to-pem.sh`.

**NOTE:** If the framework is to be deployed in production, all certificates should be recreated.

## Requirements

* **Docker 24.0**, Other versions should also work.

## Setup
Clone this repository and clone all submodules. This could be done by recursive clone. 

```
git clone --recurse-submodules <repository-url>
```

Edit your hosts file, found at `c:\Windows\System32\Drivers\etc\hosts` on windows and `/etc/hosts` on linux. Add the following to the host file, 

```
<system-ip> arrowhead-serviceregistry
<system-ip> arrowhead-authorization
<system-ip> arrowhead-orchestrator
<system-ip> event-handler
```
Replace `<system-ip>` with the ip of the system machine that you are running the system on.

**NOTE:** you do **NOT** need to follow all requirements and setup presented in the **SUB MODULES**, this repository handles all requirements and setup.

## Start
Then start the as-a-service-framework by executing,
``` 
docker-compose up -d --build
```

The framework automatically starts the `digital-twin-hub`, `work-handler`, two `technicians` and an apache spark cluster with one master and two worker nodes. 

### Digital Twin
 
In order to create digital twin instances, navigate to [https://digital-twin-hub:8080/docs/index.html](https://digital-twin-hub:8080/docs/index.html). The web page requires a client certificate, use the `sysop.p12` certificate, located in `certificates`, password is `123456`. Two create a digital twin, first add a certificate for the digital twin in the digital twin hub. Use the certificate ID when creating a new digital twin (the system name must match the certificates common name). Add all sensors, controls, physical twin connection, and all anomalies that could be handled by the digital twin. When a digital twin is created it and all services as defined by the createion, will be registerd to Arrowhead.

### Apache spark application (analytics/ML)
To start an analytics application, the model must first be trained and saved.
Navigate into the `apache-spark` directory and run, 

```
sh runApplication.sh applications/<train_script.py>
```

Choose the desired training application and enter it instead of `<train_script.py>`.

Start the prediction application by running, 

```
sh runApplication.sh applications/<prediction_script.py>
```
Choose the desired prediction application and enter it instead of `<prediction_script.py>`.

**NOTE:** If you are running the system on a Linux machine, it might be necessary to change the access for the stream directory. 

## Configuration

### Data sharing only
This configuration is for setting up the framework with no additional systems, other than the ones in this repository.  

#### Technician configuration
Change the technicians environment files `.enviroment.technician-1.env` and `.enviroment.technician-2.env`,

```
EVENT_HANDLING_SYSTEM_TYPE="DIRECT_EVENT_HANDLING"
```

This configuration will have the technicians requesting to be assigned to a work task automatically.  

#### Authorization and orchestrator rules
* Apache Spark application
  * Authorize the application for all digital twin notify services that it should send notification of events for.
  * Add orcheastration rule for all digital twin notify services that it should send notification of events for.
* Digital Twin
  * Authorize the digital twin for work handler `create-work` service.
* Technicians
  * Authorize the technicians for each event service that they should be allowed to receive.
  * Authorize the technicians to the `assign-worker` service.

**NOTE:** for each digital twin system there will two systems registerd, one is the digital tiwn services running the digital twin hub, and the other will be the event handler. All event services is provided py the event handler system and the rest services and consuming of services should be done via the system running on the digital twin hub.

An example of these authorization rules with one prediction application `anomaly-detector-decision-tree`, one digital twin `mower-1` and one event `stuck`, would look like the following,  
![image](https://github.com/MrDweller/as-a-service-framework/assets/61691900/43ba7f1f-a8f4-4185-888d-bcc871fee19e)

After all authorization and orchestrator rules are setup, attach to each technician and subscribe to the events, 

```
docker attach technician-1
```

or/and

```
docker attach technician-2
```

run,

```
subscribe <event>
```

### Web portal
If it is desired to use the web portal [web-portal](https://github.com/MrDweller/as-a-service-framework-web-portal), then use the same configuration as *Data sharing only*, except change the technicians environment files `.enviroment.technician-1.env` and `.enviroment.technician-2.env`,

```
EVENT_HANDLING_SYSTEM_TYPE="USER_INTERACTIVE_EVENT_HANDLING"
EXTERNAL_ENDPOINT_URL="http://web-portal/serviceprovider/work-task"
```

This configuration will have the technicians forwarding the event to the endpoint *"http://web-portal/serviceprovider/work-task"*, and waiting to be given a take task command from the web portal, before requesting to be assigned to a work task.  

Also if it is desired to get notifications for customers in the web-portal, setup the [notification-adapter](https://github.com/MrDweller/notifications-adapter) system. Certificates for the `notifications-adapter` system can be found in the `./certificates` directory. 


### SLA system
Using the SLA system [fabric-network](https://github.com/nalle631/fabric-network), configure the systems the same way as in *Data sharing only* except do NOT add authorization rules from the technicians to the work handlers `assign-worker` service. Instead add authorization for the technician systems that is registerd by the SLA system, to the work handlers `assign-worker` service, this also requires orchestration rules. Also, add authorization rules between this repository's technician systems to the SLA's technician systems over `assign-worker`. This is so that this repository's technician systems asks the SLA systems to be assigned the work task instead of directly to the work handler. 

## Trigger events
In order to get the analytics to trigger an event, you could simply copy an event data point that is found `apache-spark/data/mower`, and place it at `apache-spark/data/stream/mower/`.
This assumes that an spark application is running. If the running spark application is `predict_mower_decision_tree_stream.py` use the data point in `apache-spark/data/stream/mower/`. If instead `predict_mower_error_codes.py` is used, then use the data point in `apache-spark/data/stream/mower/error_codes` 

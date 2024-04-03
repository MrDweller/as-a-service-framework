# Stage 1 - Install dependencies and run health check
FROM python:3.11.8

WORKDIR /app

RUN pip install requests

COPY . .

CMD ["python", "-u", "health_check.py"]


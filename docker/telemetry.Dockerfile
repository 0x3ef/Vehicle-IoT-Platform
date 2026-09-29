FROM python:3.12-slim
WORKDIR /app
COPY telemetry-requirements.txt .
RUN --mount=type=secret,id=build-ca \
    if [ -f /run/secrets/build-ca ]; then export PIP_CERT=/run/secrets/build-ca; fi; \
    pip install --no-cache-dir -r telemetry-requirements.txt
COPY sensor-grpc/sensors.proto .
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensors.proto
COPY mqtt_config.py .
COPY gateway gateway
COPY subscriber subscriber

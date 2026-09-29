FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=secret,id=build-ca \
    if [ -f /run/secrets/build-ca ]; then export PIP_CERT=/run/secrets/build-ca; fi; \
    pip install --no-cache-dir -r requirements.txt

COPY sensor.py .

CMD ["python", "sensor.py"]

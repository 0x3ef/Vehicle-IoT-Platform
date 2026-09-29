FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=secret,id=build-ca \
    if [ -f /run/secrets/build-ca ]; then export PIP_CERT=/run/secrets/build-ca; fi; \
    pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY .chalice/config.json .chalice/config.json
CMD ["chalice", "local", "--host", "0.0.0.0", "--port", "8000"]

# Connect to AWS IoT Core

The verified setup runs the full application with Docker Compose. This guide describes how to use AWS IoT Core as the MQTT broker in your own account.

## Broker and credentials

1. Copy the regional data endpoint from AWS IoT Core. Use the hostname without a protocol prefix.
2. Create and activate separate X.509 certificates for the gateway and subscriber, then attach a policy to each certificate. Grant `iot:Connect` for the corresponding client ID. Grant the gateway `iot:Publish` on the topics it sends to and the subscriber `iot:Subscribe` and `iot:Receive` on its filters and topics. Use the corresponding `client`, `topicfilter`, and `topic` resources.
3. Mount each client certificate, its private key, and the Amazon root CA into the appropriate container as read-only files. Configure the following variables.

| Variable | Value |
| --- | --- |
| `MQTT_HOST` | AWS IoT Core data endpoint |
| `MQTT_PORT` | `8883` |
| `MQTT_CLIENT_ID` | Unique MQTT client ID authorized by its policy |
| `MQTT_CA` | Path to the root CA inside the container |
| `MQTT_CERT` | Path to the X.509 certificate inside the container |
| `MQTT_KEY` | Path to the private key inside the container |
| `TELEMETRY_API_BASE` | Subscriber only. API base URL, including the stage path when applicable. Defaults to `http://api:8000`. |

Keep PEM files in a private directory and configure the mounts and variables in an untracked Compose override. The gateway publishes with QoS 1 and the subscriber requests QoS 1. A publish acknowledgment confirms broker receipt. Production use requires idempotent writes, durable retries, and API authentication.

## API and database

You can keep Chalice and PostgreSQL local while testing the AWS broker. If you deploy Chalice through API Gateway and Lambda, give the function network access to PostgreSQL and set `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `min_connections`, and `max_connections`. Use [init.sql](../postgres/init.sql) to initialize an empty demo database.

Verify the deployment by sending a reading from each demo sensor and running the three event queries in the [quick start](../README.md#quick-start).

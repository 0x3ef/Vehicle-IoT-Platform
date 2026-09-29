import os

import paho.mqtt.client as mqtt


TOPIC_SUFFIXES = {"battery": "metrics", "airbag": "events", "fuel": "level"}


def connect_client(role, *, on_connect=None, on_message=None):
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=os.getenv("MQTT_CLIENT_ID", f"vehicle-{role}"),
    )
    client.on_connect = on_connect
    client.on_message = on_message
    hostname = os.getenv("MQTT_HOST", "mosquitto")
    certificate = os.getenv("MQTT_CERT")
    private_key = os.getenv("MQTT_KEY")
    if bool(certificate) != bool(private_key):
        raise ValueError("Set both MQTT_CERT and MQTT_KEY for mutual TLS")

    ca_file = os.getenv("MQTT_CA")
    use_tls = bool(ca_file or certificate)
    if use_tls:
        client.tls_set(ca_certs=ca_file, certfile=certificate, keyfile=private_key)
    port = int(os.getenv("MQTT_PORT", "8883" if use_tls else "1883"))
    client.connect_async(hostname, port, keepalive=60)
    return client

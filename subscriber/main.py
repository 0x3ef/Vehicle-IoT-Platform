import json
import logging
import os
import re

import requests

from mqtt_config import TOPIC_SUFFIXES, connect_client


logger = logging.getLogger(__name__)
IDENTIFIER = re.compile(r"[A-Za-z0-9_-]{1,50}")


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        logger.error("MQTT connection rejected: %s", reason_code)
        return
    for sensor_type, suffix in TOPIC_SUFFIXES.items():
        client.subscribe(f"data/+/{sensor_type}/+/{suffix}", qos=1)
    logger.info("Subscribed to vehicle telemetry")


def api_payload(event, sensor_type):
    if sensor_type == "airbag":
        return {
            "airbag_activated": event["activated"],
            "location": event["location"],
            "timestamp": event["timestamp"],
        }
    if sensor_type == "fuel":
        return {
            "level": event["fuel_level"],
            "unit": event["unit"],
            "timestamp": event["timestamp"],
        }
    return event


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    api_base = os.getenv("TELEMETRY_API_BASE", "http://api:8000").rstrip("/")
    with requests.Session() as session:
        def on_message(client, userdata, message):
            try:
                _, vehicle, sensor_type, sensor, suffix = message.topic.split("/")
                if not (
                    suffix == TOPIC_SUFFIXES[sensor_type]
                    and IDENTIFIER.fullmatch(vehicle)
                    and IDENTIFIER.fullmatch(sensor)
                ):
                    raise ValueError("Invalid telemetry topic")
                event = json.loads(message.payload)
                if event["vehicle_id"] != vehicle or event["sensor_id"] != sensor:
                    raise ValueError("Telemetry identifiers do not match the topic")
                response = session.post(
                    f"{api_base}/data/{vehicle}/sensors/{sensor_type}/{sensor}",
                    json=api_payload(event, sensor_type),
                    timeout=5,
                )
                response.raise_for_status()
                result = response.json()
                if not isinstance(result, dict) or "message" not in result:
                    raise ValueError("API did not confirm the insert")
            except (KeyError, TypeError, ValueError, requests.RequestException) as exc:
                logger.error("Could not store event on %s: %s", message.topic, exc)

        client = connect_client("subscriber", on_connect=on_connect, on_message=on_message)
        client.loop_forever(retry_first_connection=True)


if __name__ == "__main__":
    main()

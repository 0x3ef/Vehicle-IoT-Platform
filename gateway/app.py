import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Annotated

import grpc
import sensors_pb2
import sensors_pb2_grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError
from websockets.asyncio.server import serve

from mqtt_config import TOPIC_SUFFIXES, connect_client


logger = logging.getLogger(__name__)
TopicID = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{1,50}$")]


class SensorEvent(BaseModel):
    vehicle_id: TopicID
    sensor_id: TopicID
    timestamp: str


class BatteryEvent(SensorEvent):
    voltage: float
    charge_level: int
    temperature: float
    status: str


class Location(BaseModel):
    latitude: float
    longitude: float


class AirbagEvent(SensorEvent):
    activated: bool
    location: Location


class FuelEvent(SensorEvent):
    fuel_level: float
    unit: str


async def publish(client, sensor_type, event):
    if not client.is_connected():
        raise RuntimeError("MQTT broker unavailable")
    suffix = TOPIC_SUFFIXES[sensor_type]
    topic = f"data/{event.vehicle_id}/{sensor_type}/{event.sensor_id}/{suffix}"
    message = client.publish(topic, event.model_dump_json(), qos=1)
    await asyncio.to_thread(message.wait_for_publish, timeout=5)
    if not message.is_published():
        raise RuntimeError("MQTT publish timed out")


class FuelSensorService(sensors_pb2_grpc.FuelSensorServiceServicer):
    def __init__(self, client):
        self.client = client

    async def SendFuelData(self, request, context):
        try:
            event = FuelEvent(
                vehicle_id=request.vehicle_id,
                sensor_id=request.sensor_id,
                timestamp=request.timestamp,
                fuel_level=request.fuel_level,
                unit=request.unit,
            )
            await publish(self.client, "fuel", event)
        except ValidationError:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid fuel event")
        except (RuntimeError, ValueError):
            await context.abort(grpc.StatusCode.UNAVAILABLE, "MQTT broker unavailable")
        return sensors_pb2.FuelSensorResponse(success=True, message="Published")


async def receive_airbag_events(websocket, client):
    async for payload in websocket:
        try:
            await publish(client, "airbag", AirbagEvent.model_validate_json(payload))
        except ValidationError:
            await websocket.send('{"status":"error","message":"Invalid airbag event"}')
        except (RuntimeError, ValueError):
            await websocket.send('{"status":"error","message":"MQTT broker unavailable"}')
        else:
            await websocket.send('{"status":"published"}')


@asynccontextmanager
async def lifespan(app):
    client = connect_client("gateway")
    client.loop_start()
    app.state.mqtt = client
    server = grpc.aio.server()
    sensors_pb2_grpc.add_FuelSensorServiceServicer_to_server(FuelSensorService(client), server)
    try:
        server.add_insecure_port("[::]:50051")
        await server.start()
        async with serve(lambda websocket: receive_airbag_events(websocket, client), "0.0.0.0", 8765):
            yield
    finally:
        await server.stop(grace=2)
        client.disconnect()
        client.loop_stop()


app = FastAPI(lifespan=lifespan)


@app.post("/api/vehicle/battery")
async def receive_battery_event(event: BatteryEvent):
    try:
        await publish(app.state.mqtt, "battery", event)
    except (RuntimeError, ValueError) as exc:
        logger.warning("Could not publish a battery event: %s", exc)
        raise HTTPException(status_code=503, detail="MQTT broker unavailable") from exc
    return {"status": "published"}

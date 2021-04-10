import logging
import json
from paho.mqtt.publish import single
from prometheus_client import start_http_server as start_prometheus, Gauge

from prometheus_client import REGISTRY
from contextlib import suppress


for name in list(REGISTRY._names_to_collectors.values()):
    with suppress(KeyError):
        REGISTRY.unregister(name)

start_prometheus(8081)

measurements = [
    'rpm',
    'coolantTemp',
    'airIntakeTemp',
    'battery',
    'map',
    'atmosphere',
    'throttlePosition',
    'sparkAdvance',
    'injectorPulse',
    'injectorDuty'
]

gauge_map = {m: Gauge(m, m) for m in measurements}

logger = logging.getLogger('ecu.publish')


# receive a frame.Frame and convert to json for publishing
def publish_frame(frame):
    logger.info("new frame received")

    info = {m: getattr(frame, m) for m in measurements}
    info['errors'] = frame.errors()
    single("ecu", json.dumps(info), client_id="ecu_monitor")

    for m in measurements:
        gauge_map[m].set(getattr(frame, m))

    #
    # info = {
    #     'rpm': frame.rpm,
    #     'coolantTemp': frame.coolantTemp,
    #     'intakeAirTemp': frame.airIntakeTemp,
    #     'batteryVoltage': frame.battery,
    #     'map': frame.map,
    #     'atmosphere': frame.vacuum,
    #     'throttlePosition': frame.throttlePosition,
    #     'sparkAdvance': frame.sparkAdvance,
    #     'injectorPulse': frame.injectorPulse,
    #     'injectorDuty': frame.injectorDuty,
    #     'gph': frame.gph,
    #     'errors': frame.errors()
    # }

    # send to MQTT server
    # https://tewarid.github.io/2019/04/03/installing-and-configuring-the-mosquitto-mqtt-broker.html
    # try:
    #     mqttc.publish("ecu", json.dumps(info))
    # except ConnectionRefusedError:
    #     logger.error("could not connect to mqtt")

import logging
import json
from paho.mqtt.publish import single


# receive a frame.Frame and convert to json for publishing
def publish_frame(frame):
    logger = logging.getLogger('ecu.publish')
    logger.info("new frame received")
    info = {
        'rpm': frame.rpm,
        'coolantTemp': frame.coolantTemp,
        'batteryVoltage': frame.volts12,
        'map': frame.map,
        'throttle': frame.throttlePosition,
    }

    # TODO : add credential
    single("ecu", json.dumps(info))

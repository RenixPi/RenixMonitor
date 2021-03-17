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
        'intakeAirTemp': frame.airIntakeTemp,
        'batteryVoltage': frame.battery,
        'map': frame.map,
        'atmosphere': frame.vacuum,
        'throttlePosition': frame.throttlePosition,
        'sparkAdvance': frame.sparkAdvance,
        'injectorPulse': frame.injectorPulse,
        'injectorDuty': frame.injectorDuty,
        'gph': frame.gph,
        'errors': frame.errors()
    }

    # send to MQTT server
    # https://tewarid.github.io/2019/04/03/installing-and-configuring-the-mosquitto-mqtt-broker.html
    # TODO : add credentials
    try:
        single("ecu", json.dumps(info))
    except ConnectionRefusedError:
        print("could not connect to mqtt")

from receiver import Receiver
import argparse
import serial
from time import sleep
from config import loggers
import logging.config
import logging
import json
from paho.mqtt.publish import single

logging.config.dictConfig(loggers)


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

    single("ecu", json.dumps(info))


def start_receiving(interface):

    s = serial.Serial(interface, baudrate=62500)
    r = Receiver(frame_receiver=publish_frame)

    while True:
        while s.in_waiting:
            b = s.read(1)
            r.process(b)

        sleep(1)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('interface')
    args = parser.parse_args()

    start_receiving(args.interface)

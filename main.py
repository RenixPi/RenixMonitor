from receiver import Receiver
import argparse
import serial
from time import sleep
from config import loggers
import logging.config
import logging
from publish import publish_frame

logging.config.dictConfig(loggers)


# main loop
# open the serial interface, create a receive.Receiver
def start_receiving(interface):

    s = serial.Serial(interface, baudrate=62500)
    r = Receiver(frame_receiver=publish_frame)

    while True:
        # check if there's data
        while s.in_waiting:
            # read data and then send for processing
            b = s.read(1)
            r.process(b)

        sleep(1)


if __name__ == "__main__":

    # require a serial interface as a parameter
    parser = argparse.ArgumentParser()
    parser.add_argument('interface')
    args = parser.parse_args()

    # begin receiving data
    start_receiving(args.interface)

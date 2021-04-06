from receiver import Receiver
import argparse
import serial
from time import sleep
from config import loggers
import logging.config
import logging
import toml
from publish import publish_frame
from receiver.receive import ECUType

logging.config.dictConfig(loggers)


#  RENIX 4.0L
#
#                                                                     SUPPLY
#                                                                       |
#                                        SUPPLY                         \
#                                          |                            / PULL
#                             DIAGNOSTIC   |                            \ UP
#                             CONNECTOR    |                            /
#                                |         \                            |       R 1K
#                                V         / PULL                       +------/\/\/\-------
#                                          \ UP                         |                 ^
#    12V ----------------------- D4        /                            |c                |
#                                          |              R 1K       b /                  |
#                       +------- D1 -------+-------------/\/\/\-------| 2N2309          UART
#                       |                           ^                  \                SIGNAL
#                       |c                          |                   |e
#                    b /                            |                   |
#     ECU ------------|                          INVERTED              GND
#                      \                         SERIAL
#                       |e                       SIGNAL
#                       +------- D7
#                       |
#                      GND
#
# D1 is an open collector to ground, allowing SUPPLY to any voltage needed for receiver (eg 3.3V or 5V)
# If voltage spike on supply is a concern, use opto-isolator on the inverted serial signal
# R 1K are current limiting resistors to prevent transistor or receiver from overloading
# Diagnostic connector uses standard (molex) 0.093" automotive pins
# Receiver can be anything that support UART : FTDI serial cable, arduino, esp8266/32 or raspberrypi


# main loop
# open the serial interface, create a receive.Receiver
def start_receiving(interface=None, baudrate=None):

    kwargs = {}

    if baudrate:
        kwargs['baudrate'] = baudrate

    s = serial.Serial(interface, **kwargs)
    r = Receiver(frame_receiver=publish_frame, ecu_type=ECUType.FourLiter)

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
    alt = parser.add_mutually_exclusive_group(required=False)

    alt.add_argument('-c', '--config')

    items = alt.add_argument_group('items', 'individual command line arguments')
    items.add_argument('-i', '--interface')
    items.add_argument('-b', '--baudrate')

    args = parser.parse_args()

    if args.interface:
        start_receiving(args.interface, args.baudrate)
    elif args.config:
        cfg = toml.load(args.config)
        start_receiving(cfg['renix']['uart'], cfg['renix']['baudrate'])
    else:
        exit("needed options not provided")

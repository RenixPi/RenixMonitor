import time
import logging


logger = logging.getLogger("ecu.units")


class UnitException(Exception):
    pass


class Pressure:

    VOLT = 1
    HG = 2
    KPA = 3
    PSI = 4

    @staticmethod
    def convert(raw, units=PSI):
        if units == Pressure.VOLT:
            return raw / 51.2
        if units == Pressure.HG:        # range 3.1 -> 31
            return raw / 9.13 + 3.1
        if units == Pressure.KPA:       # range 11 -> 105
            return raw / 2.7 + 11
        if units == Pressure.PSI:
            return raw / 18.6 + 1.5
        
        raise UnitException("incorrect pressure unit: {}".format(units))


class Temperature:

    CELSIUS = 1
    FAHRENHEIT = 2

    @staticmethod
    def convert(raw, units=FAHRENHEIT):
        if units == Temperature.CELSIUS:
            return raw * 0.625 - 40         # range -40 -> 119
        if units == Temperature.FAHRENHEIT:
            return raw * 1.125 - 40         # range -40 -> 247
        
        raise UnitException("incorrect temperature unit: {}".format(units))


class Volts12:

    @staticmethod
    def convert(raw):
        return raw / 16.24                  # range 0 -> 15.7


class Volts5:

    @staticmethod
    def convert(raw):
        return raw / 51.2                   # range 0 -> 4.98


# 1,000,000 * 60 / Pulses per Rotation(Cyl/2)
PULSES_PER_ROTATION = 1000000 * 60 / (6 / 2)


class RevPerMinute:

    @staticmethod
    def convert(lower, upper):

        gap = upper << 8 | lower
        logger.debug("gap: {} upper: 0x{:02} lower: 0x{:02X}".format(gap, upper, lower))
        if 255 < gap < 65280:
            rpm = int(PULSES_PER_ROTATION/ gap)
            return rpm
        return 0


class ThrottlePosition:

    @staticmethod
    def convert(raw):
        return raw / 2.55 # percentage 0 -> 100


class SparkAdvance:

    @staticmethod
    def convert(raw):
        return raw # degrees range 0 -> 255


def bitRead(raw, bit):
    return (raw >> bit) & b'0x1'


class IgnitionTiming:

    @staticmethod
    def convert(raw):
        iac_count = 1280
        iac_timer = 0
        iac_dir = False

        # IAC Moving
        if bitRead(raw, 4) != 0:
            iac_timer = time.time()

        # IAC Opening
        if bitRead(raw, 5) != 0:
            iac_count += 1
            iac_dir = True

        # IAC Closing
        elif bitRead(raw, 6) != 0:
            iac_count -= 1
            iac_dir = False

        iac_count = min(2550, max(0, iac_count))

        # number / 10 roughly keeps track of iac rotations
        return iac_count / 10

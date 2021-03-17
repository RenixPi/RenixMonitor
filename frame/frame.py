from abc import ABC

from .error_codes import ErrorCodes
from .units import Pressure, Temperature, Battery, O2, RevPerMinute, ThrottlePosition, SparkAdvance, IdleAirControl
from .units import bitRead, InjectorPulse
import logging


logger = logging.getLogger('ecu.frame')


class ImproperFrameSize(Exception):
    pass


class InvalidInjectorIndex(Exception):
    pass


# create abstract base class for different engine ecu
class Frame(ABC):
    pass


class FourLiterFrame(Frame):

    frame = None

    VERSION = 0
    PROM = 1
    STATUS = 2
    MAP = 3
    CTS = 4
    IAT = 5
    BATTERY = 6
    O2 = 7
    RPM_L = 8
    RPM_U = 9
    INJECTOR_SHORT = 10
    INJECTOR_OPEN = 11
    TPS = 12
    SPARK_ADV = 13
    IAC = 14
    # 15 ?
    ATMOSPHERE = 16
    # 17 ?
    EXHAUST = 18
    INJECTOR_PULSE = 19
    WATER_TEMP_SENSOR = 20
    THROTTLE = 21
    SPARK = 22
    # 23 ?
    SHORT_FUEL = 24
    # 25 IAT Target Offset?
    LONG_FUEL = 26
    KNOCK = 27
    # 28 ?
    STARTER = 29
    ERROR_CODES = 30

    injector_map = {
        "injector 1": 2,
        "injector 2": 6,
        "injector 3": 4,
        "injector 4": 7,
        "injector 5": 3,
        "injector 6": 5
    }

    def __init__(self, _frame):
        self.frame = _frame
        if len(self.frame) < 30:
            raise ImproperFrameSize("frame is undersized : {} bytes".format(len(self.frame)))

    def _convert(self, Conversion, location):
        return Conversion.convert(self.frame[location])

    @property
    def map(self):
        return self._convert(Pressure, Frame.MAP)

    @property
    def coolantTemp(self):
        return self._convert(Temperature, Frame.CTS)

    @property
    def airIntakeTemp(self):
        return self._convert(Temperature, Frame.IAT)

    @property
    def voltage(self):
        return self._convert(Battery, Frame.BATTERY)

    @property
    def o2(self):
        return self._convert(O2, Frame.O2)

    @property
    def rpm(self):
        return RevPerMinute.convert(self.frame[Frame.RPM_L],
                                    self.frame[Frame.RPM_U])

    @property
    def throttlePosition(self):
        return self._convert(ThrottlePosition, Frame.TPS)

    @property
    def sparkAdvance(self):
        return self._convert(SparkAdvance, Frame.SPARK_ADV)

    @property
    def idleAirControl(self):
        return self._convert(IdleAirControl, Frame.IAC)

    # barometric pressure before engine start
    @property
    def atmosphere(self):
        return self._convert(Pressure, Frame.ATMOSPHERE)

    @property
    def vacuum(self):
        return self.atmosphere - self.map

    def isInjectorShort(self, num):
        if num < 1 or num > 6:
            raise InvalidInjectorIndex("{}".format(num))
        return bool(bitRead(self.frame[Frame.INJECTOR_SHORT], self.injector_map["injector {}".format(num)]))

    def isInjectorOpen(self, num):
        if num < 1 or num > 6:
            raise InvalidInjectorIndex("{}".format(num))
        return bool(bitRead(self.frame[Frame.INJECTOR_OPEN], self.injector_map["injector {}".format(num)]))

    @property
    def exhaust(self):
        raise NotImplementedError("rich / lean not yet implemented")

    @property
    def injectorPulse(self):
        return self._convert(InjectorPulse, Frame.INJECTOR_PULSE)

    @property
    def injectorDuty(self):
        return (self.rpm * self.injectorPulse) / 1200

    injector_flow_rate = 18.927             # 4L engine

    @property
    def gph(self):
        return self.injector_flow_rate * self.injectorDuty

    @property
    def shortFuelTrim(self):
        raise NotImplementedError("short fuel trim not implemented")

    @property
    def longFuelTrim(self):
        raise NotImplementedError("long fuel trim not implemented")

    @property
    def knock(self):
        raise NotImplementedError("knock sensor not implemented")

    @property
    def fuelSync(self):
        raise NotImplementedError("fuel sync not implemented")

    @property
    def starter(self):
        raise NotImplementedError("starter not implemented")

    @property
    def acSwitch(self):
        raise NotImplementedError("a/c switch not implemented")

    @property
    def acRequest(self):
        raise NotImplementedError("a/c request not implemented")

    @property
    def nss(self):
        raise NotImplementedError("nss not implemented")

    def errors(self):
        errors = []
        for injNum, injName in enumerate(self.injector_map):
            if self.isInjectorOpen(injNum):
                errors += {'error': ErrorCodes.INJECTOR_OPEN, 'info': injName}
            if self.isInjectorShort(injNum):
                errors += {'error': ErrorCodes.INJECTOR_SHORT, 'info': injName}
        if bitRead(self.frame[Frame.WATER_TEMP_SENSOR], 1) != 0:
            errors += {'error': ErrorCodes.WATER_TEMP_SENSOR}

        error_bit_map = {
            ErrorCodes.ICM_SIGNAL_OPEN: 0,
            ErrorCodes.EGR_SOLENOID_OPEN: 2,
            ErrorCodes.BPLUS_RELAY_OPEN: 4,
            ErrorCodes.O2_RELAY_OPEN: 5,
            ErrorCodes.AC_RELAY_OPEN: 6
        }

        for err, bit in error_bit_map.items():
            if bitRead(self.frame[Frame.ERROR_CODES], bit) != 0:
                errors += {'error': err}

        return errors


# TODO : translate 2.5L data stream
class TwoPointFiveLiterFrame(Frame):
    pass

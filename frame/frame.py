from .units import Pressure, Temperature, Battery, O2, RevPerMinute, ThrottlePosition, SparkAdvance, IdleAirControl
from .units import bitRead
import logging


logger = logging.getLogger('ecu.frame')


class ImproperFrameSize(Exception):
    pass


class InvalidInjectorIndex(Exception):
    pass


class Frame:

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
    MAP_INITIAL = 15
    ENGINE = 16
    # 17 ?
    EXHAUST = 18
    INJECTOR = 19
    # 20 ?
    THROTTLE = 21
    SPARK = 22
    # 23 ?
    SHORT_FUEL = 24
    # 25 ?
    LONG_FUEL = 26
    KNOCK = 27
    # 28 ?
    STARTER = 29
    # 30 ? Error Codes

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
        return self._convert(Pressure, Frame.MAP_INITIAL)

    @property
    def vacuum(self):
        return self.atmosphere - self.map

    @property
    def isInjectorShort(self, num):
        if num < 1 or num > 6:
            raise InvalidInjectorIndex("{}".format(num))
        return bitRead(self.frame[Frame.INJECTOR_SHORT], self.injector_map["injector {}".format(num)])

    @property
    def isInjectorOpen(self, num):
        if num < 1 or num > 6:
            raise InvalidInjectorIndex("{}".format(num))
        return bitRead(self.frame[Frame.INJECTOR_OPEN], self.injector_map["injector {}".format(num)])



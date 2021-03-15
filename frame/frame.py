from .units import Pressure, Temperature, Volts12, Volts5, RevPerMinute, ThrottlePosition


class Frame:

    frame = None

    VERSION = 0
    PROM = 1
    STATUS = 2
    MAP = 3
    CTS = 4
    IAT = 5
    VOLTS12 = 6
    VOLTS5 = 7
    RPM_L = 8
    RPM_U = 9
    # 10 ? INJECTOR_ERROR
    # 11 ? INJECTOR_ERROR
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

    def __init__(self, _frame):
        self.frame = _frame

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
    def volts12(self):
        return self._convert(Volts12, Frame.VOLTS12)

    @property
    def volts5(self):
        return self._convert(Volts5, Frame.VOLTS5)

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
    def ignitionTiming(self):
        return self._convert(IgnitionTiming, Frame.IAC)

    # barometric pressure before engine start
    @property
    def mapInitial(self):
        return self._convert(Pressure, Frame.MAP_INITIAL)

    @property
    def vacuum(self):
        return self.mapInitial - self.map


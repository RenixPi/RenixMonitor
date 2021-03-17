class RenixProtocol:
    pass


class TwoPointFiveProtocol(RenixProtocol):
    pass


class FourLiterProtocol(RenixProtocol):

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

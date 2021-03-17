from abc import ABC

from .error_codes import ErrorCodes
from .protocol import FourLiterProtocol
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
    frame = None
    protocol = None
    injector_map = None
    injector_flow_rate = None

    def _convert(self, Conversion, location):
        return Conversion.convert(self.frame[location])

    @property
    def map(self):
        return self._convert(Pressure, self.protocol.MAP)

    @property
    def coolantTemp(self):
        return self._convert(Temperature, self.protocol.CTS)

    @property
    def airIntakeTemp(self):
        return self._convert(Temperature, self.protocol.IAT)

    @property
    def battery(self):
        return self._convert(Battery, self.protocol.BATTERY)

    @property
    def o2(self):
        return self._convert(O2, self.protocol.O2)

    @property
    def rpm(self):
        return RevPerMinute.convert(self.frame[self.protocol.RPM_L],
                                    self.frame[self.protocol.RPM_U])

    @property
    def throttlePosition(self):
        return self._convert(ThrottlePosition, self.protocol.TPS)

    @property
    def sparkAdvance(self):
        return self._convert(SparkAdvance, self.protocol.SPARK_ADV)

    @property
    def idleAirControl(self):
        return self._convert(IdleAirControl, self.protocol.IAC)

    # barometric pressure before engine start
    @property
    def atmosphere(self):
        return self._convert(Pressure, self.protocol.ATMOSPHERE)

    @property
    def vacuum(self):
        return self.atmosphere - self.map

    def isInjectorShort(self, num):
        if num < 1 or num > 6:
            raise InvalidInjectorIndex("{}".format(num))
        return bool(bitRead(self.frame[self.protocol.INJECTOR_SHORT], self.injector_map["injector {}".format(num)]))

    def isInjectorOpen(self, num):
        if num < 1 or num > 6:
            raise InvalidInjectorIndex("{}".format(num))
        return bool(bitRead(self.frame[self.protocol.INJECTOR_OPEN], self.injector_map["injector {}".format(num)]))

    # TODO : complete frame conversion
    # @property
    # def exhaust(self):
    #     raise NotImplementedError("rich / lean not yet implemented")

    @property
    def injectorPulse(self):
        return self._convert(InjectorPulse, self.protocol.INJECTOR_PULSE)

    @property
    def injectorDuty(self):
        return (self.rpm * self.injectorPulse) / 1200

    @property
    def gph(self):
        return self.injector_flow_rate * self.injectorDuty

    # TODO : complete frame conversions
    # @property
    # def shortFuelTrim(self):
    #     raise NotImplementedError("short fuel trim not implemented")
    #
    # @property
    # def longFuelTrim(self):
    #     raise NotImplementedError("long fuel trim not implemented")
    #
    # @property
    # def knock(self):
    #     raise NotImplementedError("knock sensor not implemented")
    #
    # @property
    # def fuelSync(self):
    #     raise NotImplementedError("fuel sync not implemented")
    #
    # @property
    # def starter(self):
    #     raise NotImplementedError("starter not implemented")
    #
    # @property
    # def acSwitch(self):
    #     raise NotImplementedError("a/c switch not implemented")
    #
    # @property
    # def acRequest(self):
    #     raise NotImplementedError("a/c request not implemented")
    #
    # @property
    # def nss(self):
    #     raise NotImplementedError("nss not implemented")


class FourLiterFrame(Frame):

    frame = None
    protocol = FourLiterProtocol
    injector_flow_rate = 18.927

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

    def errors(self):
        errors = []
        for injNum, injName in enumerate(self.injector_map):
            if self.isInjectorOpen(injNum+1):
                errors += {'error': ErrorCodes.INJECTOR_OPEN, 'info': injName}
            if self.isInjectorShort(injNum+1):
                errors += {'error': ErrorCodes.INJECTOR_SHORT, 'info': injName}
        if bitRead(self.frame[self.protocol.WATER_TEMP_SENSOR], 1) != 0:
            errors += {'error': ErrorCodes.WATER_TEMP_SENSOR}

        error_bit_map = {
            ErrorCodes.ICM_SIGNAL_OPEN: 0,
            ErrorCodes.EGR_SOLENOID_OPEN: 2,
            ErrorCodes.BPLUS_RELAY_OPEN: 4,
            ErrorCodes.O2_RELAY_OPEN: 5,
            ErrorCodes.AC_RELAY_OPEN: 6
        }

        for err, bit in error_bit_map.items():
            if bitRead(self.frame[self.protocol.ERROR_CODES], bit) != 0:
                errors += {'error': err}

        return errors


# TODO : translate 2.5L data stream
class TwoPointFiveLiterFrame(Frame):
    pass

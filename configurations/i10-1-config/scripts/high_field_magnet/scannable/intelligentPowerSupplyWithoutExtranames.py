"""
Oxford Diffraction Intelligent Power Supply (High Field Magnet) scannable,
for use with GDA at Diamond Light Source
"""

from gda.device.scannable import ScannableMotionBase
from high_field_magnet.device.intelligentPowerSupply import IntelligentPowerSupply


class IntelligentPowerSupplyField(ScannableMotionBase):

    def __init__(self, name, pvroot, field_tolerance):
        self.name = name

        self.ips = IntelligentPowerSupply(pvroot)
        self.field_tolerance = field_tolerance
        self.setpoint = 0

        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%f']

    def getPosition(self):
        return self.ips.getFieldDemand()

    def rawAsynchronousMoveTo(self, setpoint):
        self.setpoint = setpoint
        self.ips.setFieldSetPoint(setpoint)

    def stop(self):
        self.rawAsynchronousMoveTo(self.ips.getFieldDemand())

    def isBusy(self):
        return abs(self.setpoint - self.ips.getFieldDemand()) > self.field_tolerance


class IntelligentPowerSupplySweepRate(ScannableMotionBase):

    def __init__(self, name, pvroot, sweeprate_tolerance):
        self.name = name

        self.ips = IntelligentPowerSupply(pvroot)
        self. sweeprate_tolerance = sweeprate_tolerance
        self.setpoint = 0

        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%f']

    def getPosition(self):
        return self.ips.getSweepRateRBV()

    def rawAsynchronousMoveTo(self, setpoint):
        self.setpoint = setpoint
        self.ips.setSweepRate(setpoint)

    def stop(self):
        self.rawAsynchronousMoveTo(self.ips.getSweepRateRBV())

    def isBusy(self):
        return abs(self.setpoint - self.ips.getSweepRateRBV()) > self.sweeprate_tolerance

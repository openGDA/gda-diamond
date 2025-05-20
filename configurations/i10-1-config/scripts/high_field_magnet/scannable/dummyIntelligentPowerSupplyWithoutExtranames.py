"""
Oxford Diffraction Intelligent Power Supply (High Field Magnet) scannable,
for use with GDA at Diamond Light Source
"""

from gda.device.scannable import ScannableMotionBase


class DummyIntelligentPowerSupplyField(ScannableMotionBase):

    def __init__(self, name, field_tolerance):
        self.name = name
        self.field_tolerance = field_tolerance
        self.setpoint = 0.0
        self.demand_field = 0.0
        self.increment = 0.0

        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%f']

    def getPosition(self):
        return self.setpoint

    def rawAsynchronousMoveTo(self, setpoint):
        self.setpoint = setpoint
        self.increment = (setpoint - self.demand_field) / 10

    def stop(self):
        self.rawAsynchronousMoveTo(self.demand_field)

    def isBusy(self):
        self.demand_field += self.increment
        return abs(self.setpoint - self.demand_field) > self.field_tolerance


class DummyIntelligentPowerSupplySweepRate(ScannableMotionBase):

    def __init__(self, name, sweeprate_tolerance):
        self.name = name
        self. sweeprate_tolerance = sweeprate_tolerance
        self.setpoint = 0
        self.demand_field = 0.0
        self.increment = 0.0
        self.readback = 0.0

        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%f']

    def getPosition(self):
        return self.readback

    def rawAsynchronousMoveTo(self, setpoint):
        self.setpoint = setpoint
        self.readback = setpoint

    def stop(self):
        self.rawAsynchronousMoveTo(self.readback)

    def isBusy(self):
        return abs(self.setpoint - self.readback) > self.sweeprate_tolerance

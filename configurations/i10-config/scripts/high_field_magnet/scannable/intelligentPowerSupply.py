"""
Oxford Diffraction Intelligent Power Supply (High Field Magnet) scannable,
for use with GDA at Diamond Light Source
"""

from gda.device.scannable import ScannableMotionBase
from high_field_magnet.device.intelligentPowerSupply import IntelligentPowerSupply

class IntelligentPowerSupplyFieldScannable(ScannableMotionBase):

    def __init__(self, name, pvroot, field_tolerance):
        self.name = name
        
        self.ips = IntelligentPowerSupply(pvroot)
        self.field_tolerance = field_tolerance
        self.setpoint = 0
        
        self.inputNames = [name]
        self.extraNames = ['demand_field']
        self.outputFormat = ['%f', '%f']

    def __repr__(self):
        return "IntelligentPowerSupplyFieldScannable(%r, %r)" % (
            self.name, self.ips.pvs.pvroot)

    def __str__(self):
        return self.name + ": setpoint=%f, demand_field=%f" % self.getPosition()

    def getPosition(self):
        return (self.ips.getFieldSetPointRBV(), self.ips.getFieldDemand())

    def rawAsynchronousMoveTo(self, setpoint):
        self.setpoint = setpoint
        self.ips.setFieldSetPoint(setpoint)

    def stop(self):
        self.rawAsynchronousMoveTo(self.ips.getFieldDemand())

    def isBusy(self):
        return abs(self.setpoint - self.ips.getFieldDemand()) > self.field_tolerance

class IntelligentPowerSupplySweepRateScannable(ScannableMotionBase):

    def __init__(self, name, pvroot, sweeprate_tolerance):
        self.name = name
        
        self.ips = IntelligentPowerSupply(pvroot)
        self. sweeprate_tolerance = sweeprate_tolerance
        self.setpoint = 0
        
        self.inputNames = [name]
        self.extraNames = ['demand_field']
        self.outputFormat = ['%f', '%f']

    def __repr__(self):
        return "IntelligentPowerSupplySweepRateScannable(%r, %r)" % (
            self.name, self.ips.pvs.pvroot)

    def __str__(self):
        return self.name + ": setpoint=%f, demand_field=%f" % self.getPosition()

    def getPosition(self):
        return (self.ips.getSweepRateRBV(), self.ips.getFieldDemand())

    def rawAsynchronousMoveTo(self, setpoint):
        self.setpoint = setpoint
        self.ips.setSweepRate(setpoint)

    def stop(self):
        self.rawAsynchronousMoveTo(self.ips.getSweepRateRBV())

    def isBusy(self):
        return abs(self.setpoint - self.ips.getSweepRateRBV()) > self.sweeprate_tolerance

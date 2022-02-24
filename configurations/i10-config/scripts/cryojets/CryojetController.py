"""
Oxford Diffraction Cryojet Intelligent Temperature Controller (ITC) device,
for use with GDA at Diamond Light Source
"""

class CryojetController():

    def __init__(self, pvroot, setpoint, sensorpoint):
        if isinstance(pvroot, str):
            from gdascripts.scannable.epics.PvManager import PvManager
            
            self.pvs = PvManager({'setpoint':   setpoint,
                                  'sensor':     sensorpoint}, pvroot)
            self.pvs.configure()
        else:
            self.pvs = pvroot
            self.pvs.pvroot = ""

    def __repr__(self):
        return "CryojetController(pvroot=%r)" % (
            self.pvs.pvroot)

    def __str__(self):
        return "setpoint=%f, sensor=%f" % (
            self.getTempSetPoint(), self.getTempSensor())

    def setTempSetPoint(self, setpoint):
        self.pvs['setpoint'].caput(setpoint)

    def getTempSetPoint(self):
        return float(self.pvs['setpoint'].caget())

    def getTempSensor(self):
        return float(self.pvs['sensor'].caget())
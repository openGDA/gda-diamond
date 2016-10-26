"""
Oxford Diffraction Cryojet Intelligent Temperature Controller (ITC) device,
for use with GDA at Diamond Light Source
"""


"""
    <OxInstCryojet desc="Magnet Intelligent Temperature Controller J1" name="MAGJ1.ITCJ1">
        <PGAIN_SET desc="set pid p"         pv="BL10J-EA-TCTRL-01:P:SET" ro="false" type="pv"/>
        <IGAIN_SET desc="set pid i"         pv="BL10J-EA-TCTRL-01:I:SET" ro="false" type="pv"/>
        <DGAIN_SET desc="set pid d"         pv="BL10J-EA-TCTRL-01:D:SET" ro="false" type="pv"/>
        <TEMP_SET desc="set target temp"    pv="BL10J-EA-TCTRL-01:TTEMP:SET" ro="false" type="pv"/>
        <SENSOR_TEMP desc="get sensor temp" pv="BL10J-EA-TCTRL-01:STEMP" ro="true" type="pv"/>
        <DISABLE desc="disable comms"       pv="BL10J-EA-TCTRL-01:DISABLE" ro="false" type="binary"/>
    </OxInstCryojet>
"""

class CryojetController():

    def __init__(self, pvroot):
        if isinstance(pvroot, str):
            from gdascripts.scannable.epics.PvManager import PvManager
            
            self.pvs = PvManager({'setpoint':   'TTEMP:SET',
                                  'sensor':     'STEMP'}, pvroot)
            self.pvs.configure()
        else:
            self.pvs = pvroot
            self.pvs.pvroot = ""

    def __repr__(self):
        return "CryojetController(pvroot=%r)" % (
            self.pvs.pvroot)

    def __str__(self):
        return "setpoint=%f, sensor=%f" % (
            self.getTempSetPoint(), self.getSensorTemp())

    def setTempSetPoint(self, setpoint):
        self.pvs['setpoint'].caput(setpoint)

    def getTempSetPoint(self):
        return float(self.pvs['setpoint'].caget())

    def getTempSensor(self):
        return float(self.pvs['sensor'].caget())
"""
Oxford Diffraction Intelligent Power Supply (High Field Magnet) device,
for use with GDA at Diamond Light Source
"""

"""
    <OxInstIPS desc="Magnet Intelligent Power Supply J1" name="MAGJ1.IPS">
        <DISABLE desc="disable comms" pv="BL10J-EA-SMC-01:DISABLE" ro="false" type="binary"/>
        <RBV_DEMANDFIELD desc="demand field readback" pv="BL10J-EA-SMC-01:RBV:DEMANDFIELD" ro="true" type="pv"/>
        <RBV_SETPOINTFIELD desc="setpoint field readback" pv="BL10J-EA-SMC-01:RBV:SETPOINTFIELD" ro="true" type="pv"/>
        <RBV_FIELDSWEEPRATE desc="field sweep rate readback" pv="BL10J-EA-SMC-01:RBV:FIELDSWEEPRATE" ro="true" type="pv"/>
        <STS_ACTIVITY desc="activity status" pv="BL10J-EA-SMC-01:STS:ACTIVITY" ro="true" type="mbbinary"/>
        <STS_SWEEPMODESWEEP desc="mode status" pv="BL10J-EA-SMC-01:STS:SWEEPMODE:SWEEP" ro="true" type="mbbinary"/>
        <STS_SWEEPMODETYPE desc="fast/slow sweep" pv="BL10J-EA-SMC-01:STS:SWEEPMODE:TYPE" ro="true" type="binary"/>
        <SET_ACTIVITY desc="activity control" pv="BL10J-EA-SMC-01:SET:ACTIVITY" ro="false" type="mbbinary"/>
        <SET_SETPOINTFIELD desc="set setpoint field" pv="BL10J-EA-SMC-01:SET:SETPOINTFIELD" ro="false" type="pv"/>
        <SET_FIELDSWEEPRATE desc="set field sweep rate" pv="BL10J-EA-SMC-01:SET:FIELDSWEEPRATE" ro="false" type="pv"/>
        <SET_SWEEPMODETYPE desc="fast/slow sweep" pv="BL10J-EA-SMC-01:SET:SWEEPMODE:TYPE" ro="false" type="binary"/>
    </OxInstIPS>

    Used:
        <SET_SETPOINTFIELD desc="set setpoint field"         pv="BL10J-EA-SMC-01:SET:SETPOINTFIELD" ro="false" type="pv"/>
        <RBV_SETPOINTFIELD desc="setpoint field readback"    pv="BL10J-EA-SMC-01:RBV:SETPOINTFIELD" ro="true" type="pv"/>
        <SET_FIELDSWEEPRATE desc="set field sweep rate"      pv="BL10J-EA-SMC-01:SET:FIELDSWEEPRATE" ro="false" type="pv"/>
        <RBV_FIELDSWEEPRATE desc="field sweep rate readback" pv="BL10J-EA-SMC-01:RBV:FIELDSWEEPRATE" ro="true" type="pv"/>
        <RBV_DEMANDFIELD desc="demand field readback"        pv="BL10J-EA-SMC-01:RBV:DEMANDFIELD" ro="true" type="pv"/>
    
    Not used:

        <STS_ACTIVITY desc="activity status"                 pv="BL10J-EA-SMC-01:STS:ACTIVITY" ro="true" type="mbbinary"/>
        <STS_SWEEPMODESWEEP desc="mode status"               pv="BL10J-EA-SMC-01:STS:SWEEPMODE:SWEEP" ro="true" type="mbbinary"/>
        <STS_SWEEPMODETYPE desc="fast/slow sweep"            pv="BL10J-EA-SMC-01:STS:SWEEPMODE:TYPE" ro="true" type="binary"/>

        <SET_ACTIVITY desc="activity control"                pv="BL10J-EA-SMC-01:SET:ACTIVITY" ro="false" type="mbbinary"/>
        <SET_SWEEPMODETYPE desc="fast/slow sweep"            pv="BL10J-EA-SMC-01:SET:SWEEPMODE:TYPE" ro="false" type="binary"/>
        
        pvroot = 'BL10J-EA-SMC-01:'
"""

class IntelligentPowerSupply():

    def __init__(self, pvroot):
        if isinstance(pvroot, str):
            from gdascripts.scannable.epics.PvManager import PvManager
            
            self.pvs = PvManager({'setpoint':     'SET:SETPOINTFIELD',
                                  'setpointRbv':  'RBV:SETPOINTFIELD',
                                  'sweeprate':    'SET:FIELDSWEEPRATE',
                                  'sweeprateRbv': 'RBV:FIELDSWEEPRATE',
                                  'demand_field': 'RBV:DEMANDFIELD'}, pvroot)
            self.pvs.configure()
        else:
            self.pvs = pvroot
            self.pvs.pvroot = ""

    def __repr__(self):
        return "IntelligentPowerSupplyScannable(%r)" % (
            self.pvs.pvroot)

    def __str__(self):
        return "setpoint=%f, demand_field=%f" % (
            self.getFieldSetPoint(), self.getFieldDemand())

    def getFieldSetPoint(self):
        return float(self.pvs['setpoint'].caget())

    def setFieldSetPoint(self, setpoint):
        self.pvs['setpoint'].caput(setpoint)

    def getFieldSetPointRBV(self):
        return float(self.pvs['setpointRbv'].caget())

    def getSweepRate(self):
        return float(self.pvs['sweeprate'].caget())

    def setSweepRate(self, setpoint):
        self.pvs['sweeprate'].caput(setpoint)

    def getSweepRateRBV(self):
        return float(self.pvs['sweeprateRbv'].caget())

    def getFieldDemand(self):
        return float(self.pvs['demand_field'].caget())

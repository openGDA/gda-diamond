'''

Created on 10 Apr 2018

@author: fy65
'''
from gdascripts.pd.epics_pds import EpicsReadWritePVClass
from utils.ExceptionLogs import localStation_exception
import installation

print("-"*100)
print("Creating scannables for High Field Magnet control using EPICS PV directly:")
print("    1. 'ips_field'     - the demand field")
print("    2. 'ips_sweeprate' - the sweep rate")
print("    3. 'itc2'          - the temperature controller 2")
print("    4. 'itc3'          - the temperature controller 3")
print("    5. 'hfmpitch_off' - the rotation offset")

if installation.isLive():
    try:
        from high_field_magnet.scannable.intelligentPowerSupply import IntelligentPowerSupplyFieldScannable,IntelligentPowerSupplySweepRateScannable
        from cryojets.CryojetScannable import CryojetScannable
        
        ips_field = IntelligentPowerSupplyFieldScannable('ips_field', 'BL10J-EA-SMC-01:', field_tolerance=0.01)
        ips_sweeprate = IntelligentPowerSupplySweepRateScannable('ips_sweeprate', 'BL10J-EA-SMC-01:', sweeprate_tolerance=0.01)
        itc2 = CryojetScannable('itc2',pvroot='BL10J-EA-TCTRL-02:', setpoint="TTEMP:SET", sensorpoint="STEMP", temp_tolerance=1, stable_time_sec=60)
        itc3 = CryojetScannable('itc3',pvroot='BL10J-EA-TCTRL-03:', setpoint="TTEMP:SET", sensorpoint="STEMP3", temp_tolerance=1, stable_time_sec=60)
        ips_field.setLevel(6)
        ips_sweeprate.setLevel(6)
        itc2.setLevel(6)
        itc3.setLevel(6)
        hfmpitch_off = EpicsReadWritePVClass('hfmpitch_off', 'BL10J-EA-MAG-01:INSERT:ROTY.OFF', 'deg', '%.6f')
    except:
        import sys
        localStation_exception(sys.exc_info(), "initialising high field magnet")
else:
    from high_field_magnet.scannable.dummyIntelligentPowerSupply import DummyIntelligentPowerSupplyFieldScannable, DummyIntelligentPowerSupplySweepRateScannable
    from cryojets.dummyCryojetScannable import DummyCryojetScannable
    from gdascripts.pd.dummy_pds import DummyEpicsReadWritePVClass
    ips_field = DummyIntelligentPowerSupplyFieldScannable('ips_field', field_tolerance=0.01)
    ips_sweeprate = DummyIntelligentPowerSupplySweepRateScannable('ips_sweeprate', sweeprate_tolerance=0.01)
    itc2 = DummyCryojetScannable('itc2', temp_tolerance=1, stable_time_sec=60)
    itc3 = DummyCryojetScannable('itc3', temp_tolerance=1, stable_time_sec=60)
    ips_field.setLevel(6)
    ips_sweeprate.setLevel(6)
    itc2.setLevel(6)
    itc3.setLevel(6)
    hfmpitch_off = DummyEpicsReadWritePVClass('hfmpitch_off', 0.0, 30.0, 'deg', '%.6f')

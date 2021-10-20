'''
Created on 10 Apr 2018

@author: fy65
'''
from gdascripts.pd.epics_pds import EpicsReadWritePVClass
from utils.ExceptionLogs import localStation_exception
import installation

print "-"*100
print "Creating scannables for High Field Magnet control using EPICS PV directly:"
print "    1. 'ips_field'     - the demand field"
print "    2. 'ips_sweeprate' - the sweep rate"
print "    3. 'itc2'          - the temperature controller"
print "    4. 'magj1yrot_off' - the rotation offset"

if installation.isLive():
    try:
        from high_field_magnet.scannable.intelligentPowerSupply import IntelligentPowerSupplyFieldScannable,IntelligentPowerSupplySweepRateScannable
        from dls_scripts.scannable.CryojetScannable import CryojetScannable
        
        ips_field = IntelligentPowerSupplyFieldScannable('ips_field', 'BL10J-EA-SMC-01:', field_tolerance=0.01)
        ips_sweeprate = IntelligentPowerSupplySweepRateScannable('ips_sweeprate', 'BL10J-EA-SMC-01:', sweeprate_tolerance=0.01)
        itc2 = CryojetScannable('itc2',pvroot='BL10J-EA-TCTRL-02:', temp_tolerance=1, stable_time_sec=60)
        ips_field.setLevel(6)
        ips_sweeprate.setLevel(6)
        itc2.setLevel(6)
        hfmpitch_off = EpicsReadWritePVClass('hfmpitch_off', 'BL10J-EA-MAG-01:INSERT:ROTY.OFF', 'deg', '%.6f')
    except:
        localStation_exception(sys.exc_info(), "initialising high field magnet")
else:
    from high_field_magnet.scannable.dummyIntelligentPowerSupply import DummyIntelligentPowerSupplyFieldScannable, DummyIntelligentPowerSupplySweepRateScannable
    from high_field_magnet.scannable.dummyCryojetScannable import DummyCryojetScannable
    from gdascripts.pd.dummy_pds import DummyEpicsReadWritePVClass
    ips_field = DummyIntelligentPowerSupplyFieldScannable('ips_field', field_tolerance=0.01)
    ips_sweeprate = DummyIntelligentPowerSupplySweepRateScannable('ips_sweeprate', sweeprate_tolerance=0.01)
    itc2 = DummyCryojetScannable('itc2',pvroot='BL10J-EA-TCTRL-02:', temp_tolerance=1, stable_time_sec=60)
    ips_field.setLevel(6)
    ips_sweeprate.setLevel(6)
    itc2.setLevel(6)
    hfmpitch_off = DummyEpicsReadWritePVClass('hfmpitch_off', 0.0, 30.0, 'deg', '%.6f')

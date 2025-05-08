print("\nRunning signal_generator.py")

from gda.device.scannable import PVScannable

#Seems good enougt - value seems to have been applied to PV once callback is received
# Need to have reasonable timeout : gda.epics.request.timeout set to 5 seconds seems ok.
# MultiPVScannable also tested, but isBusy doesn't compare demand vs readback
 
read_pv_name="BL20J-EA-AFG-01:CHAN1:AMPLITUDE:HIGH_RBV"
write_pv_name="BL20J-EA-AFG-01:CHAN1:AMPLITUDE:HIGH"

ampl_high_level = PVScannable("ampl_high_level", write_pv_name)
ampl_high_level.configure()

ampl_high_level_rbv = PVScannable("ampl_high_level_rbv", read_pv_name)
ampl_high_level_rbv.setCanMove(False)
ampl_high_level_rbv.configure()


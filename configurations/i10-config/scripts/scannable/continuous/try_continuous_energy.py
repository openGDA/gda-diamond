# run 'scannable/continuous/try_continuous_energy.py'
# When reloading, you may need to run this twice

from future.scannable.scaler import McsController, McsChannelScannable
from gda.device.detector.hardwaretriggerable import \
    DummyHardwareTriggerableDetector
from gda.scan import ConstantVelocityScanLine
from gdascripts.scan import trajscans
from gdascripts.scan.scanListener import ScanListener
from scannable.continuous.energy import ContinuousEnergyMoveController, \
    ContinuousEnergyScannable

try:
    del cemc
    del egy
    del st
    del mcs_controller
    del mcs1
    del mcs2
    del mcs3
    del mcs4
    del cvscan
    import future.scannable.scaler
    reload(future.scannable.scaler)
    import scannable.continuous.energy
    reload(scannable.continuous.energy)
except NameError:
    print ('NameError')
    pass

cemc = ContinuousEnergyMoveController()
egy = ContinuousEnergyScannable('egy', cemc)

st = DummyHardwareTriggerableDetector('st')
st.setHardwareTriggerProvider(cemc)

# RASOR counter:    ME01D-EA-SCLR-01:MCA01:
counterBasePv =    'ME01D-EA-SCLR-01:MCA01:'
# I branch counter: BL10I-DI-SCLR-01:MCA01:

mcs_controller = McsController(counterBasePv)
mcs1 = McsChannelScannable('mcs1', mcs_controller, counterBasePv, 1)
mcs1.setHardwareTriggerProvider(cemc)
mcs2 = McsChannelScannable('mcs2', mcs_controller, counterBasePv, 2)
mcs2.setHardwareTriggerProvider(cemc)
mcs3 = McsChannelScannable('mcs3', mcs_controller, counterBasePv, 3)
mcs3.setHardwareTriggerProvider(cemc)
mcs4 = McsChannelScannable('mcs4', mcs_controller, counterBasePv, 4)
mcs4.setHardwareTriggerProvider(cemc)


class TrajectoryControllerHelper(ScanListener):
    
    def prepareForScan(self):
        print "TrajectoryControllerHelper.prepareForScan"

    def update(self, scanObject):
        print "TrajectoryControllerHelper.update"


trajscans.DEFAULT_SCANNABLES_FOR_TRAJSCANS = [meta] # @UndefinedVariable

trajectory_controller_helper = TrajectoryControllerHelper()

print "Creating gda trajscan commands:"
# These will need more classes added to /uk.ac.gda.core/scripts/gdascripts/scan/trajscans.py
#trajcscan=trajscans.TrajCscan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
#trajrscan=trajscans.TrajRscan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
cvscan=trajscans.CvScan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
alias('cvscan') #@UndefinedVariable

# E.g. cvscan egy 0 20 1 mcs1 .5
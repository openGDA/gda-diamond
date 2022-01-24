from gdascripts.scannable.dummy import SingleInputDummy, SingleInputStringDummy
from gdascripts.scannable.beamokay import WaitWhileScannableBelowThreshold, WaitForScannableState
from gda.device.scannable.scannablegroup import ScannableGroup
dummyrc = SingleInputDummy('dummyrc')
dummyfe = SingleInputStringDummy('dummyfe')

dummycheckrc = WaitWhileScannableBelowThreshold('dummycheckrc', dummyrc, 300, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=5)
dummycheckfe = WaitForScannableState('dummycheckfe', dummyfe, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=0)

dummycheckbeam = ScannableGroup('dummycheckbeam', [dummycheckrc,  dummycheckfe])
dummycheckbeam.configure()
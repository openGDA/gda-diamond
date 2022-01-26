from gdascripts.scannable.dummy import SingleInputDummy, SingleInputStringDummy
from gdascripts.scannable.beamokay import WaitWhileScannableBelowThreshold, WaitForScannableState
from gda.device.scannable.scannablegroup import ScannableGroup
dummyrc = SingleInputDummy('dummyrc')
dummyfe = SingleInputStringDummy('dummyfe')

checkrc = WaitWhileScannableBelowThreshold('checkrc', rc, 300, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=5)
checkfe = WaitForScannableState('checkfe', frontend, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=0)

newcheckbeam = ScannableGroup('newcheckbeam', [newcheckrc,  newcheckfe])
newcheckbeam.configure()
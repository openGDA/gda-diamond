from gda.device.scannable import DummyScannable
from gda.device.detector.nxdetector.andor.proc.FlatAndDarkFieldPlugin import ScanType
from scanForImageCorrection import ScanForImageCorrection
import time
from gda.epics import CAClient

scannable = DummyScannable()
scannable.setName("correctionDummy")
CAClient().put("BL08I-EA-DET-01:ARR:NDArrayPort","DET1.proc")
time.sleep(1)
CAClient().put("BL08I-EA-DET-01:ARR:ArrayCounter","0")
time.sleep(1)
scanForImageCorrection.createScanForImageCorrection(ScanType.FLAT_FIELD,scannable, 1)
del scannable
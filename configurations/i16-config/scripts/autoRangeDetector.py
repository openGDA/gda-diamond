from time import sleep
from gdascripts.scannable.detector.ProcessingDetectorWrapper import SwitchableHardwareTriggerableProcessingDetectorWrapper
from gda.scan import ScanBase
from misc_functions import list_scannables, listprint, frange, attributes, caput, caget, cagetArray, add, mult
class AutoRangeDetector(SwitchableHardwareTriggerableProcessingDetectorWrapper):
	
	def collectData(self):
		caput("BL16I-DI-COR-01:CAM:TriggerSource", "FixedRate")
		caput("BL16I-DI-COR-01:CAM:AcquirePeriod", "0.1")
		caput("BL16I-DI-COR-01:CAM:GainAuto", "Off")
		caput("BL16I-DI-COR-01:CAM:Gain", 0)
		caput("BL16I-DI-COR-01:TIFF:EnableCallbacks", 0)
		caput("BL16I-DI-COR-01:CAM:ImageMode","Continuous")
		caput("BL16I-DI-COR-01:CAM:Acquire","1")
		# let the camera do an auto gain for entire range (should just saturate)
		caput("BL16I-DI-COR-01:CAM:ExposureAutoMin","21")
		caput("BL16I-DI-COR-01:CAM:ExposureAutoMax","500000")
		caput("BL16I-DI-COR-01:CAM:ExposureAutoAlg", "FitRange")
		caput("BL16I-DI-COR-01:CAM:ExposureAuto", "Once")
		sleep(0.1)
		while caget('BL16I-DI-COR-01:CAM:ExposureAuto_RBV') != '0':
			ScanBase.checkForInterrupts()
			sleep(0.1)
		
		caput("BL16I-DI-COR-01:CAM:Acquire","0")
		caput("BL16I-DI-COR-01:CAM:ImageMode","Single")
		caput("BL16I-DI-COR-01:TIFF:EnableCallbacks", 1)
		SwitchableHardwareTriggerableProcessingDetectorWrapper.collectData(self)

	def atScanEnd(self):
		SwitchableHardwareTriggerableProcessingDetectorWrapper.atScanEnd(self)
		caput("BL16I-DI-COR-01:CAM:ImageMode","Continuous")
		caput("BL16I-DI-COR-01:CAM:Acquire","1")

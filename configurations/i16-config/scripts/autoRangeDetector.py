from time import sleep, time
from gdascripts.scannable.detector.ProcessingDetectorWrapper import SwitchableHardwareTriggerableProcessingDetectorWrapper
from gda.scan import ScanBase
from misc_functions import list_scannables, listprint, frange, attributes, caput, caget, cagetArray, add, mult
class AutoRangeDetector(SwitchableHardwareTriggerableProcessingDetectorWrapper):

	def __init__(
				self,
				name,
				detector,
				hardware_triggered_detector,
				detector_for_snaps,
				rootPv,
				processors=[],
				panel_name=None,
				toreplace=None,
				replacement=None,
				iFileLoader=None,
				root_datadir=None,
				fileLoadTimout=None,
				printNfsTimes=False,
				returnPathAsImageNumberOnly=False,
				panel_name_rcp=None,
				return_performance_metrics=False,
				array_monitor_for_hardware_triggering=None):
		
		self.rootPv = rootPv
		SwitchableHardwareTriggerableProcessingDetectorWrapper.__init__(
																	self,
																	name,
																	detector,
																	hardware_triggered_detector,
																	detector_for_snaps,
																	processors,
																	panel_name,
																	toreplace,
																	replacement,
																	iFileLoader,
																	root_datadir,
																	fileLoadTimout,
																	printNfsTimes,
																	returnPathAsImageNumberOnly,
																	panel_name_rcp,
																	return_performance_metrics,
																	array_monitor_for_hardware_triggering)


	def collectData(self):
		caput(self.rootPv + "CAM:TriggerSource", "FixedRate")
		caput(self.rootPv + "CAM:AcquirePeriod", "0.1")
		caput(self.rootPv + "CAM:GainAuto", "Off")
		caput(self.rootPv + "CAM:Gain", 0)
		caput(self.rootPv + "TIFF:EnableCallbacks", 0)
		caput(self.rootPv + "CAM:ImageMode","Continuous")
		caput(self.rootPv + "CAM:Acquire","0")
		caput(self.rootPv + "CAM:Acquire","1")
		# let the camera do an auto gain for entire range (should just saturate)
		caput(self.rootPv + "CAM:ExposureAutoMin","21")
		caput(self.rootPv + "CAM:ExposureAutoMax","500000")
		caput(self.rootPv + "CAM:ExposureAutoAlg", "FitRange")
		caput(self.rootPv + "CAM:ExposureAuto", "Once")
		sleep(0.1)
		startWait = time()
		while caget(self.rootPv + "CAM:ExposureAuto_RBV") != "0":
			sleep(0.1)
			if time() - startWait > 5: #sometimes the auto gain fails and wait forever
				print "Timeout waiting for auto exposure"
				break
		caput(self.rootPv + "CAM:Acquire","0")
		caput(self.rootPv + "CAM:ImageMode","Single")
		caput(self.rootPv + "TIFF:EnableCallbacks", 1)
		SwitchableHardwareTriggerableProcessingDetectorWrapper.collectData(self)

	def atScanEnd(self):
		SwitchableHardwareTriggerableProcessingDetectorWrapper.atScanEnd(self)
		caput(self.rootPv + "CAM:ImageMode","Continuous")
		caput(self.rootPv + "CAM:Acquire","0")
		caput(self.rootPv + "CAM:Acquire","1")

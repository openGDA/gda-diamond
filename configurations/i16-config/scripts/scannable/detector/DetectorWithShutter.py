from gda.device.detector import PassthroughDetectorWrapper
from time import sleep
class DetectorWithShutter(PassthroughDetectorWrapper):
	
	def __init__(self, detector, shutter_scannable, sleep_time_after_shutter_open=.4):
		PassthroughDetectorWrapper.__init__(self, detector)
		self.shutter_scannable = shutter_scannable
		self.sleep_time_after_shutter_open = sleep_time_after_shutter_open
	
	def getName(self):
		return PassthroughDetectorWrapper.getName(self) + 's'
	
	def collectData(self):
		self.shutter_scannable(1)
		sleep(self.sleep_time_after_shutter_open)
		PassthroughDetectorWrapper.collectData(self)
		self.waitWhileBusy()
		self.shutter_scannable(0)
		
		
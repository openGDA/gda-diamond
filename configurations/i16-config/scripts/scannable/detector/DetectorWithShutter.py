from gda.device.detector import PassthroughDetectorWrapper
from gda.device.scannable import PositionCallableProvider
from time import sleep
from gda.device import DetectorSnapper

class DetectorWithShutter(PassthroughDetectorWrapper, DetectorSnapper, PositionCallableProvider):
	
	def __init__(self, detector, shutter_scannable, sleep_time_after_shutter_open=.4):
		PassthroughDetectorWrapper.__init__(self, detector)
		self.shutter_scannable = shutter_scannable
		self.sleep_time_after_shutter_open = sleep_time_after_shutter_open
		self._delegate_detector = detector
	
	def getName(self):
		return PassthroughDetectorWrapper.getName(self) + 's'
	
	def collectData(self):
		self.shutter_scannable(1)
		sleep(self.sleep_time_after_shutter_open)
		PassthroughDetectorWrapper.collectData(self)
		self.waitWhileBusy()
		self.shutter_scannable(0)
		
	def prepareForAcquisition(self, collection_time):
		self._delegate_detector.setCollectionTime(collection_time)

	def acquire(self):
		self.shutter_scannable(1)
		sleep(self.sleep_time_after_shutter_open)
		self._delegate_detector.acquire()
		self.shutter_scannable(0)

	def getPositionCallable(self):
		return self.getDelegate().getPositionCallable()

	def getFilepathRelativeToRootDataDir(self):
		return self.getDelegate().getFilepathRelativeToRootDataDir()

#	public double getAcquireTime() throws Exception;

#	public double getAcquirePeriod() throws Exception;
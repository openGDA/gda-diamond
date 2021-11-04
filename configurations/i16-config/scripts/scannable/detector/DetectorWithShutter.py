from gda.device.detector import PassthroughDetectorWrapper
from gda.device.scannable import PositionCallableProvider
from time import sleep
from gda.device import DetectorSnapper
from org.slf4j import LoggerFactory

class DetectorWithShutter(PassthroughDetectorWrapper, DetectorSnapper, PositionCallableProvider):
	
	def __init__(self, detector, shutter_scannable, sleep_time_after_shutter_open=.4, nameSuffix="s"):
		PassthroughDetectorWrapper.__init__(self, detector)
		self.shutter_scannable = shutter_scannable
		self.sleep_time_after_shutter_open = sleep_time_after_shutter_open
		self._delegate_detector = detector
		self.nameSuffix =nameSuffix
		self.logger = LoggerFactory.getLogger("DetectorWithShutter:%s" % self._getName())
		self.logger.debug("__init__({}, {}, {}, {})", detector, shutter_scannable, sleep_time_after_shutter_open, nameSuffix)

	def _getName(self):
		return PassthroughDetectorWrapper.getName(self) + self.nameSuffix

	def getName(self):
		self.logger.debug("getName()returning {}", self._getName())
		return self._getName()

	def collectData(self):
		self.logger.trace("collectData()...")
		self.shutter_scannable(1)
		sleep(self.sleep_time_after_shutter_open)
		PassthroughDetectorWrapper.collectData(self)
		self.waitWhileBusy()
		self.shutter_scannable(0)
		self.logger.trace("...collectData()")

	def prepareForAcquisition(self, collection_time):
		self.logger.trace("collectData({})", collection_time)
		self._delegate_detector.setCollectionTime(collection_time)

	def acquire(self):
		self.logger.trace("collectData()...")
		self.shutter_scannable(1)
		sleep(self.sleep_time_after_shutter_open)
		self._delegate_detector.acquire()
		self.shutter_scannable(0)
		self.logger.trace("...collectData()")

	def getPositionCallable(self):
		return self.getDelegate().getPositionCallable()

	def getFilepathRelativeToRootDataDir(self):
		return self.getDelegate().getFilepathRelativeToRootDataDir()

#	public double getAcquireTime() throws Exception;

#	public double getAcquirePeriod() throws Exception;
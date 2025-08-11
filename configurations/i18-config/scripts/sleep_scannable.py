from gda.device.detector import DetectorBase
import time


class SleepDetector(DetectorBase):
    """
        Detector that can be included in a scan that simply sleeps for the given collection time
        in the readout method.
    """
    def __init__(self, name):
        self.setName(name)
        self.inputNames = []
        self.outputFormat = ["%.4f"]
        self.collectionTime = 1.0
        
    def collectData(self):        
        time.sleep(self.collectionTime)
        
    def getStatus(self):        
        return 0

    def readout(self):
        return self.collectionTime

    def getDescription(self):
        return " "

    def getDetectorID(self):
        return " "

    def getDetectorType(self):
        return " "
    
    def createsOwnFiles(self):
        return False

sleep_detector = SleepDetector("sleep_detector")
sleep_detector.setOutputFormat(["%.4f"])
sleep_detector.configure()
sleep_detector.setLevel(150)

# Another instance, with level greater than medipix's, which only sleeps for 0.1 s
sleep_detector2 = SleepDetector("sleep_detector2")
sleep_detector2.setOutputFormat(["%.4f"])
sleep_detector2.configure()
sleep_detector2.setLevel(250) # after the medipix
sleep_detector2.collectionTime = 0.1 # fixed collection time


# This next attempt is probably closer to the real solution
# Sleep as before, but in a thread, clearing the busy status when finished

from threading import Thread
from gda.device import Detector
class AsyncSleepDetector(DetectorBase):
    def __init__(self, name):
        self.setName(name)
        self.inputNames = []
        self.outputFormat = ["%.4f"]
        self.sleep_time = 0.1
        self._status = Detector.IDLE
        
    def collectData(self):      
        Thread(target=self.sleep).start()
    
    def sleep(self):
        self._status = Detector.BUSY
        time.sleep(self.sleep_time)
        self._status = Detector.IDLE
        
    def getStatus(self):        
        return self._status

    def readout(self):
        return self.sleep_time

    def getDescription(self):
        return " "

    def getDetectorID(self):
        return " "

    def getDetectorType(self):
        return " "
    
    def createsOwnFiles(self):
        return False

async_sleep_detector = AsyncSleepDetector("async_sleep_detector")
async_sleep_detector.setOutputFormat(["%.4f"])
async_sleep_detector.configure()
async_sleep_detector.setLevel(200) # same as medipix

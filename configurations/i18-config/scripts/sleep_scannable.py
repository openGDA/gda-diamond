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

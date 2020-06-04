from gda.device.scannable import ScannableMotionBase
from time import ctime
from gda.data.metadata import Metadata
from gda.data.metadata import GDAMetadataProvider
from gda.data.metadata import Metadata
from gda.data.metadata import GDAMetadataProvider
class CollectionTimePD(ScannableMotionBase):
   
    def __init__(self, name, detectorsToCheck):
        self.setName(name)
        self.detectors = detectorsToCheck
        self.setInputNames(["time"])
        self.setExtraNames([])
        self.setOutputFormat(["%5.5f"])
        self.metadata = GDAMetadataProvider.getInstance(0);
        self.scanCommand=None
        
    def atScanStart(self):
       self.scanCommand= self.metadata.getMetadataValue("gda_command")
    
    def atScanEnd(self):
       pass
    
    def isBusy(self):
        return 0

    def asynchronousMoveTo(self,new_position):
        pass

    def getPosition(self):
        value = self.getCollectionTimeFromDefaultDetector()
        if(value == ""):
            value = self.getCollectionTimeFromScanCommand()
        return value       
    
    def setScannablesToRead(self,scannableList):
        self.scannablesToRead = scannableList
        
    def getCollectionTimeFromScanCommand(self):
        toReturn=""
        toReturn = self.scanCommand
        for detector in self.detectors:
            if(self.scanCommand.find(detector.getName())):
               toReturn = self.scanCommand.split(detector.getName())
               length = len(toReturn)
               toReturn = toReturn[length - 1]
        return toReturn
       
    def getCollectionTimeFromDefaultDetector(self):
        toReturn=""
        defaultList = command_server.getDefaultScannableNames()
        print defaultList
        for detector in self.detectors:
            for default in defaultList:
                if(detector.getName() == default):
                    toReturn = detector.getCollectionTime()
                    break
        return toReturn


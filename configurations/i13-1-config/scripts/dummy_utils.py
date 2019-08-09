from gda.device.detector.addetector.triggering import AbstractADTriggeringStrategy
from gda.device.detector import NXDetector



class DummyADTriggerringStrategy(AbstractADTriggeringStrategy):
    def __init__(self):
        #print "__init__"
        self.collectionTime = 2
        #print "__init__ = %.3f" %(self.collectionTime)
        #pass
    
    def prepareForCollection(self, collectionTime, numImages, scanInfo):
        #self.configureAcquireAndPeriodTimes(collectionTime) #this would call getAdBase()
        #pass
        self.collectionTime = collectionTime
    
    def collectData(self):
        pass
    
    def stop(self):
        pass
    
    def atCommandFailure(self):
        pass
    
    def completeCollection(self):
        pass
    
    def getNumberImagesPerCollection(self, collectionTime):
        return 1
    
    def waitWhileBusy(self):
        return None             #java.lang.Exception: during scan collection: DeviceException: TypeError: None required for void return
    
    def getAcquireTime(self):
        #print "@getAcquireTime!"
        #print "getAcquireTime = %.3f" %(self.collectionTime)
        #print "getAcquireTime = %.3f" %(0.11)
        return self.collectionTime
    
class DummyDet(NXDetector):
    def __init__(self, name, collectionStrategy, dset="entry/instrument/detector/data"):
        self.setName(name)
        self.setCollectionStrategy(collectionStrategy)
        self.afterPropertiesSet()
        #self.setExtraNames("count_time")
        self.getExtraNames()
        self.hdfpath = None
        self.dset = dset
    
    def _readout(self):
        lastReadoutValue = super(DummyDet, self).readout()
        dataTree = NXDetectorData()
        #print type(dataTree)
        #print dataTree
        #output = '/dls/i13/data/2017/cm16786-5/tmp/12345.hdf'
        output = self.hdfpath
        dataTree.addScanFileLink(self.getName(), "nxfile://" + output + "#%s" %(self.dset)); #addExternaLfileLink
        #print "from readout: %s" %(output)
        #return output
        return dataTree
    
    def readout(self):
        dataTree = super(DummyDet, self).readout()
        #dataTree = NXDetectorData()
        #print type(dataTree)
        #print dataTree
        #output = '/dls/i13/data/2017/cm16786-5/tmp/12345.hdf'
        output = self.hdfpath
        dataTree.addScanFileLink(self.getName(), "nxfile://" + output + "#%s" %(self.dset)); #addExternaLfileLink
        #print "from readout: %s" %(output)
        #return output
        return dataTree
    
    def getCollectionTime(self):
        #print "@getCollectionTime!"
        return self.getCollectionStrategy().collectionTime # instead of that getCollectionTime in DetectorBase

    def set_hdfpath(self, hdfpath):
        self.hdfpath = hdfpath

class DummyADTriggerringStrategy(AbstractADTriggeringStrategy):
    def __init__(self):
        #print "__init__"
        self.collectionTime = 2
        #print "__init__ = %.3f" %(self.collectionTime)
        #pass
    
    def prepareForCollection(self, collectionTime, numImages, scanInfo):
        #self.configureAcquireAndPeriodTimes(collectionTime) #this would call getAdBase()
        #pass
        self.collectionTime = collectionTime
    
    def collectData(self):
        pass
    
    def stop(self):
        pass
    
    def atCommandFailure(self):
        pass
    
    def completeCollection(self):
        pass
    
    def getNumberImagesPerCollection(self, collectionTime):
        return 1
    
    def waitWhileBusy(self):
        return None             #java.lang.Exception: during scan collection: DeviceException: TypeError: None required for void return
    
    def getAcquireTime(self):
        #print "@getAcquireTime!"
        print "getAcquireTime = %.3f" %(self.collectionTime)
        #print "getAcquireTime = %.3f" %(0.11)
        return self.collectionTime
    

dum_collstrat=DummyADTriggerringStrategy()
dum_det=DummyDet("dum_det", dum_collstrat, dset="data")
dum_det_zeb=DummyDet("dum_det_zeb", dum_collstrat)







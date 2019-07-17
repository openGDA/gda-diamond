'''
A wrapper detector for a EpicsFemtoWithBekhoffAdc instance to support customised EPICS shutter 
synchronisation in exposure time during a scan. 
 
Created on 18 Feb 2019

@author: fy65
'''

from gda.epics import CAClient
from gda.device.currentamplifier import EpicsFemtoWithBekhoffAdc
from gov.aps.jca.event import PutListener
from java.util.concurrent import CountDownLatch
from gda.device.detector import DetectorBase
from org.slf4j import LoggerFactory

class SynchronisedFemtoBekhofAdcDetector(DetectorBase, PutListener):
    '''
    a wrapper class for an EpicsFemtoWithBekhoffAdc instance to synchronise the exposure time with other devices.
    '''


    def __init__(self, name, detector, pvRoot="BL21I-MO-POD-01:FEMTO1:ADC101_"):
        '''
        Constructor
        '''
        self.logger=LoggerFactory.getLogger("SynchronisedFemtoBekhofAdcDetector")
        if not isinstance(detector, EpicsFemtoWithBekhoffAdc):
            raise TypeError("The given detector '%s' is not an instance of EpicsFemtoWithBekhoffAdc class!" % detector.getName())
        self.setName(name)
        self.setInputNames([name])
        self.detector=detector
        self.start=CAClient(pvRoot+"CAP:START")
        self.stop=CAClient(pvRoot+"CAP:STOP")
        self.acquiringLatch=CountDownLatch(0)
        self.instantCache=None
        
    def putCompleted(self):
        self.acquiringLatch.countDown()
        
    def setCollectionTime(self, collectionTime):
        self.detector.setCollectionTime(collectionTime)
        if self.detector.isIntegrated():
            if collectionTime == 0 or collectionTime is None:
                self.logger.debug("No collection time given, so return instantaneous value!")
                #cache setting found from the device before change it.
                self.instantCache=self.detector.isInstantaneousVoltage()
                #return instantaneous value
                self.detector.setInstantaneousVoltage(True)
    
    def collectData(self):
        self.logger.debug("collectData called")
        if not self.start.isConfigured():
            self.start.configure()
        try:
            self.start.caput(1, self)
            self.acquiringLatch=CountDownLatch(1)
        except:
            self.logger.error("Error trigger ADC start.")
            raise
        
    def waitWhileBusy(self):
        self.acquiringLatch.await()
    
    def getStatus(self):
        return self.detector.getStatus()
    
    def createsOwnFiles(self):
        return self.detector.createsOwnFiles()
    
    def atScanStart(self):
        self.detector.atScanStart()
    
    def atScanEnd(self):
        self.detector.atScanEnd()
        self.restoreCachedData()
         
    def atPointStart(self):
        self.detector.atPointStart()
        
    def atCommandFailure(self):
        self.detector.atCommandFailure()
        self.resetAllPVs()
        self.restoreCachedData()
        
    def stop(self):
        self.detector.stop()
        self.resetAllPVs()
        self.restoreCachedData()
    
    def readout(self):
        return self.detector.readout()
    
    def toFormattedString(self):
        return self.detector.toFormattedString()
    
    def prepareForCollection(self):
        self.resetAllPVs()
        
    def resetAllPVs(self):
        if not self.stop.isConfigured():
            self.stop.configure()
        #reset all PVs to their default
        self.stop.caputWait(1)
        
    def restoreCachedData(self):
        if self.instantCache is not None:
            self.detector.setInstantaneousVoltage(self.instantCache)
            self.instantCache=None   

m4sc=SynchronisedFemtoBekhofAdcDetector("m4sc", m4c1, pvRoot="BL21I-MO-POD-01:FEMTO1:ADC101_")  # @UndefinedVariable
'''
Created on Apr 24, 2023

@author: fy65
'''
from gda.device.detector import DummyDetector
from gda.epics import CAClient
from i06shared import installation
from org.slf4j import LoggerFactory
from gda.device import Detector
from time import sleep

logger =  LoggerFactory.getLogger(__name__)

class Scaler8512ChannelDetector(DummyDetector):
    '''
    a Detector implementation represent a single channel of a Scaler 8512 card. 
    It extends gda.device.detector.DummyDetector to support dummy mode.
    '''


    def __init__(self, name, preset_pv, start_count_pv, count_pv):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([])
        self.preset_channel = CAClient(preset_pv)
        self.start_count_channel =  CAClient(start_count_pv)
        self.count_channel = CAClient(count_pv)
        
    def configure(self):
        if self.isConfigured():
            return
        if installation.isLive():
            self.preset_channel.configure()
            self.start_count_channel.configure()
            self.count_channel.configure()
        else:
            logger.info("Run {} in dummy mode.", self.getName())
        super(Scaler8512ChannelDetector, self).configure()
        
    def collectData(self):
        if installation.isLive():
            self.preset_channel.caput(self.getCollectionTime())
            self.start_count_channel.caput(1)
        else:
            super(Scaler8512ChannelDetector, self).collectData()
    
    def getStatus(self):
        if installation.isLive():
            status = int(self.start_count_channel.caget())
            if status == 0:
                return Detector.IDLE
            else:
                return Detector.BUSY
        else:
            return super(Scaler8512ChannelDetector, self).getStatus()
            
    def waitWhileBusy(self):
        if installation.isLive():
            while self.getStatus() == Detector.BUSY:
                sleep(0.1)
        else:
            super(Scaler8512ChannelDetector, self).waitWhileBusy() 
    
    def readout(self):
        if installation.isLive():
            return float(self.count_channel.caget())
        else:
            return super(Scaler8512ChannelDetector, self).readout()
            
    def getDescription(self):
        if installation.isLive():
            return "Scaler Channel Count Detector"
        else:
            return super(Scaler8512ChannelDetector, self).getDescription()
            
    def getDetectorID(self):
        return self.getName()

    def getDetectorType(self):
        if installation.isLive():
            return "Scaler Channel"
        else:
            return super(Scaler8512ChannelDetector, self).getDetectorType()
            
    def getMaxDataValue(self):
        if installation.isLive():
            raise AttributeError("Method is not supported")
        else:
            return super(Scaler8512ChannelDetector, self).getMaxDataValue()
            
    def setMaxDataValue(self, val):
        if installation.isLive():
            raise AttributeError("Method is not supported")
        else:
            super(Scaler8512ChannelDetector, self).setMaxDataValue(val)
       
        
            
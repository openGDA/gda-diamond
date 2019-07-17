'''
Created on 29 Nov 2017

@author: fy65
'''
from gda.device import Detector
from time import sleep
from gda.device.detector.addetector.triggering import AbstractADTriggeringStrategy
from java.lang import IllegalStateException
from detectors.ZebraDetector import ZEBRA_PC_CAPTURE, ZEBRA_PC_CAPTURE_UNIT
from gda.device.detector.nxdata import NXDetectorDataAppender
from gda.data.nexus.extractor import NexusGroupData
from gda.device.detector.nxdetector import NXPlugin

class ZebraNXDetectorCaptureDataAppender(NXDetectorDataAppender):
    def __init__(self, data, units):
        self.data=data
        self.units=units
        
    def appendTo(self, data, detectorName) :
        for key, value in dict.iteritems():
            data.addData(key, detectorName, NexusGroupData(value), self.units[key], 1)


class ZebraDetectorCollectionStrategy(AbstractADTriggeringStrategy, NXPlugin):
    '''
    A collection strategy for using zebra as NXDetector to save data captured in PC_BIT_CAP fields' waveform into a data file,
    with gate width representing exposure time, pulse step defining the sampling rate.
    
    1. Due to the timing different on status in Zebra and its AD wrapper in EPICS, it needs to use area detector acquiring field
     for detector status!
    2. designed to capture NAMED waveform
       
    '''
    OUTPUT_FORMAT = ["%5.5g"]

    def __init__(self, zebra, zebraADBase=None):
        '''
        Constructor
        '''
        self.controller=zebra
        self.adBase=zebraADBase
        self.captureChannels=[]
    
    ### methods must be implemented and override here 
    def completeCollection(self):
        pass
    
    def atCommandFailure(self):
        print "Command failure. Stopping detector"
        if self.adBase is not None:
            self.adBase.stopAcquiring()
        else:
            self.controller.pcDisarm()
        self.completeCollection()
    
    def stop(self):
        print "Stopping detector"
        if self.adBase is not None:
            self.adBase.stopAcquiring()
        else:
            self.controller.pcDisarm()
        
    def getAcquireTime(self):
        return self.getGateWidth()
    
    def getAcquirePeriod(self):
        return self.getGateStep()
    
    def configureAcquireAndPeriodTimes(self, t):
        pass #N/A
    
    def prepareForCollection(self, collectionTime, numberOfImagesPerCollection,scanInfo):
        #TODO
        
        pass
    
    def collectData(self):
        if self.adBase is not None:
            self.adBase.startAcquiring()
        else:
            self.controller.pcArm()
        
    def getStatus(self):
        if self.adBase is not None:
            return self.adBase.getStatus()
        else: 
            if self.controller.isPCArmed():
                return Detector.BUSY
            else:
                return Detector.IDLE
        
    def waitWhileBusy(self):
        if self.adBase is not None:
            self.adBase.waitWhileStatusBusy()
        else:
            while self.controller.isPCArmed():
                sleep(0.1)

    def afterPropertiesSet(self):
        #override to allow adBase to be None
        if self.controller is None:
            raise IllegalStateException("zebra controller must be set!")
        if len(self.captureChannels) == 0:
            raise IllegalStateException("No captured Channel names is set! ")
    
    def getInputStreamNames(self):
        return self.captureChannels
    
    def getInputStreamFormats(self):
        outputformats=["%f" for x in self.captureChannels]
        return outputformats

    def read(self, maxToRead):
        appenders=[]
        captured_data={}
        captured_data_units={}
        for each in self.captureChannels:
            captured_data[each] = self.getCapturedData(each)
            captured_data_units[each]=ZEBRA_PC_CAPTURE_UNIT[each]
        appenders.append(ZebraNXDetectorCaptureDataAppender(captured_data,captured_data_units))
        return appenders

    def getCapturedData(self, capture):
        '''get captured data from channel specified         
        @param capture: list of name to be captured - possible values: ["PC_ENC1", "PC_ENC2", "PC_ENC3", "PC_ENC4", "PC_SYS1", "PC_SYS2", "PC_DIV1", "PC_DIV2", "PC_DIV3", "PC_DIV4", "PC_TIME"]
        '''
        pcnumber_of_points_captured = self.controller.getPCNumberOfPointsCaptured()
        return self.controller.getPcCapturePV(ZEBRA_PC_CAPTURE.index(capture)).get(pcnumber_of_points_captured)
    
        
    def setCaptureChannels(self, channels=[]):
        self.captureChannels=channels
    
    def getCaptureChannels(self):
        return self.captureChannels

    def getGateWidth(self):
        '''return exposure time in seconds
        '''
        pcgate_width = float(self.controller.getPCGateWidthRBV())
        pctime_unit = self.controller.getPCTimeUnit()
        if pctime_unit == 0: #ms
            return pcgate_width/1000.0
        elif pctime_unit == 1: #s
            return pcgate_width
        elif pctime_unit == 2: #10s
            return pcgate_width*10.0
        
    def getGateStep(self):
        '''return exposure time in seconds
        '''
        pcgate_step = float(self.controller.getPCGateStep())
        pctime_unit = self.controller.getPCTimeUnit()
        if pctime_unit == 0: #ms
            return pcgate_step/1000.0
        elif pctime_unit == 1: #s
            return pcgate_step
        elif pctime_unit == 2: #10s
            return pcgate_step*10.0
        
    def getNumberImagesPerCollection(self, t):
        return 1

##### following method in super class are OK for this class
#     def willRequireCallbacks(self):
#         return False #no other plugin in the chain
#     
#     def prepareForLine(self):
#         pass #no-op
#     
#     def completeLine(self):
#         pass #no-op
    
#     def setGenerateCallbacks(self, b):
#         pass #no-op
#     
#     def isGenerateCallbacks(self):
#         return False
#     
#     def requiresAsynchronousPlugins(self):
#         return False
#
### following 2 methods have to be implements in Java as Jython does not support method overload!!!
#     def prepareForCollection(numberImagesPerCollection, scanInfo):
#         raise UnsupportedOperationException("Must be operated via prepareForCollection(collectionTime, numberImagesPerCollection)");
# 
#     def prepareForCollection(collectionTime, numImages, scanInfo):
#        pass

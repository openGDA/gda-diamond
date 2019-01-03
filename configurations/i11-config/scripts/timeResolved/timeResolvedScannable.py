'''
This module defines a Scannable class that delivers time resolved experiment data collection. 
It is implemented as a scannable so that it will support easy integration with other sample 
environment scannables, such as laser or temperature controller.

This module delivers 2 scannables for use in GDA 'scan' command
    1. a 'delayTime' scannable - allow scan the delayTime between laser pulse and PSD exposure;
    2. a 'timeresolvedscannable' - which integrate tfg2 and mythen detector to deliver diffraction data at specified delay time.
Usages:
    1. you need to configure 
        >>>timeresolvedscannable.config(numberOfFrames, numberOfGates, gateTime, writerTime )
        or set each parameter individually using its getter/setter method.
        
    2. do data collection with 
        >>>scan delayTime 0.0 0.08 0.01 timeresolvedscannable
        >>>scan delayTime 0.0 0.08 0.01 timeresolvedscannable gateTime
        >>>scan delayTime 0.0 0.08 0.01 timeresolvedscannable [numberOfCycles, numberOfFrames, numberOfGates, gateTime, writerTime]

Created on 9 Jun 2015

@author: fy65
'''
#from peloop.tfg2 import TFG2
#from uk.ac.gda.devices.mythen.epics import MythenDetector
from gda.data import NumTracker
from gda.device.scannable import SimpleScannable, ScannableBase
from types import FloatType, ListType
import threading
from time import sleep
import time
from gda.jython.commands import GeneralCommands
from threading import Thread

#mythen=MythenDetector()
#tfg2=TFG2()
scanNumTracker = NumTracker("i11");
delayTime=SimpleScannable()
delayTime.setName("delayTime")
delayTime.setCurrentPosition(0)

class DetectorThread(threading.Thread):
    def __init__(self, detector, numberOfCycles, numberOfFrames, numberOfGates, scanNumber, collectionNumber):
        threading.Thread.__init__(self)
        self.detector=detector
        self.numberOfCycles=numberOfCycles
        self.numberOfFrames=numberOfFrames
        self.numberOfGate=numberOfGates
        self.scanNumber=scanNumber
        self.collectionNumber = collectionNumber
                
    def run(self):
        self.detector.gated(self.numberOfFrames, self.numberOfGate, self.scanNumber, self.collectionNumber)
        
class TimeResolvedExperimentScannable(ScannableBase):
    def __init__(self, name,  numberOfCycles, numberOfFrames, numberOfGates, gateTime, writerTime, delayScannable=delayTime, tfg=tfg2, detector=mythen, shutter=fastshutter):  # @UndefinedVariable
        self.name=name
        self.numberOfCycles=numberOfCycles
        self.numberOfFrames=numberOfFrames
        self.numberOfGate=numberOfGates
        self.gateTime=gateTime
        self.delayScannable=delayScannable
        self.tfg=tfg
        self.detector=detector
        self.writerTime=writerTime
        self.collectionNumber = 0;
        self.scanNumber = scanNumTracker.getCurrentFileNumber()
        self.setLevel(9)
        self.shutter=shutter
        
    def config(self, numberOfFrames, numberOfGates, gateTime, writerTime ):
        self.setNumberOfFrames(numberOfFrames)
        self.setNumberOfGates(numberOfGates)
        self.setGateTime(gateTime)
        self.setWriterTime(writerTime)
        
    def gateDetector(self, *args):
        self.gateDetectorCompleted=False
        print "start PSD detector"
        self.detector.gated4TimeResolvedExperiment(args[0], args[1], args[2], args[3], args[4])  # block until all frames and gates are collected
        print "PSD collection number %d completed." % (args[4])
        self.gateDetectorCompleted=True

    def startDetector(self, numCycles, numFrames, numGates, scanNumber, collectionNumber):
        print "\ncollecting %d frames, %d gates per frame, Scan number %d, Collection number %d" % (numFrames, numGates, scanNumber, collectionNumber)
        Thread(target=self.gateDetector, name="MythenGatedCollection", args=(numCycles, numFrames, numGates, scanNumber, collectionNumber), kwargs={}).start()
        sleep(1)

    def atScanStart(self):
        self.collectionNumber = 0;
        self.scanNumber = scanNumTracker.getCurrentFileNumber();

    def atPointStart(self):
        self.shutter.moveTo("OPEN")
    
    def getPosition(self):
        return self.collectionNumber
    
    def asynchronousMoveTo(self, value=None):
        if value is None:
            pass #parameters must be set before scan
        elif type(value)==FloatType:
            # override gate time in scan - a single value
            self.gateTime=float(value)
        elif type(value) == ListType and len(value)==5:
            #override parameters in scan - a single list [numberOfFrames, numberOfGates, gateTime, writerTime]
            self.numberOfCycles=value[0]
            self.numberOfFrames=value[1]
            self.numberOfGate=value[2]
            self.gateTime=value[3]
            self.writerTime=value[4]
        else:
            raise Exception("Cannot parse input parameters to " +str(self.getName()))
        self.startDetector(self.numberOfCycles, self.numberOfFrames, self.numberOfGate, self.scanNumber, self.collectionNumber)
        self.tfg.startTimeResolvedExperiment(self.numberOfCycles,  self.numberOfFrames, self.numberOfGate, self.gateTime, float(self.delayScannable.getPosition()), self.writerTime)
        
    def isBusy(self):
        return not self.tfg.status()=="IDLE"
    
    def stop(self):
        print "    %s: stop called at %d" % (self.getName(),time())
        GeneralCommands.pause()
        self.tfg.stop()
        self.detector.stop()
        
    def atPointEnd(self):
        self.shutter.moveTo("CLOSE")
        self.collectionNumber=self.collectionNumber+1
        
    def atScanEnd(self):
        pass

    def getNumberOfFrames(self):
        return self.numberOfFrames
    def setNumberOfFrames(self,value):
        self.numberOfFrames=value
        
    def getNumberOfGates(self):
        return self.numberOfGate
    def setNumberOfGates(self,value):
        self.numberOfGate=value
        
    def getGateTime(self):
        return self.gateTime
    def setGateTime(self, value):
        self.gateTime=value
        
    def getDelayScannable(self):
        return self.delayScannable
    def setdelayScannable(self, scannable):
        self.delayScannable=scannable
        
    def getTfg(self):
        return self.tfg
    def setTtg(self, tfgObject):
        self.tfg=tfgObject
        
    def getDetector(self):
        return self.detector
    def setDetector(self, detector):
        self.detector=detector
        
    def getWriterTime(self):
        return self.writerTime
    def setWriterTime(self,value):
        self.writerTime=value
        
#example time resolved experiment scannable object
timeresolvedscannable=TimeResolvedExperimentScannable("timeresolvedscannable",1, 1, 10, 0.00001, 2.0, delayScannable=delayTime, tfg=tfg2, detector=mythen, shutter=fastshutter)   # @UndefinedVariable


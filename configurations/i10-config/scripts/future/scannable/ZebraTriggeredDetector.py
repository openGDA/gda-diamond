# Based on gda-mt.git/configurations/i16-config/scripts/scannable/scaler.py

from datetime import datetime
#from gda.device.detector.hardwaretriggerable import HardwareTriggerableDetectorBase
from gda.device.detector import DetectorBase
from gda.device.zebra.controller.impl import ZebraImpl
from threading import Timer
from time import sleep
import time

class ZebraTriggeredDetector(DetectorBase):

    def __init__(self, name, zebra, notScanInput, notReadyInput, triggerOutSoftInput, setCollectionTimeInstructions, prepareForCollectionInstructions):
        # channel from 1
        self.name = name
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%i']
        
        self.zebra = ZebraImpl()
        #self.zebra = zebra
        self.notScanInput = notScanInput
        self.notReadyInput = notReadyInput
        self.triggerOutSoftInput - triggerOutSoftInput
        self.setCollectionTimeInstructions = setCollectionTimeInstructions
        self.prepareForCollectionInstructions = prepareForCollectionInstructions
        
        self.exposure_time = -1

    def collectData(self):
        print str(datetime.now()), self.name, 'collectData()'
        self.zebra.setSoftInput(self.triggerOutSoftInput, True)
        self.collectDataTimer = Timer(0.1, self._collectData_complete)
        self.collectDataTimer.start()

    def _collectData_complete(self):
        print str(datetime.now()), self.name, '_collectData_complete() start...'
        self.zebra.setSoftInput(self.triggerOutSoftInput, False)
        print str(datetime.now()), self.name, '_collectData_complete()...end'

    def setCollectionTime(self, t):
        print str(datetime.now()), self.name, 'setCollectionTime('+t+')'
        print str(datetime.now()), self.name, 'Please ensure that the acquisition time is set to %r in detector' % t
        print self.setCollectionTimeInstructions
        self.exposure_time = t

    def getCollectionTime(self):
        print str(datetime.now()), self.name, 'This detector is unable to tell what the collection time is, the last time requested was %r' % self.exposure_time
        return self.exposure_time

    def getStatus(self):
        return DetectorBase.IDLE if self.zebra.isSysStatSet(self.notScanInput) else DetectorBase.BUSY

    def readout(self):
        # read the last element collected
        raise Exception(self.name + " didn't expect readout to be called!")

    #def waitWhileBusy(self): Use default based on getStatus

    def getDataDimensions(self):
        return (1,)

    def prepareForCollection(self):
        print str(datetime.now()), self.name, 'prepareForCollection()'
        print self.prepareForCollectionInstructions
        lastTime=time.clock()
        while self.zebra.isSysStatSet(self.notReadyInput):
            sleep(0.1)
            thisTime=time.clock()
            if thisTime-lastTime > 5:
                lastTime=thisTime
                print "Waiting for ready signal from camera..."

    # Are these used when prepareForCollection() is defined?
    def atScanLineStart(self):
        print str(datetime.now()), self.name, 'atScanLineStart()'

    def atScanLineEnd(self):
        print str(datetime.now()), self.name, 'atScanLineEnd()'

    #def endCollection(self): Needed?

    def createsOwnFiles(self):
        return True

    def getDescription(self):
        return "Semi-automated detector which uses Zebra I/O to determine when a camera can be triggered and when it has completed."

    def getDetectorID(self):
        return self.name

    def getDetectorType(self):
        return "ZebraTriggeredDetector"


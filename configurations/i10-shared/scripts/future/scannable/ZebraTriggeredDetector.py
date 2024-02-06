# Based on gda-mt.git/configurations/i16-config/scripts/scannable/scaler.py

from datetime import datetime
#from gda.device.detector.hardwaretriggerable import HardwareTriggerableDetectorBase
from gda.device.detector import DetectorBase
from gda.device.zebra.controller.impl import ZebraImpl
from threading import Timer
from time import sleep
import time

class ZebraTriggeredDetector(DetectorBase):
    """ ZebraTriggeredDetector is a semi-automated detector connected by Zebra I/O.

        At the start of a scan this detector waits while notReadyInput is True
            Note that this is only needed if the detector is not busy when it is
            not ready, otherwise this can be disabled with notReadyInput=None

        If zebraPulse is defined, then setCollectionTime writes the time to the
            requested PULSE module.

        For each point it then briefly pulses triggerOutSoftInput True (triggered mode)
            or sets triggerOutSoftInput True for the acquisition time (gated mode)
        It then waits while notScanInput is False before proceeding to the next point

        Note: if notReadyInput is Null, it assumes that the camera was ready and
            waiting to be triggered before the scan was started

        For backwards compatibility, notScanInput was supplemented with notScanInverted=False
            rather than renaming it busyInput and adding busyActiveLow=True
    """
    def __init__(self, name, zebra, notScanInput, notReadyInput, triggerOutSoftInput,
                 setCollectionTimeInstructions, prepareForCollectionInstructions,
                 scanStartInstructions=None, gateNotTrigger=False,
                 notScanInverted=False, zebraPulse=None):
        
        self.name = name
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%i']
        
        self.zebra = ZebraImpl()
        self.zebra = zebra
        self.notScanInput = notScanInput
        self.notReadyInput = notReadyInput
        self.triggerOutSoftInput = triggerOutSoftInput
        self.setCollectionTimeInstructions = setCollectionTimeInstructions
        self.prepareForCollectionInstructions = prepareForCollectionInstructions
        self.scanStartInstructions = scanStartInstructions
        self.gateNotTrigger = gateNotTrigger
        self.notScanInverted = notScanInverted
        self.zebraPulse = zebraPulse
        
        self.exposure_time = -1
        self.verbose = False
        self.collectDataTimer = None

    def collectData(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'collectData()'
        self.zebra.setSoftInput(self.triggerOutSoftInput, True)
        if self.exposure_time < 0:
            raise Exception("Acquisition time is not set!")
        if self.gateNotTrigger:
            self.collectDataTimer = Timer(self.collectionTime, self._collectData_complete)
        else:
            self.collectDataTimer = Timer(0.1, self._collectData_complete)
        self.collectDataTimer.start()

    def _collectData_complete(self):
        if self.verbose:
            print str(datetime.now()), self.name, '_collectData_complete() start...'
        self.zebra.setSoftInput(self.triggerOutSoftInput, False)
        if self.verbose:
            print str(datetime.now()), self.name, '_collectData_complete()...end'

    def setCollectionTime(self, t):
        if self.verbose:
            print str(datetime.now()), self.name, 'setCollectionTime(%d)' % t
        if self.gateNotTrigger:
            if self.zebraPulse:
                if t > self.zebra.PulseDelayMax*10.:
                    raise Exception("Maximum acquisition time is %d" % self.zebra.PulseDelayMax*10)
                    # TODO: Fall back to Timer based gate when acquisition time too high.
                elif t > self.zebra.PulseDelayMax:
                    t = t/10
                    self.zebra.setPulseDelay(self.zebraPulse, 0)
                    self.zebra.setPulseWidth(self.zebraPulse, t)
                    self.zebra.setPulseTimeUnit(self.zebraPulse, self.zebra.PULSE_TIMEUNIT_10SEC)
                else:
                    self.zebra.setPulseDelay(self.zebraPulse, 0)
                    self.zebra.setPulseWidth(self.zebraPulse, t)
                    self.zebra.setPulseTimeUnit(self.zebraPulse, self.zebra.PULSE_TIMEUNIT_SEC)
            else:
                print str(datetime.now()), self.name, 'Software timed triggering is less accurate than Zebra controlled.'
        else:
                print str(datetime.now()), self.name, 'Please ensure that the acquisition time is set to %r in detector'
        
        print self.setCollectionTimeInstructions
        
        self.exposure_time = t

    def getCollectionTime(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'This detector is unable to tell what the collection time is, the last time requested was %r' % self.exposure_time
        return self.exposure_time

    def getStatus(self):
        return DetectorBase.IDLE if (self.zebra.isSysStatSet(self.notScanInput) != self.notScanInverted) else DetectorBase.BUSY

    def readout(self):
        def msg():
            return 'self.collectDataTimer.finished=%r & self.getStatus()=%r' % (
                    self.collectDataTimer.finished.isSet(),     self.getStatus())
        if self.verbose:
            print str(datetime.now()), self.name, 'readout()...' + msg()

        while not self.collectDataTimer.finished.isSet():
            sleep(0.1)

        if self.verbose:
            print str(datetime.now()), self.name, '...readout()...' + msg()
        
        lastTime=time.clock()
        while self.getStatus() == DetectorBase.BUSY:
            sleep(0.1)
            thisTime=time.clock()
            if thisTime-lastTime > 5:
                lastTime=thisTime
                print "Waiting for not busy signal from camera in readout..."
        
        if self.verbose:
            print str(datetime.now()), self.name, '...readout()' + msg()
        
        return self.exposure_time
        # read the last element collected
        raise Exception(self.name + " didn't expect readout to be called!")

    #def waitWhileBusy(self): Use default based on getStatus

    def getDataDimensions(self):
        return (1,)

    def prepareForCollection(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'prepareForCollection()'
        if self.prepareForCollectionInstructions:
            print self.prepareForCollectionInstructions
        if not self.notReadyInput:
            return
        lastTime=time.clock()
        while self.zebra.isSysStatSet(self.notReadyInput):
            sleep(0.1)
            thisTime=time.clock()
            if thisTime-lastTime > 5:
                lastTime=thisTime
                print "Waiting for ready signal from camera in prepare for collection..."
                #print self.zebra.isSysStatSet(self.notReadyInput)

    def atScanStart(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'atScanStart()'
        print self.scanStartInstructions

    # Are these used when prepareForCollection() is defined?
    def atScanLineStart(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'atScanLineStart()'

    def atScanLineEnd(self):
        if self.verbose:
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


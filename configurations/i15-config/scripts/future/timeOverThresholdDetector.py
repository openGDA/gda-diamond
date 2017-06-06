from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gdascripts.pd.time_pds import tictoc
from gdascripts.messages.handle_messages import simpleLog
from gov.aps.jca.event import PutListener
from gov.aps.jca import CAStatus
from threading import Thread
from time import sleep

class TimeOverThresholdDetector(DetectorBase):
    """ 
    Useful for triggering detectors which have been setup to record images on 
    hardware triggers.
    
    When asked to move, this arms the edge detector then toggles a binary PV
    from normalLevel to triggerLevel and then back to normalLevel. Remains
    busy until the edge callback is received.
    
    The exposure time is treated as a timeout.
    """
    def __init__(self, name, pvstring, normalLevel='on', triggerLevel='off', edgeDetectorPvString=None, triggerPulseLength=0.1):
        self.name = name
        self.cli = CAClient(pvstring)
        self.normalLevel = normalLevel
        self.triggerLevel = triggerLevel
        self.completed_cli = CAClient(edgeDetectorPvString)
        self.triggerPulseLength = triggerPulseLength
        
        self.setInputNames([name])
        self.setOutputFormat(['%5.5f'])
        self.setLevel(9)
        self.timer=tictoc()
        self.startTime=0
        self.endTime=0
        self.cli.configure()
        self.completed_cli.configure()
        if not self.completed_cli.isConfigured():
            self.completed_cli.configure();
        self.detectorStatus = self.IDLE
        self.putListener = TimeOverThresholdDetector.CaputCallbackListenerClass(self);
        
        self.verbose=False
        self.setNormal()

    #CA Put Callback listener that handles the callback event
    class CaputCallbackListenerClass(PutListener):
        def __init__ (self, detector):
            self.detector = detector
            
        def putCompleted(self, event):
            if event.getStatus() != CAStatus.NORMAL:
                print 'Completion trigger failed!'
                print 'Failed source: ' + event.getSource().getName();
                print 'Failed status: ' + event.getStatus();
            else:
                if self.detector.detectorStatus == TimeOverThresholdDetector.IDLE:
                    print 'WARNING: %s completion trigger called back when idle' % self.detector.name
                else:
                    self.detector.endTime = self.detector.timer()
                    self.detector.detectorStatus = TimeOverThresholdDetector.IDLE;
                    if self.detector.verbose:
                        print '%s completion trigger called back' % self.detector.name
            return;

        def getStatus(self):
            return self.detector.detectorStatus;

    def get_values(self):
        return self.name, self.cli.getPvName(), self.normalLevel, self.triggerLevel, self.completed_cli.getPvName(), self.triggerPulseLength

    def __repr__(self):
        return "TimeOverThresholdDetector(name=%s, pvstring=%s, normalLevel=%s, triggerLevel=%s, edgeDetectorPvString=%s, triggerPulseLength=%f)" % (self.get_values())

    def setNormal(self):
        if self.verbose:
            simpleLog("self.cli.caput(%r)" % self.normalLevel)
        self.cli.caput(self.normalLevel)

    def setTrigger(self): 
        if self.verbose:
            simpleLog("self.cli.caput(%r)" % self.triggerLevel)
        self.cli.caput(self.triggerLevel)
            
    def trigger(self, exposureTime):
        self.setTrigger()
        sleep(exposureTime)
        self.setNormal()

    ###    DetectorBase implementations:

    def prepareForCollection(self):
        if self.verbose:
            simpleLog("TimeOverThresholdDetector.prepareForCollection started...")
        self.setNormal()
        

    def collectData(self):
        """ Tells the detector to begin to collect a set of data, then returns
            immediately. """
        if self.verbose:
            simpleLog("TimeOverThresholdDetector.collectData started...")
        
        self.timeouttime=self.timer()+self.collectionTime+self.triggerPulseLength
        self.detectorStatus = self.BUSY
        
        self.completed_cli.getController().caput(self.completed_cli.getChannel(), 1, self.putListener);
        self.startTime=self.timer()
        self.CollectDataAsync(self.trigger, self.triggerPulseLength).start()

    class CollectDataAsync(Thread):
        def __init__(self, trigger, collectionTime):
            Thread.__init__(self)
            self.trigger = trigger
            self.collectionTime = collectionTime
        
        def run(self):
            self.trigger(self.collectionTime)

#    def setCollectionTime(self):
        """ Sets the collection time, in seconds, to be used during the next
            call of collectData.
        self.collectionTime defined by DetectorBase """

#    def getCollectionTime(self):
        """ Returns the time, in seconds, the detector collects for during the
            next call to collectData()
        self.collectionTime defined by DetectorBase """

    def getStatus(self):
        """ Returns the current collecting state of the device. BUSY if the
            detector has not finished the requested operation(s), IDLE if in
            an completely idle state and STANDBY if temporarily suspended. """
        if self.detectorStatus == self.BUSY and self.timer()>self.timeouttime:
            # Reverse start and end times so that readout gives a -ve time on a timeout
            self.startTime, self.endTime = self.timer(), self.startTime
            self.detectorStatus = self.IDLE
            self.completed_cli.caput(0)
            print "WARNING: %s timed out! Continuing..." % self.name
        
        return self.detectorStatus

    def readout(self):
        """ Returns the latest data collected. The size of the Object returned
            must be consistent with the values returned by getDataDimensions
            and getExtraNames. """
        if self.verbose:
            simpleLog("TimeOverThresholdDetector.readout started...")
        return self.endTime - self.startTime

    def getDataDimensions(self):
        """ Returns the dimensions of the data object returned by the readout()
            method. """
        if self.verbose:
            simpleLog("TimeOverThresholdDetector.getDataDimensions started...")
        return [ 1 ]

#    def prepareForCollection(self):
        """ Method called before a scan starts. May be used to setup detector
            for collection, for example MAR345 uses this to erase. """

#    def endCollection(self):
        """ Method called at the end of collection to tell detector when a
            scan has finished. Typically integrating detectors used in powder
            diffraction do not output until the end of the scan and need to be
            told when this happens. """

    def createsOwnFiles(self):
        """ Returns a value which indicates whether the detector creates its
            own files. If it does (return true) the readout() method returns
            the name of the latest file created as a string. If it does not
            (return false) the readout() method will return the data directly. """
        if self.verbose:
            simpleLog("createsOwnFiles started...")
        return False; 

    def getDescription(self):
        """ A description of the detector. """
        return "Time Over Threshold Detector";

    def getDetectorID(self):
        """ A identifier for this detector. """
        return self.name;

    def getDetectorType(self):
        """ The type of detector. """
        return "TimeOverThresholdDetector";

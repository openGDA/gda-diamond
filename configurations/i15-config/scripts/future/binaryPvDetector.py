from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gdascripts.pd.time_pds import tictoc
from gdascripts.messages.handle_messages import simpleLog
from threading import Thread
from time import sleep

class BinaryPvDetector(DetectorBase):
    """ 
    Useful for triggering detectors which have been setup to record images on 
    hardware triggers.
    
    When asked to move, toggles a binary PV from normalLevel to triggerLevel and
    then back to normalLevel. Remains busy until the single exposure+readout time
    is reached.
    """
    def __init__(self, name, pvstring, normalLevel='on', triggerLevel='off'):
        self.name = name
        self.cli = CAClient(pvstring)
        self.setInputNames([name])
        self.setOutputFormat(['%5.5f'])
        self.setLevel(9)        
        self.timer=tictoc()
        self.waitfortime=0
        self.cli.configure()
        self.normalLevel = normalLevel
        self.triggerLevel = triggerLevel
        self.verbose=False
        self.setNormal()
        self.lastExposureTime=0

    def get_values(self):
        return self.name

    def __repr__(self):
        return "BinaryPvDetector(name=%r)" % (self.get_values())

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
            simpleLog("BinaryPvDetector.prepareForCollection started...")
        self.setNormal()

    def collectData(self):
        """ Tells the detector to begin to collect a set of data, then returns
            immediately. """
        if self.verbose:
            simpleLog("BinaryPvDetector.collectData started...")
        self.lastExposureTime = self.collectionTime
        self.waitfortime=self.timer()+self.collectionTime
        self.CollectDataAsync(self.trigger, self.collectionTime).start()

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
        #if self.verbose:
        #    simpleLog("BinaryPvDetector.getStatus started...")
        if self.timer()<self.waitfortime:
            return self.BUSY
        else:
            return self.IDLE

    def readout(self):
        """ Returns the latest data collected. The size of the Object returned
            must be consistent with the values returned by getDataDimensions
            and getExtraNames. """
        if self.verbose:
            simpleLog("BinaryPvDetector.readout started...")
        return self.lastExposureTime

    def getDataDimensions(self):
        """ Returns the dimensions of the data object returned by the readout()
            method. """
        if self.verbose:
            simpleLog("BinaryPvDetector.getDataDimensions started...")
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
        return "Generic Binary PV Detector";

    def getDetectorID(self):
        """ A identifier for this detector. """
        return self.name;

    def getDetectorType(self):
        """ The type of detector. """
        return "BinaryPvDetector";

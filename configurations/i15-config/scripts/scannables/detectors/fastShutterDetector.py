from gda.device.detector import DetectorBase
from gdascripts.pd.time_pds import tictoc
from gdascripts.messages.handle_messages import simpleLog
from threading import Thread
from time import sleep

class FastShutterDetector(DetectorBase):
    
    def __init__(self, name, isccd):
        self.name = name
        self.isccd = isccd
        self.setInputNames([name])
        self.setOutputFormat(['%5.5f'])
        self.setLevel(100) # Same as PE
        self.timer=tictoc()
        self.waitfortime=0
        self.lastExposureTime=0
        
        self.verbose=False
        self.setNormal()

    def get_values(self):
        return self.name, self.isccd

    def __repr__(self):
        return "FastShutterDetector(name=%r, isccd=%r)" % (self.get_values())

    def setNormal(self):
        if self.verbose:
            simpleLog("self.isccd.closeS()")
        self.isccd.closeS()

    def setTrigger(self): 
        if self.verbose:
            simpleLog("self.isccd.openS()")
        self.isccd.openS()
            
    def trigger(self, exposureTime):
        self.setTrigger()
        sleep(exposureTime)
        self.setNormal()

    class CollectDataAsync(Thread):
        def __init__(self, trigger, collectionTime):
            Thread.__init__(self)
            self.trigger = trigger
            self.collectionTime = collectionTime
        
        def run(self):
            self.trigger(self.collectionTime)

    ###    Detector interface implementations:

    def collectData(self):
        """ Tells the detector to begin to collect a set of data, then returns
            immediately. """
        if self.verbose:
            simpleLog("FastShutterDetector.collectData started...")
        self.lastExposureTime = self.collectionTime
        self.waitfortime=self.timer()+self.collectionTime
        self.CollectDataAsync(self.trigger, self.collectionTime).start()

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
        #    simpleLog("FastShutterDetector.getStatus started...")
        if self.timer()<self.waitfortime:
            return self.BUSY
        else:
            return self.IDLE

    def readout(self):
        """ Returns the latest data collected. The size of the Object returned
            must be consistent with the values returned by getDataDimensions
            and getExtraNames. """
        if self.verbose:
            simpleLog("FastShutterDetector.readout started...")
        return self.lastExposureTime

#    def waitWhileBusy(self):
        """ Wait while the detector collects data. Should return as soon as
            the exposure completes and it is safe to move motors. i.e. counts
            must be safely latched either in hardware or software before
            returning.
        self.waitWhileBusy defined by ScannableBase
        self.isBusy definedby DetectorBase"""

    def getDataDimensions(self):
        """ Returns the dimensions of the data object returned by the readout()
            method. """
        if self.verbose:
            simpleLog("FastShutterDetector.getDataDimensions started...")
        return [ 1 ]

    def prepareForCollection(self):
        """ Method called before a scan starts. May be used to setup detector
            for collection, for example MAR345 uses this to erase. """
        if self.verbose:
            simpleLog("FastShutterDetector.prepareForCollection started...")
        self.setNormal()

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
        return "FastShutterDetector";

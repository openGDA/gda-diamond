#beam position monitor

from gda.device.detector import DetectorBase
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.scannable.epics.PvManager import PvManager

TIMEOUT=5

class FastShutterZebraDetector(DetectorBase):
    
    def __init__(self, name, rootPV="BL15I-EA-ZEBRA-01:"):
        self.name = name
        self.setInputNames([name])
        self.setOutputFormat(['%5.5f'])
        self.setLevel(100) # Same as PE
        self.pvs = PvManager(pvroot = rootPV)
        
        self.verbose=False
        
        self.timeunit='ms'
        self.timeconvert=1000

    def get_values(self):
        return self.name, self.isccd

    def __repr__(self):
        return "FastShutterDetector(name=%r, isccd=%r)" % (self.get_values())

    ### Special commands for supporting manual shutter open/close.

    def forceOpen(self):
        """ TODO: This sets bit 3 only, we shouldn't clear the other bits."""
        self.pvs['SOFT_IN'].caput(TIMEOUT, 4)
    
    def forceOpenRelease(self):
        """TODO: This clears all bits, we should really only clear bit 3 leaving other bits as is."""
        self.pvs['SOFT_IN'].caput(TIMEOUT, 0)

    def isOpen(self):
        shutterFeedback=self.pvs['OR3_INP2:STA'].caput(TIMEOUT, 0)
        if shutterFeedback == 0:
            return 'CLOSED'
        else:
            return 'OPEN'

    ###    Detector interface implementations:

    def collectData(self):
        """ Tells the detector to begin to collect a set of data, then returns
            immediately. """
        if self.verbose:
            simpleLog("FastShutterDetector.collectData started...")
        self.lastExposureTime = self.collectionTime
        self.pvs['SYS_RESET.PROC'].caput(TIMEOUT, 1)
        self.pvs['PC_ARM'].caput(TIMEOUT, 1)

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
        return self.IDLE

    def readout(self):
        """ Returns the latest data collected. The size of the Object returned
            must be consistent with the values returned by getDataDimensions
            and getExtraNames. """
        if self.verbose:
            simpleLog("FastShutterDetector.readout started...")
        return float(self.pvs['PC_DIV3_LAST'].caget())/1000.
        # Hard coded to 1000 as we are using a 1KHz clock for the pulses.

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

        self.pvs['PC_TSPRE'      ].caput(TIMEOUT, self.timeunit)
        self.pvs['PC_BIT_CAP'    ].caput(TIMEOUT, 961)      # Complex bitfield

        self.pvs['OR3_ENA'       ].caput(TIMEOUT, 3)        # 1 & 2
        self.pvs['OR3_INP1'      ].caput(TIMEOUT, 31)       # PC_PULSE
        self.pvs['OR3_INP2'      ].caput(TIMEOUT, 62)       # SOFT_IN3
        self.pvs['OUT3_OC'       ].caput(TIMEOUT, 38)       # OR3

        self.pvs['PC_ARM_SEL'    ].caput(TIMEOUT, 'Soft')
        self.pvs['PC_GATE_SEL'   ].caput(TIMEOUT, 'Time')
        self.pvs['PC_GATE_START' ].caput(TIMEOUT, 0)
        self.pvs['PC_GATE_WID'   ].caput(TIMEOUT, self.collectionTime*self.timeconvert)
        self.pvs['PC_GATE_NGATE' ].caput(TIMEOUT, 1)

        self.pvs['PC_PULSE_SEL'  ].caput(TIMEOUT, 'Time')
        self.pvs['PC_PULSE_START'].caput(TIMEOUT, 0)
        self.pvs['PC_PULSE_WID'  ].caput(TIMEOUT, self.collectionTime*self.timeconvert)
        self.pvs['PC_PULSE_STEP' ].caput(TIMEOUT, 0)
        self.pvs['PC_PULSE_DLY'  ].caput(TIMEOUT, self.collectionTime*self.timeconvert)
        self.pvs['PC_PULSE_MAX'  ].caput(TIMEOUT, 1)

        self.pvs['AND3_ENA'      ].caput(TIMEOUT, 3)        # 1 & 2
        self.pvs['AND3_INP1'     ].caput(TIMEOUT, 8)        # IN3_OC Shutter feedback
        self.pvs['AND3_INP2'     ].caput(TIMEOUT, 58)       # CLOCK_1KHZ
        self.pvs['DIV3_INP'      ].caput(TIMEOUT, 34)       # AND3
        self.pvs['DIV3_DIV'      ].caput(TIMEOUT, 10000000) # 10m ms = 10k s
        self.pvs['DIV3_DIV'      ].caput(TIMEOUT, 10000000) # Setting is notreliable, three times seems to be the charm
        self.pvs['DIV3_DIV'      ].caput(TIMEOUT, 10000000) 
        self.pvs['POLARITY'      ].caput(TIMEOUT, 0)

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

#beam position monitor

from gda.device.detector import DetectorBase
from gda.device.detector.hardwaretriggerable import HardwareTriggeredDetector
from gda.scan import DetectorWithReadoutTime
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.scannable.epics.PvManager import PvManager
from org.slf4j import LoggerFactory

TIMEOUT=5

class FastShutterZebraDetector(DetectorBase, HardwareTriggeredDetector, DetectorWithReadoutTime):
    
    def __init__(self, name, rootPV, continuousMoveController):
        self.logger = LoggerFactory.getLogger("FastShutterZebraDetector:%s" % name)
        self.name = name
        self.setInputNames([name])
        self.setOutputFormat(['%5.5f'])
        self.setLevel(100) # Same as PE
        self.pvs = PvManager(pvroot = rootPV)
        self.continuousMoveController = continuousMoveController
        #from gda.device.zebra.controller.impl import ZebraImpl
        #self.zebra = ZebraImpl()
        self.verbose=False
        self.zebraVersion=0x23

    def __repr__(self):
        return "%s(name=%r, rootPV=%r, continuousMoveController=%s)" % (self.__class__.__name__, self.name,
            self.pvs.pvroot, self.continuousMoveController.name)

    ### Special commands for supporting manual shutter open/close.

    def forceOpen(self):
        if self.verbose:
            simpleLog("%s:%s() Forcing shutter open..." % (self.name, self.pfuncname()))
        if self.zebraVersion < 0x23:
            # TODO: This sets bit 3 only, we shouldn't clear the other bits.
            self.pvs['SOFT_IN'].caput(TIMEOUT, 4)
        else:
            self.pvs['SOFT_IN:B2'].caput(TIMEOUT, 1) # SOFT_IN:B2 is SOFT_IN3

    def forceOpenRelease(self):
        if self.zebraVersion < 0x23:
            # TODO: This clears all bits, we should really only clear bit 3 leaving other bits as is.
            self.pvs['SOFT_IN'].caput(TIMEOUT, 0)
        else:
            self.pvs['SOFT_IN:B2'].caput(TIMEOUT, 0) # SOFT_IN:B2 is SOFT_IN3
        if self.verbose:
            simpleLog("%s:%s() Released Force shutter open" % (self.name, self.pfuncname()))

    def isOpen(self):
        shutterFeedback=self.pvs['OR3_INP2:STA'].caput(TIMEOUT, 0)
        if shutterFeedback == 0:
            return 'CLOSED'
        else:
            return 'OPEN'

    ### Local helper functions

    def pfuncname(self):
        import traceback
        return "%s" % traceback.extract_stack()[-2][2]

    ###    Detector interface implementations:

    def collectData(self):
        """ Tells the detector to begin to collect a set of data, then returns
            immediately. """
        self.logger.trace("%s:%s() started... collectionTime=%r" % (self.name, self.pfuncname(), self.collectionTime))
        self.lastExposureTime = self.collectionTime
        # Reset the zebra box before each arm, so that internal dividers are reset
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
        num_cap = int(float(self.pvs['PC_NUM_CAP'].caget()))
        num_down = int(float(self.pvs['PC_NUM_DOWN'].caget()))
        array_acq = int(float(self.pvs['ARRAY_ACQ'].caget()))
        # num_cap and num_down react much more quickly than array_acq, but may
        # not be equal if a previous scan failed, so check for both.
        #busy = self.IDLE if array_acq == 0 or num_cap == num_down else self.BUSY
        # MBB: Originally ^, why did I switch it to V
        busy = self.BUSY if array_acq != 0 or (num_down != 0 and num_cap != num_down) else self.IDLE
        self.logger.trace("%s:%s() returning %r (ARRAY_ACQ=%r, PC_NUM_CAP=%r, PC_NUM_DOWN=%r)" % (
                self.name, self.pfuncname(), busy, array_acq, num_cap, num_down))
        return busy

    def readout(self):
        """ Returns the latest data collected. The size of the Object returned
            must be consistent with the values returned by getDataDimensions
            and getExtraNames. """
        pc_div3_last = float(self.pvs['PC_DIV3_LAST'].caget())
        self.logger.trace("%s:%s() started... collectionTime=%r" % (self.name, self.pfuncname(), self.collectionTime))
        pc_div3 = float(self.pvs['PC_DIV3'].caget())
        self.logger.trace("%s:%s() ARRAY_ACQ=%r, PC_NUM_CAP=%r, PC_NUM_DOWN=%r, PC_DIV3_LAST=%r, PC_DIV3=%r" % (self.name, self.pfuncname(),
                self.pvs['ARRAY_ACQ'].caget(), self.pvs['PC_NUM_CAP'].caget(), self.pvs['PC_NUM_DOWN'].caget(), pc_div3_last, pc_div3))
        return pc_div3_last/1000.
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
        self.logger.trace("%s:%s() started... collectionTime=%r" % (self.name, self.pfuncname(), self.collectionTime))
        return [ 1 ]

    def prepareForCollection(self):
        """ Method called before a scan starts. May be used to setup detector
            for collection, for example MAR345 uses this to erase. """
        self.logger.trace("%s:%s() started... collectionTime=%r" % (self.name, self.pfuncname(), self.collectionTime))

        # Reset the zebra box before trying to set any parameters
        self.pvs['SYS_RESET.PROC'].caput(TIMEOUT, 1)

        # Note that max gate width is 214881.9984, so max collection time is 214s at ms resolution, or 59d at s resolution.
        if self.collectionTime > 20: # Using 20 rather 214 makes it easier to test the switchover. 
            self.timeunit='s'
            self.timeconvert=1
        else:
            self.timeunit='ms'
            self.timeconvert=1000
        
        pc_arm_out = self.pvs['PC_ARM_OUT'].caget()
        msg="%s:%s() ... PC_ARM_OUT=%r (type=%r)" % (self.name, self.pfuncname(), pc_arm_out, type(pc_arm_out))
        if pc_arm_out == '1.0': # Watch out for Zebra already being armed.
            self.logger.warn(msg)
        else:
            self.logger.trace(msg)

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
        self.pvs['PC_PULSE_STEP' ].caput(TIMEOUT, self.collectionTime*self.timeconvert+0.0002) # PULSE_STEP *must* be bigger than PULSE_WID, maybe more than 0.0001 bigger
        self.pvs['PC_PULSE_DLY'  ].caput(TIMEOUT, self.collectionTime*self.timeconvert)
        self.pvs['PC_PULSE_MAX'  ].caput(TIMEOUT, 1)

        self.pvs['AND3_ENA'      ].caput(TIMEOUT, 3)        # 1 & 2
        self.pvs['AND3_INP1'     ].caput(TIMEOUT, 8)        # IN3_OC Shutter feedback
        self.pvs['AND3_INP2'     ].caput(TIMEOUT, 58)       # CLOCK_1KHZ
        self.pvs['DIV3_INP'      ].caput(TIMEOUT, 34)       # AND3
        self.pvs['DIV3_DIV'      ].caput(TIMEOUT, 10000000) # 10m ms = 10k s
        self.pvs['DIV3_DIV'      ].caput(TIMEOUT, 10000000) # Setting is not reliable, three times seems to be the charm
        self.pvs['DIV3_DIV'      ].caput(TIMEOUT, 10000000) # TODO: Remove when this fixed
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
        self.logger.trace("%s:%s() started..." % (self.name, self.pfuncname()))
        return False; 

    def getDescription(self):
        """ A description of the detector. """
        self.logger.trace("%s:%s() started..." % (self.name, self.pfuncname()))
        return "Generic Binary PV Detector";

    def getDetectorID(self):
        """ A identifier for this detector. """
        self.logger.trace("%s:%s() started..." % (self.name, self.pfuncname()))
        return self.name;

    def getDetectorType(self):
        """ The type of detector. """
        self.logger.trace("%s:%s() started..." % (self.name, self.pfuncname()))
        return "FastShutterDetector";

    ###    HardwareTriggeredDetector interface implementations:

    def getHardwareTriggerProvider(self):
        """ Get the HardwareTriggerProvider that represents the controller this Detector is wired to."""
        self.logger.trace("FastShutterDetector.getHardwareTriggerProvider started...")
        return self.continuousMoveController

    def setNumberImagesToCollect(self, numberImagesToCollect):
        """ Tell the detector how many scan points to collect. (Unfortunately named images)."""
        self.logger.trace("FastShutterDetector.setNumberImagesToCollect started...")
        if not numberImagesToCollect == 1:
            pass

    def integratesBetweenPoints(self):
        """ Detectors that sample some value at the time of a trigger should return False. Detectors such as counter timers
            should return True. If true ,TrajectoryScanLine will generate a trigger half a point before the motor reaches a
            demanded point such that the resulting bin of data is centred on the demand position. Area detectors that will be
            triggered by the first pulse should also return true."""
        self.logger.trace("FastShutterDetector.integratesBetweenPoints started...")
        return True

    ###    DetectorWithReadoutTime interface implementations:

    def getReadOutTime(self):
        self.logger.trace("FastShutterDetector.getReadOutTime started...")
        return 0.1 # To match the PE
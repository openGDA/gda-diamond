""" Based on /i15-config/scripts/scannables/detectors/fastShutterZebraDetector.py at 52a1a9
"""

from gda.device.detector import DetectorBase
from gda.device.detector.hardwaretriggerable import HardwareTriggeredDetector
from gda.scan import DetectorWithReadoutTime
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.scannable.epics.PvManager import PvManager
from time import sleep

TIMEOUT=5

class FastDichroismZebraDetector(DetectorBase, HardwareTriggeredDetector, DetectorWithReadoutTime):
    
    def __init__(self, name, rootPV, continuousMoveController):
        self.name = name
        self.setInputNames([name])
        self.setExtraNames(self._getExtraNames())
        self.setOutputFormat(self._getOutputFormat())
        self.setLevel(100)
        self.pvs = PvManager(pvroot = rootPV)
        self.continuousMoveController = continuousMoveController
        #from gda.device.zebra.controller.impl import ZebraImpl
        #self.zebra = ZebraImpl()
        self.verbose=False
        self.negative_offset=0.05
        self.setDelayAfterRise(-0.01)
        self.setDelayAfterFall(-0.01)
        self.setAcquireTimePerPulse(0.02)

    def __repr__(self):
        return "%s(name=%r, rootPV=%r, continuousMoveController=%s)" % (self.__class__.__name__, self.name,
            self.pvs.pvroot, "")#self.continuousMoveController.name)

    ### Special commands for setting delays.

    def setDelayAfterRise(self, delay_after_rise_s):
        """ Time from 10Hz rise to start of acquire, in seconds. """
        if delay_after_rise_s < 0.:
            simpleLog("Note that %s delay_after_rise_s (%r) < 0 so %rs will be added at acquire time." % (self.name, delay_after_rise_s, self.negative_offset))
            self.absolute_delay_after_rise_s = delay_after_rise_s + self.negative_offset
            #low_limit = 0.05
            #high_limit = 0.1-self.acquire_time_per_pulse_s
        else:
            self.absolute_delay_after_rise_s = delay_after_rise_s
            #low_limit = 0
            #high_limit = 0.05-self.acquire_time_per_pulse_s
        # TODO: Work out how to sanity check these values.
        #if self.absolute_delay_after_rise_s < low_limit :
        #    simpleLog("Warning, %r is less than %r so acquire time per pulse should be reduced for this delay." % (delay_after_rise_s, low_limit))
        #if self.absolute_delay_after_rise_s > high_limit :
        #    simpleLog("Warning, %r is more than %r so acquire time per pulse should be reduced for this delay." % (delay_after_rise_s, high_limit))

        self.delay_after_rise_s = delay_after_rise_s

    def setDelayAfterFall(self, delay_after_fall_s):
        """ Time from 10Hz fall to start of acquire, in seconds. """
        if delay_after_fall_s < 0.:
            simpleLog("Note that %s delay_after_fall_s (%r) < 0 so %rs will be added at acquire time." % (self.name, delay_after_fall_s, self.negative_offset))
            self.absolute_delay_after_fall_s = delay_after_fall_s + self.negative_offset
            #low_limit = 0.05
            #high_limit = 0.1-self.acquire_time_per_pulse_s
        else:
            self.absolute_delay_after_fall_s = delay_after_fall_s
            #low_limit = 0
            #high_limit = 0.05-self.acquire_time_per_pulse_s
        # TODO: Work out how to sanity check these values.
        #if self.absolute_delay_after_fall_s < low_limit :
        #    simpleLog("Warning, %r is less than %r so acquire time per pulse should be reduced for this delay." % (delay_after_fall_s, low_limit))
        #if self.absolute_delay_after_fall_s > high_limit :
        #    simpleLog("Warning, %r is more than %r so acquire time per pulse should be reduced for this delay." % (delay_after_fall_s, high_limit))
        
        self.delay_after_fall_s = delay_after_fall_s

    def setAcquireTimePerPulse(self, acquire_time_per_pulse_s):
        """ Time spent acquiring for each from 10Hz rise to start of acquire, in seconds. """
        self.acquire_time_per_pulse_s = acquire_time_per_pulse_s
        # Warn about constraints
        # TODO: Restore these when they calculates the constraints correctly
        #self.setDelayAfterRise(self.delay_after_rise_s)
        #self.setDelayAfterFall(self.delay_after_fall_s)

    def getDelayAfterRise(self):
        return self.delay_after_rise_s

    def getDelayAfterFall(self):
        return self.delay_after_fall_s

    def getAcquireTimePerPulse(self):
        return self.acquire_time_per_pulse_s

    # Special command to set up Zebra

    def setupZebra(self):
        if self.verbose:
            simpleLog("%s:%s() started..." % (self.name, self.pfuncname()))

        DISCONNECT=0
        IN1_TTL=1
        IN2_TTL=4
        IN3_TTL=7
        PC_ARM=29
        AND1=32
        AND2=33
        AND3=34
        AND4=35
        OR1=36
        GATE1=40
        PULSE1=52
        PULSE2=53
        SOFT_IN1=60

        Yes=1
        No=0
        TriggerOnRisingEdge=No
        TriggerOnFallingEdge=Yes
        DivFirstPulseNumbered1_OUTN=No

        # Perform a Zebra RESET to ensure all of the PVs can be configured.
        self.pvs['SYS_RESET.PROC'].caput(TIMEOUT, 1)

        # The Position compare is used to control the length of acquisition
        # according to the number of pulses acquired, and capture the
        # total number of detector pulses for each phase of the acquisition.
        self.pvs['PC_BIT_CAP:B0' ].caput(TIMEOUT, No)       # Enc1
        self.pvs['PC_BIT_CAP:B1' ].caput(TIMEOUT, No)       # Enc2
        self.pvs['PC_BIT_CAP:B2' ].caput(TIMEOUT, No)       # Enc3
        self.pvs['PC_BIT_CAP:B3' ].caput(TIMEOUT, No)       # Enc4
        self.pvs['PC_BIT_CAP:B4' ].caput(TIMEOUT, No)       # Sys1
        self.pvs['PC_BIT_CAP:B5' ].caput(TIMEOUT, No)       # Sys2
        self.pvs['PC_BIT_CAP:B6' ].caput(TIMEOUT, Yes)      # Div1
        self.pvs['PC_BIT_CAP:B7' ].caput(TIMEOUT, Yes)      # Div2
        self.pvs['PC_BIT_CAP:B8' ].caput(TIMEOUT, Yes)      # Div3
        self.pvs['PC_BIT_CAP:B9' ].caput(TIMEOUT, Yes)      # Div4

        self.pvs['PC_ARM_SEL'    ].caput(TIMEOUT, 'External')
        self.pvs['PC_ARM_INP'    ].caput(TIMEOUT, OR1) 

        self.pvs['PC_GATE_SEL'   ].caput(TIMEOUT, 'External')
        self.pvs['PC_GATE_INP'   ].caput(TIMEOUT, PULSE2) 

        # PC_PULSE is only used to determine when the capture is performed.
        # If PC_PULSE_DLY were less than acquire_time_per_pulse_s then the
        # capture of the final point would be too early and we would miss some
        # counts.
        self.pvs['PC_PULSE_SEL'  ].caput(TIMEOUT, 'Time')
        self.pvs['PC_TSPRE'      ].caput(TIMEOUT, 's')

        # The AND gates are used to ensure that Detector and Monitor signals
        # are gated according to both the appropriate windows and whether the
        # acquisition is in progress.
        self.pvs['AND1_ENA:B0'   ].caput(TIMEOUT, Yes)      # INP1_ENA
        self.pvs['AND1_ENA:B1'   ].caput(TIMEOUT, Yes)      # INP2_ENA
        self.pvs['AND1_ENA:B2'   ].caput(TIMEOUT, Yes)      # INP3_ENA
        self.pvs['AND1_ENA:B3'   ].caput(TIMEOUT, No)       # INP4_ENA
        self.pvs['AND1_INP1'     ].caput(TIMEOUT, IN2_TTL)
        self.pvs['AND1_INP2'     ].caput(TIMEOUT, PULSE1)
        self.pvs['AND1_INP3'     ].caput(TIMEOUT, PC_ARM)
        self.pvs['AND1_INP4'     ].caput(TIMEOUT, DISCONNECT)
        self.pvs['AND1_INV:B0'   ].caput(TIMEOUT, No)       # INP1_INV
        self.pvs['AND1_INV:B1'   ].caput(TIMEOUT, No)       # INP2_INV
        self.pvs['AND1_INV:B2'   ].caput(TIMEOUT, No)       # INP3_INV
        self.pvs['AND1_INV:B3'   ].caput(TIMEOUT, No)       # INP4_INV

        self.pvs['AND2_ENA:B0'   ].caput(TIMEOUT, Yes)      # INP1_ENA
        self.pvs['AND2_ENA:B1'   ].caput(TIMEOUT, Yes)      # INP2_ENA
        self.pvs['AND2_ENA:B2'   ].caput(TIMEOUT, Yes)      # INP3_ENA
        self.pvs['AND2_ENA:B3'   ].caput(TIMEOUT, No)       # INP4_ENA
        self.pvs['AND2_INP1'     ].caput(TIMEOUT, IN2_TTL)
        self.pvs['AND2_INP2'     ].caput(TIMEOUT, PULSE2)
        self.pvs['AND2_INP3'     ].caput(TIMEOUT, PC_ARM)
        self.pvs['AND2_INP4'     ].caput(TIMEOUT, DISCONNECT)
        self.pvs['AND2_INV:B0'   ].caput(TIMEOUT, No)       # INP1_INV
        self.pvs['AND2_INV:B1'   ].caput(TIMEOUT, No)       # INP2_INV
        self.pvs['AND2_INV:B2'   ].caput(TIMEOUT, No)       # INP3_INV
        self.pvs['AND2_INV:B3'   ].caput(TIMEOUT, No)       # INP4_INV

        self.pvs['AND3_ENA:B0'   ].caput(TIMEOUT, Yes)      # INP1_ENA
        self.pvs['AND3_ENA:B1'   ].caput(TIMEOUT, Yes)      # INP2_ENA
        self.pvs['AND3_ENA:B2'   ].caput(TIMEOUT, Yes)      # INP3_ENA
        self.pvs['AND3_ENA:B3'   ].caput(TIMEOUT, No)       # INP4_ENA
        self.pvs['AND3_INP1'     ].caput(TIMEOUT, IN3_TTL)
        self.pvs['AND3_INP2'     ].caput(TIMEOUT, PULSE1)
        self.pvs['AND3_INP3'     ].caput(TIMEOUT, PC_ARM)
        self.pvs['AND3_INP4'     ].caput(TIMEOUT, DISCONNECT)
        self.pvs['AND3_INV:B0'   ].caput(TIMEOUT, No)       # INP1_INV
        self.pvs['AND3_INV:B1'   ].caput(TIMEOUT, No)       # INP2_INV
        self.pvs['AND3_INV:B2'   ].caput(TIMEOUT, No)       # INP3_INV
        self.pvs['AND3_INV:B3'   ].caput(TIMEOUT, No)       # INP4_INV

        self.pvs['AND4_ENA:B0'   ].caput(TIMEOUT, Yes)      # INP1_ENA
        self.pvs['AND4_ENA:B1'   ].caput(TIMEOUT, Yes)      # INP2_ENA
        self.pvs['AND4_ENA:B2'   ].caput(TIMEOUT, Yes)      # INP3_ENA
        self.pvs['AND4_ENA:B3'   ].caput(TIMEOUT, No)       # INP4_ENA
        self.pvs['AND4_INP1'     ].caput(TIMEOUT, IN3_TTL)
        self.pvs['AND4_INP2'     ].caput(TIMEOUT, PULSE2)
        self.pvs['AND4_INP3'     ].caput(TIMEOUT, PC_ARM)
        self.pvs['AND4_INP4'     ].caput(TIMEOUT, DISCONNECT)
        self.pvs['AND4_INV:B0'   ].caput(TIMEOUT, No)       # INP1_INV
        self.pvs['AND4_INV:B1'   ].caput(TIMEOUT, No)       # INP2_INV
        self.pvs['AND4_INV:B2'   ].caput(TIMEOUT, No)       # INP3_INV
        self.pvs['AND4_INV:B3'   ].caput(TIMEOUT, No)       # INP4_INV

        # OR1 is being used as a NOT gate, since there is no option to invert
        # the output of GATE1
        self.pvs['OR1_ENA:B0'    ].caput(TIMEOUT, Yes)      # INP1_ENA
        self.pvs['OR1_ENA:B1'    ].caput(TIMEOUT, No)       # INP2_ENA
        self.pvs['OR1_ENA:B2'    ].caput(TIMEOUT, No)       # INP3_ENA
        self.pvs['OR1_ENA:B3'    ].caput(TIMEOUT, No)       # INP4_ENA
        self.pvs['OR1_INP1'      ].caput(TIMEOUT, GATE1)
        self.pvs['OR1_INP2'      ].caput(TIMEOUT, DISCONNECT)
        self.pvs['OR1_INP3'      ].caput(TIMEOUT, DISCONNECT)
        self.pvs['OR1_INP4'      ].caput(TIMEOUT, DISCONNECT)
        self.pvs['OR1_INV:B0'    ].caput(TIMEOUT, Yes)       # INP1_INV
        self.pvs['OR1_INV:B1'    ].caput(TIMEOUT, No)       # INP2_INV
        self.pvs['OR1_INV:B2'    ].caput(TIMEOUT, No)       # INP3_INV
        self.pvs['OR1_INV:B3'    ].caput(TIMEOUT, No)       # INP4_INV

        # GATE1 is used to ensure that only whole acquisition windows are
        # acquired. See collectData() for details of how this works.
        self.pvs['GATE1_INP1'    ].caput(TIMEOUT, SOFT_IN1)
        self.pvs['POLARITY:B0'   ].caput(TIMEOUT, TriggerOnRisingEdge)  # GATE1 Set
        self.pvs['GATE1_INP2'    ].caput(TIMEOUT, PULSE1)
        self.pvs['POLARITY:B4'   ].caput(TIMEOUT, TriggerOnRisingEdge)  # GATE1 Reset

        # The DIV blocks are used to accumulate the detector counts during the
        # acquisition windows defined.
        MaxPulseCount=1000000000
        self.pvs['DIV1_INP'      ].caput(TIMEOUT, AND1)
        self.pvs['POLARITY:B8'   ].caput(TIMEOUT, TriggerOnRisingEdge)  # DIV1 trigger
        self.pvs['DIV1_DIV'      ].caput(TIMEOUT, MaxPulseCount)
        self.pvs['DIV1_DIV'      ].caput(TIMEOUT, MaxPulseCount)    # Setting is not reliable, three times seems to be the charm
        self.pvs['DIV1_DIV'      ].caput(TIMEOUT, MaxPulseCount)    # TODO: Remove when this fixed
        self.pvs['DIV_FIRST:B0'  ].caput(TIMEOUT, DivFirstPulseNumbered1_OUTN)  # DIV1

        self.pvs['DIV2_INP'      ].caput(TIMEOUT, AND2)
        self.pvs['POLARITY:B9'   ].caput(TIMEOUT, TriggerOnRisingEdge)  # DIV2 trigger
        self.pvs['DIV2_DIV'      ].caput(TIMEOUT, MaxPulseCount)
        self.pvs['DIV2_DIV'      ].caput(TIMEOUT, MaxPulseCount)    # Setting is not reliable, three times seems to be the charm
        self.pvs['DIV2_DIV'      ].caput(TIMEOUT, MaxPulseCount)    # TODO: Remove when this fixed
        self.pvs['DIV_FIRST:B1'  ].caput(TIMEOUT, DivFirstPulseNumbered1_OUTN)  # DIV2

        self.pvs['DIV3_INP'      ].caput(TIMEOUT, AND3)
        self.pvs['POLARITY:BA'   ].caput(TIMEOUT, TriggerOnRisingEdge)  # DIV3 trigger
        self.pvs['DIV3_DIV'      ].caput(TIMEOUT, MaxPulseCount)
        self.pvs['DIV3_DIV'      ].caput(TIMEOUT, MaxPulseCount)    # Setting is not reliable, three times seems to be the charm
        self.pvs['DIV3_DIV'      ].caput(TIMEOUT, MaxPulseCount)    # TODO: Remove when this fixed
        self.pvs['DIV_FIRST:B2'  ].caput(TIMEOUT, DivFirstPulseNumbered1_OUTN)  # DIV3

        self.pvs['DIV4_INP'      ].caput(TIMEOUT, AND4)
        self.pvs['POLARITY:BB'   ].caput(TIMEOUT, TriggerOnRisingEdge)  # DIV4
        self.pvs['DIV4_DIV'      ].caput(TIMEOUT, MaxPulseCount)
        self.pvs['DIV4_DIV'      ].caput(TIMEOUT, MaxPulseCount)    # Setting is not reliable, three times seems to be the charm
        self.pvs['DIV4_DIV'      ].caput(TIMEOUT, MaxPulseCount)    # TODO: Remove when this fixed
        self.pvs['DIV_FIRST:B3'  ].caput(TIMEOUT, DivFirstPulseNumbered1_OUTN)  # DIV4

        self.pvs['PULSE1_INP'    ].caput(TIMEOUT, IN1_TTL)
        self.pvs['POLARITY:BC'   ].caput(TIMEOUT, TriggerOnRisingEdge)  # PULSE1 trigger
        self.pvs['PULSE1_PRE'    ].caput(TIMEOUT, 's')

        self.pvs['PULSE2_INP'    ].caput(TIMEOUT, IN1_TTL)
        self.pvs['POLARITY:BD'   ].caput(TIMEOUT, TriggerOnFallingEdge) # PULSE2 trigger
        self.pvs['PULSE2_PRE'    ].caput(TIMEOUT, 's')

        if self.verbose:
            simpleLog("%s:%s() completed." % (self.name, self.pfuncname()))
    ### Local helper functions

    def pfuncname(self):
        import traceback
        return "%s" % traceback.extract_stack()[-2][2]

    ###    Detector interface implementations:

    def collectData(self):
        """ Tells the detector to begin to collect a set of data, then returns
            immediately. """
        if self.verbose:
            simpleLog("%s:%s() started... collectionTime=%r" % (self.name, self.pfuncname(), self.collectionTime))

        # Ensure that the SOFT_IN1 is reset before RESET is performed to ensure
        # that the Arm is not triggered by the RESET.
        self.pvs['SOFT_IN:B0'].caput(TIMEOUT, 0)    # SOFT_IN1

        # Perform a Zebra RESET to clear the DIV counters.
        self.pvs['SYS_RESET.PROC'].caput(TIMEOUT, 1)

        # Reset the last number of points captured so we don't finish before we've started
        self.pvs['PC_NUM_CAP'].caput(TIMEOUT, 0)

        # Set the SOFT_IN1 so that the next PULSE1 will Arm the position compare
        self.pvs['SOFT_IN:B0'].caput(TIMEOUT, 1)

        """ This delays the start of the first count until the first PULSE so that
            we only ever count over the whole PULSE period and never get a partial
            pulse at the start of acquisition:
            
            Option 1, SOFT_IN1 goes high while IN1_TTL is Low:
                10Hz (IN1_TTL) ____~~~~____~~~~____
                      SOFT_IN1 __~~~~~~~~~~~~~~~~~~
                         GATE1 __~~________________
               Not GATE1 (OR1) ~~__~~~~~~~~~~~~~~~~
                  Arm triggers     ^
            
            Option 2, SOFT_IN1 goes high while IN1_TTL is High, :
                10Hz (IN1_TTL) ____~~~~____~~~~____
                      SOFT_IN1 ______~~~~~~~~~~~~~~
                         GATE1 ______~~~~~~________
               Not GATE1 (OR1) ~~~~~~______~~~~~~~~
                  Arm triggers             ^
        """
        if self.verbose:
            simpleLog("%s:%s() completed." % (self.name, self.pfuncname()))

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
        #    simpleLog("%s:%s() started... SOFT_IN1=%r" % (self.name, self.pfuncname(), self.pvs['SOFT_IN:B0'].caget()))

        # If we are acquiring and we haven't captured the required number of points
        if (self.pvs['SOFT_IN:B0'].caget() == u'1'):
            num_captured = int(float(self.pvs['PC_NUM_CAP'].caget()))
            
            #if self.verbose:
            #    simpleLog("%s:%s() PC_NUM_CAP=%r, acquire_time_in_pulses=%r" % (self.name, self.pfuncname(), num_captured, self.acquire_time_in_pulses))
            
            if num_captured < self.acquire_time_in_pulses:
                return self.BUSY

        return self.IDLE
        """
        How do we tell if we are idle?

                                        PC_ARM_OUT    SOFT_IN1    ARRAY_ACQ    PC_NUM_CAP    PC_NUM_DOWN
        After prepareForCollection():      off          off         off         old value     old value
        After collectData():               off           on         off            0          old value     status=BUSY
        After first trigger:                on           on          on            0              0
        After last capture                 off           on         off          last          not last     status=IDLE
        After Download completed           off           on         off          last           last        readout can return
        """

    def readout(self):
        """ Returns the latest data collected. The size of the Object returned
            must be consistent with the values returned by getDataDimensions
            and getExtraNames. """
        if self.verbose:
            simpleLog("%s:%s() started..." % (self.name, self.pfuncname()))
        
        wait_count=0
        while True:
            sleep(.1)
            num_downloaded = int(float(self.pvs['PC_NUM_DOWN'].caget()))
            if num_downloaded == self.acquire_time_in_pulses:
                if self.verbose:
                    simpleLog("Number of points downloaded (%r) == acquire time in pulses (%r)" % (num_downloaded, self.acquire_time_in_pulses) )
                break
            if wait_count > 50:
                simpleLog("Waiting for Number of points downloaded (%r) == acquire time in pulses (%r)" % (num_downloaded, self.acquire_time_in_pulses) )
                wait_count=0
            wait_count += 1
        
        # TODO: We really should return different values when delays are negative, since this also swaps the signals
        mon_rise = float(self.pvs['PC_DIV1_LAST'].caget())
        mon_fall = float(self.pvs['PC_DIV2_LAST'].caget())
        det_rise = float(self.pvs['PC_DIV3_LAST'].caget())
        det_fall = float(self.pvs['PC_DIV4_LAST'].caget())
        return [ self.acquire_time_in_pulses*self.acquire_time_per_pulse_s, 
                 mon_rise, mon_fall, mon_rise-mon_fall, det_rise, det_fall, det_rise-det_fall]

    def _getExtraNames(self):
        return ['t', 'mon_rise', 'mon_fall', 'mon_diff', 'det_rise', 'det_fall', 'det_diff']

    def _getOutputFormat(self):
        return ['%5.5f', '%5.5f', '%d', '%d', '%d', '%d', '%d', '%d']

#    def waitWhileBusy(self):
        """ Wait while the detector collects data. Should return as soon as
            the exposure completes and it is safe to move motors. i.e. counts
            must be safely latched either in hardware or software before
            returning.
        self.waitWhileBusy defined by ScannableBase
        self.isBusy defined by DetectorBase"""

    def getDataDimensions(self):
        """ Returns the dimensions of the data object returned by the readout()
            method. """
        if self.verbose:
            simpleLog("%s:%s() started..." % (self.name, self.pfuncname()))
        return [ 1 ]

    def prepareForCollection(self):
        """ Method called before a scan starts. May be used to setup detector
            for collection, for example MAR345 uses this to erase. """
        if self.verbose:
            simpleLog("%s:%s() started... collectionTime=%r" % (self.name, self.pfuncname(), self.collectionTime))

        #self.setupZebra() Doing this every time adds 40 seconds to the time it takes to prepare the scan

        self.acquire_time_in_pulses = self.collectionTime*10 # 10Hz

        self.pvs['PC_GATE_NGATE' ].caput(TIMEOUT, self.acquire_time_in_pulses)
        self.pvs['PC_PULSE_STEP' ].caput(TIMEOUT, self.acquire_time_per_pulse_s+0.001)
        self.pvs['PC_PULSE_DLY' ].caput(TIMEOUT, self.acquire_time_per_pulse_s)
        # PC_PULSE is only used to determine when the capture is performed.
        # If PC_PULSE_DLY were less than acquire_time_per_pulse_s then the
        # capture of the final point would be too early and we would miss some
        # counts.

        self.pvs['PULSE1_DLY'    ].caput(TIMEOUT, self.absolute_delay_after_rise_s)
        self.pvs['PULSE1_WID'    ].caput(TIMEOUT, self.acquire_time_per_pulse_s)

        self.pvs['PULSE2_DLY'    ].caput(TIMEOUT, self.absolute_delay_after_fall_s)
        self.pvs['PULSE2_WID'    ].caput(TIMEOUT, self.acquire_time_per_pulse_s)

        # Ensure that the SOFT_IN1 is reset so we don't think we have started collection already..
        self.pvs['SOFT_IN:B0'].caput(TIMEOUT, 0)    # SOFT_IN1

        if self.verbose:
            simpleLog("%s:%s() completed." % (self.name, self.pfuncname()))

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
            simpleLog("%s:%s() started..." % (self.name, self.pfuncname()))
        return False

    def getDescription(self):
        """ A description of the detector. """
        if self.verbose:
            simpleLog("%s:%s() started..." % (self.name, self.pfuncname()))
        return "Fast Dicroism Zebra Detector"

    def getDetectorID(self):
        """ A identifier for this detector. """
        if self.verbose:
            simpleLog("%s:%s() started..." % (self.name, self.pfuncname()))
        return self.name

    def getDetectorType(self):
        """ The type of detector. """
        if self.verbose:
            simpleLog("%s:%s() started..." % (self.name, self.pfuncname()))
        return "FastDichroismZebraDetector"

    ###    HardwareTriggeredDetector interface implementations:

    def getHardwareTriggerProvider(self):
        """ Get the HardwareTriggerProvider that represents the controller this Detector is wired to."""
        if self.verbose:
            simpleLog("%s:%s() started..." % (self.name, self.pfuncname()))
        return self.continuousMoveController

    def setNumberImagesToCollect(self, numberImagesToCollect):
        """ Tell the detector how many scan points to collect. (Unfortunately named images)."""
        if self.verbose:
            simpleLog("%s:%s() started..." % (self.name, self.pfuncname()))
        if not numberImagesToCollect == 1:
            simpleLog("Warning numberImagesToCollect > 1 in  %s.%s(%f)" % (self.name, self.pfuncname(), numberImagesToCollect))

    def integratesBetweenPoints(self):
        """ Detectors that sample some value at the time of a trigger should return False. Detectors such as counter timers
            should return True. If true ,TrajectoryScanLine will generate a trigger half a point before the motor reaches a
            demanded point such that the resulting bin of data is centred on the demand position. Area detectors that will be
            triggered by the first pulse should also return true."""
        if self.verbose:
            simpleLog("%s:%s() started..." % (self.name, self.pfuncname()))
        return True

    ###    DetectorWithReadoutTime interface implementations:

    def getReadOutTime(self):
        if self.verbose:
            simpleLog("%s:%s() started..." % (self.name, self.pfuncname()))
        return 0.1 # ToDo: Word out if zero is appropriate here
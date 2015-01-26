"""
Unit tests for ZebraTriggeredDetector for use with GDA at Diamond Light Source
"""

from datetime import datetime
from gda.device.detector import DetectorBase
from Test.mock import Mock, call
from time import sleep
from future.scannable.ZebraTriggeredDetector import ZebraTriggeredDetector
import unittest
from gda.device.zebra.controller.impl import ZebraImpl

class ZebraTriggeredDetectorGatedTest(unittest.TestCase):

    def setUp(self):
        zebra = Mock()
        
        ################### Start Example configuration ###################

        in4ttl=10
        setCollectionTimeInstructions = "Setting collection time in Zebra"
        prepareForCollectionInstructions= """
        It is assumed that the Detector will ready to accept gate signals before
        the scan is started.
        
        If you are having problems, on the Zebra EDM screen (Launchers > Beamlines > BL10I BLADE > ZEB1) ensure that:
            On the SYS tab:
                OUT4 TTL is 55 (PULSE4)
            On the PULSE tab, ensure that:
                PULSE4 input is 63 (SOFT_IN4) and Trigger on Rising Edge
        Also make sure that:
            The Zebra TTL Out 4 is connected to the Camera exp. trig (control in)
            The Zebra TTL In 4  is connected to the Camera busy (status out)
        Finally, make sure that the PCO software is ready and waiting for trigger pulses and that you have noted down
            the filename of the first image which will be saved for this scan."""
        pco = ZebraTriggeredDetector('pco', zebra=zebra, 
            notScanInput=in4ttl, notReadyInput=None, triggerOutSoftInput=4,
            setCollectionTimeInstructions=setCollectionTimeInstructions,
            prepareForCollectionInstructions=prepareForCollectionInstructions,
            gateNotTrigger=True, notScanInverted=True, zebraPulse=4)

        #################### End Example configuration ####################
        
        self.zebra = zebra
        self.detector = pco
        
        self.detector.verbose = True

    def tearDown(self):
        pass

    def testCollectData(self):
        self.detector.exposure_time = 2.2
        self.detector.collectData()
        
        calls = [call(4, True)]
        self.zebra.setSoftInput.assert_has_calls(calls)
        self.assertEqual(self.zebra.setSoftInput.call_count, len(calls))
        
        sleep(self.detector.exposure_time+0.01)
        
        calls.append(call(4,False))
        self.zebra.setSoftInput.assert_has_calls(calls)
        self.assertEqual(self.zebra.setSoftInput.call_count, len(calls))

    def testGetStatusIdle(self):
        self.zebra.isSysStatSet.return_value = False
        
        result = self.detector.getStatus()
        
        self.assertEqual(result, DetectorBase.IDLE)

    def testGetStatusBusy(self):
        self.zebra.isSysStatSet.return_value = True
        
        result = self.detector.getStatus()
        
        self.assertEqual(result, DetectorBase.BUSY)

    def testPrepareForCollection(self):
        self.zebra.isSysStatSet.side_effect = Exception('isSysStatSet should never have been called!')
        self.detector.prepareForCollection()

    def testSetCollectionTimeTooHigh(self):
        #self.zebra.PulseDelayMax = ZebraImpl.PulseDelayMax
        #self.zebra.PULSE_TIMEUNIT_SEC = Exception('PULSE_TIMEUNIT_SEC should not be needed!')
        #self.zebra.PULSE_TIMEUNIT_10SEC = Exception('PULSE_TIMEUNIT_10SEC should not be needed!')
        
        self.assertRaises(Exception, self.detector.setCollectionTime, 655)
        
        self.assertEqual(self.zebra.setPulseDelay.call_count, 0)
        self.assertEqual(self.zebra.setPulseWidth.call_count, 0)
        self.assertEqual(self.zebra.setPulseTimeUnit.call_count, 0)

    def testSetCollectionTimeSeconds(self):
        self.zebra.PulseDelayMax = ZebraImpl.PulseDelayMax
        self.zebra.PULSE_TIMEUNIT_SEC = ZebraImpl.PULSE_TIMEUNIT_SEC
        
        self.detector.setCollectionTime(5.5)
        
        self.zebra.setPulseDelay.assert_called_once_with(self.detector.zebraPulse, 0)
        self.zebra.setPulseWidth.assert_called_once_with(self.detector.zebraPulse, 5.5)
        self.zebra.setPulseTimeUnit.assert_called_once_with(self.detector.zebraPulse, self.zebra.PULSE_TIMEUNIT_SEC)

    def testSetCollectionTime10Secs(self):
        self.zebra.PulseDelayMax = ZebraImpl.PulseDelayMax
        self.zebra.PULSE_TIMEUNIT_SEC = ZebraImpl.PULSE_TIMEUNIT_SEC
        self.zebra.PULSE_TIMEUNIT_10SEC = ZebraImpl.PULSE_TIMEUNIT_10SEC
        
        self.detector.setCollectionTime(65.5)
        
        self.zebra.setPulseDelay.assert_called_once_with(self.detector.zebraPulse, 0)
        self.zebra.setPulseWidth.assert_called_once_with(self.detector.zebraPulse, 6.55)
        self.zebra.setPulseTimeUnit.assert_called_once_with(self.detector.zebraPulse, self.zebra.PULSE_TIMEUNIT_10SEC)

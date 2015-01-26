"""
Unit tests for ZebraTriggeredDetector for use with GDA at Diamond Light Source
"""

from datetime import datetime
from gda.device.detector import DetectorBase
from Test.mock import Mock, call
from time import sleep
from future.scannable.ZebraTriggeredDetector import ZebraTriggeredDetector
import unittest

class ZebraTriggeredDetectorTest(unittest.TestCase):

    def setUp(self):
        zebra = Mock()
        
        ################### Start Example configuration ###################
        in4ttl=10
        in3ttl=7
        setCollectionTimeInstructions = """    In addition:
            On the Main tab, as well as setting the exposure time, make sure that:
                Number of images is set to 1
                CCD Readout is set to Full
                Accumulations is set to 1
            On the Data File tab make sure that:
                The Data file is set to a suitable name and that it
                will be written to your visit directory
            On the ADC tab make sure that:
                Rate is set to 1MHz
            On the Timing tab make sure that:
                Mode is set to External Sync
                The Continuous Cleans checkbox is checked
                Shutter Control is Normal
                Safe mode is selected
                Delay time is 0.5seconds
                Edge trigger is + edge
        Also make sure that:
            The Zebra TTL Out 4 is connected to the ST-133 Ext Sync input
            The Zebra TTL In 4  is connected to the ST-133 NOT SCAN output
            The Zebra TTL In 3  is connected to the ST-133 NOT READY output"""
        prepareForCollectionInstructions="Please ensure that all acquisition parameters are correct before pressing the Acquire button."
        pimte = ZebraTriggeredDetector('pimte', zebra=zebra, 
            notScanInput=in4ttl, notReadyInput=in3ttl, triggerOutSoftInput=4,
            setCollectionTimeInstructions=setCollectionTimeInstructions,
            prepareForCollectionInstructions=prepareForCollectionInstructions)
        
        #################### End Example configuration ####################
        
        self.zebra = zebra
        self.detector = pimte
        
        self.detector.verbose = True

    def tearDown(self):
        pass

    def testCollectData(self):
        self.detector.exposure_time = 2.2
        self.detector.collectData()
        
        calls = [call(4, True)]
        self.zebra.setSoftInput.assert_has_calls(calls)
        self.assertEqual(self.zebra.setSoftInput.call_count, len(calls))
        
        sleep(0.1+0.01)
        
        calls.append(call(4,False))
        self.zebra.setSoftInput.assert_has_calls(calls)
        self.assertEqual(self.zebra.setSoftInput.call_count, len(calls))

    def testGetStatusIdle(self):
        self.zebra.isSysStatSet.return_value = True
        
        result = self.detector.getStatus()
        
        self.assertEqual(result, DetectorBase.IDLE)

    def testGetStatusBusy(self):
        self.zebra.isSysStatSet.return_value = False
        
        result = self.detector.getStatus()
        
        self.assertEqual(result, DetectorBase.BUSY)

    def testPrepareForCollection(self):
        # Note: this test takes over 5 seconds to run, due to the sleeps in prepareForCollection.
        #self.zebra.isSysStatSet.side_effect = lambda x: {self.detector.notReadyInput: 0}[x]
        returnValues=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0]
        
        self.zebra.isSysStatSet.side_effect = returnValues
        self.detector.prepareForCollection()
        
        calls = [call(self.detector.notReadyInput)]*len(returnValues)
        self.zebra.isSysStatSet.assert_has_calls(calls)
        self.assertEqual(self.zebra.isSysStatSet.call_count, len(returnValues))

    def testSetCollectionTime(self):
        self.detector.setCollectionTime(5.5)
        
        self.assertEqual(self.zebra.setPulseDelay.call_count, 0)
        self.assertEqual(self.zebra.setPulseWidth.call_count, 0)
        self.assertEqual(self.zebra.setPulseTimeUnit.call_count, 0)

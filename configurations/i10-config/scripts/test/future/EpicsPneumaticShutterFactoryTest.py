"""
Unit tests for Factory for creating open/close commands for shutters and
valves for use with GDA at Diamond Light Source

For help with configuring the Factory, see the example configuration below,
search for "Start Example configuration".
"""

import unittest
from Test.mock import Mock, call

from future.EpicsPneumaticShutterFactory import EpicsPneumaticShutterFactory

class EpicsPneumaticShutterFactoryTest(unittest.TestCase):

    def setUp(self):
        beamline = Mock()
        
        ################### Start Example configuration ###################
        
        #beamline = Finder.find("Beamline")
        shopen = EpicsPneumaticShutterFactory(beamline, "EH Shutter", "-PS-SHTR-02", True)
        shclose = EpicsPneumaticShutterFactory(beamline, "EH Shutter", "-PS-SHTR-02", False)
        
        #################### End Example configuration ####################
        
        self.beamline = beamline
        self.shopen = shopen
        self.shclose = shclose

    def tearDown(self):
        pass

    def testOpen(self):
        self.beamline.getValue.return_value = '1'
        
        result = self.shopen()
        
        calls = [call("Top", "-PS-SHTR-02:CON", 2),
                 call("Top", "-PS-SHTR-02:CON", 0) ]
        self.beamline.setValue.assert_has_calls(calls)
        self.beamline.getValue.assert_called_with(None, "Top", "-PS-SHTR-02:STA")
        
        self.assertEqual(' -> EH Shutter Open.', result)

    def testOpenTimeout(self):
        self.beamline.getValue.return_value = '0'
        
        result = self.shopen()
        
        self.assertEqual(" -> Time out: Could not Open EH Shutter.", result)

    def testClose(self):
        self.beamline.getValue.return_value = '3'
        
        result = self.shclose()
        
        calls = [call("Top", "-PS-SHTR-02:CON", 2),
                 call("Top", "-PS-SHTR-02:CON", 1) ]
        self.beamline.setValue.assert_has_calls(calls)
        self.beamline.getValue.assert_called_with(None, "Top", "-PS-SHTR-02:STA")
        
        self.assertEqual(' -> EH Shutter Closed.', result)

    def testCloseTimeout(self):
        self.beamline.getValue.return_value = '0'
        
        result = self.shclose()
        
        self.assertEqual(" -> Time out: Could not Close EH Shutter.", result)

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
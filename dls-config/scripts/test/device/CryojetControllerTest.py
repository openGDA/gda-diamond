"""
Oxford Diffraction Cryojet Intelligent Temperature Controller (ITC) device
Unit tests for use with GDA at Diamond Light Source
"""

import unittest
from mock import Mock
from dls_scripts.device.CryojetController import CryojetController

class CryojetControllerTest(unittest.TestCase):

    def setUp(self):
        self.itc = CryojetController(Mock)

    def tearDown(self):
        pass

    def testDeviceSetup(self):
        itc = CryojetController(Mock)
        
        self.assertEquals(repr(self.itc), repr(itc))

    def test__repr__(self):
        self.assertEquals(repr(self.itc),
            "CryojetController(pvroot='')")

    # TODO: Work out how to simulate a gdascripts.scannable.epics.PvManager with
    #       a Mock() object. Until then, this test will fail.
    #def test__str__(self):
    #    self.itc.pvs['setpoint'].caget.return_value=0.123
    #    self.itc.pvs['demand_field'].caget.return_value=0.234
    #    self.assertEquals(str(self.itc), 
    #        'setpoint=0123, demand_field=0234')

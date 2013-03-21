"""
Unit tests for Oxford Diffraction Intelligent Temperature Controller device
for use with GDA at Diamond Light Source
"""

import unittest
from mock import Mock
from high_field_magnet.device.intelligentTemperatureController import IntelligentTemperatureController

class IntelligentPowerSupplyDeviceTest(unittest.TestCase):

    def setUp(self):
        self.itc = IntelligentTemperatureController(Mock)

    def tearDown(self):
        pass

    def testDeviceSetup(self):
        ips = IntelligentTemperatureController(Mock)
        
        self.assertEquals(repr(self.itc), repr(ips))

    def test__repr__(self):
        self.assertEquals(repr(self.itc),
            "IntelligentTemperatureController('')")

    # TODO: Work out how to simulate a gdascripts.scannable.epics.PvManager with
    #       a Mock() object. Until then, this test will fail.
    def test__str__(self):
        self.itc.pvs['setpoint'].caget.return_value=0.123
        self.itc.pvs['demand_field'].caget.return_value=0.234
        self.assertEquals(str(self.retRotFE), 
            'setpoint=0123, demand_field=0234')

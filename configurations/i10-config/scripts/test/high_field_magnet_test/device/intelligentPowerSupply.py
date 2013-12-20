"""
Unit tests for Oxford Diffraction Intelligent Power Supply device
for use with GDA at Diamond Light Source
"""

import unittest
from Test.mock import MagicMock
from high_field_magnet.device.intelligentPowerSupply import IntelligentPowerSupply

class IntelligentPowerSupplyDeviceTest(unittest.TestCase):

    def setUp(self):
        self.ips = IntelligentPowerSupply(MagicMock())
        

    def tearDown(self):
        pass

    def testDeviceSetup(self):
        ips = IntelligentPowerSupply(MagicMock())
        
        self.assertEquals(repr(self.ips), repr(ips))

    def test__repr__(self):
        self.assertEquals(repr(self.ips),
            "IntelligentPowerSupplyScannable('')")

    # TODO: Work out how to simulate a gdascripts.scannable.epics.PvManager with
    #       a Mock() object. Until then, this test will fail.
    def test__str__(self):
        self.ips.pvs['setpoint'].caget.return_value=0.123 # Mock() fails here.
        self.ips.pvs['demand_field'].caget.return_value=0.234
        self.assertEquals(str(self.ips), # MagicMock() fails here.
            'setpoint=0.123, demand_field=0.234')

    def testGetSetpoint(self):
        self.ips.pvs['setpoint'].caget.return_value=0.123
        self.assertEquals(self.ips.getFieldSetPoint(), 0.123)

    def testGetFieldDemand(self):
        self.ips.pvs['demand_field'].caget.return_value=0.123
        self.assertEquals(self.ips.getFieldDemand(), 0.123)

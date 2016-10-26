"""
Oxford Diffraction Cryojet Intelligent Temperature Controller (ITC) scannable
Unit tests for use with GDA at Diamond Light Source
"""

import unittest
from mock import Mock
from dls_scripts.scannable.CryojetScannable import CryojetScannable

class CryojetScannableTest(unittest.TestCase):

    def setUp(self):
        self.cryo = CryojetScannable('cryo', Mock, 1, 0)

    def tearDown(self):
        pass

    def testDeviceSetup(self):
        cryo = CryojetScannable('cryo', Mock, 1, 0)
        
        self.assertEquals(repr(self.cryo), repr(cryo))

    def test__repr__(self):
        self.assertEquals(repr(self.cryo),
            "CryojetScannable(name=u'cryo', pvroot='', temp_tolerance=1, stable_time_sec=0)")

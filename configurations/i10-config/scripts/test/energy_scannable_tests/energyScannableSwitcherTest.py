"""
Unit tests for Energy scannable for use with I10 insertion devices on GDA at
Diamond Light Source

For help with configuring an Energy scannable, see the example configuration
below, search for "Start Example configuration".
"""

import unittest
from mock import Mock
from Diamond.energyScannableSwitcher import EnergyScannableSwitcher

class EnergyScannableSwitcherTest(unittest.TestCase):

    def setUp(self):
        # Initialise these as local, so the example code looks the same
        # as it will in localstation or a user script.
        self.idd_pos_neg_switchable = Mock()
        self.idd_pos_neg_switchable.name = 'idd_pos_neg_switchable'
        ################### Start Example configuration ###################

        idd_pos_neg_switcher = EnergyScannableSwitcher(
            'idd_pos_neg_switcher', self.idd_pos_neg_switchable)

        #################### End Example configuration ####################  
        self.idd_pos_neg_switcher = idd_pos_neg_switcher

    def tearDown(self):
        pass

    def testScannableSetup(self):
        idd_pos_neg_switcher = EnergyScannableSwitcher(
            'idd_pos_neg_switcher', self.idd_pos_neg_switchable)
        
        self.assertEquals(repr(self.idd_pos_neg_switcher),
                          repr(idd_pos_neg_switcher))
        
        self.assertEqual('idd_pos_neg_switcher', self.idd_pos_neg_switcher.name)
        self.assertEqual(list(self.idd_pos_neg_switcher.inputNames), ['idd_pos_neg_switcher'])
        self.assertEqual(list(self.idd_pos_neg_switcher.extraNames), [])
        self.assertEqual(list(self.idd_pos_neg_switcher.outputFormat), ['%d'])

    def test__str__(self):
        self.idd_pos_neg_switchable.getNextScannable.return_value = 456
        self.assertEquals(str(self.idd_pos_neg_switcher), "idd_pos_neg_switcher=456")

    def test__repr__(self):
        self.assertEquals(repr(self.idd_pos_neg_switcher), "EnergyScannableSwitchable(u'idd_pos_neg_switcher', 'idd_pos_neg_switchable')")

    def testAsynchronousMoveTo(self):
        self.idd_pos_neg_switcher.asynchronousMoveTo(123)
        self.idd_pos_neg_switchable.setNextScannable.assert_called_with(123)

    def testGetPosition(self):
        self.idd_pos_neg_switchable.getNextScannable.return_value = 234
        self.assertEqual(self.idd_pos_neg_switcher.getPosition(), 234)

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
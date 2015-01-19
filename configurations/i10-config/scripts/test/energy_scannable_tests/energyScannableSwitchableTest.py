"""
Unit tests for Energy scannable for use with I10 insertion devices on GDA at
Diamond Light Source

For help with configuring an Energy scannable, see the example configuration
below, search for "Start Example configuration".
"""

import unittest
from mock import Mock
from Diamond.energyScannableSwitchable import EnergyScannableSwitchable

class EnergyScannableSwitchableTest(unittest.TestCase):

    def setUp(self):
        # Initialise these as local, so the example code looks the same
        # as it will in localstation or a user script.
        self.idd_pos = Mock()
        self.idd_pos.name = 'idd_pos'
        self.idd_pos.getExtraNames.return_value = ['extra1', 'extra2']
        self.idd_pos.getOutputFormat.return_value = ['%f', '%f', '%f']
        self.idd_neg = Mock()
        self.idd_neg.name = 'idd_neg'
        self.idd_neg.getExtraNames.return_value = ['extra1', 'extra2']
        self.idd_neg.getOutputFormat.return_value = ['%f', '%f', '%f']
        ################### Start Example configuration ###################

        idd_pos_neg_switchable = EnergyScannableSwitchable(
            'idd_pos_neg_switchable', [self.idd_pos, self.idd_neg])

        #################### End Example configuration ####################  
        self.idd_pos_neg_switchable = idd_pos_neg_switchable

    def tearDown(self):
        pass

    def testScannableSetup(self):
        idd_pos_neg_switchable = EnergyScannableSwitchable(
            'idd_pos_neg_switchable', [self.idd_pos, self.idd_neg])
        
        self.assertEquals(repr(self.idd_pos_neg_switchable),
                          repr(idd_pos_neg_switchable))
        
        self.assertEqual('idd_pos_neg_switchable', self.idd_pos_neg_switchable.name)
        self.assertEqual(list(self.idd_pos_neg_switchable.inputNames), ['idd_pos_neg_switchable'])
        self.assertEqual(list(self.idd_pos_neg_switchable.extraNames), ['extra1', 'extra2'])
        self.assertEqual(list(self.idd_pos_neg_switchable.outputFormat), ['%f', '%f', '%f'])

    def test__str__(self):
        self.idd_pos.getPosition.return_value = (1.2, 2.3, 3.4)
        self.assertEquals(str(self.idd_pos_neg_switchable), "idd_pos_neg_switchable=1.200000, extra1=2.300000, extra2=3.400000")
#
    def test__repr__(self):
        self.assertEquals(repr(self.idd_pos_neg_switchable), "EnergyScannableSwitchable(u'idd_pos_neg_switchable', ['idd_pos', 'idd_neg'])")

    def testAsynchronousMoveToFirst(self):
        self.idd_pos_neg_switchable.energyScannableInsideSwitcher = None
        self.idd_pos_neg_switchable.asynchronousMoveTo(1234.5)
        self.idd_pos.asynchronousMoveTo.assert_called_with(1234.5)
        self.assertEqual(self.idd_neg.asynchronousMoveTo.call_count, 0)

    def testAsynchronousMoveToInner(self):
        self.idd_pos_neg_switchable.energyScannableInsideSwitcher = True
        self.idd_pos_neg_switchable.asynchronousMoveTo(1234.5)
        self.idd_pos.asynchronousMoveTo.assert_called_with(1234.5)
        self.assertEqual(self.idd_neg.asynchronousMoveTo.call_count, 0)

    def testAsynchronousMoveToOuter(self):
        self.idd_pos_neg_switchable.energyScannableInsideSwitcher = False
        self.idd_pos_neg_switchable.asynchronousMoveTo(1234.5)
        self.assertEqual(self.idd_pos.asynchronousMoveTo.call_count, 0)
        self.assertEqual(self.idd_neg.asynchronousMoveTo.call_count, 0)

    def testGetPosition(self):
        self.idd_pos.getPosition.return_value = (1.2, 2.3, 3.4)
        self.assertEqual(list(self.idd_pos_neg_switchable.getPosition()), [1.2, 2.3, 3.4])

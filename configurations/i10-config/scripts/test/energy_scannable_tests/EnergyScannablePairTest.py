"""
Unit tests for Energy scannable for use with I10 insertion devices on GDA at
Diamond Light Source

For help with configuring an Energy scannable, see the example configuration
below, search for "Start Example configuration".
"""

import unittest
from Test.mock import MagicMock
from Diamond.Poly import Poly
from Diamond.EnergyScannable import EnergyScannable
from Diamond.EnergyScannablePair import EnergyScannablePair

class EnergyScannablePairTest(unittest.TestCase):

    def setUp(self):
        # Initialise these as local, so the example code looks the same
        # as it will in localstation or a user script.
        (idu_gap, idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, idu_jawphase,
         idd_gap, idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, idd_jawphase,
         pgm_energy) = self.setUpMocks()
        
        ################### Start Example configuration ###################  
        # Positive circular polarisation
        idu_circ_pos_energy = EnergyScannable('idu_circ_pos_energy', idu_gap, 
            idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, 
            idu_jawphase, pgm_energy,
            gap=16, rowphase1=15.1724, rowphase2=0, rowphase3=15.1724, rowphase4=0,  
            jawphase_poly=Poly(power0first=False, coeffs=
                          [1.9348427564961812e-40, -3.1126995721309230e-36,
                           2.3047622879259613e-32, -1.0412681219138865e-28,
                           3.2081024655562872e-25, -7.1352299398740346e-22,
                           1.1827360301838759e-18, -1.4868981155109573e-15,
                           1.4284943075718623e-12, -1.0481476204057386e-09,
                           5.8225647884164763e-07, -2.4036499938966973e-04,
                           7.1349214643820852e-02, -1.4372449558778261e+01,
                           1.7564915878491570e+03, -9.8177319470976290e+04 ] ) )
        
        # Negative circular polarisation
        idd_circ_neg_energy = EnergyScannable('idd_circ_neg_energy', idd_gap, 
            idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, 
            idd_jawphase, pgm_energy,
            gap=16, rowphase1=-15.1724, rowphase2=0, rowphase3=-15.1724, rowphase4=0,  
            jawphase_poly=Poly(power0first=False, coeffs=
                          [7.2663310131321569e-43, -1.0175127616060827e-37,
                           1.4214278244059263e-33, -9.4388200887468604e-30,
                           3.8351579795646889e-26, -1.0581689343594696e-22,
                           2.0916183094103308e-19, -3.0497195398509381e-16,
                           3.3285639917557250e-13, -2.7303600657863037e-10,
                           1.6739050602639844e-07, -7.5457697253971458e-05,
                           2.4242927611627316e-02, -5.2460103475433995e+00,
                           6.8435482439065288e+02, -4.0611673888060664e+04 ] ) )

        id_circ_energy = EnergyScannablePair('id_circ_energy',
            idu_circ_pos_energy, idd_circ_neg_energy)

        #################### End Example configuration ####################  

        self.idu_circ_pos_energy = idu_circ_pos_energy
        self.idd_circ_neg_energy = idd_circ_neg_energy
        self.id_circ_energy = id_circ_energy

    def mockMotor(self, name):
        motor = MagicMock()
        motor.name = name
        motor.isBusy.return_value = False
        return motor

    def setUpMocks(self):
        self.idu_gap = self.mockMotor("idu_gap")
        self.idu_rowphase1 = self.mockMotor("idu_rowphase1")
        self.idu_rowphase2 = self.mockMotor("idu_rowphase2")
        self.idu_rowphase3 = self.mockMotor("idu_rowphase3")
        self.idu_rowphase4 = self.mockMotor("idu_rowphase4")
        self.idu_jawphase = self.mockMotor("idu_jawphase")
        
        self.idd_gap = self.mockMotor("idd_gap")
        self.idd_rowphase1 = self.mockMotor("idd_rowphase1")
        self.idd_rowphase2 = self.mockMotor("idd_rowphase2")
        self.idd_rowphase3 = self.mockMotor("idd_rowphase3")
        self.idd_rowphase4 = self.mockMotor("idd_rowphase4")
        self.idd_jawphase = self.mockMotor("idd_jawphase")
        
        self.pgm_energy = self.mockMotor("pgm_energy")

        return (self.idu_gap, self.idu_rowphase1, self.idu_rowphase2,
                self.idu_rowphase3, self.idu_rowphase4, self.idu_jawphase,
                self.idd_gap, self.idd_rowphase1, self.idd_rowphase2,
                self.idd_rowphase3, self.idd_rowphase4, self.idd_jawphase,
                self.pgm_energy)
        
    def tearDown(self):
        pass

    def testScannablePairSetup(self):
        ice = EnergyScannablePair('id_circ_energy', self.idu_circ_pos_energy, self.idd_circ_neg_energy)

        self.assertEquals(repr(self.id_circ_energy), repr(ice))
        
        self.assertEqual('id_circ_energy', self.id_circ_energy.name)
        self.assertEqual(list(self.id_circ_energy.inputNames), ['id_circ_energy'])
        self.assertEqual(list(self.id_circ_energy.extraNames), [u'idu_gap', u'idu_rowphase1', u'idu_rowphase2', u'idu_rowphase3', u'idu_rowphase4', u'idu_jawphase', u'idd_gap', u'idd_rowphase1', u'idd_rowphase2', u'idd_rowphase3', u'idd_rowphase4', u'idd_jawphase', u'pgm_energy', u'diff_energy'])
        self.assertEqual(list(self.id_circ_energy.outputFormat), ['%f', 
                                                                  '%f', '%f', '%f', '%f', '%f', '%f',
                                                                  '%f', '%f', '%f', '%f', '%f', '%f',
                                                                  '%f', '%f'])

    def test__str__(self):
        self.idu_gap.getPosition.return_value = 1234
        self.idu_rowphase1.getPosition.return_value = 2345
        self.idu_rowphase2.getPosition.return_value = 3456
        self.idu_rowphase3.getPosition.return_value = 4567
        self.idu_rowphase4.getPosition.return_value = 5678
        self.idu_jawphase.getPosition.return_value = 6789
        self.pgm_energy.getPosition.return_value = 7890
        self.idd_gap.getPosition.return_value = 4321
        self.idd_rowphase1.getPosition.return_value = 5432
        self.idd_rowphase2.getPosition.return_value = 6543
        self.idd_rowphase3.getPosition.return_value = 7654
        self.idd_rowphase4.getPosition.return_value = 8765
        self.idd_jawphase.getPosition.return_value = 9876
        
        self.assertEquals(str(self.id_circ_energy), "id_circ_energy=0.000000, idu_gap=1234.000000, idu_rowphase1=2345.000000, idu_rowphase2=3456.000000, idu_rowphase3=4567.000000, idu_rowphase4=5678.000000, idu_jawphase=6789.000000, idd_gap=4321.000000, idd_rowphase1=5432.000000, idd_rowphase2=6543.000000, idd_rowphase3=7654.000000, idd_rowphase4=8765.000000, idd_jawphase=9876.000000, pgm_energy=7890.000000, diff_energy=-7890.000000")

    def test__repr__(self):
        self.assertEquals(repr(self.id_circ_energy), "EnergyScannablePair(u'id_circ_energy', u'idu_circ_pos_energy', u'idd_circ_neg_energy')")

    def testAsynchronousMoveTo1(self):
        self.assert_id_circ_energy(372.9, 0.45074769097846, 0.09828315057529835)

    def testAsynchronousMoveTo2(self):
        self.assert_id_circ_energy(683, 6.722407042281702, 6.3007987740202225)

    def testAsynchronousMoveTo3(self):
        self.assert_id_circ_energy(1706, 11.461331958184019, 11.262104026587622)

    def assert_id_circ_energy(self, energy_eV, expected_idu_jawphase, expected_idd_jawphase):
        self.id_circ_energy.asynchronousMoveTo(energy_eV)

        # NOTE: assert_called_once_with silently fails with Mock() objects. 
        assert(isinstance(self.pgm_energy, MagicMock))

        self.pgm_energy.asynchronousMoveTo.assert_called_once_with(energy_eV)

        self.idu_gap.asynchronousMoveTo.assert_called_once_with(16)
        self.idu_rowphase1.asynchronousMoveTo.assert_called_once_with(15.1724)
        self.idu_rowphase2.asynchronousMoveTo.assert_called_once_with(0)
        self.idu_rowphase3.asynchronousMoveTo.assert_called_once_with(15.1724)
        self.idu_rowphase4.asynchronousMoveTo.assert_called_once_with(0)
        self.idu_jawphase.asynchronousMoveTo.assert_called_once_with(expected_idu_jawphase)

        self.idd_gap.asynchronousMoveTo.assert_called_once_with(16)
        self.idd_rowphase1.asynchronousMoveTo.assert_called_once_with(-15.1724)
        self.idd_rowphase2.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_rowphase3.asynchronousMoveTo.assert_called_once_with(-15.1724)
        self.idd_rowphase4.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_jawphase.asynchronousMoveTo.assert_called_once_with(expected_idd_jawphase)

    def testGetPositionCN(self):
        self.id_circ_energy.last_energy_eV = 890

        self.idu_gap.getPosition.return_value = 123
        self.idu_rowphase1.getPosition.return_value = 234
        self.idu_rowphase2.getPosition.return_value = 345
        self.idu_rowphase3.getPosition.return_value = 456
        self.idu_rowphase4.getPosition.return_value = 567
        self.idu_jawphase.getPosition.return_value = 678

        self.idd_gap.getPosition.return_value = 321
        self.idd_rowphase1.getPosition.return_value = 432
        self.idd_rowphase2.getPosition.return_value = 543
        self.idd_rowphase3.getPosition.return_value = 654
        self.idd_rowphase4.getPosition.return_value = 765
        self.idd_jawphase.getPosition.return_value = 876

        self.pgm_energy.getPosition.return_value = 789

        self.assertEqual(list(self.id_circ_energy.getPosition()), [890, 123, 234, 345, 456, 567, 678, 321, 432, 543, 654, 765, 876, 789, 101])

    ''' testIsBusy creates a dictionary of tests as keys and populates the
        expected results as the values '''        
    def testIsBusy(self):
        # Generate combinations, with a default of expecting True
        combinations=dict([((a,b,c,d),True) for a in (True,False) for b in (True,False) for c in (True,False) for d in (True,False)])
        # Exceptions
        combinations[(False,False,False,False)]=False

        for (a, b, c, d), assertion in combinations.iteritems():
            self.idu_gap.isBusy.return_value = a
            self.idu_rowphase1.isBusy.return_value = b
            self.idu_rowphase2.isBusy.return_value = b
            self.idu_rowphase3.isBusy.return_value = b
            self.idu_rowphase4.isBusy.return_value = b
            self.idu_jawphase.isBusy.return_value = c
            self.pgm_energy.isBusy.return_value = d

            # Put the args in the assert, so we get to see which one fails.
            self.assertEqual(((a,b,c,d),self.id_circ_energy.isBusy()),
                             ((a,b,c,d),assertion))

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
"""
Unit tests for Energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source

For help with configuring an Energy scannable, see the example configuration
below, search for "Start Example configuration".
"""

import unittest
from Test.mock import MagicMock
from Diamond.energyScannableLookup import EnergyScannableLookup

class EnergyScannableLookupTest(unittest.TestCase):

    def setUp(self):
        # Initialise these as local, so the example code looks the same
        # as it will in localstation or a user script.
        (idd_gap, idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4,
         idd_jawphase, pgm_energy) = self.setUpMocks()

        ################### Start Example configuration ###################  
        # Linear horizontal polarisation
        idd_lin_hor_energy = EnergyScannableLookup('idd_lin_hor_energy', idd_gap, 
            idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, 
            idd_jawphase, pgm_energy,
            gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0,  
            jawphase_lookup={234.9 :  0.35757490864580177,
                             318.1 :  4.500804625652563,
                             516.3 :  7.060484231163173,
                             1660. : 11.226959483586143} )
        #################### End Example configuration ####################  
        self.idd_lin_hor_energy = idd_lin_hor_energy

    def mockMotor(self, name):
        motor = MagicMock()
        motor.name = name
        motor.isBusy.return_value = False
        return motor

    def setUpMocks(self):
        self.idd_gap = self.mockMotor("idd_gap")
        self.idd_rowphase1 = self.mockMotor("idd_rowphase1")
        self.idd_rowphase2 = self.mockMotor("idd_rowphase2")
        self.idd_rowphase3 = self.mockMotor("idd_rowphase3")
        self.idd_rowphase4 = self.mockMotor("idd_rowphase4")
        self.idd_jawphase = self.mockMotor("idd_jawphase")
        self.pgm_energy = self.mockMotor("pgm_energy")

        return (self.idd_gap, self.idd_rowphase1, self.idd_rowphase2,
                self.idd_rowphase3, self.idd_rowphase4,
                self.idd_jawphase, self.pgm_energy)

    def tearDown(self):
        pass

    def test__str__(self):
        self.idd_gap.getPosition.return_value = 1234
        self.idd_rowphase1.getPosition.return_value = 2345
        self.idd_rowphase2.getPosition.return_value = 3456
        self.idd_rowphase3.getPosition.return_value = 5678
        self.idd_rowphase4.getPosition.return_value = 6789
        self.idd_jawphase.getPosition.return_value = 7.890
        self.pgm_energy.getPosition.return_value = 8901
        
        self.assertEquals(str(self.idd_lin_hor_energy), "idd_lin_hor_energy=0.000000, idd_gap=1234.000000, idd_rowphase1=2345.000000, idd_rowphase2=3456.000000, idd_rowphase3=5678.000000, idd_rowphase4=6789.000000, idd_jawphase=7.890000, pgm_energy=8901.000000, diff_energy=-8901.000000, id_energy=744.002585, id_diff=-744.002585")

    def test__repr__LH(self):
        self.assertEquals(repr(self.idd_lin_hor_energy), "EnergyScannableLookup(u'idd_lin_hor_energy', 'idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0, jawphase_lookup={234.9: 0.35757490864580177, 318.1: 4.500804625652563, 516.3: 7.060484231163173, 1660.0: 11.226959483586143})")

    def testAsynchronousMoveToLH1(self):
        self.assert_idd_lin_hor_energy(234.9, 0.35757490864580177)

    def testAsynchronousMoveToLH2(self):
        self.assert_idd_lin_hor_energy(318.1, 4.500804625652563)

    def testAsynchronousMoveToLH3(self):
        self.assert_idd_lin_hor_energy(516.3, 7.060484231163173)

    def testAsynchronousMoveToLH4(self):
        self.assert_idd_lin_hor_energy(1660, 11.226959483586143)

    def testAsynchronousMoveToLH5(self):
        pass # self.assert_idd_lin_hor_energy(100, 1)

    def testAsynchronousMoveToLH6(self):
        self.assert_idd_lin_hor_energy(300, 3.599452968467197)

    def testAsynchronousMoveToLH7(self):
        self.assert_idd_lin_hor_energy(400, 5.558512797657199)

    def testAsynchronousMoveToLH8(self):
        self.assert_idd_lin_hor_energy(600, 7.365401585913372)

    def testAsynchronousMoveToLH9(self):
        pass # self.assert_idd_lin_hor_energy(1900, 10)

    def assert_idd_lin_hor_energy(self, energy_eV, jawphase):
        self.idd_lin_hor_energy.asynchronousMoveTo(energy_eV)

        #self.assertEquals(energy_eV, self.idd_lin_hor_energy.getEnergy(self.idd_lin_hor_energy.getIdPosition(energy_eV)))
        
        # NOTE: assert_called_once_with silently fails with Mock() objects. 
        assert(isinstance(self.pgm_energy, MagicMock))

        self.pgm_energy.asynchronousMoveTo.assert_called_once_with(energy_eV)
        self.idd_gap.asynchronousMoveTo.assert_called_once_with(16)
        self.idd_rowphase1.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_rowphase2.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_rowphase3.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_rowphase4.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_jawphase.asynchronousMoveTo.assert_called_once_with(jawphase)

    ''' testIsBusy creates a dictionary of tests as keys and populates the
        expected results as the values '''        
    def testIsBusy(self):
        # Generate combinations, with a default of expecting True
        combinations=dict([((a,b,c,d),True) for a in (True,False) for b in (True,False) for c in (True,False) for d in (True,False)])
        # Exceptions
        combinations[(False,False,False,False)]=False

        for (a, b, c, d), assertion in combinations.iteritems():
            self.idd_gap.isBusy.return_value = a
            self.idd_rowphase1.isBusy.return_value = b
            self.idd_rowphase2.isBusy.return_value = b
            self.idd_rowphase3.isBusy.return_value = b
            self.idd_rowphase4.isBusy.return_value = b
            self.idd_jawphase.isBusy.return_value = c
            self.pgm_energy.isBusy.return_value = d

            # Put the args in the assert, so we get to see which one fails.
            self.assertEqual(((a,b,c,d),self.idd_lin_hor_energy.isBusy()),
                             ((a,b,c,d),assertion))

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
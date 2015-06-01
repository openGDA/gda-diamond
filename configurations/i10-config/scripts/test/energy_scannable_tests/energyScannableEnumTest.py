"""
Unit tests for Energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source

For help with configuring an Energy scannable, see the example configuration
below, search for "Start Example configuration".
"""

import unittest
from mock import Mock
from Diamond.energyScannableEnum import EnergyScannableEnum
from Diamond.idPosition import IdPosition

class EnergyScannablePolyTest(unittest.TestCase):

    def setUp(self):
        # Initialise these as local, so the example code looks the same
        # as it will in localstation or a user script.
        (idd_gap, idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4,
         idd_jawphase, pgm_energy) = self.setUpMocks()

        idd_select_energy = EnergyScannableEnum('idd_select_energy', idd_gap, 
            idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, 
            idd_jawphase, pgm_energy,
            {234.9 : IdPosition(gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0, jawphase=0.235)
            ,318.1 : IdPosition(gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0, jawphase=4.524)
            ,516.3 : IdPosition(gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0, jawphase=7.076)
            ,1660  : IdPosition(gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0, jawphase=11.25)
            } )
        
        #################### End Example configuration ####################  

        self.idd_select_energy = idd_select_energy
        
    def mockMotor(self, name):
        motor = Mock()
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

    def testScannableSetup(self):
        ilhe = EnergyScannableEnum('idd_select_energy', self.idd_gap, 
            self.idd_rowphase1, self.idd_rowphase2, self.idd_rowphase3, 
            self.idd_rowphase4, self.idd_jawphase, self.pgm_energy,
            {234.9 : IdPosition(16, 0, 0, 0, 0, 0.235)
            ,318.1 : IdPosition(16, 0, 0, 0, 0, 4.524)
            ,516.3 : IdPosition(16, 0, 0, 0, 0, 7.076)
            ,1660  : IdPosition(16, 0, 0, 0, 0, 11.25)                                    
            } )

        self.assertEquals(repr(self.idd_select_energy), repr(ilhe))
        
        self.assertEqual('idd_select_energy', self.idd_select_energy.name)
        self.assertEqual(list(self.idd_select_energy.inputNames), ['idd_select_energy'])
        self.assertEqual(list(self.idd_select_energy.extraNames), ['idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', 'diff_energy'])
        self.assertEqual(list(self.idd_select_energy.outputFormat), ['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f'])
    
    def test__str__(self):
        self.idd_gap.getPosition.return_value = 1234
        self.idd_rowphase1.getPosition.return_value = 2345
        self.idd_rowphase2.getPosition.return_value = 3456
        self.idd_rowphase3.getPosition.return_value = 5678
        self.idd_rowphase4.getPosition.return_value = 6789
        self.idd_jawphase.getPosition.return_value = 7890
        self.pgm_energy.getPosition.return_value = 8901
        
        self.assertEquals(str(self.idd_select_energy), "idd_select_energy=0.000000, idd_gap=1234.000000, idd_rowphase1=2345.000000, idd_rowphase2=3456.000000, idd_rowphase3=5678.000000, idd_rowphase4=6789.000000, idd_jawphase=7890.000000, pgm_energy=8901.000000, diff_energy=-8901.000000")

    def test__repr__LH(self):
        self.assertEquals(repr(self.idd_select_energy), "EnergyScannableEnum(u'idd_select_energy', 'idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', energyPositions={234.9: IdPosition(gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0, jawphase=0.235), 318.1: IdPosition(gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0, jawphase=4.524), 516.3: IdPosition(gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0, jawphase=7.076), 1660: IdPosition(gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0, jawphase=11.25)})")

    # idd_select_energy  234.9    318.1    516.3    1660
    # jawPhase            0.235    4.524    7.076    11.25
    def testAsynchronousMoveToLH1(self): #    0.235
        self.assert_idd_select_energy(234.9, 0.235) # 0.3575749086385258)

    def testAsynchronousMoveToLH2(self): #    4.524
        self.assert_idd_select_energy(318.1, 4.524) # 4.500804625623459)

    def testAsynchronousMoveToLH3(self): #    7.076
        self.assert_idd_select_energy(516.3, 7.076) # 7.060484231163173)

    def testAsynchronousMoveToLH4(self): #   11.25
        self.assert_idd_select_energy(1660, 11.25)  # 11.226959483586143)

    def assert_idd_select_energy(self, energy_eV, jawphase):
        self.idd_select_energy.asynchronousMoveTo(energy_eV)
        
        self.pgm_energy.asynchronousMoveTo.assert_called_with(energy_eV)
        self.idd_gap.asynchronousMoveTo.assert_called_with(16)
        self.idd_rowphase1.asynchronousMoveTo.assert_called_with(0)
        self.idd_rowphase2.asynchronousMoveTo.assert_called_with(0)
        self.idd_rowphase3.asynchronousMoveTo.assert_called_with(0)
        self.idd_rowphase4.asynchronousMoveTo.assert_called_with(0)
        self.idd_jawphase.asynchronousMoveTo.assert_called_with(jawphase)

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
            self.assertEqual(((a,b,c,d),self.idd_select_energy.isBusy()),
                             ((a,b,c,d),assertion))

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
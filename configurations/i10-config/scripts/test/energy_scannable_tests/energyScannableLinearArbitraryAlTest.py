"""
Unit tests for Energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source

For help with configuring an Energy scannable, see the example configuration
below, search for "Start Example configuration".
"""

import unittest
from mock import Mock
from Diamond.Poly import Poly
from Diamond.energyScannableLinearArbitrary import EnergyScannableLinearArbitrary, PolarisationAngleScannable

class EnergyScannableLinearArbitraryAlTest(unittest.TestCase):

    def setUp(self):
        # Initialise these as local, so the example code looks the same
        # as it will in localstation or a user script.
        (idd_gap, idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4,
         idd_jawphase, pgm_energy) = self.setUpMocks()

        ################### Start Example configuration ###################  

        idd_lin_al_energy = EnergyScannableLinearArbitrary('idd_lin_al_energy',
            idd_gap, idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, 
            idd_jawphase, pgm_energy, 'idd_lin_al_angle',
            angle_min_Deg=0., angle_max_Deg=180., angle_threshold_Deg=27., 
            energy_min_eV=1520., energy_max_eV=1620.,  
            #gap = -26.026 + 0.037523 * energy_eV
            gap_from_energy=Poly([-26.026, 0.037523], power0first=True),
            rowphase1_from_energy=-17.22, rowphase2_from_energy=0.,
            rowphase3_from_energy=17.22, rowphase4_from_energy=0.,
            #jawphase = ( alpha_real - 117. ) / 7.5
            jawphase_from_angle=Poly([-117./7.5, 1./7.5], power0first=True))

        idd_lin_al_angle = PolarisationAngleScannable('idd_lin_al_angle',
            idd_lin_al_energy)
        #################### End Example configuration ####################  

        self.idd_lin_al_energy = idd_lin_al_energy
        self.idd_lin_al_angle = idd_lin_al_angle

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
        ilae = EnergyScannableLinearArbitrary(name='idd_lin_al_energy',
            id_gap_scannable=self.idd_gap, 
            id_rowphase1_scannable=self.idd_rowphase1,
            id_rowphase2_scannable=self.idd_rowphase2, 
            id_rowphase3_scannable=self.idd_rowphase3, 
            id_rowphase4_scannable=self.idd_rowphase4, 
            id_jawphase_scannable=self.idd_jawphase, 
            pgm_energy_scannable=self.pgm_energy,
            pol_angle_scannable_name='idd_lin_al_angle', 
            angle_min_Deg=0., angle_max_Deg=180., angle_threshold_Deg=27., 
            energy_min_eV=1520., energy_max_eV=1620.,  
            gap_from_energy=Poly([-26.026, 0.037523], power0first=True),
            rowphase1_from_energy=-17.22, rowphase2_from_energy=0.,
            rowphase3_from_energy=17.22, rowphase4_from_energy=0.,
            jawphase_from_energy=None, gap_from_angle=None,
            rowphase1_from_angle=None, rowphase2_from_angle=None,
            rowphase3_from_angle=None, rowphase4_from_angle=None,
            jawphase_from_angle=Poly([-117./7.5, 1./7.5], power0first=True))

        self.assertEquals(repr(self.idd_lin_al_energy), repr(ilae))
        
        self.assertEqual('idd_lin_al_energy', self.idd_lin_al_energy.name)
        self.assertEqual(list(self.idd_lin_al_energy.inputNames), ['idd_lin_al_energy'])
        self.assertEqual(list(self.idd_lin_al_energy.extraNames), [u'idd_lin_al_angle', u'idd_gap', u'idd_rowphase1', u'idd_rowphase2', u'idd_rowphase3', u'idd_rowphase4', u'idd_jawphase', u'pgm_energy', u'diff_energy'])
        self.assertEqual(list(self.idd_lin_al_energy.outputFormat), [u'%f', u'%f', u'%f', u'%f', u'%f', u'%f', u'%f', u'%f', u'%f', u'%f'])

        self.assertEqual('idd_lin_al_angle', self.idd_lin_al_angle.name)
        self.assertEqual(list(self.idd_lin_al_angle.inputNames), ['idd_lin_al_angle'])
        self.assertEqual(list(self.idd_lin_al_angle.extraNames), [u'idd_lin_al_energy', u'idd_gap', u'idd_rowphase1', u'idd_rowphase2', u'idd_rowphase3', u'idd_rowphase4', u'idd_jawphase', u'pgm_energy', u'diff_energy'])
        self.assertEqual(list(self.idd_lin_al_angle.outputFormat), [u'%f', u'%f', u'%f', u'%f', u'%f', u'%f', u'%f', u'%f', u'%f', u'%f'])
    
    def test__str__(self):
        self.idd_gap.getPosition.return_value = 1234
        self.idd_rowphase1.getPosition.return_value = 2345
        self.idd_rowphase2.getPosition.return_value = 3456
        self.idd_rowphase3.getPosition.return_value = 5678
        self.idd_rowphase4.getPosition.return_value = 6789
        self.idd_jawphase.getPosition.return_value = 7890
        self.pgm_energy.getPosition.return_value = 8901

        self.idd_lin_al_energy.angle_Deg = 90.
        self.assertEquals(str(self.idd_lin_al_energy), "idd_lin_al_energy=0.000000, idd_lin_al_angle=90.000000, idd_gap=1234.000000, idd_rowphase1=2345.000000, idd_rowphase2=3456.000000, idd_rowphase3=5678.000000, idd_rowphase4=6789.000000, idd_jawphase=7890.000000, pgm_energy=8901.000000, diff_energy=-8901.000000")
        self.assertEquals(str(self.idd_lin_al_angle),  "idd_lin_al_angle=90.000000, idd_lin_al_energy=0.000000, idd_gap=1234.000000, idd_rowphase1=2345.000000, idd_rowphase2=3456.000000, idd_rowphase3=5678.000000, idd_rowphase4=6789.000000, idd_jawphase=7890.000000, pgm_energy=8901.000000, diff_energy=-8901.000000")

    def test__repr__LH(self):
        self.assertEquals(repr(self.idd_lin_al_energy), "EnergyScannableLinearArbitrary(u'idd_lin_al_energy', 'idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', angle_min_Deg=0.0, angle_max_Deg=180.0, angle_threshold_Deg=27.0, energy_min_eV=1520.0, energy_max_eV=1620.0, gap_from_energy=Poly(coeffs=[0.037523, -26.026], power0first=False), rowphase1_from_energy=-17.22, rowphase2_from_energy=0.0, rowphase3_from_energy=17.22, rowphase4_from_energy=0.0, jawphase_from_energy=None, gap_from_angle=None, rowphase1_from_angle=None, rowphase2_from_angle=None, rowphase3_from_angle=None, rowphase4_from_angle=None, jawphase_from_angle=Poly(coeffs=[0.133333333333, -15.6], power0first=False))")
        self.assertEquals(repr(self.idd_lin_al_angle),  "PolarisationAngleScannable(u'idd_lin_al_angle', u'idd_lin_al_energy')")

    def testAsynchronousMoveToLin1(self):
        self.assert_idd_lin_energy(1520, 31.00896, 8.399999999939999)

    def testAsynchronousMoveToLin2(self):
        self.assert_idd_lin_energy(1570, 32.88511, 8.399999999939999)

    def testAsynchronousMoveToLin3(self):
        self.idd_lin_al_energy.angle_Deg = 45
        self.assert_idd_lin_energy(1570, 32.88511, -9.600000000015001)

    def testAsynchronousMoveToLin4(self):
        self.assert_idd_lin_energy(1620, 34.76126000000001, 8.399999999939999)

    def testAsynchronousMoveToLin5(self):
        #self.idd_lin_al_energy.asynchronousMoveTo(689.)
        #self.idd_lin_al_energy.asynchronousMoveTo(731.)
        pass

    def testAsynchronousMoveToAngle0(self):
        self.assert_idd_lin_angle(0, 32.88511, 8.399999999939999)

    def testAsynchronousMoveToLAngle26(self):
        self.assert_idd_lin_angle(26, 32.88511, 11.866666666597999)

    def testAsynchronousMoveToLAngle28(self):
        self.assert_idd_lin_angle(28, 32.88511, -11.866666666676)

    def testAsynchronousMoveToLAngle45(self):
        self.assert_idd_lin_angle(45, 32.88511, -9.600000000015001)

    def testAsynchronousMoveToLAngle90(self):
        self.assert_idd_lin_angle(90, 32.88511, -3.6000000000300005)

    def testAsynchronousMoveToLAngle135(self):
        self.assert_idd_lin_angle(135, 32.88511, 2.399999999954998)

    def testAsynchronousMoveToLAngle180(self):
        self.assert_idd_lin_angle(180, 32.88511, 8.399999999939999)

    def assert_idd_lin_energy(self, energy_eV, gap, jawphase):
        self.idd_lin_al_energy.asynchronousMoveTo(energy_eV)
        
        self.pgm_energy.asynchronousMoveTo.assert_called_with(energy_eV)
        self.idd_gap.asynchronousMoveTo.assert_called_with(gap)
        self.idd_rowphase1.asynchronousMoveTo.assert_called_with(-17.22)
        self.idd_rowphase2.asynchronousMoveTo.assert_called_with(0)
        self.idd_rowphase3.asynchronousMoveTo.assert_called_with(17.22)
        self.idd_rowphase4.asynchronousMoveTo.assert_called_with(0)
        self.idd_jawphase.asynchronousMoveTo.assert_called_with(jawphase)
        
    def assert_idd_lin_angle(self, angle_Deg, gap, jawphase):
        self.pgm_energy.getPosition.return_value = 1570
        
        self.idd_lin_al_angle.asynchronousMoveTo(angle_Deg)
        
        self.pgm_energy.asynchronousMoveTo.assert_called_with(1570)
        self.idd_gap.asynchronousMoveTo.assert_called_with(gap)
        self.idd_rowphase1.asynchronousMoveTo.assert_called_with(-17.22)
        self.idd_rowphase2.asynchronousMoveTo.assert_called_with(0)
        self.idd_rowphase3.asynchronousMoveTo.assert_called_with(17.22)
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
            self.assertEqual(((a,b,c,d),self.idd_lin_al_energy.isBusy()),
                             ((a,b,c,d),assertion))

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
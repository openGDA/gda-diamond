"""
Unit tests for Circular Polarisation Energy scannable for use with GDA at
Diamond Light Source

For help with configuring a Circular Polarisation Energy scannable, see the
example configuration below, search for "Start Example configuration".
"""

import unittest
from mock import Mock
from Diamond.Poly import Poly
from Diamond.CircularPolarisation import CircularPolarisationDeprecated

class CircularPolarisationTest(unittest.TestCase):

    def setUp(self):
        # Initialise these as local, so the example code looks the same
        idu_gap = Mock() # as it will in localstation or a user script.
        idu_gap.name = "idu_gap"
        idu_rp_upper = Mock()
        idu_rp_upper.name = "idu_rp_upper"
        idu_rp_lower = Mock()
        idu_rp_lower.name = "idu_rp_lower"
        pgm_energy = Mock()
        pgm_energy.name = "pgm_energy"

        ################### Start Example configuration ###################  
        # Positive circular polarisation
        idupgmpos_energy = CircularPolarisationDeprecated('idupgmpos_energy', idu_gap, 
            idu_rp_upper, idu_rp_lower, pgm_energy,
            #y = (4.7691433e-023*energy_eV**9 -3.5614398e-019*energy_eV**8 +
            #     1.1661506e-015*energy_eV**7 -2.1961059e-012*energy_eV**6 +
            #     2.6198401e-009*energy_eV**5 -2.0520865e-006*energy_eV**4 +
            #     1.0549550e-003*energy_eV**3 -3.4313173e-001*energy_eV**2 +
            #     6.4087669e+001*energy_eV    -5.2115204e+003 )
            gap_poly=Poly(power0first=False, coeffs=
                          [4.7691433e-023, -3.5614398e-019, 
                           1.1661506e-015, -2.1961059e-012,
                           2.6198401e-009, -2.0520865e-006,
                           1.0549550e-003, -3.4313173e-001,
                           6.4087669e+001, -5.2115204e+003] ),
            #raw_phase = (15.383 +0.26758*y -0.0022704*y**2 +6.7308e-6*y**3)
            row_phase_poly=Poly(power0first=True, coeffs=
                          [15.383, 0.26758, -0.0022704, 6.7308e-6]),
            positiveDirection=True)
        
        # Negative circular polarisation
        idupgmneg_energy = CircularPolarisationDeprecated('idupgmneg_energy', idu_gap, 
            idu_rp_upper, idu_rp_lower, pgm_energy, 
            #y = (4.0910687e-023*energy_eV**9 -3.0510962e-019*energy_eV**8 +
            #     9.9770369e-016*energy_eV**7 -1.8761810e-012*energy_eV**6 + 
            #     2.2346384e-009*energy_eV**5 -1.7472620e-006*energy_eV**4 + 
            #     8.9646577e-004*energy_eV**3 -2.9093976e-001*energy_eV**2 +
            #     5.4213087e+001*energy_eV    -4.3939492e+003 )
            gap_poly=Poly(power0first=False, coeffs=
                          [4.0910687e-023, -3.0510962e-019,
                           9.9770369e-016, -1.8761810e-012, 
                           2.2346384e-009, -1.7472620e-006, 
                           8.9646577e-004, -2.9093976e-001,
                           5.4213087e+001, -4.3939492e+003] ),
            #raw_phase = -(15.383 +0.26758*y -0.0022704*y**2 +6.7308e-6*y**3)
            row_phase_poly=Poly(power0first=True, coeffs=
                          [15.383, 0.26758, -0.0022704, 6.7308e-6] ),
            positiveDirection=False)

        #################### End Example configuration ####################  

        self.idu_gap = idu_gap
        self.idu_rp_upper = idu_rp_upper
        self.idu_rp_lower = idu_rp_lower
        self.pgm_energy = pgm_energy
        self.idupgmpos_energy = idupgmpos_energy
        self.idupgmneg_energy = idupgmneg_energy
        
    def tearDown(self):
        pass

    def testScannableSetup(self):
        idupgmneg_energy = CircularPolarisationDeprecated('idupgmpos_energy', self.idu_gap, 
            self.idu_rp_upper, self.idu_rp_lower, self.pgm_energy,
            gap_poly=Poly(power0first=False, coeffs=
                          [4.7691433e-023, -3.5614398e-019, 
                           1.1661506e-015, -2.1961059e-012,
                           2.6198401e-009, -2.0520865e-006,
                           1.0549550e-003, -3.4313173e-001,
                           6.4087669e+001, -5.2115204e+003] ),
            row_phase_poly=Poly(power0first=True, coeffs=
                          [15.383, 0.26758, -0.0022704, 6.7308e-6]),
            positiveDirection=True)

        self.assertEquals(repr(self.idupgmpos_energy), repr(idupgmneg_energy))
        
        self.assertEqual('idupgmpos_energy', self.idupgmpos_energy.name)
        self.assertEqual(list(self.idupgmpos_energy.inputNames), ['idupgmpos_energy'])
        self.assertEqual(list(self.idupgmpos_energy.extraNames), ['idu_gap', 'idu_rp_upper', 'idu_rp_lower', 'pgm_energy', 'diff_energy'])
        self.assertEqual(list(self.idupgmpos_energy.outputFormat), ['%f', '%f', '%f', '%f', '%f', '%f'])
    
        cpn = CircularPolarisationDeprecated('idupgmneg_energy', self.idu_gap, 
            self.idu_rp_upper, self.idu_rp_lower, self.pgm_energy, 
            gap_poly=Poly(power0first=False, coeffs=
                          [4.0910687e-023, -3.0510962e-019,
                           9.9770369e-016, -1.8761810e-012, 
                           2.2346384e-009, -1.7472620e-006, 
                           8.9646577e-004, -2.9093976e-001,
                           5.4213087e+001, -4.3939492e+003] ),
            row_phase_poly=Poly(power0first=True, coeffs=
                          [15.383, 0.26758, -0.0022704, 6.7308e-6] ),
            positiveDirection=False)

        self.assertEquals(repr(self.idupgmneg_energy), repr(cpn))
        
        self.assertEqual('idupgmneg_energy', self.idupgmneg_energy.name)
        self.assertEqual(list(self.idupgmneg_energy.inputNames), ['idupgmneg_energy'])
        self.assertEqual(list(self.idupgmneg_energy.extraNames), ['idu_gap', 'idu_rp_upper', 'idu_rp_lower', 'pgm_energy', 'diff_energy'])
        self.assertEqual(list(self.idupgmneg_energy.outputFormat), ['%f', '%f', '%f', '%f', '%f', '%f'])
    
    def test__str__Pos(self):
        self.idu_gap.getPosition.return_value = 44.762648294615246
        self.idu_rp_upper.getPosition.return_value = 23.415091055209764
        self.idu_rp_lower.getPosition.return_value = 23.415091055209764
        self.pgm_energy.getPosition.return_value = 987.6
        
        self.assertEquals(str(self.idupgmpos_energy), "idupgmpos_energy=987.600000, idu_gap=44.762648, idu_rp_upper=23.415091, idu_rp_lower=23.415091, pgm_energy=987.600000, diff_energy=0.000000")

    def test__str__Neg(self):
        self.idu_gap.getPosition.return_value = 44.89103277083177
        self.idu_rp_upper.getPosition.return_value = -23.428520821216466
        self.idu_rp_lower.getPosition.return_value = -23.428520821216466
        self.pgm_energy.getPosition.return_value = 987.6
        
        self.assertEquals(str(self.idupgmneg_energy), "idupgmneg_energy=987.600000, idu_gap=44.891033, idu_rp_upper=-23.428521, idu_rp_lower=-23.428521, pgm_energy=987.600000, diff_energy=0.000000")

    def test__repr__(self):
        self.assertEquals(repr(self.idupgmpos_energy), "CircularPolarisation(u'idupgmpos_energy', 'idu_gap', 'idu_rp_upper', 'idu_rp_lower', 'pgm_energy', gap_poly=Poly(coeffs=[4.7691433e-23, -3.5614398e-19, 1.1661506e-15, -2.1961059e-12, 2.6198401e-09, -2.0520865e-06, 0.001054955, -0.34313173, 64.087669, -5211.5204], power0first=False), row_phase_poly=Poly(coeffs=[6.7308e-06, -0.0022704, 0.26758, 15.383], power0first=False), energy_poly=None, positiveDirection=True)")
        self.assertEquals(repr(self.idupgmneg_energy), "CircularPolarisation(u'idupgmneg_energy', 'idu_gap', 'idu_rp_upper', 'idu_rp_lower', 'pgm_energy', gap_poly=Poly(coeffs=[4.0910687e-23, -3.0510962e-19, 9.9770369e-16, -1.876181e-12, 2.2346384e-09, -1.747262e-06, 0.00089646577, -0.29093976, 54.213087, -4393.9492], power0first=False), row_phase_poly=Poly(coeffs=[6.7308e-06, -0.0022704, 0.26758, 15.383], power0first=False), energy_poly=None, positiveDirection=False)")

    def testAsynchronousMoveToPos(self):
        self.idupgmpos_energy.asynchronousMoveTo(987.6)
        
        self.pgm_energy.asynchronousMoveTo.assert_called_with(987.6)
        self.idu_gap.asynchronousMoveTo.assert_called_with(44.762648294615246)
        self.idu_rp_lower.asynchronousMoveTo.assert_called_with(23.415091055209764)
        self.idu_rp_upper.asynchronousMoveTo.assert_called_with(23.415091055209764)

    def testAsynchronousMoveToNeg(self):
        self.idupgmneg_energy.asynchronousMoveTo(987.6)
        
        self.pgm_energy.asynchronousMoveTo.assert_called_with(987.6)
        self.idu_gap.asynchronousMoveTo.assert_called_with(44.89103277083177)
        self.idu_rp_lower.asynchronousMoveTo.assert_called_with(-23.428520821216466)
        self.idu_rp_upper.asynchronousMoveTo.assert_called_with(-23.428520821216466)
        
    def testGetPositionPos(self):
        self.idu_gap.getPosition.return_value = 44.89103277083177
        self.idu_rp_upper.getPosition.return_value = 23.415091055209764
        self.idu_rp_lower.getPosition.return_value = 23.415091055209764
        self.pgm_energy.getPosition.return_value = 987.6

        self.assertEqual(list(self.idupgmpos_energy.getPosition()), [987.6, 44.89103277083177, 23.415091055209764, 23.415091055209764, 987.6, 0.0])

    def testGetPositionNeg(self):
        self.idu_gap.getPosition.return_value = 44.89103277083177
        self.idu_rp_upper.getPosition.return_value = -23.428520821216466
        self.idu_rp_lower.getPosition.return_value = -23.428520821216466
        self.pgm_energy.getPosition.return_value = 987.6

        self.assertEqual(list(self.idupgmneg_energy.getPosition()), [987.6, 44.89103277083177, -23.428520821216466, -23.428520821216466, 987.6, 0.0])

    ''' testIsBusy creates a dictionary of tests as keys and populates the
        expected results as the values '''        
    def testIsBusy(self):
        # Generate combinations, with a default of expecting True
        combinations=dict([((a,b,c,d),True) for a in (True,False) for b in (True,False) for c in (True,False) for d in (True,False)])
        # Exceptions
        combinations[(False,False,False,False)]=False

        for (a, b, c, d), assertion in combinations.iteritems():
            self.idu_gap.isBusy.return_value = a
            self.idu_rp_upper.isBusy.return_value = b
            self.idu_rp_lower.isBusy.return_value = c
            self.pgm_energy.isBusy.return_value = d

            # Put the args in the assert, so we get to see which one fails.
            self.assertEqual(((a,b,c,d),self.idupgmpos_energy.isBusy()),
                             ((a,b,c,d),assertion))

class CircularPolarisationWithEnergyPolyTest(unittest.TestCase):
    # Test CircularPolarisation with optional energy_poly
    #
    # Only test functions which are different if energy_poly is defined.
    
    def setUp(self):
        # Initialise these as local, so the example code looks the same
        idu_gap = Mock() # as it will in localstaion or user script.
        idu_gap.name = "idu_gap"
        idu_rp_upper = Mock()
        idu_rp_upper.name = "idu_rp_upper"
        idu_rp_lower = Mock()
        idu_rp_lower.name = "idu_rp_lower"
        pgm_energy = Mock()
        pgm_energy.name = "pgm_energy"

        ################### Start Example configuration ###################  
        # Positive circular polarisation
        idupgmpos_energy = CircularPolarisationDeprecated('idupgmpos_energy', idu_gap, 
            idu_rp_upper, idu_rp_lower, pgm_energy,
            #y = (4.7691433e-023*energy_eV**9 -3.5614398e-019*energy_eV**8 +
            #     1.1661506e-015*energy_eV**7 -2.1961059e-012*energy_eV**6 +
            #     2.6198401e-009*energy_eV**5 -2.0520865e-006*energy_eV**4 +
            #     1.0549550e-003*energy_eV**3 -3.4313173e-001*energy_eV**2 +
            #     6.4087669e+001*energy_eV    -5.2115204e+003 )
            gap_poly=Poly(power0first=False, coeffs=
                          [4.7691433e-023, -3.5614398e-019, 
                           1.1661506e-015, -2.1961059e-012,
                           2.6198401e-009, -2.0520865e-006,
                           1.0549550e-003, -3.4313173e-001,
                           6.4087669e+001, -5.2115204e+003] ),
            #raw_phase = (15.383 +0.26758*y -0.0022704*y**2 +6.7308e-6*y**3)
            row_phase_poly=Poly(power0first=True, coeffs=
                          [15.383, 0.26758, -0.0022704, 6.7308e-6]),
            # -49346.58366 +9867.22012*X-872.05044*X^2+44.82437*X^3-1.47804*X^4+0.03252*X^5-4.77652E-4*X^6+4.50905E-6*X^7-2.47586E-8*X^8+6.0086E-11*X^9
            #            -49346.58366    9867.22012
            #            -872.05044      44.82437
            #            -1.47804        0.03252
            #            -4.77652E-4     4.50905E-6
            #            -2.47586E-8     6.0086E-11 
            energy_poly=Poly(power0first=True, coeffs=
                          [-49346.58366, 9867.22012,
                           -872.05044,   44.82437,
                           -1.47804,     0.03252,
                           -4.77652E-4,  4.50905E-6,
                           -2.47586E-8,  6.0086E-11] ),
            positiveDirection=True)
        
        # Negative circular polarisation
        idupgmneg_energy = CircularPolarisationDeprecated('idupgmneg_energy', idu_gap, 
            idu_rp_upper, idu_rp_lower, pgm_energy, 
            #y = (4.0910687e-023*energy_eV**9 -3.0510962e-019*energy_eV**8 +
            #     9.9770369e-016*energy_eV**7 -1.8761810e-012*energy_eV**6 + 
            #     2.2346384e-009*energy_eV**5 -1.7472620e-006*energy_eV**4 + 
            #     8.9646577e-004*energy_eV**3 -2.9093976e-001*energy_eV**2 +
            #     5.4213087e+001*energy_eV    -4.3939492e+003 )
            gap_poly=Poly(power0first=False, coeffs=
                          [4.0910687e-023, -3.0510962e-019,
                           9.9770369e-016, -1.8761810e-012, 
                           2.2346384e-009, -1.7472620e-006, 
                           8.9646577e-004, -2.9093976e-001,
                           5.4213087e+001, -4.3939492e+003] ),
            #raw_phase = -(15.383 +0.26758*y -0.0022704*y**2 +6.7308e-6*y**3)
            row_phase_poly=Poly(power0first=True, coeffs=
                          [15.383, 0.26758, -0.0022704, 6.7308e-6] ),
            # -79839.41241+15921.489*X-1395.34995*X^2+70.64799*X^3-2.27902*X^4+0.04869*X^5-6.8987E-4*X^6+6.24992E-6*X^7-3.28325E-8*X^8+7.61341E-11*X^9
            #              -79839.41241     15921.489
            #              -1395.34995      70.64799
            #              -2.27902         0.04869
            #              -6.8987E-4       6.24992E-6
            #              -3.28325E-8      7.61341E-11                            
            energy_poly=Poly(power0first=True, coeffs=
                          [-79839.41241,    15921.489,
                           -1395.34995,     70.64799,
                           -2.27902,        0.04869,
                           -6.8987E-4,      6.24992E-6,
                           -3.28325E-8,     7.61341E-11 ] ), 
            positiveDirection=False)

        #################### End Example configuration ####################  

        self.idu_gap = idu_gap
        self.idu_rp_upper = idu_rp_upper
        self.idu_rp_lower = idu_rp_lower
        self.pgm_energy = pgm_energy
        self.idupgmpos_energy = idupgmpos_energy
        self.idupgmneg_energy = idupgmneg_energy
        
    def tearDown(self):
        pass

    def testScannableSetup(self):
        idupgmneg_energy = CircularPolarisationDeprecated('idupgmpos_energy', self.idu_gap, 
            self.idu_rp_upper, self.idu_rp_lower, self.pgm_energy,
            gap_poly=Poly(power0first=False, coeffs=
                          [4.7691433e-023, -3.5614398e-019, 
                           1.1661506e-015, -2.1961059e-012,
                           2.6198401e-009, -2.0520865e-006,
                           1.0549550e-003, -3.4313173e-001,
                           6.4087669e+001, -5.2115204e+003] ),
            row_phase_poly=Poly(power0first=True, coeffs=
                          [15.383, 0.26758, -0.0022704, 6.7308e-6]),
            energy_poly=Poly(power0first=True, coeffs=
                          [-49346.58366, 9867.22012,
                           -872.05044,   44.82437,
                           -1.47804,     0.03252,
                           -4.77652E-4,  4.50905E-6,
                           -2.47586E-8,  6.0086E-11] ),
            positiveDirection=True)

        self.assertEquals(repr(self.idupgmpos_energy), repr(idupgmneg_energy))
        
        cpn = CircularPolarisationDeprecated('idupgmneg_energy', self.idu_gap, 
            self.idu_rp_upper, self.idu_rp_lower, self.pgm_energy, 
            gap_poly=Poly(power0first=False, coeffs=
                          [4.0910687e-023, -3.0510962e-019,
                           9.9770369e-016, -1.8761810e-012, 
                           2.2346384e-009, -1.7472620e-006, 
                           8.9646577e-004, -2.9093976e-001,
                           5.4213087e+001, -4.3939492e+003] ),
            row_phase_poly=Poly(power0first=True, coeffs=
                          [15.383, 0.26758, -0.0022704, 6.7308e-6] ),
            energy_poly=Poly(power0first=True, coeffs=
                          [-79839.41241,    15921.489,
                           -1395.34995,     70.64799,
                           -2.27902,        0.04869,
                           -6.8987E-4,      6.24992E-6,
                           -3.28325E-8,     7.61341E-11 ] ), 
            positiveDirection=False)

        self.assertEquals(repr(self.idupgmneg_energy), repr(cpn))
        
    def test__str__Pos(self):
        self.idu_gap.getPosition.return_value = 44.762648294615246
        self.idu_rp_upper.getPosition.return_value = 23.415091055209764
        self.idu_rp_lower.getPosition.return_value = 23.415091055209764
        self.pgm_energy.getPosition.return_value = 987.6
        
        self.assertEquals(str(self.idupgmpos_energy), "idupgmpos_energy=987.600000, idu_gap=44.762648, idu_rp_upper=23.415091, idu_rp_lower=23.415091, pgm_energy=987.600000, diff_energy=0.000000")
        # Results:                                   'idupgmpos_energy=1084.933424, idu_gap=44.762648, idu_rp_upper=23.415091, idu_rp_lower=23.415091, pgm_energy=987.600000, diff_energy=97.333424'

    def test__str__Neg(self):
        self.idu_gap.getPosition.return_value = 44.89103277083177
        self.idu_rp_upper.getPosition.return_value = -23.428520821216466
        self.idu_rp_lower.getPosition.return_value = -23.428520821216466
        self.pgm_energy.getPosition.return_value = 987.6
        
        self.assertEquals(str(self.idupgmneg_energy), "idupgmneg_energy=987.600000, idu_gap=44.891033, idu_rp_upper=-23.428521, idu_rp_lower=-23.428521, pgm_energy=987.600000, diff_energy=0.000000")
        # Results:                                    'idupgmneg_energy=524.477418, idu_gap=44.891033, idu_rp_upper=-23.428521, idu_rp_lower=-23.428521, pgm_energy=987.600000, diff_energy=-463.122582'

    def test__repr__(self):
        self.assertEquals(repr(self.idupgmpos_energy), "CircularPolarisation(u'idupgmpos_energy', 'idu_gap', 'idu_rp_upper', 'idu_rp_lower', 'pgm_energy', gap_poly=Poly(coeffs=[4.7691433e-23, -3.5614398e-19, 1.1661506e-15, -2.1961059e-12, 2.6198401e-09, -2.0520865e-06, 0.001054955, -0.34313173, 64.087669, -5211.5204], power0first=False), row_phase_poly=Poly(coeffs=[6.7308e-06, -0.0022704, 0.26758, 15.383], power0first=False), energy_poly=Poly(coeffs=[6.0086e-11, -2.47586e-08, 4.50905e-06, -0.000477652, 0.03252, -1.47804, 44.82437, -872.05044, 9867.22012, -49346.58366], power0first=False), positiveDirection=True)")
        self.assertEquals(repr(self.idupgmneg_energy), "CircularPolarisation(u'idupgmneg_energy', 'idu_gap', 'idu_rp_upper', 'idu_rp_lower', 'pgm_energy', gap_poly=Poly(coeffs=[4.0910687e-23, -3.0510962e-19, 9.9770369e-16, -1.876181e-12, 2.2346384e-09, -1.747262e-06, 0.00089646577, -0.29093976, 54.213087, -4393.9492], power0first=False), row_phase_poly=Poly(coeffs=[6.7308e-06, -0.0022704, 0.26758, 15.383], power0first=False), energy_poly=Poly(coeffs=[7.61341e-11, -3.28325e-08, 6.24992e-06, -0.00068987, 0.04869, -2.27902, 70.64799, -1395.34995, 15921.489, -79839.41241], power0first=False), positiveDirection=False)")

    def testGetPositionPos(self):
        self.idu_gap.getPosition.return_value = 44.762648294615246
        self.idu_rp_upper.getPosition.return_value = 23.415091055209764
        self.idu_rp_lower.getPosition.return_value = 23.415091055209764
        self.pgm_energy.getPosition.return_value = 987.6

        self.assertEqual(list(self.idupgmpos_energy.getPosition()), [987.6, 44.762648294615246, 23.415091055209764, 23.415091055209764, 987.6, 0.0])
        # Results:                                     [1084.9334241770048, 44.762648294615246, 23.415091055209764, 23.415091055209764, 987.6, 97.33342417700476]

    def testGetPositionNeg(self):
        self.idu_gap.getPosition.return_value = 44.89103277083177
        self.idu_rp_upper.getPosition.return_value = -23.428520821216466
        self.idu_rp_lower.getPosition.return_value = -23.428520821216466
        self.pgm_energy.getPosition.return_value = 987.6

        self.assertEqual(list(self.idupgmneg_energy.getPosition()), [987.6, 44.89103277083177, -23.428520821216466, -23.428520821216466, 987.6, 0.0])
        # Results:                                      [524.4774178260559, 44.89103277083177, -23.428520821216466, -23.428520821216466, 987.6, -463.1225821739441]

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
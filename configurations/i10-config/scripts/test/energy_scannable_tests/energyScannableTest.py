"""
Unit tests for Energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source

For help with configuring an Energy scannable, see the example configuration
below, search for "Start Example configuration".
"""

import unittest
from Test.mock import MagicMock
from Diamond.Poly import Poly
from Diamond.EnergyScannable import EnergyScannable

class EnergyScannableTest(unittest.TestCase):

    def setUp(self):
        # Initialise these as local, so the example code looks the same
        # as it will in localstation or a user script.
        (idd_gap, idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4,
         idd_jawphase, pgm_energy) = self.setUpMocks()

        ################### Start Example configuration ###################  
        # Linear horizontal polarisation
        idd_lin_hor_energy = EnergyScannable('idd_lin_hor_energy', idd_gap, 
            idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, 
            idd_jawphase, pgm_energy,
            gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0,  
            jawphase_poly=Poly(power0first=False, coeffs=
                          [3.3502671895516406e-41, -5.0443866954149711e-37,
                           3.4803215641954580e-33, -1.4580246046390974e-29,
                           4.1431184271800654e-26, -8.4487057979195192e-23,
                           1.2756618081729026e-19, -1.4503475672160905e-16,
                           1.2502244299182579e-13, -8.1604278898212417e-11,
                           3.9951747689787648e-08, -1.4390652672680635e-05,
                           3.6880906351653684e-03, -6.3450605014502259e-01,
                           6.5540526156906154e+01, -3.0647533992737303e+03 ] ) )
        
        # Linear Vertical polarisation
        idd_lin_ver_energy = EnergyScannable('idd_lin_ver_energy', idd_gap, 
            idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, 
            idd_jawphase, pgm_energy,
            gap=16, rowphase1=24, rowphase2=0, rowphase3=24, rowphase4=0,  
            jawphase_poly=Poly(power0first=False, coeffs=
                          [5.7872984268363729e-40, -9.6927773095637603e-36,
                           7.4982177899089000e-32, -3.5528632008418775e-28,
                           1.1527662093156713e-24, -2.7121091920521087e-21,
                           4.7781854501432704e-18, -6.4172005413018581e-15,
                           6.6219983201434882e-12, -5.2490014435732980e-09,
                           3.1691535622688745e-06, -1.4309597792932307e-03,
                           4.6765853517087802e-01, -1.0442119397102638e+02,
                           1.4242875040183506e+04, -8.9460467908767762e+05 ] ) )
        
        # Positive circular polarisation
        idd_circ_pos_energy = EnergyScannable('idd_circ_pos_energy', idd_gap, 
            idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, 
            idd_jawphase, pgm_energy,
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

        #################### End Example configuration ####################  

        self.idd_lin_hor_energy = idd_lin_hor_energy
        self.idd_lin_ver_energy = idd_lin_ver_energy
        self.idd_circ_pos_energy = idd_circ_pos_energy
        self.idd_circ_neg_energy = idd_circ_neg_energy
        
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

    def testScannableSetup(self):
        ilhe = EnergyScannable('idd_lin_hor_energy', self.idd_gap, 
            self.idd_rowphase1, self.idd_rowphase2, self.idd_rowphase3, 
            self.idd_rowphase4, self.idd_jawphase, self.pgm_energy,
            gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0,  
            jawphase_poly=Poly(power0first=False, coeffs=
                          [3.3502671895516406e-41, -5.0443866954149711e-37,
                           3.4803215641954580e-33, -1.4580246046390974e-29,
                           4.1431184271800654e-26, -8.4487057979195192e-23,
                           1.2756618081729026e-19, -1.4503475672160905e-16,
                           1.2502244299182579e-13, -8.1604278898212417e-11,
                           3.9951747689787648e-08, -1.4390652672680635e-05,
                           3.6880906351653684e-03, -6.3450605014502259e-01,
                           6.5540526156906154e+01, -3.0647533992737303e+03 ] ) )

        self.assertEquals(repr(self.idd_lin_hor_energy), repr(ilhe))
        
        self.assertEqual('idd_lin_hor_energy', self.idd_lin_hor_energy.name)
        self.assertEqual(list(self.idd_lin_hor_energy.inputNames), ['idd_lin_hor_energy'])
        self.assertEqual(list(self.idd_lin_hor_energy.extraNames), ['idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', 'diff_energy'])
        self.assertEqual(list(self.idd_lin_hor_energy.outputFormat), ['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f'])
    
        ilve = EnergyScannable('idd_lin_ver_energy', self.idd_gap, 
            self.idd_rowphase1, self.idd_rowphase2, self.idd_rowphase3, 
            self.idd_rowphase4, self.idd_jawphase, self.pgm_energy,
            gap=16, rowphase1=24, rowphase2=0, rowphase3=24, rowphase4=0,  
            jawphase_poly=Poly(power0first=False, coeffs=
                          [5.7872984268363729e-40, -9.6927773095637603e-36,
                           7.4982177899089000e-32, -3.5528632008418775e-28,
                           1.1527662093156713e-24, -2.7121091920521087e-21,
                           4.7781854501432704e-18, -6.4172005413018581e-15,
                           6.6219983201434882e-12, -5.2490014435732980e-09,
                           3.1691535622688745e-06, -1.4309597792932307e-03,
                           4.6765853517087802e-01, -1.0442119397102638e+02,
                           1.4242875040183506e+04, -8.9460467908767762e+05 ] ) )

        self.assertEquals(repr(self.idd_lin_ver_energy), repr(ilve))
        
        self.assertEqual('idd_lin_hor_energy', self.idd_lin_hor_energy.name)
        self.assertEqual(list(self.idd_lin_hor_energy.inputNames), ['idd_lin_hor_energy'])
        self.assertEqual(list(self.idd_lin_hor_energy.extraNames), ['idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', 'diff_energy'])
        self.assertEqual(list(self.idd_lin_hor_energy.outputFormat), ['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f'])
        
        icpe = EnergyScannable('idd_circ_pos_energy', self.idd_gap, 
            self.idd_rowphase1, self.idd_rowphase2, self.idd_rowphase3, 
            self.idd_rowphase4, self.idd_jawphase, self.pgm_energy,
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

        self.assertEquals(repr(self.idd_circ_pos_energy), repr(icpe))
        
        self.assertEqual('idd_circ_pos_energy', self.idd_circ_pos_energy.name)
        self.assertEqual(list(self.idd_circ_pos_energy.inputNames), ['idd_circ_pos_energy'])
        self.assertEqual(list(self.idd_circ_pos_energy.extraNames), ['idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', 'diff_energy'])
        self.assertEqual(list(self.idd_circ_pos_energy.outputFormat), ['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f'])

        icne = EnergyScannable('idd_circ_neg_energy', self.idd_gap, 
            self.idd_rowphase1, self.idd_rowphase2, self.idd_rowphase3, 
            self.idd_rowphase4, self.idd_jawphase, self.pgm_energy,
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

        self.assertEquals(repr(self.idd_circ_neg_energy), repr(icne))
        
        self.assertEqual('idd_circ_neg_energy', self.idd_circ_neg_energy.name)
        self.assertEqual(list(self.idd_circ_neg_energy.inputNames), ['idd_circ_neg_energy'])
        self.assertEqual(list(self.idd_circ_neg_energy.extraNames), ['idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', 'diff_energy'])
        self.assertEqual(list(self.idd_circ_neg_energy.outputFormat), ['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f'])

    def test__str__(self):
        self.idd_gap.getPosition.return_value = 1234
        self.idd_rowphase1.getPosition.return_value = 2345
        self.idd_rowphase2.getPosition.return_value = 3456
        self.idd_rowphase3.getPosition.return_value = 5678
        self.idd_rowphase4.getPosition.return_value = 6789
        self.idd_jawphase.getPosition.return_value = 7890
        self.pgm_energy.getPosition.return_value = 8901
        
        self.assertEquals(str(self.idd_lin_hor_energy), "idd_lin_hor_energy=0.000000, idd_gap=1234.000000, idd_rowphase1=2345.000000, idd_rowphase2=3456.000000, idd_rowphase3=5678.000000, idd_rowphase4=6789.000000, idd_jawphase=7890.000000, pgm_energy=8901.000000, diff_energy=-8901.000000")

    def test__repr__LH(self):
        self.assertEquals(repr(self.idd_lin_hor_energy), "EnergyScannable(u'idd_lin_hor_energy', 'idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0, jawphase_poly=Poly(coeffs=[3.35026718955e-41, -5.04438669541e-37, 3.4803215642e-33, -1.45802460464e-29, 4.14311842718e-26, -8.44870579792e-23, 1.27566180817e-19, -1.45034756722e-16, 1.25022442992e-13, -8.16042788982e-11, 3.99517476898e-08, -1.43906526727e-05, 0.00368809063517, -0.634506050145, 65.5405261569, -3064.75339927], power0first=False))")
        #                                                                                                                                                                                                                                                                                          [3.3502671895516406e-41,

    def test__repr__LV(self):
        self.assertEquals(repr(self.idd_lin_ver_energy), "EnergyScannable(u'idd_lin_ver_energy', 'idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', gap=16, rowphase1=24, rowphase2=0, rowphase3=24, rowphase4=0, jawphase_poly=Poly(coeffs=[5.78729842684e-40, -9.69277730956e-36, 7.49821778991e-32, -3.55286320084e-28, 1.15276620932e-24, -2.71210919205e-21, 4.77818545014e-18, -6.4172005413e-15, 6.62199832014e-12, -5.24900144357e-09, 3.16915356227e-06, -0.00143095977929, 0.467658535171, -104.421193971, 14242.8750402, -894604.679088], power0first=False))")

    def test__repr__CP(self):
        self.assertEquals(repr(self.idd_circ_pos_energy), "EnergyScannable(u'idd_circ_pos_energy', 'idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', gap=16, rowphase1=15.1724, rowphase2=0, rowphase3=15.1724, rowphase4=0, jawphase_poly=Poly(coeffs=[1.9348427565e-40, -3.11269957213e-36, 2.30476228793e-32, -1.04126812191e-28, 3.20810246556e-25, -7.13522993987e-22, 1.18273603018e-18, -1.48689811551e-15, 1.42849430757e-12, -1.04814762041e-09, 5.82256478842e-07, -0.00024036499939, 0.0713492146438, -14.3724495588, 1756.49158785, -98177.319471], power0first=False))")

    def test__repr__CN(self):
        self.assertEquals(repr(self.idd_circ_neg_energy), "EnergyScannable(u'idd_circ_neg_energy', 'idd_gap', 'idd_rowphase1', 'idd_rowphase2', 'idd_rowphase3', 'idd_rowphase4', 'idd_jawphase', 'pgm_energy', gap=16, rowphase1=-15.1724, rowphase2=0, rowphase3=-15.1724, rowphase4=0, jawphase_poly=Poly(coeffs=[7.26633101313e-43, -1.01751276161e-37, 1.42142782441e-33, -9.43882008875e-30, 3.83515797956e-26, -1.05816893436e-22, 2.09161830941e-19, -3.04971953985e-16, 3.32856399176e-13, -2.73036006579e-10, 1.67390506026e-07, -7.5457697254e-05, 0.0242429276116, -5.24601034754, 684.354824391, -40611.6738881], power0first=False))")

    # idd_lin_hor_energy  234.9    318.1    516.3    1660
    # jawPhase            0.235    4.524    7.076    11.25
    def testAsynchronousMoveToLH1(self): #    0.235
        self.assert_idd_lin_hor_energy(234.9, 0.35757490864580177)

    def testAsynchronousMoveToLH2(self): #    4.524
        self.assert_idd_lin_hor_energy(318.1, 4.500804625652563)

    def testAsynchronousMoveToLH3(self): #    7.076
        self.assert_idd_lin_hor_energy(516.3, 7.060484231163173)

    def testAsynchronousMoveToLH4(self): #   11.25
        self.assert_idd_lin_hor_energy(1660, 11.226959483586143)

    def assert_idd_lin_hor_energy(self, energy_eV, jawphase):
        self.idd_lin_hor_energy.asynchronousMoveTo(energy_eV)

        # NOTE: assert_called_once_with silently fails with Mock() objects. 
        assert(isinstance(self.pgm_energy, MagicMock))

        self.pgm_energy.asynchronousMoveTo.assert_called_once_with(energy_eV)
        self.idd_gap.asynchronousMoveTo.assert_called_once_with(16)
        self.idd_rowphase1.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_rowphase2.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_rowphase3.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_rowphase4.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_jawphase.asynchronousMoveTo.assert_called_once_with(jawphase)
        
    # idd_lin_ver_energy    487.2    903.2    1728
    # jawPhase              0.12     6.96     11.88
    def testAsynchronousMoveToLV1(self): #    0.12
        self.assert_idd_lin_ver_energy(487.2, 0.2894148149061948)

    def testAsynchronousMoveToLV2(self): #    6.96
        self.assert_idd_lin_ver_energy(903.2, 6.953907061601058)

    def testAsynchronousMoveToLV3(self): #   11.88
        self.assert_idd_lin_ver_energy(1728, 13.844424862647429) 

    def assert_idd_lin_ver_energy(self, energy_eV, jawphase):
        self.idd_lin_ver_energy.asynchronousMoveTo(energy_eV)
        
        self.pgm_energy.asynchronousMoveTo.assert_called_once_with(energy_eV)
        self.idd_gap.asynchronousMoveTo.assert_called_once_with(16)
        self.idd_rowphase1.asynchronousMoveTo.assert_called_once_with(24)
        self.idd_rowphase2.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_rowphase3.asynchronousMoveTo.assert_called_once_with(24)
        self.idd_rowphase4.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_jawphase.asynchronousMoveTo.assert_called_once_with(jawphase)

    # idd_lin_ver_energy    0
    # jawPhase              0
    def testAsynchronousMoveToCP1(self): #     0.472
        self.assert_idd_circ_pos_energy(372.9, 0.45074769097846)

    def testAsynchronousMoveToCP2(self): #   6.726
        self.assert_idd_circ_pos_energy(683, 6.722407042281702)

    def testAsynchronousMoveToCP3(self): #    11.56
        self.assert_idd_circ_pos_energy(1706, 11.461331958184019)

    def assert_idd_circ_pos_energy(self, energy_eV, jawphase):
        self.idd_circ_pos_energy.asynchronousMoveTo(energy_eV)
        
        self.pgm_energy.asynchronousMoveTo.assert_called_once_with(energy_eV)
        self.idd_gap.asynchronousMoveTo.assert_called_once_with(16)
        self.idd_rowphase1.asynchronousMoveTo.assert_called_once_with(15.1724)
        self.idd_rowphase2.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_rowphase3.asynchronousMoveTo.assert_called_once_with(15.1724)
        self.idd_rowphase4.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_jawphase.asynchronousMoveTo.assert_called_once_with(jawphase)

    # idd_lin_ver_energy    0
    # jawPhase              0
    def testAsynchronousMoveToCN1(self): #     0.239
        self.assert_idd_circ_neg_energy(375.1, 0.33201639874459943)

    def testAsynchronousMoveToCN2(self): #     5.999
        self.assert_idd_circ_neg_energy(644.5, 5.968564011876879)

    def testAsynchronousMoveToCN3(self): #    11.64
        self.assert_idd_circ_neg_energy(1743, 11.70182095545897)

    def assert_idd_circ_neg_energy(self, energy_eV, expected_idd_jawphase):
        self.idd_circ_neg_energy.asynchronousMoveTo(energy_eV)
        
        self.pgm_energy.asynchronousMoveTo.assert_called_once_with(energy_eV)
        self.idd_gap.asynchronousMoveTo.assert_called_once_with(16)
        self.idd_rowphase1.asynchronousMoveTo.assert_called_once_with(-15.1724)
        self.idd_rowphase2.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_rowphase3.asynchronousMoveTo.assert_called_once_with(-15.1724)
        self.idd_rowphase4.asynchronousMoveTo.assert_called_once_with(0)
        self.idd_jawphase.asynchronousMoveTo.assert_called_once_with(expected_idd_jawphase)

    def testGetPositionCN(self):
        self.idd_gap.getPosition.return_value = 123
        self.idd_rowphase1.getPosition.return_value = 234
        self.idd_rowphase2.getPosition.return_value = 345
        self.idd_rowphase3.getPosition.return_value = 456
        self.idd_rowphase4.getPosition.return_value = 567
        self.idd_jawphase.getPosition.return_value = 678
        self.pgm_energy.getPosition.return_value = 789
        self.idd_circ_neg_energy.last_energy_eV = 890
        
        self.assertEqual(list(self.idd_circ_neg_energy.getPosition()), [890, 123, 234, 345, 456, 567, 678, 789, 101])

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

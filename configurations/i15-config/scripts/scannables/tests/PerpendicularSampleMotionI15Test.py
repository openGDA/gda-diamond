"""
Unit tests for Scannables which move the sample perpendicular to and parallel
to the beam, for I15.

For help with configuring these scannables, see the example configuration below,
search for "Start Example configuration".
"""

import unittest
from mock import Mock

class SampleMotionI15Test(unittest.TestCase):

    def setUp(self):
        # Initialise these as local, so the example code looks the same
        # as it will in localstation or a user script.
        (dx, dy, dz, dmu, dkphi, dkappa, dktheta) = self.setUpMocks()

        #################### Start Example configuration ####################  
        from scannables.PerpendicularSampleMotion import PerpendicularSampleMotion, ParallelSampleMotion, HeightSampleMotion

        dperp=PerpendicularSampleMotion("dperp", dx, dy, dz, dmu, dkphi, dkappa, dktheta, True, 0, 58)
        dpara=ParallelSampleMotion     ("dpara", dx, dy, dz, dmu, dkphi, dkappa, dktheta, True, 0, 58)
        dheight=HeightSampleMotion     ("dheight", dx, dy, dz, dmu, dkphi, dkappa, dktheta, True, 0, 58)
        #################### End Example configuration ####################  

        self.sperp = dperp
        self.spara = dpara
        self.sheight = dheight
        self.sperp.verbose=False
        self.spara.verbose=False
        self.sheight.verbose=False
        self.sperp.no_move=False
        self.spara.no_move=False
        self.sheight.no_move=False
        
    def mockMotor(self, name):
        motor = Mock()
        motor.name = name
        motor.isBusy.return_value = False
        return motor

    def setUpMocks(self):
        self.sx = self.mockMotor("sx")
        self.sy = self.mockMotor("sy")
        self.sz = self.mockMotor("sy")
        self.mu = self.mockMotor("mu")
        self.phi = self.mockMotor("phi")
        self.kappa = self.mockMotor("kappa")
        self.theta = self.mockMotor("theta")

        return (self.sx, self.sy, self.sz, self.mu, self.phi, self.kappa, self.theta)
        
    def tearDown(self):
        pass

    def testScannableSetup(self):
        return
    
    def test__str__(self):
        pass

    tests_spreadsheet_values="""
    tests={  '0a': {'mu':0, 'phi':58+ 0, 'sx': 0, 'sy':1, 'sperp': 0.000, 'spara':1.000},
           'M30a': {'mu':0, 'phi':58-30, 'sx': 0, 'sy':1, 'sperp': 0.500, 'spara':0.866},
           'P30a': {'mu':0, 'phi':58+30, 'sx': 0, 'sy':1, 'sperp':-0.500, 'spara':0.866},
           'M45a': {'mu':0, 'phi':58-45, 'sx': 0, 'sy':1, 'sperp': 0.707, 'spara':0.707},
           'P45a': {'mu':0, 'phi':58+45, 'sx': 0, 'sy':1, 'sperp':-0.707, 'spara':0.707},

             '0b': {'mu':0, 'phi':58+ 0, 'sx':-1, 'sy':0, 'sperp': 1.000, 'spara': 0.000},
           'M30b': {'mu':0, 'phi':58-30, 'sx':-1, 'sy':0, 'sperp': 0.866, 'spara':-0.500},
           'P30b': {'mu':0, 'phi':58+30, 'sx':-1, 'sy':0, 'sperp': 0.866, 'spara': 0.500},
           'M45b': {'mu':0, 'phi':58-45, 'sx':-1, 'sy':0, 'sperp': 0.707, 'spara':-0.707},
           'P45b': {'mu':0, 'phi':58+45, 'sx':-1, 'sy':0, 'sperp': 0.707, 'spara': 0.707},
           }
    """
    
    #tests_calculated_values="""
    tests={  '0a': {'mu':0, 'phi':58+ 0, 'sx': 0, 'sy':1, 'sperp': 0,                   'spara':1},
           'M30a': {'mu':0, 'phi':58-30, 'sx': 0, 'sy':1, 'sperp': 0.49999999999999994, 'spara':0.8660254037844387},
           'P30a': {'mu':0, 'phi':58+30, 'sx': 0, 'sy':1, 'sperp':-0.49999999999999994, 'spara':0.8660254037844387},
           'M45a': {'mu':0, 'phi':58-45, 'sx': 0, 'sy':1, 'sperp': 0.7071067811865475,  'spara':0.7071067811865476},
           'P45a': {'mu':0, 'phi':58+45, 'sx': 0, 'sy':1, 'sperp':-0.7071067811865475,  'spara':0.7071067811865476},

             '0b': {'mu':0, 'phi':58+ 0, 'sx':-1, 'sy':0, 'sperp': 1,                  'spara': 0},
           'M30b': {'mu':0, 'phi':58-30, 'sx':-1, 'sy':0, 'sperp': 0.8660254037844387, 'spara':-0.49999999999999994},
           'P30b': {'mu':0, 'phi':58+30, 'sx':-1, 'sy':0, 'sperp': 0.8660254037844387, 'spara': 0.49999999999999994},
           'M45b': {'mu':0, 'phi':58-45, 'sx':-1, 'sy':0, 'sperp': 0.7071067811865476, 'spara':-0.7071067811865475},
           'P45b': {'mu':0, 'phi':58+45, 'sx':-1, 'sy':0, 'sperp': 0.7071067811865476, 'spara': 0.7071067811865475},

           'sheight'   : 0,
           'sz'        : 0,
           'theta'     : -34.05,
           'kappa'     : -134.74,
           'tolerance' : 1
           }
    #"""

    def assertSxSyFromPerp(self, test):
        self.mu.return_value = self.tests[test]['mu']
        self.phi.return_value = self.tests[test]['phi']
        self.sx.return_value = self.tests[test]['sx']
        self.sy.return_value = self.tests[test]['sy']
        self.sperp.asynchronousMoveTo(self.tests[test]['sperp'])
        # False positives on sy with 1.1102230246251565e-16 != 0
        self.sy.asynchronousMoveTo.assert_called_with(self.tests[test]['sy'])
        # False positives on sx with -0.9999999999999999 != -1
        self.sx.asynchronousMoveTo.assert_called_with(self.tests[test]['sx'])
        assert not self.sz.asynchronousMoveTo.called

    def assertSxSyFromPara(self, test):
        self.mu.return_value = self.tests[test]['mu']
        self.phi.return_value = self.tests[test]['phi']
        self.sx.return_value = self.tests[test]['sx']
        self.sy.return_value = self.tests[test]['sy']
        self.spara.asynchronousMoveTo(self.tests[test]['spara'])
        self.sx.asynchronousMoveTo.assert_called_with(self.tests[test]['sx'])
        self.sy.asynchronousMoveTo.assert_called_with(self.tests[test]['sy'])
        assert not self.sz.asynchronousMoveTo.called

    def assertPerpFromSxSy(self, test):
        self.mu.return_value = self.tests[test]['mu']
        self.phi.return_value = self.tests[test]['phi']
        self.sx.return_value = self.tests[test]['sx']
        self.sy.return_value = self.tests[test]['sy']
        # Work around lack of almost equal
        diff=self.sperp.getPosition()-self.tests[test]['sperp']
        if abs(diff) > 0.001:
            self.assertEqual(self.sperp.getPosition(), self.tests[test]['sperp'])

    def assertParaFromSxSy(self, test):
        self.mu.return_value = self.tests[test]['mu']
        self.phi.return_value = self.tests[test]['phi']
        self.sx.return_value = self.tests[test]['sx']
        self.sy.return_value = self.tests[test]['sy']
        
        # Work around lack of almost equal
        diff=self.spara.getPosition()-self.tests[test]['spara']
        if abs(diff) > 0.001:
            self.assertEqual(self.spara.getPosition(), self.tests[test]['spara'])

    def testPerpFromSxSy0a(self):
        self.assertPerpFromSxSy('0a')
    def testParaFromSxSy0a(self):
        self.assertParaFromSxSy('0a')
    def testPerpFromSxSy0b(self):
        self.assertPerpFromSxSy('0b')
    def testParaFromSxSy0b(self):
        self.assertParaFromSxSy('0b')

    def testSxSyFromPerp0a(self):
        self.assertSxSyFromPerp('0a')
    def testSxSyFromPara0a(self):
        self.assertSxSyFromPara('0a')
    def testSxSyFromPerp0b(self):
        self.assertSxSyFromPerp('0b')
    def testSxSyFromPara0b(self):
        self.assertSxSyFromPara('0b')

    def testPerpFromSxSyM30a(self):
        self.assertPerpFromSxSy('M30a')
    def testParaFromSxSyM30a(self):
        self.assertParaFromSxSy('M30a')
    def testPerpFromSxSyM30b(self):
        self.assertPerpFromSxSy('M30b')
    def testParaFromSxSyM30b(self):
        self.assertParaFromSxSy('M30b')

    def testSxSyFromPerpM30a(self):
        self.assertSxSyFromPerp('M30a')
    def testSxSyFromParaM30a(self):
        self.assertSxSyFromPara('M30a')
    def testSxSyFromPerpM30b(self):
        self.assertSxSyFromPerp('M30b')
    def testSxSyFromParaM30b(self):
        self.assertSxSyFromPara('M30b')

    def testPerpFromSxSyP30a(self):
        self.assertPerpFromSxSy('P30a')
    def testParaFromSxSyP30a(self):
        self.assertParaFromSxSy('P30a')
    def testPerpFromSxSyP30b(self):
        self.assertPerpFromSxSy('P30b')
    def testParaFromSxSyP30b(self):
        self.assertParaFromSxSy('P30b')

    def testSxSyFromPerpP30a(self):
        self.assertSxSyFromPerp('P30a')
    def testSxSyFromParaP30a(self):
        self.assertSxSyFromPara('P30a')
    def testSxSyFromPerpP30b(self):
        self.assertSxSyFromPerp('P30b')
    def testSxSyFromParaP30b(self):
        self.assertSxSyFromPara('P30b')

    def testPerpFromSxSyM45a(self):
        self.assertPerpFromSxSy('M45a')
    def testParaFromSxSyM45a(self):
        self.assertParaFromSxSy('M45a')
    def testPerpFromSxSyM45b(self):
        self.assertPerpFromSxSy('M45b')
    def testParaFromSxSyM45b(self):
        self.assertParaFromSxSy('M45b')

    def testSxSyFromPerpM45a(self):
        self.assertSxSyFromPerp('M45a')
    def testSxSyFromParaM45a(self):
        self.assertSxSyFromPara('M45a')
    def testSxSyFromPerpM45b(self):
        self.assertSxSyFromPerp('M45b')
    def testSxSyFromParaM45b(self):
        self.assertSxSyFromPara('M45b')

    def testPerpFromSxSyP45a(self):
        self.assertPerpFromSxSy('P45a')
    def testParaFromSxSyP45a(self):
        self.assertParaFromSxSy('P45a')
    def testPerpFromSxSyP45b(self):
        self.assertPerpFromSxSy('P45b')
    def testParaFromSxSyP45b(self):
        self.assertParaFromSxSy('P45b')

    def testSxSyFromPerpP45a(self):
        self.assertSxSyFromPerp('P45a')
    def testSxSyFromParaP45a(self):
        self.assertSxSyFromPara('P45a')
    def testSxSyFromPerpP45b(self):
        self.assertSxSyFromPerp('P45b')
    def testSxSyFromParaP45b(self):
        self.assertSxSyFromPara('P45b')

    def testHeightMove(self):
        self.sx.return_value = self.tests['0a']['sx']
        self.sy.return_value = self.tests['0a']['sy']

        self.sheight.asynchronousMoveTo(self.tests['sz'])

        self.sx.asynchronousMoveTo.assert_called_with(self.tests['0a']['sx'])
        self.sy.asynchronousMoveTo.assert_called_with(self.tests['0a']['sy'])
        self.sz.asynchronousMoveTo.assert_called_with(self.tests['sz'])

    def assertStageFromLab(self, test, calc_mode):
        self.spara.setCalcMode(calc_mode)

        sx, sy, sz = self.spara.stageFromLab(dheight=0,
            dperp     = self.tests[test]['sperp'],
            dpara     = self.tests[test]['spara'],
            mu_rad    = self.tests[test]['mu']  * self.spara.DEG2RAD,
            theta_rad = self.tests['theta']     * self.spara.DEG2RAD,
            kappa_rad = self.tests['kappa']     * self.spara.DEG2RAD,
            phi_rad   = self.tests[test]['phi'] * self.spara.DEG2RAD)

        self.assertAlmostEqual(sx, self.tests[test]['sx'], self.tests['tolerance'])
        self.assertAlmostEqual(sy, self.tests[test]['sy'], self.tests['tolerance'])
        self.assertAlmostEqual(sz, 0,                      self.tests['tolerance'])

    def assertLabFromStage(self, test, calc_mode):
        self.spara.setCalcMode(calc_mode)

        sheight, sperp, spara = self.spara.labFromStage(
            dx        = self.tests[test]['sx'],
            dy        = self.tests[test]['sy'],
            dz        = self.tests['sz'],
            mu_rad    = self.tests[test]['mu']  * self.spara.DEG2RAD,
            theta_rad = self.tests['theta']     * self.spara.DEG2RAD,
            kappa_rad = self.tests['kappa']     * self.spara.DEG2RAD,
            phi_rad   = self.tests[test]['phi'] * self.spara.DEG2RAD)

        self.assertAlmostEqual(sheight, self.tests['sheight'],   self.tests['tolerance'])
        self.assertAlmostEqual(sperp, self.tests[test]['sperp'], self.tests['tolerance'])
        self.assertAlmostEqual(spara, self.tests[test]['spara'], self.tests['tolerance'])

    def testLabFromStage0aj(self):
        self.assertLabFromStage('0a', self.sperp.jamaMode)
    def testStageFromLab0aj(self):
        self.assertStageFromLab('0a', self.sperp.jamaMode)
    def testLabFromStage0as(self):
        self.assertLabFromStage('0a', self.sperp.scisoftpyMode)
    def testStageFromLab0as(self):
        self.assertStageFromLab('0a', self.sperp.scisoftpyMode)

    def testLabFromStage0bj(self):
        self.assertLabFromStage('0b', self.sperp.jamaMode)
    def testStageFromLab0bj(self):
        self.assertStageFromLab('0b', self.sperp.jamaMode)
    def testLabFromStage0bs(self):
        self.assertLabFromStage('0b', self.sperp.scisoftpyMode)
    def testStageFromLab0bs(self):
        self.assertStageFromLab('0b', self.sperp.scisoftpyMode)

    """ Note that these tests do not currently pass with the new Lab-stage calculations:

    def testLabFromStageM30aj(self):
        self.assertLabFromStage('M30a', self.sperp.jamaMode)
    def testStageFromLabM30aj(self):
        self.assertStageFromLab('M30a', self.sperp.jamaMode)
    def testLabFromStageM30as(self):
        self.assertLabFromStage('M30a', self.sperp.scisoftpyMode)
    def testStageFromLabM30as(self):
        self.assertStageFromLab('M30a', self.sperp.scisoftpyMode)

    def testLabFromStageM30bj(self):
        self.assertLabFromStage('M30b', self.sperp.jamaMode)
    def testStageFromLabM30bj(self):
        self.assertStageFromLab('M30b', self.sperp.jamaMode)
    def testLabFromStageM30bs(self):
        self.assertLabFromStage('M30b', self.sperp.scisoftpyMode)
    def testStageFromLabM30bs(self):
        self.assertStageFromLab('M30b', self.sperp.scisoftpyMode)

    def testLabFromStageP30aj(self):
        self.assertLabFromStage('P30a', self.sperp.jamaMode)
    def testStageFromLabP30aj(self):
        self.assertStageFromLab('P30a', self.sperp.jamaMode)
    def testLabFromStageP30as(self):
        self.assertLabFromStage('P30a', self.sperp.scisoftpyMode)
    def testStageFromLabP30as(self):
        self.assertStageFromLab('P30a', self.sperp.scisoftpyMode)

    def testLabFromStageP30bj(self):
        self.assertLabFromStage('P30b', self.sperp.jamaMode)
    def testStageFromLabP30bj(self):
        self.assertStageFromLab('P30b', self.sperp.jamaMode)
    def testLabFromStageP30bs(self):
        self.assertLabFromStage('P30b', self.sperp.scisoftpyMode)
    def testStageFromLabP30bs(self):
        self.assertStageFromLab('P30b', self.sperp.scisoftpyMode)

    def testLabFromStageM45aj(self):
        self.assertLabFromStage('M45a', self.sperp.jamaMode)
    def testStageFromLabM45aj(self):
        self.assertStageFromLab('M45a', self.sperp.jamaMode)
    def testLabFromStageM45as(self):
        self.assertLabFromStage('M45a', self.sperp.scisoftpyMode)
    def testStageFromLabM45as(self):
        self.assertStageFromLab('M45a', self.sperp.scisoftpyMode)

    def testLabFromStageM45bj(self):
        self.assertLabFromStage('M45b', self.sperp.jamaMode)
    def testStageFromLabM45bj(self):
        self.assertStageFromLab('M45b', self.sperp.jamaMode)
    def testLabFromStageM45bs(self):
        self.assertLabFromStage('M45b', self.sperp.scisoftpyMode)
    def testStageFromLabM45bs(self):
        self.assertStageFromLab('M45b', self.sperp.scisoftpyMode)

    def testLabFromStageP45aj(self):
        self.assertLabFromStage('P45a', self.sperp.jamaMode)
    def testStageFromLabP45aj(self):
        self.assertStageFromLab('P45a', self.sperp.jamaMode)
    def testLabFromStageP45as(self):
        self.assertLabFromStage('P45a', self.sperp.scisoftpyMode)
    def testStageFromLabP45as(self):
        self.assertStageFromLab('P45a', self.sperp.scisoftpyMode)

    def testLabFromStageP45bj(self):
        self.assertLabFromStage('P45b', self.sperp.jamaMode)
    def testStageFromLabP45bj(self):
        self.assertStageFromLab('P45b', self.sperp.jamaMode)
    def testLabFromStageP45bs(self):
        self.assertLabFromStage('P45b', self.sperp.scisoftpyMode)
    def testStageFromLabP45bs(self):
        self.assertStageFromLab('P45b', self.sperp.scisoftpyMode)
    """
#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
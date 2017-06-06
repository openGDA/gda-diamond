"""
Unit tests for Scannables which move the sample perpendicular to and parallel
to the beam, for I16.

For help with configuring these scannables, see the example configuration below,
search for "Start Example configuration".
"""

import unittest
from mock import Mock

class SampleMotionI16Test(unittest.TestCase):

    def setUp(self):
        # Initialise these as local, so the example code looks the same
        # as it will in localstation or a user script.
        (sx, sy, sz, mu, phi, kappa, theta) = self.setUpMocks()

        #################### Start Example configuration ####################  
        from scannables.PerpendicularSampleMotion import PerpendicularSampleMotion, ParallelSampleMotion

        sperp=PerpendicularSampleMotion("sperp", sx, sy, sz, mu, phi, kappa, theta)
        spara=ParallelSampleMotion     ("spara", sx, sy, sz, mu, phi, kappa, theta)

        #################### End Example configuration ####################  

        self.sperp = sperp
        self.spara = spara
        self.sperp.verbose=False
        self.spara.verbose=False
        self.sperp.no_move=False
        self.spara.no_move=False
        
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

    tests={  '0a': {'mu':0, 'phi':  0, 'sx':0, 'sy':1, 'sperp': 1,                   'spara': 0},
           'M30a': {'mu':0, 'phi':-30, 'sx':0, 'sy':1, 'sperp': 0.8660254037844387,  'spara':-0.49999999999999994},
           'P30a': {'mu':0, 'phi': 30, 'sx':0, 'sy':1, 'sperp': 0.8660254037844387,  'spara': 0.49999999999999994},
           'M45a': {'mu':0, 'phi':-45, 'sx':0, 'sy':1, 'sperp': 0.7071067811865476,  'spara':-0.7071067811865475},
           'P45a': {'mu':0, 'phi': 45, 'sx':0, 'sy':1, 'sperp': 0.7071067811865476,  'spara': 0.7071067811865475},
           
             '0b': {'mu':0, 'phi':  0, 'sx':1, 'sy':0, 'sperp': 0,                   'spara': 1},
           'M30b': {'mu':0, 'phi':-30, 'sx':1, 'sy':0, 'sperp': 0.49999999999999994, 'spara': 0.8660254037844387},
           'P30b': {'mu':0, 'phi': 30, 'sx':1, 'sy':0, 'sperp':-0.49999999999999994, 'spara': 0.8660254037844387},
           'M45b': {'mu':0, 'phi':-45, 'sx':1, 'sy':0, 'sperp': 0.7071067811865475,  'spara': 0.7071067811865476},
           'P45b': {'mu':0, 'phi': 45, 'sx':1, 'sy':0, 'sperp':-0.7071067811865475,  'spara': 0.7071067811865476},
           }

    def assertSxSyFromPerp(self, test):
        self.mu.return_value = self.tests[test]['mu']
        self.phi.return_value = self.tests[test]['phi']
        self.sx.return_value = self.tests[test]['sx']
        self.sy.return_value = self.tests[test]['sy']
        self.sperp.asynchronousMoveTo(self.tests[test]['sperp'])
        # False positives here with -1 != -0.9999999999999999
        self.sx.asynchronousMoveTo.assert_called_with(self.tests[test]['sx'])
        self.sy.asynchronousMoveTo.assert_called_with(self.tests[test]['sy'])

    def assertSxSyFromPara(self, test):
        self.mu.return_value = self.tests[test]['mu']
        self.phi.return_value = self.tests[test]['phi']
        self.sx.return_value = self.tests[test]['sx']
        self.sy.return_value = self.tests[test]['sy']
        self.spara.asynchronousMoveTo(self.tests[test]['spara'])
        self.sx.asynchronousMoveTo.assert_called_with(self.tests[test]['sx'])
        self.sy.asynchronousMoveTo.assert_called_with(self.tests[test]['sy'])

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

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
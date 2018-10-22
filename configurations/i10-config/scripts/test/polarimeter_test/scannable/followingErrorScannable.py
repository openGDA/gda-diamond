"""
Unit tests for Scannable Motor with Following Error scannable for use with
GDA at Diamond Light Source
"""

import unittest
from mock import Mock
from polarimeter.scannable.followingErrorScannable \
                    import FollowingErrorScannable

class FollowingErrorTest(unittest.TestCase):

    def setUp(self):
        self.scannable = Mock()
        self.scannable.name = "RetRotation"
        self.scannable.getLevel.return_value=8
        
        self.retRotFE = FollowingErrorScannable('retRotFE', self.scannable,
            'ME02P-MO-RET-01:ROT')
        
        #self.retRotFE.configure()
        self.retRotFE.feError = Mock()
        self.retRotFE.feErrorMax = Mock()
        self.retRotFE.feMaxReset = Mock()

    def tearDown(self):
        pass

    def testScannableSetup(self):
        retRotFE = FollowingErrorScannable(
            'retRotFE', self.scannable, 'ME02P-MO-RET-01:ROT')

        self.assertEquals(repr(self.retRotFE), repr(retRotFE))
        
        self.assertEqual('retRotFE', self.retRotFE.name)
        self.assertEqual(list(self.retRotFE.inputNames), [u'retRotFE'])
        self.assertEqual(list(self.retRotFE.extraNames), [u'max'])
        self.assertEqual(list(self.retRotFE.outputFormat), ['%f', '%f'])

    def test__repr__(self):
        self.assertEquals(repr(self.retRotFE), "FollowingErrorScannable"+
            "(u'retRotFE', 'RetRotation', 'ME02P-MO-RET-01:ROT')")
    
    def test__str__(self):
        self.retRotFE.feError.caget.return_value=0.123
        self.retRotFE.feErrorMax.caget.return_value=0.234
        self.assertEquals(str(self.retRotFE), 
            'followingError=0.123, maxFollowingError=0.234')

    def testAtLevelMoveStart(self):
        self.retRotFE.atLevelMoveStart()
        self.retRotFE.feMaxReset.caput.assert_called_with(1)

    def testAtScanStart(self):
        self.retRotFE.feError.isConfigured.return_value = False
        self.retRotFE.feErrorMax.isConfigured.return_value = False
        self.retRotFE.feMaxReset.isConfigured.return_value = False

        self.retRotFE.atScanStart()
        
        self.retRotFE.feError.configure.assert_called_with()
        self.retRotFE.feErrorMax.configure.assert_called_with()
        self.retRotFE.feMaxReset.configure.assert_called_with()
        
    def testGetPosition(self):
        # Why are the isConfigured.return_value 's not needed here?
        self.retRotFE.feError.caget.return_value=0.123
        self.retRotFE.feErrorMax.caget.return_value=0.234
        self.assertEqual(list(self.retRotFE.getPosition()), [0.123, 0.234])

    def testIsBusy(self):
        self.scannable.isBusy.return_value = False
        self.assertEqual(False, self.retRotFE.isBusy())
            
        self.scannable.isBusy.return_value = True
        self.assertEqual(True, self.retRotFE.isBusy())
        
#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
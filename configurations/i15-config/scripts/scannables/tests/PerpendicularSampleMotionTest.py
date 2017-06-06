"""
Unit tests for Scannables which move the sample perpendicular to and parallel
to the beam, for I15 & I16.
"""

import unittest
from scannables.tests.PerpendicularSampleMotionI15Test import SampleMotionI15Test
from scannables.tests.PerpendicularSampleMotionI16Test import SampleMotionI16Test

suite1 = unittest.TestLoader().loadTestsFromTestCase(SampleMotionI15Test)
suite2 = unittest.TestLoader().loadTestsFromTestCase(SampleMotionI16Test)
alltests = unittest.TestSuite([suite1, suite2])

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
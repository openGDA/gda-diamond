"""
Unit tests for Insertion Device position class
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""

import unittest
from Diamond.idPosition import IdPosition

class IdPositionTest(unittest.TestCase):

    def setUp(self):
        self.idPosition = IdPosition(gap=0, rowphase1=1, \
            rowphase2=2, rowphase3=3, rowphase4=4, jawphase=5)

    def tearDown(self):
        pass

    def testEquivalence(self):
        idPosition=IdPosition(0, 1, 2, 3, 4, 5)
                
        self.assertEquals(repr(self.idPosition), repr(idPosition))

    def test__str__(self):
        self.assertEquals(str(self.idPosition), "gap=0, rowphase1=1, rowphase2=2, rowphase3=3, rowphase4=4, jawphase=5")

    def test__repr__(self):
        self.assertEquals(repr(self.idPosition), "IdPosition(gap=0, rowphase1=1, rowphase2=2, rowphase3=3, rowphase4=4, jawphase=5)")

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
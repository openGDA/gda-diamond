"""
Unit tests for Polynomial evaluator for use with GDA at Diamond Light Source
"""

import unittest
from Diamond.Poly import Poly

class PolyTest(unittest.TestCase):

    def setUp(self):
        self.poly=Poly(power0first=True, coeffs=[3, 2, 1])

    def tearDown(self):
        pass

    def testEquivalence(self):
        poly=Poly(power0first=True, coeffs=[3, 2, 1])
        
        self.assertEquals(repr(self.poly), repr(poly))

        poly=Poly([1, 2, 3])

        self.assertEquals(repr(self.poly), repr(poly))

    def test__str__(self):
        self.assertEquals(str(self.poly), "((1)*x**2)+((2)*x**1)+((3)*x**0)")

    def test__repr__(self):
        self.assertEquals(repr(self.poly), "Poly(coeffs=[1, 2, 3], power0first=False)")

    def test__call__(self):
        self.assertEquals(18, self.poly(3))

class PolyTestDegenerate(unittest.TestCase):

    def setUp(self):
        self.poly=Poly([])

    def tearDown(self):
        pass

    def testEquivalence(self):
        poly=Poly(power0first=True, coeffs=[0])
        
        self.assertEquals(repr(self.poly), repr(poly))

        poly=Poly([0])

        self.assertEquals(repr(self.poly), repr(poly))

    def test__str__(self):
        self.assertEquals(str(self.poly), "0")

    def test__repr__(self):
        self.assertEquals(repr(self.poly), "Poly(coeffs=[0], power0first=False)")

    def test__call__(self):
        self.assertEquals(0, self.poly(3))
        self.assertEquals(0, self.poly(0.1e88))

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()
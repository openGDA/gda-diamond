'''
Created on 19 Jul 2012

@author: fy65
'''
from calibration.Energy_class import BeamEnergy
import string
import unittest


class TestBeamEnergy(unittest.TestCase):


    def setUp(self):
        self.lines=self.readTestData("igapcal.txt")
        self.energy=BeamEnergy("energy",rootNameSpace=globals())
        


    def tearDown(self):
        self.lines = None


    def testIdgap(self):
        i=1
        for n,e,g in self.lines:
            gap=self.energy.idgap(e, n)
            print ("%d\t%f\t%f\t%f\t%f" % (n,e,g,gap, g-gap))
            self.assertAlmostEquals(gap, g, 3, "line number " + str(i))
            i=i+1

    
    def readTestData(self,filename): 
        '''
        read in the test data
        :param filename:
        '''
        f = open(filename, "r")
        lines = f.readlines()
        f.close()
        lines = map(string.split, map(string.strip, lines))
        lines = [(int(x[0]), float(x[1]), float(x[2])) for x in lines[2:]]
        return lines

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testIdgap']
    unittest.main()

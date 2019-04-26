'''
Created on 20 Sep 2016

@author: fy65
'''
import string

def loadLookupTable(filename):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    lines = map(string.split, map(string.strip, lines))
    lookuptable={}
    for line in lines[2:]:
        print line
        lookuptable[(float(line[0]),float(line[1]))]=[float(item) for item in line[2:]]
    return lookuptable    

def test():
    lookuptable=loadLookupTable("/dls_sw/i21/software/gda/config/lookupTables/IDEnergy2GapCalibrations.txt")
    for key, value in lookuptable.iteritems():
        print key, value
    print
    print lookuptable[("LH","1200-1400")]

if __name__ == "__main__":
    test()
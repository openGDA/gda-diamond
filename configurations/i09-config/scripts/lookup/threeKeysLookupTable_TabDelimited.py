'''
Created on 20 Sep 2016

@author: fy65
'''
import string
import os

def loadLookupTable(filename):
    f = open(os.path.realpath(filename), "r")
    lines = f.readlines()
    f.close()
    lines = map(string.split, map(string.strip, lines))
    lookuptable={}
    for line in lines[2:]:
        #print line
        lookuptable[(line[0],float(line[1]),float(line[2]))]=[float(item) for item in line[3:]]
    return lookuptable    

def test():
    lookuptable=loadLookupTable("../../lookupTables/JIDEnergy2GapCalibrations.txt")
    formatstring="%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s"
    print (formatstring % ("Mode", "Min Energy", "Max Energy", "Coefficent0", "Coefficent1", "Coefficent2", "Coefficent3", "Coefficent4"))
    for key, value in sorted(lookuptable.iteritems()):
        print (formatstring % (key[0],key[1],key[2],value[0],value[1],value[2],value[3],value[4]))    
    print

    print lookuptable.keys()
    lowEnergies=sorted([e[1] for e in lookuptable.keys() if e[0]=="LH"])
    highEnergies=sorted([e[2] for e in lookuptable.keys() if e[0]=="LH"])
    print lowEnergies
    print highEnergies
    minEnergy=min(lowEnergies)
    maxEnergy=max(highEnergies)
    print minEnergy, maxEnergy    
    limits=zip(lowEnergies, highEnergies)
    for low, high in limits:
        print low, high
    from calibration.energy_polarisation_class import getFittingCoefficents
    print getFittingCoefficents("LH", 0.81, lookuptable)

if __name__ == "__main__":
    test()
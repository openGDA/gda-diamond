'''
load lookup table from a CSV (comma separated value) file

- test is limited to 4 keys and 7-order polynomial

Created on 24 Spet 2019

@author: fy65
'''
import csv

def loadLookupTable(filename):
    with open(filename) as csv_data:
        reader = csv.reader(csv_data)
        rows = [row for row in reader if row or not row.startswith('#')]
        header = rows[0]

    lookuptable={}
    for row in rows[1:]:
        #print row
        lookuptable[(row[0],int(row[1]),int(row[2]),row[3])]=[float(item) for item in row[4:]]
    return lookuptable, header   

def test():
    lookuptable, header=loadLookupTable("../../lookupTables/IDEnergy2GapCalibrations.csv")
    formatstring="%4s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s"
    print (formatstring % (header[0],header[1],header[2],header[3],header[4],header[5],header[6],header[7],header[8],header[9],header[10],header[11]))
    for key, value in sorted(lookuptable.iteritems()):
        print (formatstring % (key[0],key[1],key[2],key[3],value[0],value[1],value[2],value[3],value[4], value[5],value[6],value[7]))    
    print
    print "return for key ('LH',1050,1220,'VPG1') = %s" % lookuptable[('LH',1050,1220,'VPG1')]
    print "available keys: %s" % lookuptable.keys()
    lowEnergies=sorted([e[1] for e in lookuptable.keys() if e[0]=="LH"])
    highEnergies=sorted([e[2] for e in lookuptable.keys() if e[0]=="LH"])
    print "low limits: %s " % lowEnergies
    print "high limits: %s" % highEnergies
    minEnergy=min(lowEnergies)
    maxEnergy=max(highEnergies)
    print "Overall energy limits: [%i, %i]" % (minEnergy, maxEnergy)    
    limits=zip(lowEnergies, highEnergies)
    
    print 
    print "Energy limits in table"
    for low, high in limits:
        print low, high
    from calibration.energy_polarisation_class import getFittingCoefficents
    print "Coefficients for ('LH', 750.1,'VPG1') = %s" % getFittingCoefficents("LH", 750.1,'VPG1',lookuptable)

if __name__ == "__main__":
    test()
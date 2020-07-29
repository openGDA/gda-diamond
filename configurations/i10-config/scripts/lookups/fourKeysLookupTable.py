'''
load lookup table from a CSV (comma separated value) file

- test is limited to 4 keys and 7-order polynomial

Created on 24 Spet 2019

@author: fy65
'''
import csv

def get_fitting_coefficents(source, polarisation, energy, lut={}):  
    '''
    returns the coefficients of polynomial calibrated for the specified source, polarisation and energy.
    
    :param source: X-ray source, idd or idu
    :param polarisation: X-ray polarisation, lh, lv, pc, nc, la, or lh3
    :param energy: X-ray energy in eV
    :param lut: the lookup table storing the calibrated data.
    '''
    lowEnergies=sorted([e[2] for e in lut.keys() if (e[0]==source and e[1]==polarisation)])
    #print lowEnergies
    highEnergies=sorted([e[3] for e in lut.keys() if (e[0]==source and e[1]==polarisation)])
    #print highEnergies
    minEnergy=min(lowEnergies)
    maxEnergy=max(highEnergies)
    limits=zip(lowEnergies, highEnergies)
    #print "Calibrated energy ranges: %s" % (limits)   
    if (energy<minEnergy or energy > maxEnergy):
        raise ValueError("Demanding energy must lie between %s and %s eV!"%(minEnergy, maxEnergy))
    else:
        for low, high in limits:
            if (energy >= low and energy < high): 
                return lut[(source, polarisation, low, high)]
        raise Exception("Cannot find polynomial coefficients for your requested energy. There might be gap in the calibration lookup table.")
            

def load_lookup_table(filename):
    '''read a CSV file storing lookup table and create a dictionar using values in the fisrt 4 columns as key and return both dictionary and header
    '''
    with open(filename) as csv_data:
        reader = csv.reader(csv_data)
        rows = [row for row in reader if row or not row.startswith('#')]
        header = rows[0]

    lookuptable={}
    for row in rows[1:]:
        #print row
        lookuptable[(row[0],row[1],float(row[2]),float(row[3]))]=[float(item) for item in row[4:]]
    return lookuptable, header   

def test():
    lookuptable, header=load_lookup_table("../../lookupTables/IDEnergy2GapCalibrations.csv")
    formatstring="%4s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s"
    print (formatstring % (header[0],header[1],header[2],header[3],header[4],header[5],header[6],header[7],header[8],header[9],header[10],header[11]))
    for key, value in sorted(lookuptable.iteritems()):
        print (formatstring % (key[0],key[1],key[2],key[3],value[0],value[1],value[2],value[3],value[4], value[5],value[6],value[7]))    
    print
    print "return for key ('idd','lh',1050,1220) = %s" % lookuptable[('idd','lh',1050,1220)]
    print "available keys: %s" % lookuptable.keys()
    lowEnergies=sorted([e[2] for e in lookuptable.keys() if e[0]=="idd" and e[1]=="lh"])
    highEnergies=sorted([e[3] for e in lookuptable.keys() if e[0]=="idd" and e[1]=="lh"])
    print "low limits: %s " % lowEnergies
    print "high limits: %s" % highEnergies
    minEnergy=min(lowEnergies)
    maxEnergy=max(highEnergies)
    print "Overall energy limits: [%f, %f]" % (minEnergy, maxEnergy)    
    limits=zip(lowEnergies, highEnergies)
    
    print 
    print "Energy limits in table"
    for low, high in limits:
        print low, high
    print "Coefficients for ('idd', 'lh', 750.1) = %s" % get_fitting_coefficents("idd", "lh", 750.1, lookuptable)

if __name__ == "__main__":
    test()
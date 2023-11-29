'''
load lookup table from a CSV (comma separated value) file

- test is limited to 4 keys and 7-order polynomial

Created on 24 Spet 2019

@author: fy65
'''
import csv

def get_fitting_coefficents(polarisation, energy, lut={}):  
    '''
    returns the coefficients of polynomial calibrated for the specified polarisation and energy range.
    
    :param polarisation: X-ray polarisation, LH, LV, CR, CL, or LH3
    :param energy: X-ray energy in eV
    :param lut: the lookup table storing the calibrated data.
    '''
    low_energies=sorted([e[1] for e in lut.keys() if (e[0]==polarisation)])
    high_energies=sorted([e[2] for e in lut.keys() if (e[0]==polarisation)])
    min_energy=min(low_energies)
    max_energy=max(high_energies)
    limits=zip(low_energies, high_energies)
    if (energy<min_energy or energy > max_energy):
        raise ValueError("Demanding energy must lie between %s and %s eV!"%(min_energy, max_energy))
    else:
        for low, high in limits:
            if (energy >= low and energy < high): 
                return lut[(polarisation, low, high)]
        raise ValueError("Cannot find polynomial coefficients for your requested energy. There might be gap in the calibration lookup table.")
            

def load_lookup_table(filename):
    '''read a CSV file storing lookup table and create a dictionar using values in the fisrt 4 columns as key and return both dictionary and header
    '''
    import os
    if not os.path.isabs(filename):
        filename=os.path.realpath(filename)
    with open(filename) as csv_data:
        reader = csv.reader(csv_data)
        rows = [row for row in reader if row and not row[0].startswith('#')]
        header = rows[0]

    lookuptable={}
    for row in rows[1:]:
        lookuptable[(row[0],float(row[1]),float(row[2]))]=[float(item) for item in row[3:]]
    return lookuptable, header   

def test():
    lookuptable, header=load_lookup_table("../../lookupTables/JIDEnergy2GapCalibrations.csv")
    formatstring="%4s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s"
    print (formatstring % tuple([x for x in header]))
    for key, value in sorted(lookuptable.iteritems()):
        print (formatstring % tuple([x for x in key] + [x for x in value]))
       
    print ("return for key ('LH',0.1040,1.200) = %s" % lookuptable[('LH',0.1040,1.200)])
    print ("available keys: %s" % lookuptable.keys())
    low_energies=sorted([e[1] for e in lookuptable.keys() if e[0]=="LH"])
    high_energies=sorted([e[2] for e in lookuptable.keys() if e[0]=="LH"])
    print("low limits: %s " % low_energies)
    print("high limits: %s" % high_energies)
    min_energy=min(low_energies)
    max_energy=max(high_energies)
    print ("Overall energy limits: [%f, %f]" % (min_energy, max_energy))    
    limits=zip(low_energies, high_energies)
    

    print ("Energy limits in table")
    for low, high in limits:
        print (low, high)
    print ("Coefficients for ('LH', 0.7501) = %s" % get_fitting_coefficents("LH", 0.7501, lookuptable))

if __name__ == "__main__":
    test()
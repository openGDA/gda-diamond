'''
load lookup table from a CSV (comma separated value) file

- test is limited to 4 keys and 7-order polynomial

Created on 24 Spet 2019

@author: fy65
'''
import csv

def get_fitting_coefficents(polarisation_mode, Ep, vpg, lut={}):
    if not (polarisation_mode in [key[0] for key in lut.keys()]):
        raise KeyError("Polarisation Mode '%s' is not available in the calibration lookup table!" % (polarisation_mode))
    low_energies = sorted([e[1] for e in lut.keys() if (e[0]==polarisation_mode and e[3]==vpg)])
    # print("Low energy limits %s" % str(low_energies))
    high_energies = sorted([e[2] for e in lut.keys() if (e[0]==polarisation_mode and e[3]==vpg)])
    # print("High energy limits %s" % str(high_energies))
    minimum_energy = min(low_energies)
    maximum_energy = max(high_energies)
    limits = zip(low_energies, high_energies)
    # print("Calibrated energy ranges: %s" % (limits))   
    if (Ep < minimum_energy or Ep > maximum_energy):
        raise ValueError("Demanding energy must lie between %s and %s eV!"%(minimum_energy, maximum_energy))
    else:
        for low, high in limits:
            if (Ep >= low and Ep < high): 
                return lut[(polarisation_mode, low, high, vpg)]
            
def load_lookup_table(filename):
    with open(filename) as csv_data:
        reader = csv.reader(csv_data)
        rows = [row for row in reader if row or not row.startswith('#')]
        header = rows[0]

    lookuptable={}
    for row in rows[1:]:
        #print(row)
        lookuptable[(row[0],int(row[1]),int(row[2]),row[3])]=[float(item) for item in row[4:]]
    return lookuptable, header   

def test():
    lookuptable, header=load_lookup_table("../../lookupTables/IDEnergy2GapCalibrations.csv")
    formatstring="%4s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s\t%10s"
    print (formatstring % (header[0],header[1],header[2],header[3],header[4],header[5],header[6],header[7],header[8],header[9],header[10],header[11]))
    for key, value in sorted(lookuptable.iteritems()):
        print (formatstring % (key[0],key[1],key[2],key[3],value[0],value[1],value[2],value[3],value[4], value[5],value[6],value[7]))    
    print()
    print("return for key ('LH',1050,1220,'VPG1') = %s" % lookuptable[('LH',1050,1220,'VPG1')])
    print("available keys: %s" % lookuptable.keys())
    low_energies=sorted([e[1] for e in lookuptable.keys() if e[0]=="LH"])
    high_energies=sorted([e[2] for e in lookuptable.keys() if e[0]=="LH"])
    print("low limits: %s " % low_energies)
    print("high limits: %s" % high_energies)
    min_energy=min(low_energies)
    max_energy=max(high_energies)
    print("Overall energy limits: [%i, %i]" % (min_energy, max_energy))    
    limits=zip(low_energies, high_energies)
    
    print()
    print("Energy limits in table")
    for low, high in limits:
        print("Low Limit = %f, High Limit = %f" %(low, high))

    print("Coefficients for ('LH', 750.1,'VPG1') = %s" % get_fitting_coefficents("LH", 750.1,'VPG1',lookuptable))

if __name__ == "__main__":
    test()
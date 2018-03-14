'''
Created on 6 Feb 2014

@author: fy65
'''
import string
    
def readLookupTable(filename): 
    '''
    read in the lookup table from a tab-delimited data file. 
    :param filename:
    '''
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    lines = map(string.split, map(string.strip, lines))
    
    lookuptable={}
    for x in lines[1:]:
        print x
        lookuptable[str(x[0])]=[str(item) for item in x[1:]]
    return lookuptable

lowtable=readLookupTable("/dls_sw/i09/software/gda_versions/gda_master_2/workspace/i09-config/lookupTables/low_energy_table.txt")
hightable=readLookupTable("/dls_sw/i09/software/gda_versions/gda_master_2/workspace/i09-config/lookupTables/high_energy_table.txt")
print lowtable
print hightable
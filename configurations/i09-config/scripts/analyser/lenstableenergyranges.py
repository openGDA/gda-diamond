'''
Created on 6 Feb 2014

@author: fy65
'''
import string
import os
from gda.configuration.properties import LocalProperties #@UnresolvedImport

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
        if "#" != x[0][0]:
            lookuptable[str(x[0])]=[str(item) for item in x[1:]]
    return lookuptable

lowtable = readLookupTable(os.path.join(LocalProperties.get("gda.config"), "lookupTables/low_elementset_table.txt"))
hightable = readLookupTable(os.path.join(LocalProperties.get("gda.config"), "lookupTables/high_elementset_table.txt"))
print(lowtable)
print(hightable)
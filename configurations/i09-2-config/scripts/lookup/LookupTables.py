import string
    
def readLookupTable(filename): 
    '''
    read in the lookupTable table from a tab-delimited data file. 
    :param filename:
    '''
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    lines = map(string.split, map(string.strip, lines))
    lookuptable={}
    for x in lines[3:]:
        lookuptable[int(x[0])]=[float(item) for item in x[1:]]
    return lookuptable
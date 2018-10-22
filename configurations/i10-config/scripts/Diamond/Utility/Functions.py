#Define a list of useful functions for beamline control

def swap(a, b):
    return b,a

#To get the current scan number
def getScanNumber():
    from gda.data import NumTracker
    nt = NumTracker("tmp")
    scanNumber = nt.getCurrentFileNumber();
    del nt;
    return scanNumber

#To get the current scan number
def incScanNumber():
    from gda.data import NumTracker
    nt = NumTracker("tmp")
    nt.incrementNumber();
    del nt;
    return;

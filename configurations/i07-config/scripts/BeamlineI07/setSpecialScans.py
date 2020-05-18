
from gda.jython.commands.GeneralCommands import alias

from Diamond.Scans.BasicScan import BasicScanClass
from Diamond.Scans.RegionalScan import RegionalScanClass
from Diamond.Scans.PowerSeriesScan import PowerSeriesScanClass
from Diamond.Scans.CentroidScan import CentroidScanClass

from BeamlineI07.scan.position_provider import ValidPositionsProvider

#Usage
rscan=RegionalScanClass()
alias('rscan');

#Usage:
print "Use rscan motor (R1, R2, ... R3) for multiple-region scan"
print "where the region Rx is defined by a [start, stop, step] list and all regions are grouped in a tuple"
print "For example:"
print "    rscan testMotor1 ([0, 5, 1], [6,10,0.1], [10,15,1]) dummyCounter1 0.1"


iscan=PowerSeriesScanClass()
alias('iscan');
#Usage:
print "Use iscan motor start stop growthRate for scan in a exponential increase of steps. "
print "The n-th scan point is calculated using a0*(1+q)^n, where a0 is the starting point and q is the growth rate."
print "For example:"
print "    iscan testMotor1 1 100, 1 dummyCounter1 0.1"


del cscan
cscan=CentroidScanClass()
alias('cscan');
#Usage:
#print "Use cscan motor centre width step for centroid scan"

del scan
scan=BasicScanClass()
alias('scan');

def scanvalid(scannable, start, stop, step, *args):
    scanPosProv = ValidPositionsProvider(scannable, start, stop, step)
    scan(scannable, scanPosProv, *args)

alias('scanvalid')

def validtest(scannable, start, stop, step):
    """
    Create a ValidPositionsProvider but don't run a scan
    Provides an indication (via print statements) which points
    would be ignored.
    """
    ValidPositionsProvider(scannable, start, stop, step)

alias('validtest')

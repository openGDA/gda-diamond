
from gda.jython.commands.GeneralCommands import alias

from Diamond.Scans.RegionalScan import RegionalScanClass
from Diamond.Scans.PowerSeriesScan import PowerSeriesScanClass

#Usage
rscan=RegionalScanClass()
alias('rscan');

#Usage:
print "Use rscan motor (R1, R2, ... R3) for multiple-region scan"
print "where Rx is defined by a [start, stop, step] list"
print "For example:"
print "    rscan testMotor1 ([0, 5, 1], [6,10,0.1], [10,15,1]) dummyCounter1 0.1"
print "Note that if there is only one region, a comma at the end of tuple is necessary:"
print "For example:"
print "    rscan testMotor1 ([0, 5, 1],) dummyCounter1 0.1"


iscan=PowerSeriesScanClass()
alias('iscan');

#Usage:
print "Use iscan motor start stop increaseInPercentage scan with increased steps"

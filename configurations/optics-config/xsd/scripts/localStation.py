#localStation.py
#For beamline specific initialisation code.

print "===================================================================";
print "Performing Laboratory 80 specific initialisation code for polarimeter (localStation.py).";
print


from gda.jython.commands.GeneralCommands import alias

print "-"*100
print "Set scan returns to the start positions on completion"
print "   To set scan returns to its start positions on completion please do:"
print "      >>>scansReturnToOriginalPositions=1"
scansReturnToOriginalPositions=0;
print

print "-"*100
import functions.dirFileCommands
print functions.dirFileCommands.__doc__
from functions.dirFileCommands import pwd,lwf,nwf,nfn,setSubdirectory,getSubdirectory  # @UnusedImport
alias("pwd")
alias("lwf")
alias("nwf")
alias("nfn")
alias("setSubdirectory")
alias("getSubdirectory")
print

from scannables.polarimeterHexapod import hpcontroller,hpx,hpy,hpz,hpc,hpb,hpa,hexapod  # @UnusedImport
from scannables.polarimeterTemperatureMonitor import anatemp,rettemp  # @UnusedImport

print "==================================================================="; print; print;

print "end of localStation.py"
#import scannables.detector.andormcd
#i06ccd2 = scannables.detector.andormcd.AndorMCD('i06ccd2')



import math #@UnusedImport
from gda.configuration.properties import LocalProperties
from gda.jython.commands import GeneralCommands
from gda.factory import Finder #@UnusedImport
from gda.jython.commands.GeneralCommands import vararg_alias, alias #@UnusedImport
from gda.device.scannable.scannablegroup import ScannableGroup #@UnusedImport

print(""*100);
print "Performing general initialisation code for i09-shared.";
print(""*100)

print "-"*100
print "Set if scan returns to the original positions on completion."
print "    scansReturnToOriginalPositions=0, not return to its start position (the default);"
print "    scansReturnToOriginalPositions=1, return to its start position;"
scansReturnToOriginalPositions=0;
print("")

###############################################################################
###                            Directory manipulation                       ###
###############################################################################
from i09shared.utils.directory_operation_commands import pwd, lwf, nwf, nfn, cfn, setSubdirectory, getSubdirectory #@UnusedImport

###############################################################################
###                            Time objects                                 ###
###############################################################################
print("-"*100)
print "Creating time utilities"
from gdascripts.scannable.timerelated import clock, t, dt, w, epoch, timerelated #@UnusedImport
print("Defines Scannables that deal with time. Five standard Scannables available as:")
print("t           := Time since the scan start")
print("dt          := Time since last getPosition() call")
print("w           := Wait time since last asked to move")
print("clock       := Time of the day")
print("epoch       := Time since last epoch")
print("timerelated := ScannableGroup containing all of the above")
print("")
from gdascripts.pd.time_pds import showtimeClass, showincrementaltimeClass,waittimeClass, waittimeClass2, actualTimeClass, showtime, inctime, waittime, atime #@UnusedImport
print("")

###############################################################################
###                            Epics utilites                               ###
###############################################################################
print("-"*100)
print "Load EPICS Pseudo Device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import * #@UnusedWildImport
print("")

print("-"*100)
print "Load EPICS utilities:"
from gdascripts.utils import caput_string2waveform, caput_wait, cagetArray, caput, caget #@UnusedImport
print("    caput_string2waveform(pvstring, value), caput_wait(pvstring, value, timeout=10), cagetArray(pvstring), caput(pvstring,value), caget(pvstring)")
print("")

###############################################################################
###                            Core utilities and constants                 ###
###############################################################################

print("-"*100)
print "Load core utilities:"
from gdascripts.utils import functional, jobs, default_scannables, attributes, iterableprint, listprint, frange #@UnusedImport
print("    functional, jobs, default_scannables(*scn), attributes(object), iterableprint(iterable), listprint(list), frange(start,end,step)")
print("")

print("-"*100)
print("Load drange:")
from i09shared.utils.dRangeUtil import drange #@UnusedImport
print("    Decimal version of range():   drange(start,end,step) to provide exact number of decimal places as step value inputed")
print("")

print("-"*100)
print "Load common physical constants:"
from gdascripts.constants import amu, aum, clight, eV, hPlanck, hPlanckeV, hbar, hbareV, m_e, me, one_angstrom_in_electronvolts, pi, r_e, re, tau #@UnusedImport
print("\tamu, aum, clight, eV, hPlanck, hPlanckeV, hbar, hbareV, m_e, me, one_angstrom_in_electronvolts, pi, r_e, re, tau")
print("")

print("-"*100)
print "Create an 'interruptable()' function which can be used to make for-loop interruptable in GDA."
print "    To use this, you must place 'interruptable()' call as the 1st or last line in your for-loop."

def interruptable():
    GeneralCommands.pause()
print("")

###############################################################################
###                            Plotting utilities                           ###
###############################################################################
from i09shared.plottings.configScanPlot import setYFieldVisibleInScanPlot, getYFieldVisibleInScanPlot, setXFieldInScanPlot, getXFieldInScanPlot, useSeparateYAxes, useSingleYAxis #@UnusedImport

#ToDo - Is this needed?
### Pipeline
def configureScanPipeline(length = None, simultaneousPoints = None):
    lengthProp = LocalProperties.GDA_SCAN_MULTITHREADED_SCANDATA_POINT_PIPElINE_LENGTH
    simultaneousProp = LocalProperties.GDA_SCAN_MULTITHREADED_SCANDATA_POINT_PIPElINE_POINTS_TO_COMPUTE_SIMULTANEOUSELY
    def show():
        print "ScanDataPoint pipeline:"
        print " " + lengthProp + " = " + LocalProperties.get(lengthProp, '4') # duplicated in ScannableCommands
        print " " + simultaneousProp + " = " + LocalProperties.get(simultaneousProp, '3') # duplicated in ScannableCommands
    if (length == None) or (simultaneousPoints == None):
        show()
    else:
        LocalProperties.set(lengthProp, `length`)
        LocalProperties.set(simultaneousProp, `simultaneousPoints`)
        show()
alias('configureScanPipeline')

print("-"*100);
print "i09-shared script complete.";
print(""*100)
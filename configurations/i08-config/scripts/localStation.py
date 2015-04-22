from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
from gda.factory import Finder
from gdascripts.messages import handle_messages
from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableBase, CoupledScannable
from gda.device.monitor import EpicsMonitor
from gdascripts.parameters.beamline_parameters import JythonNameSpaceMapping
#from gdascripts.scannable.beamokay import WaitWhileScannableBelowThreshold, WaitForScannableState

print "Initialisation Started";


from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names, vararg_alias

def ls_scannables():
    ls_names(Scannable)


from ScannableInvertedValue import PositionInvertedValue
photoDiode1Inverted = PositionInvertedValue("photoDiode1Inverted","photoDiode1")

#from epics_scripts.pv_scannable_utils import createPVScannable, caput, caget
#alias("createPVScannable")
#alias("caput")
#alias("caget")

#from gda.scan.RepeatScan import create_repscan, repscan
#vararg_alias("repscan")

from gdascripts.metadata.metadata_commands import setTitle, meta_add, meta_ll, meta_ls, meta_rm
alias("setTitle")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")

from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()

from gdascripts.pd.time_pds import waittimeClass, showtimeClass, showincrementaltimeClass, actualTimeClass
waittime=waittimeClass('waittime')
showtime=showtimeClass('showtime')
inctime=showincrementaltimeClass('inctime')
actualTime=actualTimeClass("actualTime")

# Use for the calibration of the pgm energy, create a scannable idEnergy
from idEnergy import my_energy_class1


#checkrc = WaitWhileScannableBelowThreshold('checkrc', rc, 190, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=5) #@UndefinedVariable
#checkfe = WaitForScannableState('checkfe', frontend, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=60) #@UndefinedVariable
#checkshtr1 = WaitForScannableState('checkshtr1', shtr1, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=60) #@UndefinedVariable
#checkbeam = ScannableGroup('checkbeam', [checkrc,  checkfe, checkshtr1])
#checkbeam.configure()

#if (LocalProperties.get("gda.mode") == 'live'): 
#    beamMonitor.configure()
#    add_default beamMonitor
#    add_default topupMonitor 
   

# set up the Andor Area Detector ROIs etc for hardware-driven mapping
#run "AndorConfiguration"
# create the command to run STXM mpas which involve andor

run "andormap"
run "xrfmap"

#
print "Initialisation Complete";

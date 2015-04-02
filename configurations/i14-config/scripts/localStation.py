from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
from gda.factory import Finder
from gdascripts.messages import handle_messages
from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableBase
from gda.device.monitor import EpicsMonitor
from gdascripts.parameters.beamline_parameters import JythonNameSpaceMapping
#from gdascripts.scannable.beamokay import WaitWhileScannableBelowThreshold, WaitForScannableState

print "Initialisation Started";


from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names, vararg_alias

def ls_scannables():
    ls_names(Scannable)
    
#from gda.scan.RepeatScan import create_repscan, repscan
#vararg_alias("repscan")

from gdascripts.metadata.metadata_commands import setTitle, meta_add, meta_ll, meta_ls, meta_rm
alias("setTitle")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")
from gda.data.scan.datawriter import NexusDataWriter
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop")

from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()

from gdascripts.pd.time_pds import waittimeClass, showtimeClass, showincrementaltimeClass, actualTimeClass
waittime=waittimeClass('waittime')
showtime=showtimeClass('showtime')
inctime=showincrementaltimeClass('inctime')
actualTime=actualTimeClass("actualTime")

print "Initialisation Complete";

from java.io import FileNotFoundException
from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
from gda.factory import Finder
from gdascripts.messages import handle_messages
from gda.jython import InterfaceProvider
from gda.jython.commands.GeneralCommands import alias, cmd, ls, pause, reset_namespace, run, vararg_regex
from gda.device.scannable import ScannableBase
from gda.device.monitor import EpicsMonitor
from gdascripts.parameters.beamline_parameters import JythonNameSpaceMapping
from gdascripts.scan import gdascans

from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names, alias
from mapping_scan_commands import * 

from shutter_control import toggle_oh1_shtr, toggle_oh2_shtr, toggle_oh3_shtr, toggle_eh2_nano_shtr

from i14_utilities import isLive

# DCM control
#from beamline.dcm_enrg import *
from beamline.EpicsScannable import *
from harmonics.offset_harmonic import *

print "Initialisation Started";

run('setup_motors.py')

def ls_scannables():
    ls_names(Scannable)

rscan=gdascans.Rscan()
alias('rscan');print rscan.__doc__.split('\n')[2]

from gdascripts.metadata.metadata_commands import setTitle, meta_add, meta_ll, meta_ls, meta_rm
alias("setTitle")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")

from gda.data.scan.datawriter import NexusDataWriter
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop")

from gdascripts.pd.time_pds import waittimeClass, showtimeClass, showincrementaltimeClass, actualTimeClass
waittime=waittimeClass('waittime')
showtime=showtimeClass('showtime')
inctime=showincrementaltimeClass('inctime')
actualTime=actualTimeClass("actualTime")

from gdascripts.watchdogs.watchdogs import enableWatchdogs, disableWatchdogs, listWatchdogs
alias("enableWatchdogs")
alias("disableWatchdogs")
alias("listWatchdogs")

# For compatibility with previous versions
ringCurrentMonitor = ring_current

if isLive():
    print "Running in live mode: attempting to run localStationUser.py in users script directory"
    try:
        run("localStationUser.py")
    except FileNotFoundException, e:
        print "No localStationUser run"
    except:
        print "Exception running localStationUser"
else:
    print "Running in dummy mode"
    from beamline.dcm_enrg import DCMpdq
    dcm_enrg = DCMpdq("dcm_enrg", dcm_bragg, dcm_perp, id_gap, m1_mirror_stripe, m2_mirror_stripe, ringCurrentMonitor)

# Export dcm_enrg over RMI
print "Exporting dcm_enrg"
from uk.ac.gda.remoting.server import GdaRmiServiceExporter
dcm_enrg_exporter = GdaRmiServiceExporter()
dcm_enrg_exporter.serviceName = "gda/dcm_enrg"
dcm_enrg_exporter.service = dcm_enrg
dcm_enrg_exporter.serviceInterface = Scannable
dcm_enrg_exporter.afterPropertiesSet()

# Initialise the array plugin for all detectors
from prepare_for_snapshot import prepare_detectors
prepare_detectors()

# Define functions to change interferometer/stage offsets
run('ifs_functions.py')

print "Initialisation Complete";

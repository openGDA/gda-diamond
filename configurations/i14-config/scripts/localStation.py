from java.io import FileNotFoundException
from gdaserver import dcm_bragg, dcm_perp, id_gap, m1_mirror_stripe, m2_mirror_stripe, ring_current, sample_dtab_addetector
from gda.configuration.properties import LocalProperties
from gda.jython.commands.GeneralCommands import alias, cmd, ls, ls_names, pause, reset_namespace, run
from gdascripts.scan import gdascans

from gda.device import Scannable, ScannableMotionUnits
from mapping_scan_commands import *

from i14_utilities import isLive

print("Initialisation Started")

def ls_scannables():
    ls_names(Scannable)

rscan = gdascans.Rscan()
alias('rscan')
print(rscan.__doc__.split('\n')[2])

from gdascripts.metadata.metadata_commands import setTitle, meta_add, meta_ll, meta_ls, meta_rm
alias("setTitle")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")

from gda.data.scan.datawriter import NexusDataWriter
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME, "metashop")

from gdascripts.pd.time_pds import waittimeClass, showtimeClass, showincrementaltimeClass, actualTimeClass
waittime = waittimeClass('waittime')
showtime = showtimeClass('showtime')
inctime = showincrementaltimeClass('inctime')
actualTime = actualTimeClass("actualTime")

from gdascripts.watchdogs.watchdogs import enableWatchdogs, disableWatchdogs, listWatchdogs
from gdascripts.watchdogs.watchdogs import enable_watchdogs, disable_watchdogs, list_watchdogs, set_watchdog_enabled, is_watchdog_enabled
alias("enableWatchdogs")
alias("disableWatchdogs")
alias("listWatchdogs")

# For compatibility with previous versions
ringCurrentMonitor = ring_current

if isLive():
    print("Running in live mode: attempting to run localStationUser.py in users script directory")
    try:
        run("localStationUser.py")
    except FileNotFoundException, e:
        print("No localStationUser run")
    except:
        print("Exception running localStationUser")
else:
    print("Running in dummy mode")
    from dummy.dummy_beam_monitor import DummyBeamMonitor
    from Beamline.MotionsAndDetectors.dcm_enrg import DCMpdq
    dcm_enrg = DCMpdq("dcm_enrg", DummyBeamMonitor(), dcm_bragg, dcm_perp, id_gap, m1_mirror_stripe, m2_mirror_stripe, ring_current)
    run("dummy/xanes_scan.py")
    run("dummy/cross_hairs.py")
    run("dummy/standards_scan.py")
    run("dummy/tomo_scan.py")
    run("dummy/ptychography_scan.py")
    run("dummy/gui_automation.py")

# Export dcm_enrg over RMI
print("Exporting dcm_enrg")
from uk.ac.gda.remoting.server import GdaRmiServiceExporter
dcm_enrg_exporter = GdaRmiServiceExporter()
dcm_enrg_exporter.serviceName = "gda/dcm_enrg"
dcm_enrg_exporter.service = dcm_enrg
dcm_enrg_exporter.serviceInterface = ScannableMotionUnits
dcm_enrg_exporter.afterPropertiesSet()

# Initialise the array plugin for all detectors
from initialise_detectors import initialise_detectors
initialise_detectors()

# Define functions to change interferometer/stage offsets
run('ifs_functions.py')

# Define functions to control shutters
run('shutter_control.py')

# Define autofocus function
run('autofocus/autofocus.py')

# Define tomography scan functions
run('scanning/tomo_scan_functions.py')

# Make DTAB overlay available
dtab_overlay = sample_dtab_addetector.getNdOverlays().get(0)

print("Initialisation Complete")

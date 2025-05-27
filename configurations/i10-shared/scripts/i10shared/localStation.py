from gda.device.scannable import DummyScannable
import installation
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import alias
from org.slf4j import LoggerFactory

print("*"*80)
print("Running the I10 startup script localStation.py...")
print("\n")
logger = LoggerFactory.getLogger(__name__)

print("-"*100)
print("Set scan returns to the original positions on completion to false (0); default is 0.")
print("   To set scan returns to its start positions on completion please do:")
print("      >>>scansReturnToOriginalPositions=1")
scansReturnToOriginalPositions = 0;
print("\n")
###Import common commands, utilities, etc#####
from i10commands.dirFileCommands import pwd, lwf, nwf, nfn, setSubdirectory, getSubdirectory  # @UnusedImport

print("\n")
from plottings.configScanPlot import setYFieldVisibleInScanPlot, getYFieldVisibleInScanPlot, setXFieldInScanPlot, useSeparateYAxes, useSingleYAxis  # @UnusedImport
alias("useSeparateYAxes")
alias("useSingleYAxis")
print("\n")


def interruptable():
    GeneralCommands.pause()


alias("interruptable")

print("\n")
print("-"*100)
print("load EPICS Pseudo Device utilities for creating scannable object from a PV name.")
from gdascripts.pd.epics_pds import DisplayEpicsPVClass, EpicsReadWritePVClass, SingleEpicsPositionerClass, SingleEpicsPositionerNoStatusClass, SingleEpicsPositionerNoStatusClassDeadband, SingleChannelBimorphClass  # @UnusedImport
print("-"*100)
print("load time utilities objects.")
from gdascripts.pd.time_pds import showtime, inctime, waittime, tictoc, showtimeClass, showincrementaltimeClass, waittimeClass2  # @UnusedImport
wait = waittime
showtime.setLevel(4)  # so it is operated before anything else in a scan
print("-"*100)
print("Load utilities: caget(pv), caput(pv,value), caput_string2waveform(pvstring, value), caput_wait(pvstring, value, timeout=10), cagetArray(pvstring)")
print("    iterableprint(iterable), listprint(list), frange(start,end,step), attributes(object), default_scannables(*scn), jobs()")
from gdascripts.utils import attributes, frange, listprint, iterableprint, caget, caput, cagetArray, caput_wait, caput_string2waveform, default_scannables, jobs  # @UnusedImport
print("-"*100)
print("load common physical constants")
from gdascripts.constants import pi, eV, hPlanck, hbar, hPlanckeV, hbareV, clight, m_e, r_e, amu  # @UnusedImport
print("-"*100)
print("Adding timer devices t, dt, and w, clock")
from gdascripts.scannable.timerelated import timerelated, t, dt, w, clock, epoch  # @UnusedImport
print("-"*100)
print("load nexus metadata commands")
from gdascripts.metadata.nexus_metadata_class import meta  # @UnusedImport
print("\n")

ds = DummyScannable("ds")
# Create snap command for capturing a snapshot of camera
from i10commands.snapshot import dummy, snap  # @UnusedImport
# commands for data file format control
from i10commands.switchDataWriter import asciiformat, nexusformat, whichformat  # @UnusedImport
from pgm.grating import grating  # @UnusedImport

from scannables.haxpod.m1_haxpod_motors import m1fpitch  # @UnusedImport
from scannables.haxpod.m3m5_haxpod_motors import m3m5fpitch  # @UnusedImport
from scannables.frontEndBeamMonitors import xbpm, xbpm1_x, xbpm1_y, xbpm2_x, xbpm2_y, xbpm_anglex, xbpm_anglex_urad, xbpm_angley, xbpm_angley_urad  # @UnusedImport
if installation.isLive():
    from scannables.haxpod.m1_haxpod_motors import m1_x, m1_y, m1_z, m1_yaw, m1_pitch, m1_roll, M1  # @UnusedImport
    from scannables.haxpod.m3m5_haxpod_motors import m3m5_x, m3m5_y, m3m5_z, m3m5_yaw, m3m5_pitch, m3m5_roll, M3M5  # @UnusedImport

# objects available for all 3 end-stations
from scannables.continuous.energy_move_controller import energy_controller  # @UnusedImport
from scannables.continuous.continuous_energy_scannables_diagnose import energyd, mcsd16, mcsd17, mcsd18, mcsd19, mcsd20, mcsd21, mcsd22, mcsd23  # @UnusedImport

# check beam scannables
from scannables.checkbeanscannables import checkrc, checktopup_time, checkfe, checkbeam, checkbeamcv, checkfe_cv, checkrc_cv, checktopup_time_cv, checkbeam4scan, checkbeam4cvscan  # @UnusedImport
print("-"*100)
# multiple images per scan data point scan
from gdascripts.scan.miscan import miscan; print(miscan.__doc__)  # @UndefinedVariable
print("-"*100)
from scan.flyscan_command import flyscannable, FlyScanPositionsProvider, flyscan, flyscancn  # @UnusedImport
from  scan import flyscan_command; print(flyscan_command.__doc__)  # @UndefinedVariable
print("-"*100)
from scan.cvscan import cvscan  # @UnusedImport
alias('cvscan')

from scan.MultiRegionScan import mrscan, ALWAYS_COLLECT_AT_STOP_POINT, NUMBER_OF_DECIMAL_PLACES  # @UnusedImport

# import post scan data processor and go function and scan commands
from gdascripts.scan.installStandardScansWithProcessing import scan_processor, go, ascan, a2scan, a3scan, mesh, dscan, d2scan, d3scan, scan, rscan, cscan  # @UnusedImport
from data_process.scanDataProcess import scan_processing_off, scan_processing_on  # @UnusedImport

# source, energy, polarisation, linear arbitrary angle definitions
from calibrations.mode_polarisation_energy_instances import smode, pol, energy_s, energy_pol, laa, setBeamHarmonicsOrder, initialisation  # @UnusedImport
from calibrations.energy_Offset import energy_offset  # @UnusedImport
from calibrations.energy_polarisation_class import ROW_PHASE_MOTOR_TOLERANCE  # @UnusedImport
from calibrations.xraysource import X_RAY_SOURCE_MODES
from calibrations.energy_polarisation_class import X_RAY_POLARISATIONS
idd, idu, unknown = X_RAY_SOURCE_MODES
pc, nc, lh, lv, la, lh3, unknown = X_RAY_POLARISATIONS
initialisation()

# ID metadata scannables
from scannables.stokesParameters import StokesParameters
stokes_parameters = StokesParameters("stokes_parameters", pol, laa)
from scannables.idcontrols.gapScannable import GapScannable
from gdaserver import idd_gap, idu_gap# @UnresolvedImport
gap = GapScannable("gap", smode, idd_gap, idu_gap, "mm", "%.3f")  # @UndefinedVariable
from scannables.idcontrols.taperScannable import TaperScannable
taper = TaperScannable("taper", smode, "urad", "%.3f", iddtaper = None, idutaper = None)
from scannables.idcontrols.harmonicScannable import HarmonicScannable
harmonic = HarmonicScannable("harmonic", pol)
from scannables.sampleScannable import SampleName
sample = SampleName("sample", sample_name = "name not given")

print("-"*100)
print("Import 'XASMode' class, and 'xasscan' command for X-ray Absorption Spectroscopy experiments ")
from gdascripts.scannable.XAS_Mode import XASMode, XASModePathMapper  # @UnusedImport
from gdascripts.scan.XASScan import xasscan  # @UnusedImport
from gdascripts.functions.nexusYamlTemplateProcessor import apply_template_to_nexus_file, set_nexus_tamplate  # @UnusedImport

from keithley.keithley2400_scannables_instances import keiCur1, keiVol1  # @UnusedImport

# Please leave Panic stop customisation last - specify scannables to be excluded from Panic stop
from i10commands.stopJythonScannables import stopJythonScannablesExceptExcluded  # @UnusedImport
STOP_ALL_EXCLUSIONS = []  # @UndefinedVariable

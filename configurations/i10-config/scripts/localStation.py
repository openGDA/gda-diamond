from utils.ExceptionLogs import localStation_exceptions, localStation_exception
from Diamond.Poly import Poly
from gda.device.scannable import DummyScannable
from gdascripts.messages.handle_messages import simpleLog
    
import installation
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import alias

print("*"*80)
print("Running the I10 startup script localStation.py...")
print()

global RASOR_SCALER, UI1, UJ1

print("-"*100)
print("Set scan returns to the original positions on completion to false (0); default is 0.")
print("   To set scan returns to its start positions on completion please do:")
print("      >>>scansReturnToOriginalPositions=1")
scansReturnToOriginalPositions=0;
print()
###Import common commands, utilities, etc#####
from i10commands.dirFileCommands import pwd, lwf,nwf,nfn,setSubdirectory,getSubdirectory  # @UnusedImport

print()
from plottings.configScanPlot import setYFieldVisibleInScanPlot,getYFieldVisibleInScanPlot,setXFieldInScanPlot,useSeparateYAxes,useSingleYAxis  # @UnusedImport
alias("useSeparateYAxes")
alias("useSingleYAxis")
print()

def interruptable():
    GeneralCommands.pause()
alias("interruptable")

print()
print("-"*100)
print("load EPICS Pseudo Device utilities for creating scannable object from a PV name.")
from gdascripts.pd.epics_pds import DisplayEpicsPVClass,EpicsReadWritePVClass,SingleEpicsPositionerClass,SingleEpicsPositionerNoStatusClass,SingleEpicsPositionerNoStatusClassDeadband,SingleChannelBimorphClass  # @UnusedImport
print("-"*100)
print("load time utilities objects.")
from gdascripts.pd.time_pds import showtime,inctime,waittime,tictoc, showtimeClass, showincrementaltimeClass, waittimeClass2  # @UnusedImport
wait = waittime
showtime.setLevel(4) # so it is operated before anything else in a scan
print("-"*100)
print("Load utilities: caget(pv), caput(pv,value), caput_string2waveform(pvstring, value), caput_wait(pvstring, value, timeout=10), cagetArray(pvstring)")
print("    iterableprint(iterable), listprint(list), frange(start,end,step), attributes(object), default_scannables(*scn), jobs()")
from gdascripts.utils import attributes, frange, listprint, iterableprint,caget, caput, cagetArray, caput_wait, caput_string2waveform, default_scannables, jobs  # @UnusedImport
print("-"*100)
print("load common physical constants")
from gdascripts.constants import pi, eV, hPlanck, hbar,hPlanckeV,hbareV,clight,m_e,r_e,amu # @UnusedImport
print("-"*100)
print("Adding timer devices t, dt, and w, clock")
from gdascripts.scannable.timerelated import timerelated,t,dt,w,clock,epoch #@UnusedImport
print("-"*100)
print("load nexus metadata commands")
from gdascripts.metadata.nexus_metadata_commands import add_meta, add_meta_link, add_meta_pv, add_meta_scalar, add_meta_scannable, clear_meta, disable_meta, enable_meta, ll_meta, ls_meta, rm_meta   # @UnusedImport
print()

ds = DummyScannable("ds")
#Create snap command for capturing a snapshot of camera
from i10commands.snapshot import dummy, snap  # @UnusedImport
#commands for data file format control
from i10commands.switchDataWriter import asciiformat, nexusformat, whichformat  # @UnusedImport
from scannable.pgm.grating import grating  # @UnusedImport

from scannable.haxpod.m1_haxpod_motors import m1fpitch  # @UnusedImport
from scannable.haxpod.m3m5_haxpod_motors import m3m5fpitch  # @UnusedImport
from scannable.frontEndBeamMonitors import xbpm, xbpm1_x, xbpm1_y, xbpm2_x, xbpm2_y, xbpm_anglex, xbpm_anglex_urad, xbpm_angley, xbpm_angley_urad  # @UnusedImport
if installation.isLive():
    from scannable.haxpod.m1_haxpod_motors import m1_x, m1_y, m1_z, m1_yaw, m1_pitch, m1_roll, M1  # @UnusedImport
    from scannable.haxpod.m3m5_haxpod_motors import m3m5_x, m3m5_y, m3m5_z, m3m5_yaw, m3m5_pitch, m3m5_roll, M3M5  # @UnusedImport

########setting up the diagnostic cameras###############
from detectors.diagnostic_cameras import cameraFactory
cam1, peak2d1, max2d1 = cameraFactory('cam1', 'peak2d1', 'max2d1', d1camtiff, None)
cam2, peak2d2, max2d2 = cameraFactory('cam2', 'peak2d2', 'max2d2', d2camtiff, None)
cam3, peak2d3, max2d3 = cameraFactory('cam3', 'peak2d3', 'max2d3', d3camtiff, None)

from java.lang import System
spring_profiles = System.getProperty("gda.spring.profiles.active")

if "scattering" in spring_profiles:
    ###Save and reload positions of a given scannable group and/or a list of scannables
    from rasor.saveAndReload import SaveAndReload  # @UnusedImport
    print(SaveAndReload.__doc__)
    #RASOR Multilayer support
    from rasor.scannable.polarisation_analyser_example import ml, mss, pa  # @UnusedImport
    from scannable.haxpod.m4_haxpod_motors import m4fpitch  # @UnusedImport
    from scannable.rasor.theta2theta_offsets import tth_off,th_off  # @UnusedImport
    from amplifiers.femto_instances import rca1, rca2, rca3  # @UnusedImport
    if installation.isLive():
        from scannable.haxpod.m4_haxpod_motors import m4_x, m4_y, m4_z, m4_yaw, m4_pitch, m4_roll, M4  # @UnusedImport
        
    #PIMTE detectors customised to display image in 'Plot 1' view and return results of image process
    from detectors.pimteWithDataProcessor import pimteSMPV, pimte2d  # @UnusedImport
    
    #PIXIS detectors customised to display image in 'Plot 1' view and return results of image process
    from detectors.pixisWithDataProcessor import pixisSMPV, pixis2d  # @UnusedImport
        
    cam4, peak2d4, max2d4 = cameraFactory('cam4', 'peak2d4', 'max2d4', d4camtiff, None)
    cam6, peak2d6, max2d6 = cameraFactory('cam6', 'peak2d6', 'max2d6', d6camtiff, None)
 
    from scannable.continuous.continuous_energy_scannables_scattering import energy, energy_controller, mcs16,mcs17,mcs18,mcs19,mcs20,mcs21,mcs22,mcs23 # @UnusedImport
    from rasor.scannable.ThArea import thArea  # @UnusedImport
    from rasor.scannable.TthArea import tthArea  # @UnusedImport
    print()
    print("*"*80)
    #DiffCalc
    print("import DIFFCALC support for I10")
    try:
        from startup.i10 import *  # @UnusedWildImport
    except:
        localStation_exception(sys.exc_info(), "import diffcalc error.")

    ##Position Wrapper
    print("-"*100)
    print("Creating 'wa' command for returning RASOR motor positions")
    wascannables = [tth, th, chi, dsu, dsd, eta, ttp, thp, py, pz, alpha_rasor, difx, lgf, lgb, lgm, sx, sy, sz]  # @UndefinedVariable
    from rasor.positionWrapper import PositionWrapper
    try:
        wa=PositionWrapper(wascannables)
    except:
        localStation_exception(sys.exc_info(), "create wa error.")
    
    alias('wa')
    
    print "Creating 'wh' command for return RASOR positions in DIFFCALC HKL"
    wherescannables=[tth,th,chi,phi,h,k,l,en]  # @UndefinedVariable
    try:
        wh=PositionWrapper(wherescannables) ##can only be used with diffcalc
    except:
        localStation_exception(sys.exc_info(), "create wh error.")
    
    alias('wh')
    
    from scannable.rocking.detectorWithRockingMotion import NXDetectorWithRockingMotion  # @UnusedImport
    from gdaserver import pimte, pixis  # @UnresolvedImport
    thpimte=NXDetectorWithRockingMotion("thpimte", th, pimte)  # @UndefinedVariable
    thpixis=NXDetectorWithRockingMotion("thpixis", th, pixis)  # @UndefinedVariable
    
if "absorption" in spring_profiles:
    from scannable.haxpod.m6_haxpod_motors import m6fpitch  # @UnusedImport
    from amplifiers.femto_instances import ca1je, ca2je, ca3je  # @UnusedImport
    if installation.isLive():
        from scannable.haxpod.m6_haxpod_motors import m6_x, m6_y, m6_z, m6_yaw, m6_pitch, m6_roll, M6  # @UnusedImport

    camj1, peak2dj1, max2dj1 = cameraFactory('camj1', 'peak2dj1', 'max2dj1', dj1camtiff, None)  # @UndefinedVariable
    camj3, peak2dj3, max2dj3 = cameraFactory('camj3', 'peak2dj3', 'max2dj3', dj3camtiff, None)  # @UndefinedVariable
    from scannable.continuous.continuous_energy_scannables_absorption import energy_controller, energye, mcse16, mcse17,mcse18,mcse19,mcse20,mcse21,mcse22,mcse23 # @UnusedImport

if "hfm" in spring_profiles:
    #High Field Magnet support
    from high_field_magnet.scannable.intelligent_power_supply_instances import ips_field, ips_sweeprate, itc2, hfmpitch_off  # @UnusedImport
    if installation.isLive():
        try:
            from Diamond.PseudoDevices.EpicsDevices import EpicsDeviceClass
            gflow2=EpicsDeviceClass(name='gflow2', pvSet="BL10J-EA-TCTRL-02:GFLOW:SET", pvGet="BL10J-EA-TCTRL-02:GFLOW", pvStatus=None, strUnit="", strFormat="%.2f", timeout=None)
        except:
            localStation_exception(sys.exc_info(), "creating gflow2 scannable")
    
if "em" in spring_profiles:
    from scannable.positions.magnet_instances import magnetCurrent, magnetField  # @UnusedImport
    
# check beam scannables
from scannable.checkbeanscannables import checkrc, checktopup_time, checkfe, checkbeam, checkbeamcv, checkfe_cv, checkrc_cv, checktopup_time_cv, checkbeam4scan, checkbeam4cvscan # @UnusedImport
print("-"*100)
# multiple images per scan data point scan
from scan.miscan import miscan; print(miscan.__doc__)  # @UndefinedVariable
print("-"*100)
from scan.flyscan_command import flyscannable, FlyScanPositionsProvider, flyscan  # @UnusedImport
from  scan import flyscan_command; print(flyscan_command.__doc__)  # @UndefinedVariable
print("-"*100)
from scan.cvscan import cvscan  # @UnusedImport
alias('cvscan')

#import post scan data process The following 5 lines must be in localStation.py 
from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
import gdascripts
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()
from data_process.scanDataProcess import *  # @UnusedWildImport

# source, energy, polarisation definitions
from calibrations.mode_polarisation_energy_instances import smode, pol, energy_s, energy_pol, setBeamHarmonicsOrder, initialisation  # @UnusedImport
from calibrations.energy_polarisation_class import ROW_PHASE_MOTOR_TOLERANCE  # @UnusedImport
from calibrations.xraysource import X_RAY_SOURCE_MODES
from calibrations.energy_polarisation_class import X_RAY_POLARISATIONS
idd,idu,unknown = X_RAY_SOURCE_MODES
pc,nc,lh,lv,la,lh3,unknown = X_RAY_POLARISATIONS
initialisation()
from calibrations.linearArbitraryAngle import LinearArbitraryAngle
laa = LinearArbitraryAngle("laa", idu_jawphase, idd_jawphase, smode, pol, jawphase_from_angle=Poly([-120./7.5, 1./7.5], power0first=True), angle_threshold_deg = 30.0)  # @UndefinedVariable

#ID metadata scannables
from scannable.stokesParameters import StokesParameters
stokes_parameters = StokesParameters("stokes_parameters", pol, laa)
from scannable.idcontrols.gapScannable import GapScannable
gap = GapScannable("gap", smode, idd_gap, idu_gap, "mm", "%.3f")  # @UndefinedVariable
from scannable.idcontrols.taperScannable import TaperScannable
taper = TaperScannable("taper", smode, "urad", "%.3f", iddtaper=None, idutaper=None)
from scannable.idcontrols.harmonicScannable import HarmonicScannable
harmonic = HarmonicScannable("harmonic", pol)

#Please leave Panic stop customisation last - specify scannables to be excluded from Panic stop
from i10commands.stopJythonScannables import stopJythonScannablesExceptExcluded  # @UnusedImport
STOP_ALL_EXCLUSIONS=[]  # @UndefinedVariable

if len(localStation_exceptions) > 0:
    simpleLog("=============== %r ERRORS DURING STARTUP ================" % len(localStation_exceptions))

for localStationException in localStation_exceptions:
    simpleLog(localStationException)

print("**************************************************")
print("localStation.py completed.")
print("**************************************************")

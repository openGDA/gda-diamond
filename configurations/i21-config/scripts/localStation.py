import sys
import installation

from gdascripts.messages.handle_messages import simpleLog
from gdascripts.degas.degas import Degas  # @UnusedImport
from gda.jython.commands.GeneralCommands import alias
from calibration.Energy_class import BeamEnergy
from gda.jython.commands import GeneralCommands
from gdaserver import lakeshore, b2, x, sgmpitch, polarisergamma, polariserstick, fastshutter  # @UnusedImport @UnresolvedImport
import gdascripts
from utils.ExceptionLogs import localStation_exception, localStation_exceptions
from gda.device.scannable import DummyScannable

simpleLog("================ INITIALISING I21 GDA ================")
print("-"*100)
print("Set scan returns to the original positions on completion to false (0); default is 0.")
print("   To set scan returns to its start positions on completion please do:")
print("      >>>scansReturnToOriginalPositions=1")
#turn off return to the original position before scan off, to turn it on set it to 1
scansReturnToOriginalPositions=0;

# set up a nice method for getting the latest file path
from i21commands.dirFileCommands import pwd, lwf, nwf, nfn, setSubdirectory, getSubdirectory  # @UnusedImport
alias("pwd")
alias("lwf")
alias("nwf")
alias("nfn")
from plottings.configScanPlot import setYFieldVisibleInScanPlot,getYFieldVisibleInScanPlot,setXFieldInScanPlot,useSeparateYAxes,useSingleYAxis  # @UnusedImport
alias("useSeparateYAxes")
alias("useSingleYAxis")
def interruptable():
    GeneralCommands.pause()
alias("interruptable")
print("-"*100)
print("load EPICS Pseudo Device utilities for creating scannable object from a PV name.")
from gdascripts.pd.epics_pds import EpicsReadWritePVClass, DisplayEpicsPVClass, SingleEpicsPositionerClass, SingleEpicsPositionerNoStatusClass, SingleEpicsPositionerNoStatusClassDeadband  # @UnusedImport
from gdascripts.pd.dummy_pds import DummyDisplayEpicsPVClass, DummyEpicsReadWritePVClass  # @UnusedImport
print("-"*100)
print("load time utilities for creating timer objects.")
from gdascripts.pd.time_pds import showtime,inctime,waittime,tictoc,showtimeClass,showincrementaltimeClass,waittimeClass2  # @UnusedImport
print("-"*100)
print("Load utilities: printJythonEnvironment(), caget(pv), caput(pv,value), attributes(object), ")
print("    iterableprint(iterable), listprint(list), frange(start,end,step)")
from gdascripts.utils import frange,listprint,iterableprint,attributes,caget, caput, cagetArray, caput_wait,caput_string2waveform,default_scannables,jobs  # @UnusedImport
print("-"*100)
print("load common physical constants")
from gdascripts.constants import pi,eV,hPlanck,hbar,hPlanckeV,hbareV, clight,m_e,r_e,aum,me  # @UnusedImport
print("-"*100)
print("Adding timer devices t, dt, and w, clock")
from gdascripts.scannable.timerelated import timerelated, t,dt,clock,epoch #@UnusedImport
print("-"*100)
print("Adding timer devices t, dt, and w, clock")
print("-"*100)
print("load nexus metadata commands")
from gdascripts.metadata.nexus_metadata_class import meta   # @UnusedImport

ds=DummyScannable("ds")
ds1=DummyScannable("ds1")

if installation.isLive():
    print("Running in live mode")
    print("create camera total count scannables: d1camtotal, d2camtotal, d3acamtotal, d4camtotal, smpcam1total,smpcam2total,smpcam3total, smpcam4total")
    try:
        d1camtotal=DisplayEpicsPVClass('d1camtotal', 'BL21I-DI-DCAM-01:STAT:Total_RBV', 'counts', '%10d')
        d2camtotal=DisplayEpicsPVClass('d2camtotal', 'BL21I-DI-DCAM-02:STAT:Total_RBV', 'counts', '%10d')
        d3acamtotal=DisplayEpicsPVClass('d3acamtotal', 'BL21I-DI-DCAM-03:STAT:Total_RBV', 'counts', '%10d')
        d4camtotal=DisplayEpicsPVClass('d4camtotal', 'BL21I-DI-DCAM-04:STAT:Total_RBV', 'counts', '%10d')
        d8camtotal=DisplayEpicsPVClass('d8camtotal', 'BL21I-DI-DCAM-24:STAT:Total_RBV', 'counts', '%10d')
        smpcam1total=DisplayEpicsPVClass('smpcam1total', 'BL21I-DI-DCAM-20:STAT1:Total_RBV', 'counts', '%10d')
        smpcam2total=DisplayEpicsPVClass('smpcam2total', 'BL21I-DI-DCAM-21:STAT1:Total_RBV', 'counts', '%10d')
        smpcam3total=DisplayEpicsPVClass('smpcam3total', 'BL21I-DI-DCAM-22:STAT1:Total_RBV', 'counts', '%10d')
        smpcam4total=DisplayEpicsPVClass('smpcam4total', 'BL21I-DI-DCAM-23:STAT1:Total_RBV', 'counts', '%10d')
        s5camtotal=DisplayEpicsPVClass('s5camtotal', 'BL21I-DI-DCAM-55:STAT:Total_RBV', 'counts', '%10d')
        andortotal=DisplayEpicsPVClass('andortotal', 'BL21I-EA-DET-01:STAT:Total_RBV', 'counts', '%10d')
    except:
        localStation_exception(sys.exc_info(), "Error creating scannables for camera total count.")
    try:
        m1fpsetpoint=DisplayEpicsPVClass('m1fpsetpoint', 'BL21I-OP-MIRR-01:FP:FB.CVAL', 'unitless', '%.10f')
        m2fpsetpoint=DisplayEpicsPVClass('m2fpsetpoint', 'BL21I-OP-MIRR-02:FP:FB.CVAL', 'px', '%.10f')
    except:
        localStation_exception(sys.exc_info(), "Error creating 'm1fpsetpoint' or 'm2fpsetpoint'.")

    from epics_scripts.pv_scannable_utils import createPVScannable

    try:
        pgmMirrorPitch_UserOffset = createPVScannable('pgmMirrorPitch_UserOffset', 'BL21I-OP-PGM-01:MIR:PITCH.OFF')
        pgmGratingPitch_UserOffset = createPVScannable('pgmGratingPitch_UserOffset', 'BL21I-OP-PGM-01:GRT:PITCH.OFF')
    except:
        localStation_exception(sys.exc_info(), "Error creating 'pgmMirrorPitch_UserOffset'  or 'pgmGratingPitch_UserOffset'.")

    from scannabledevices.feedbackScannable import FeedbackScannable, FeedbackOffScannable
    try:
        fbs=FeedbackScannable("fbs", pvroot="BL21I-OP-MIRR-01:FBCTRL")
        fboff=FeedbackOffScannable("fboff", pvroot="BL21I-OP-MIRR-01:FBCTRL")
    except:
        localStation_exception(sys.exc_info(), "Error creating 'fbs' or 'fboff'.")
        
else:
    print("Running in dummy mode")
    m1fpsetpoint=DummyDisplayEpicsPVClass('m1fpsetpoint', 0.0, 50.0, '', '%.10f')
    m2fpsetpoint=DummyDisplayEpicsPVClass('m2fpsetpoint', 0.0, 50.0, 'px', '%.10f')


from shutters.detectorShutterControl import erio, primary, polarimeter  # @UnusedImport
from lights.chamberLight import lightOff, lightOn  # @UnusedImport

print("create clever amplifier scannables: cleverd7femto1, cleverd7femto2")
from i21_utils import DisplayEpicsPVClass_neg, DisplayEpicsPVClass_pos
d7femto1_neg = DisplayEpicsPVClass_neg('d7femto1_neg', d7femto1)  # @UndefinedVariable
d7femto2_pos = DisplayEpicsPVClass_pos('d7femto2_pos', d7femto2)  # @UndefinedVariable

from scannabledevices.cleverAmplifier import CleverAmplifier
cleverd7femto1=CleverAmplifier("cleverd7femto1", d7femto1, 0.5, 9.0, "%.4f", "%.4e")  # @UndefinedVariable
cleverd7femto2=CleverAmplifier("cleverd7femto2", d7femto2, 0.5, 9.0, "%.4f", "%.4e")  # @UndefinedVariable
cleverm4femto1=CleverAmplifier("cleverm4femto1", m4femto1, 0.5, 9.0, "%.4f", "%.4e")  # @UndefinedVariable
cleverm4femto2=CleverAmplifier("cleverm4femto2", m4femto2, 0.5, 9.0, "%.4f", "%.4e")  # @UndefinedVariable
clevertdiff1=CleverAmplifier("clevertdiff1", diff1, 0.5, 9.0, "%.4f", "%.4e")  # @UndefinedVariable

print("-"*100)
print("Create an 'dummyenergy' scannable which can be used for test energy scan in GDA. It moves dummy motor 'ds' and 'ds1'")
dummyenergy=BeamEnergy("dummyenergy",idscannable, ds, ds1, pgmGratingSelect)  # @UndefinedVariable
print("Create an 'energy_s', 'polarisation', and 'energypolarisation' scannables")

from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]
from calibration.energy_polarisation_instances import energy_s, energypolarisation, polarisation  # @UnusedImport

from scannabledevices.coupledSampleStageMotion import CoupledSampleStageMotion
sapara=CoupledSampleStageMotion("sapara", x, y, th) # @UndefinedVariable
saperp=CoupledSampleStageMotion("saperp", x, y, th) # @UndefinedVariable

from feedbacks.warmup_instance import tsample  # @UnusedImport

def input_tsample():
    lakeshore.setInput(1)
    
def input_tshield():
    lakeshore.setInput(2)
    
def input_tcryostat():
    lakeshore.setInput(3)
    
alias("input_tsample")
alias("input_tshield")
alias("input_tcryostat")

from scannable.continuous.continuous_energy_scannables import energy, energy_move_controller, draincurrent_c,diff1_c,m4c1_c,fy2_c  # @UnusedImport
from scan.cvscan import cvscan  # @UnusedImport
from scan.miscan import miscan; print(miscan.__doc__)  # @UndefinedVariable
print("-"*100)
from scan.flyscan_command import flyscannable, FlyScanPositionsProvider, flyscan  # @UnusedImport
from  scan import flyscan_command; print(flyscan_command.__doc__)  # @UndefinedVariable
from scan.MultiRegionScan import mrscan, ALWAYS_COLLECT_AT_STOP_POINT, NUMBER_OF_DECIMAL_PLACES  # @UnusedImport

b2.setOutputFormat(["%7.4f"])
x.setOutputFormat(["%10.6f"])

#Mapping scan
#from mapping_scan_commands import *
from gdascripts.mscanHandler import *  # @UnusedWildImport

from scannabledevices.xrayBeamMonitor import XRayBeamMonitor
xbm=XRayBeamMonitor("xbm", xraywatchdog="XRayWatchdog")

from scannabledevices.samplePoistioner_instance import smp_positioner  # @UnusedImport

from acquisition.acquire_images import acquireImages, clearEncoderLoss, acquireRIXS, acquiredark  # @UnusedImport
from acquisition.acquireCarbonTapeImages import acquire_ctape_image, remove_ctape_image  # @UnusedImport
from acquisition.darkImageAcqusition import acquire_dark_image, remove_dark_image  # @UnusedImport
from acquisition.flatFieldAcqusition import acquire_flat_field, remove_flat_field  # @UnusedImport
    
from gdascripts.scan.installStandardScansWithProcessing import ascan,a2scan,a3scan,mesh,dscan,d2scan,d3scan,scan,rscan,cscan,scan_processor  # @UnusedImport
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()
scan_processor_normal_processes = scan_processor.processors
scan_processor_empty_processes  = []
goto = scan_processor.go
alias("goto")
 
def scan_processing_on():
    scan_processor.processors = scan_processor_normal_processes
 
def scan_processing_off():
    scan_processor.processors = scan_processor_empty_processes
 
print("Switch off scan processor by default !!!")    
print(" To manually switch on scan processor, run 'scan_processing_on()' function on Jython Terminal.")
print(" To manually switch off scan processor, run 'scan_processing_off()' function on Jython Terminal.")
scan_processing_off()

#check beam scannables
from scannabledevices.checkbeanscannables import checkbeam, checkrc, checkfe, checktopup_time  # @UnusedImport

# from scannabledevices.pausableScannable_instances import *  #@UnusedWildImport #this is reverted to before not monitor the scanner light

# GeneralCommands.run("/dls_sw/i21/software/gda/config/scripts/i21commands/checkedMotion.py")
from i21commands.checkedMotion import move, asynmove, SGMR1_TOLERANCE, SPECL_TOLERANCE  # @UnusedImport
# alias("move")
# alias("asynmove")
from functions.go_founctions import go, goLH, goLV, goCL, goCR  # @UnusedImport

print("create 'alltth' scannable")
from scannabledevices.M5GroupScannable import alltth

print("-"*100)
#DiffCalc
print("import DIFFCALC support for I21")
# Import toolpoint scannables into namespace
from scannabledevices.ToolpointMotion import tp, u, v, w, ps_chi, ps_phi, uvw  # @UnusedImport

try:
    from startup.i21 import *  # @UnusedWildImport
    #toolpoint_off()  # @UndefinedVariable
except:
    localStation_exception(sys.exc_info(), "import diffcalc error.")
    
from calibration.extraPVCoupledScannable import ScannableWithPVControl
pgm_energy = ScannableWithPVControl('pgm_energy', pgmEnergy, pvname="BL21I-OP-MIRR-01:FBCTRL:MODE",pvvaluebefore=0, pvvalueafter=4)  # @UndefinedVariable

#initialize Jython Scannable Wrappers must be done after the wrapped scannable become available
uvw_wrapper.connectScannable()  # @UndefinedVariable

#nexus metadata items
from scannabledevices.stokesParameters import StokesParameters
stokes_parameters = StokesParameters("stokes_parameters", polarisation)
from metadata.taperScannable import TaperScannable
taper = TaperScannable("taper", "urad", "%.3f", idtaper=None)
from metadata.harmonicScannable import HarmonicScannable
harmonic = HarmonicScannable("harmonic",polarisation)
from metadata.beamDivergence import BeamDivergence
beam_divergence_at_sample = BeamDivergence("beam_divergence_at_sample", pgmEnergy, pgmGratingSelect, lut="divergence_polynomial_at_sample.csv")  # @UndefinedVariable
from metadata.beamFlux import BeamFlux
beam_flux_at_sample = BeamFlux("beam_flux_at_sample", pgmEnergy, pgmGratingSelect, lut="flux_polynomial_at_sample.csv")  # @UndefinedVariable
from metadata.beamExtent import BeamExtent
beam_size_at_sample =  BeamExtent("beam_size_at_sample", horizontal_size = 40.0, vertical_size = 2.5)

#Please leave Panic stop customisation last - specify scannables to be excluded from Panic stop
from i21commands.stopJythonScannables import stopJythonScannablesExceptExcluded  # @UnusedImport
STOP_ALL_EXCLUSIONS=[s5cam]  # @UndefinedVariable

if len(localStation_exceptions) > 0:
    simpleLog("=============== %r ERRORS DURING STARTUP ================" % len(localStation_exceptions))

for localStationException in localStation_exceptions:
    simpleLog(localStationException)

simpleLog("===================== GDA ONLINE =====================")

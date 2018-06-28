from utils.ExceptionLogs import localStation_exceptions
from gdaserver import alpha_rasor, chi, difx, dsd, dsu, eta,\
    lgb, lgf, lgm, th, tth, sx, sy, sz
import installation
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import alias

print "**************************************************"
print "Running the I10 startup script localStation.py..."
print ""

global RASOR_SCALER, UI1, UJ1
from gdascripts.messages.handle_messages import simpleLog

print "-"*100
print "Set scan returns to the original positions on completion to false (0); default is 0."
print "   To set scan returns to its start positions on completion please do:"
print "      >>>scansReturnToOriginalPositions=1"
scansReturnToOriginalPositions=0;
print
###Import common commands, utilities, etc#####
from i10commands.dirFileCommands import pwd, lwf,nwf,nfn,setSubdirectory,getSubdirectory  # @UnusedImport

print
from plottings.configScanPlot import setYFieldVisibleInScanPlot,getYFieldVisibleInScanPlot,setXFieldInScanPlot,useSeparateYAxes,useSingleYAxis  # @UnusedImport
alias("useSeparateYAxes")
alias("useSingleYAxis")
print

def interruptable():
    GeneralCommands.pause()
alias("interruptable")

print
print "-"*100
print "load EPICS Pseudo Device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import DisplayEpicsPVClass,EpicsReadWritePVClass,SingleEpicsPositionerClass,SingleEpicsPositionerNoStatusClass,SingleEpicsPositionerNoStatusClassDeadband,SingleChannelBimorphClass  # @UnusedImport
print "-"*100
print "load time utilities objects."
from gdascripts.pd.time_pds import showtime,inctime,waittime,tictoc, showtimeClass, showincrementaltimeClass, waittimeClass2  # @UnusedImport
wait = waittime
showtime.setLevel(4) # so it is operated before anything else in a scan
print "-"*100
print "Load utilities: printJythonEnvironment(), caget(pv), caput(pv,value), attributes(object), "
print "    iterableprint(iterable), listprint(list), frange(start,end,step)"
from gdascripts.utils import * #@UnusedWildImport
print "-"*100
print "load common physical constants"
from gdascripts.constants import * #@UnusedWildImport
print "-"*100
print "Adding timer devices t, dt, and w, clock"
from gdascripts.scannable.timerelated import timerelated,t,dt,w,clock,epoch #@UnusedImport

###Save and reload positions of a given scannable group and/or a list of scannables
from rasor.saveAndReload import SaveAndReload  # @UnusedImport
print SaveAndReload.__doc__

#Create snap command for capturing a snapshot of camera
from i10commands.snapshot import *  # @UnusedWildImport
#commands for data file format control
from i10commands.switchDataWriter import asciiformat, nexusformat, whichformat  # @UnusedImport

#RASOR Multilayer support
from rasor.scannable.polarisation_analyser_example import *  # @UnusedWildImport

if installation.isLive():
    #High Field Magnet support
    from high_field_magnet.scannable.intelligent_power_supply_instances import *  # @UnusedWildImport
#     from scannable.temporaryIDControls import *  # @UnusedWildImport
    from scannable.frontEndBeamMonitors import *  # @UnusedWildImport
    from scannable.mirrors_fine_pitch_motors import *  # @UnusedWildImport
    try:
        th_off = EpicsReadWritePVClass('th_off', 'ME01D-MO-DIFF-01:THETA.OFF', 'deg', '%.6f')
        tth_off = EpicsReadWritePVClass('tth_off', 'ME01D-MO-DIFF-01:TWOTHETA.OFF', 'deg', '%.6f')
    except:
        localStation_exception(sys.exc_info(), "creating th & tth offset and encoder offset scannables")
    try:
        print "Fixing extra names on RASOR mac scannables"
        for scn in RASOR_SCALER.getGroupMembers():
            scn.setInputNames([scn.name])
    
        print "Fixing extra names on UI1 mac scannables"
        for scn in UI1.getGroupMembers():
            scn.setInputNames([scn.name])
    
        print "Fixing extra names on UJ1 mac scannables"
        for scn in UJ1.getGroupMembers():
            scn.setInputNames([scn.name])
        
        print "Fixed extra names on all mac scannables"
    except:
        localStation_exception(sys.exc_info(), "fixing extra names on mac scannables")

    try:
        from Diamond.PseudoDevices.EpicsDevices import EpicsDeviceClass
        gflow2=EpicsDeviceClass(name='gflow2', pvSet="BL10J-EA-TCTRL-02:GFLOW:SET", pvGet="BL10J-EA-TCTRL-02:GFLOW", pvStatus=None, strUnit="", strFormat="%.2f", timeout=None)
    except:
        localStation_exception(sys.exc_info(), "creating gflow2 scannable")
else:
    global m1fpitch
        
######## Setting up the Andor Rasor camera ###############
andor_installed = False
if andor_installed:
    pass #there is no andor bean in I10 in GDA 8.50

######## Setting up the I10 Pimte camera ###############
pimte_installed = True
if pimte_installed:
    #PIMTE detectors customised to display image in 'Plot 1' view and return results of image process
    from detectors.pimteWithDataProcessor import pimteSMPV, pimte2d  # @UnusedImport

######## Setting up the I10 Pixis camera ###############
pixis_installed = True
if pixis_installed:
    #PIXIS detectors customised to display image in 'Plot 1' view and return results of image process
    from detectors.pixisWithDataProcessor import pixisSMPV, pixis2d  # @UnusedImport
    
######## Setting up the semi-automatic Zebra triggered cameras ###############
zebra_triggered_pimte_detector_installed = False
if zebra_triggered_pimte_detector_installed:
    from detectors.pimte_zebra_triggered import pimtez  # @UnusedImport

zebra_triggered_pco_detector_installed = True
if zebra_triggered_pco_detector_installed:
    from detectors.pco_zebra_triggered import pcoz  # @UnusedImport
    
######## Setting up the Zebra as a fast dichriosm counter ###############
zebra_fastdicr_installed = True
if zebra_fastdicr_installed:
    from detectors.fastDichroism import fastDichroism  # @UnusedImport

########setting up the diagnostic cameras###############
from detectors.diagnostic_cameras import peak2d1,max2d1,peak2d2,max2d2,peak2d3,max2d3,peak2d4,max2d4,peak2d6,max2d6,peak2dj1,max2dj1,peak2dj3,max2dj3  # @UnusedImport

#short hand commands for shutter and valves
#from i10commands.shutterValveCommands import *  # @UnusedWildImport

##setup metadata for the file
from rasor.pd_metadata import MetaDataPD
rmotors=MetaDataPD("rmotors", [tth, th, chi, eta, ttp, thp, py, pz, dsu, dsd, difx, alpha_rasor, lgm, lgf, lgb])
#add_default rmotors

# meta data
from metadata.metadataItems import *  # @UnusedWildImport
try:
    #SRS file metadata only works when run in localStation.py - see globals()
    print "-"*50
    print "SRS or ASCII file metadata command:"
    from gdascripts.scannable.installStandardScannableMetadataCollection import *  # @UnusedWildImport
    meta.rootNamespaceDict=globals()
    note.rootNamespaceDict=globals()
    def stdmeta():
        setmeta_ret=setmeta(*stdmetadatascannables)
        print "Standard metadata scannables: " + setmeta_ret
    stdmeta()
    print "    Use 'stdmeta' to reset to standard scannables"
    alias('stdmeta')
    from gda.jython.commands.ScannableCommands import add_default
    add_default(meta)
    meta.quiet = True
except:
    localStation_exception(sys.exc_info(), "creating SRS file metadata objects")

# check beam scannables
from scannable.checkbeanscannables import checkrc, checktopup_time, checkfe, checkbeam, checkbeam_cv, checkbeamcv, checkfe_cv, checkrc_cv, checktopup_time_cv, checkbeam4scan, checkbeam4cvscan # @UnusedImport


# multi-image per scan data point scan
from scan.miscan import miscan; print miscan.__doc__  # @UndefinedVariable

#import post scan data process The following 5 lines must be in localStation.py 
from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
import gdascripts
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()
from data_process.scanDataProcess import *  # @UnusedWildImport

#Continuous Scan scannables and commands
from scannable.continuous.continuous_energy_scannables import *  # @UnusedWildImport
from scan.cvscan import cvscan, cvscan2 # @UnusedImport
from scannable.id_energys.idu_energy_gap import * # @UnusedWildImport
from scannable.id_energys.idd_energy_gap import *  # @UnusedWildImport
from scannable.id_energys.idu_energy_jawphase import *  # @UnusedWildImport
from scannable.id_energys.idd_lin_energy import * # @UnusedWildImport
from scannable.id_energys.idu_switchable import *  # @UnusedWildImport
from scan.trajectory_scans import trajcscan, trajrscan  # @UnusedImport

#create 'smode', 'pol', and 'enenry'
from scannable.idcontrols.mode_polarisation_energy_instances import *  # @UnusedWildImport
idd,idu = SourceMode.SOURCE_MODES
pc,nc,lh,lv,la,lh3 = Polarisation.POLARISATIONS

print
print "*"*80
#DiffCalc
# print "import DIFFCALC support for I10"
# from startup.i10 import *  # @UnusedWildImport

##Position Wrapper
print "-"*100
print "Creating 'wa' command for returning RASOR motor positions"
wascannables = [tth, th, chi, dsu, dsd, eta, ttp, thp, py, pz, alpha_rasor, difx, lgf, lgb, lgm, sx, sy, sz]
from rasor.positionWrapper import PositionWrapper
wa=PositionWrapper(wascannables)
alias('wa')

# print "Creating 'wh' command for return RASOR positions in DIFFCALC HKL"
# wherescannables=[delta,eta,chi,phi,h,k,l,en]
# wh=PositionWrapper(wherescannables) ##can only be used with diffcalc
# alias('wh')

#Please leave Panic stop customisation last - specify scannables to be excluded from Panic stop
from i10commands.stopJythonScannables import stopJythonScannablesExceptExcluded  # @UnusedImport
STOP_ALL_EXCLUSIONS=[]  # @UndefinedVariable

if len(localStation_exceptions) > 0:
    simpleLog("=============== %r ERRORS DURING STARTUP ================" % len(localStation_exceptions))

for localStationException in localStation_exceptions:
    simpleLog(localStationException)

print "**************************************************"
print "localStation.py completed."
print "**************************************************"

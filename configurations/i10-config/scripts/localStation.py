from utils.ExceptionLogs import localStation_exceptions
from gdaserver import shtr1, gv12 , pgm_energy, alpha, chi, difx, dsd, dsu, eta,\
    lgb, lgf, lgm, th, tth, sx, sy, sz, idd_gap, idd_rowphase1, idd_jawphase,\
    idd_rowphase3, idd_rowphase4, idd_rowphase2, idd_sepphase, idu_gap,\
    idu_rowphase1, idu_rowphase2, idu_jawphase, idu_rowphase3, idu_rowphase4,\
    idu_sepphase
import installation
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import alias
from gda.device.scannable import DummyScannable

print "**************************************************"
print "Running the I10 startup script localStation.py..."
print ""

global RASOR_SCALER, UI1, UJ1
import java
from gdascripts.messages.handle_messages import simpleLog

print "-"*100
print "Set scan returns to the original positions on completion to false (0); default is 0."
print "   To set scan returns to its start positions on completion please do:"
print "      >>>scansReturnToOriginalPositions=1"
scansReturnToOriginalPositions=0;
print
###Import common commands, utilities, etc#####
from i10commands.dirFileCommands import pwd, lwf,nwf,nfn,setSubdirectory,getSubdirectory  # @UnusedImport
alias("pwd")
alias("lwf")
alias("nwf")
alias("nfn")
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

print "-"*100
print "creating 'dummy' & `denergy` scannables"
dummy = DummyScannable("dummy")
denergy = pgm_energy #used in I10 diffcalc

#Create snap command for capturing a snapshot of camera
print "-"*100
print "creating 'snap' command for capturing a snapshot off a detector:"
print "    Usage example: >>>snap pimte 6.0"
def snap(det, t, *args):
    newargs=[dummy, 1,1,1, det,t]
    for arg in args:
        newargs.append(arg)
    scan([e for e in newargs])
alias("snap")


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
    from detectors.pimteWithDataProcessor import pimte_tiff, pimteSMPV, pimte2d  # @UnusedImport

######## Setting up the I10 Pixis camera ###############
pixis_installed = True
if pixis_installed:
    #PIXIS detectors customised to display image in 'Plot 1' view and return results of image process
    from detectors.pixisWithDataProcessor import pixis_tiff, pixisSMPV, pixis2d  # @UnusedImport
    
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
from detectors.diagnostic_cameras import *  # @UnusedWildImport

try:
    shtropen = shtr1.moveTo("Open")
    shtrclose = shtr1.moveTo("Close")
    gv12open = gv12.moveTo("Open")
    gv12close = gv12.moveTo("Close")
except:
    localStation_exception(sys.exc_info(), "creating shutter & valve objects")

##setup metadata for the file
from rasor.pd_metadata import MetaDataPD
rmotors=MetaDataPD("rmotors", [tth, th, chi, eta, ttp, thp, py, pz, dsu, dsd, difx, alpha, lgm, lgf, lgb])
#add_default rmotors

##Position Wrapper
wascannables = [tth, th, chi, dsu, dsd, eta, ttp, thp, py, pz, alpha, difx, lgf, lgb, lgm, sx, sy, sz]
from rasor.positionWrapper import PositionWrapper
wa=PositionWrapper(wascannables)
alias('wa')

#wherescannables=[rasor_tth,rasor_th,rasor_chi,h,k,l,energy]
#wh=PositionWrapper(wherescannables) ##can only be used with diffcalc
#alias('wh')

# meta should be created last to ensure we have all required scannables
try:
    print '-'*80
    from gdascripts.scannable.installStandardScannableMetadataCollection import * #@UnusedWildImport
    meta.rootNamespaceDict=globals()
    note.rootNamespaceDict=globals()

    def stdmeta():
        iddmetadatascannables = (idd_gap, idd_rowphase1, idd_rowphase2,
                                 idd_rowphase3, idd_rowphase4, idd_jawphase, 
                                 idd_sepphase)
        stdmetadatascannables = (idu_gap, idu_rowphase1, idu_rowphase2,
                                 idu_rowphase3, idu_rowphase4, idu_jawphase,
                                 idu_sepphase,
                                 pgm_energy)
        
#         if polarimeter_installed:
#             stdmetadatascannables += (RetTilt, RetRotation, AnaTilt ,AnaRotation, 
#                                  AnaDetector, AnaTranslation,hpx, hpy, hpc, hpb)
        setmeta_ret=setmeta(*stdmetadatascannables)
        print "Standard metadata scannables: " + setmeta_ret

    stdmeta()
    print "Use 'stdmeta()' to reset to standard scannables"
    #alias('stdmeta')
    from gda.jython.commands.ScannableCommands import add_default
    add_default(meta)
    meta.quiet = True
    
except:
    localStation_exception(sys.exc_info(), "creating metadata objects")

from scannable.checkbeanscannables import checkrc, checktopup_time, checkfe, checkbeam, checkbeam_cv, checkbeamcv, checkfe_cv, checkrc_cv, checktopup_time_cv  # @UnusedImport

print "-"*100
print "Creating 'miscan' - multiple image per scan data point"
print "    Syntax: miscan (scannable1, scannable2) [(1,2), (3,4),(5,6)] pixis 0.1 10"
from scan.miscan import miscan  # @UnusedImport
print miscan.__doc__  # @UndefinedVariable
alias("miscan")

#Continuous Scan commands
from scan.cvscan import cvscan  # @UnusedImport
from scan.trajectory_scans import trajcscan, trajrscan  # @UnusedImport
#Import continuous scannables
if installation.isLive():
    from scan.cvscan import cvscan2  # @UnusedImport
    from scannable.continuous.continuous_energy_scannables import *  # @UnusedWildImport

print
print "*"*80
#DiffCalc
print "import DIFFCALC support for I10"
from startup.i10 import *  # @UnusedWildImport

#Please leave this to be last but one items as it calls 'globals() for data process - enable standard scan data process
from data_process.scanDataProcess import *  # @UnusedWildImport
#Please leave Panic stop customisation last - specify scannables to be excluded from Panic stop
STOP_ALL_EXCLUSIONS=[]  # @UndefinedVariable

print "*"*100
print "Attempting to run localStationUser.py from users script directory"
try:
    from gda.jython.commands.GeneralCommands import run
    run("localStationUser")
    print "localStationUser.py completed."
except java.io.FileNotFoundException, e:
    print "No localStationUser.py found in user scripts directory"
except:
    localStation_exception(sys.exc_info(), "running localStationUser user script")

if len(localStation_exceptions) > 0:
    simpleLog("=============== %r ERRORS DURING STARTUP ================" % len(localStation_exceptions))

for localStationException in localStation_exceptions:
    simpleLog(localStationException)

print "**************************************************"
print "localStation.py completed."
print "**************************************************"

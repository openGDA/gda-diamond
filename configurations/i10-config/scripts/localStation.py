from utils.ExceptionLogs import localStation_exceptions
import sys
try:
    from gdaserver import alpha_rasor, chi, difx, dsd, dsu, eta,\
        lgb, lgf, lgm, th, tth, sx, sy, sz
except:
    print "gdaserver.py not yet generated!"
    
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
    from scannable.m1_haxpod_motors import *  # @UnusedWildImport
    from scannable.m3m5_haxpod_motors import *  # @UnusedWildImport
    from scannable.m4_haxpod_motors import *  # @UnusedWildImport
    from scannable.m6_haxpod_motors import *  # @UnusedWildImport
    
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
    
    try:
        from scannable.autoGainAmplifer import AutoGainAmplifier
        rca1=AutoGainAmplifier("rca1", "ME01D-EA-IAMP-01", 0.5, 9.0, "%.4e")  # @UndefinedVariable
        rca2=AutoGainAmplifier("rca2", "ME01D-EA-IAMP-02", 0.5, 9.0, "%.4e")  # @UndefinedVariable
        rca3=AutoGainAmplifier("rca3", "ME01D-EA-IAMP-03", 0.5, 9.0, "%.4e")  # @UndefinedVariable
    except:
        localStation_exception(sys.exc_info(), "creating AutoGainAmplifer scannables")

else:
    pass
        
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
try:
    rmotors=MetaDataPD("rmotors", [tth, th, chi, eta, ttp, thp, py, pz, dsu, dsd, difx, alpha_rasor, lgm, lgf, lgb])
except:
    localStation_exception(sys.exc_info(), "creating rmotors metadata objects")

# meta data
try:
    from gdaserver import idd_gap, idd_rowphase1, idd_jawphase,\
        idd_rowphase3, idd_rowphase4, idd_rowphase2, idd_sepphase, idu_gap,\
        idu_rowphase1, idu_rowphase2, idu_jawphase, idu_rowphase3, idu_rowphase4,\
        idu_sepphase, pgm_grat_pitch, pgm_m2_pitch,pgm_energy
except:
    pass #the oject should already in jython namespace - only occur 1st time running server    

print '-'*80
print "Define metadata list for data collection:"
metadatalist=[]
iddlist = [idd_gap,idd_rowphase1,idd_rowphase2,idd_rowphase3,idd_rowphase4,idd_jawphase,idd_sepphase]
idulist = [idu_gap,idu_rowphase1,idu_rowphase2,idu_rowphase3,idu_rowphase4,idu_jawphase,idu_sepphase]
pgmlist = [pgm_energy, pgm_grat_pitch, pgm_m2_pitch]

metadatalist=metadatalist+iddlist+idulist+pgmlist
try:
    #SRS file metadata only works when run in localStation.py - see globals()
    print "-"*50
    print "SRS or ASCII file metadata command:"
    from gdascripts.scannable.installStandardScannableMetadataCollection import *  # @UnusedWildImport
    meta.rootNamespaceDict=globals()
    note.rootNamespaceDict=globals()
    def stdmeta():
        setmeta_ret=setmeta(*metadatalist)
        print "Standard metadata scannables: " + setmeta_ret
    stdmeta()
    print "    Use 'stdmeta' to reset to standard scannables"
    alias('stdmeta')
    add_default(meta)  # @UndefinedVariable
    meta.quiet = True
except:
    localStation_exception(sys.exc_info(), "creating SRS file metadata objects")

#Nexus file
print "-"*50
print "Nexus file metadata commands:"
print "    'meta_add' - add a scannable or scannables to the scan metadata"
print "    'meta_ll'  - list the items and their values to be put into the scan metadata"
print "    'meta_ls'  - list only the items to be put into the scan metadata"
print "    'meta_rm'  - remove a scannable or scannables from the scan metadata"

from metadata.metashop import *  # @UnusedWildImport
meta_add(*metadatalist)

# check beam scannables
from scannable.checkbeanscannables import checkrc, checktopup_time, checkfe, checkbeam, checkbeamcv, checkfe_cv, checkrc_cv, checktopup_time_cv, checkbeam4scan, checkbeam4cvscan # @UnusedImport
print "-"*100
# multi-image per scan data point scan
from scan.miscan import miscan; print miscan.__doc__  # @UndefinedVariable
print "-"*100
from scan.flyscan_command import flyscannable, FlyScanPositionsProvider, flyscan  # @UnusedImport
from  scan import flyscan_command; print flyscan_command.__doc__  # @UndefinedVariable
print "-"*100

#import post scan data process The following 5 lines must be in localStation.py 
from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
import gdascripts
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()
from data_process.scanDataProcess import *  # @UnusedWildImport

#####source_polarisation specific energy scannables - using lookup table individually
# from scannable.id_energys.idu_energy_gap import * # @UnusedWildImport
# from scannable.id_energys.idd_energy_gap import *  # @UnusedWildImport
# from scannable.id_energys.idu_energy_jawphase import *  # @UnusedWildImport
# from scannable.id_energys.idd_lin_energy import * # @UnusedWildImport
# from scannable.id_energys.idu_switchable import *  # @UnusedWildImport
# from scan.trajectory_scans import trajcscan, trajrscan  # @UnusedImport
#####create 'smode', 'pol', and 'energy' - using source polarisation specific energy scannables
# from scannable.idcontrols.mode_polarisation_energy_instances import *  # @UnusedWildImport
# idd,idu,unknown = SourceMode.SOURCE_MODES
# pc,nc,lh,lv,la,lh3,unknown = Polarisation.POLARISATIONS
#####Continuous Scan scannables and commands - support egy, egy_g, and 'energy'
#from scannable.continuous.continuous_energy_scannables import *  # @UnusedWildImport
#from scan.cvscan_0 import cvscan, cvscan2  # @UnusedImport

#####
from calibrations.mode_polarisation_energy_instances import smode, pol, energy_s, energy_pol, setBeamHarmonicsOrder, initialisation  # @UnusedImport
from calibrations.xraysource import X_RAY_SOURCE_MODES
from calibrations.energy_polarisation_class import X_RAY_POLARISATIONS
idd,idu,unknown = X_RAY_SOURCE_MODES
pc,nc,lh,lv,la,lh3,unknown = X_RAY_POLARISATIONS
initialisation()

from scannable.continuous.continuous_energy_scannables_new import energy, energy_controller, mcs16,mcs17,mcs18,mcs19  # @UnusedImport
from scan.cvscan import cvscan  # @UnusedImport
alias('cvscan')

print
print "*"*80
#DiffCalc
print "import DIFFCALC support for I10"
from rasor.scannable.ThArea import thArea
from rasor.scannable.TthArea import tthArea
try:
    from startup.i10 import *  # @UnusedWildImport
except:
    localStation_exception(sys.exc_info(), "import diffcalc error.")
    
##Position Wrapper
print "-"*100
print "Creating 'wa' command for returning RASOR motor positions"
wascannables = [tth, th, chi, dsu, dsd, eta, ttp, thp, py, pz, alpha_rasor, difx, lgf, lgb, lgm, sx, sy, sz]
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
from gdaserver import pimte, pixis

thpimte=NXDetectorWithRockingMotion("thpimte", th, pimte)
thpixis=NXDetectorWithRockingMotion("thpixis", th, pixis)

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

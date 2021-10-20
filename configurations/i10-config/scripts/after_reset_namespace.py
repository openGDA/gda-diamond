'''
Created on 13 Aug 2019

@author: fy65
'''
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import alias
from gdascripts.messages.handle_messages import simpleLog
from i10commands.dirFileCommands import pwd, lwf,nwf,nfn,setSubdirectory,getSubdirectory  # @UnusedImport
from plottings.configScanPlot import setYFieldVisibleInScanPlot,getYFieldVisibleInScanPlot,setXFieldInScanPlot,useSeparateYAxes,useSingleYAxis  # @UnusedImport
from gdascripts.pd.epics_pds import DisplayEpicsPVClass,EpicsReadWritePVClass,SingleEpicsPositionerClass,SingleEpicsPositionerNoStatusClass,SingleEpicsPositionerNoStatusClassDeadband,SingleChannelBimorphClass  # @UnusedImport
from gdascripts.pd.time_pds import showtime,inctime,waittime,tictoc, showtimeClass, showincrementaltimeClass, waittimeClass2  # @UnusedImport
from gdascripts.utils import * #@UnusedWildImport
from gdascripts.constants import * #@UnusedWildImport
from gdascripts.scannable.timerelated import timerelated,t,dt,w,clock,epoch #@UnusedImport
from rasor.saveAndReload import SaveAndReload  # @UnusedImport
from i10commands.snapshot import *  # @UnusedWildImport
from i10commands.switchDataWriter import asciiformat, nexusformat, whichformat  # @UnusedImport
from rasor.scannable.polarisation_analyser_example import *  # @UnusedWildImport
if installation.isLive():
    #High Field Magnet support
    from high_field_magnet.scannable.intelligent_power_supply_instances import *  # @UnusedWildImport
#     from scannable.temporaryIDControls import *  # @UnusedWildImport
    from scannable.frontEndBeamMonitors import *  # @UnusedWildImport
    from scannable.mirrors_fine_pitch_motors import m1fpitch, m3m5fpitch,m4fpitch, m6fpitch
    m1.addGroupMember(m1fpitch)
    m3m5.addGroupMember(m3m5fpitch)
    m4.addGroupMember(m4fpitch)
    m6.addGroupMember(m6fpitch)
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
    except:
        localStation_exception(sys.exc_info(), "creating gflow2 scannable")
    try:
        from scannable.autoGainAmplifer import AutoGainAmplifier
    except:
        localStation_exception(sys.exc_info(), "creating AutoGainAmplifer scannables")
else:
    pass

from detectors.pimteWithDataProcessor import pimteSMPV, pimte2d
from detectors.pixisWithDataProcessor import pixisSMPV, pixis2d
from detectors.fastDichroism import fastDichroism
from detectors.diagnostic_cameras import peak2d1,max2d1,peak2d2,max2d2,peak2d3,max2d3,peak2d4,max2d4,peak2d6,max2d6,peak2dj1,max2dj1,peak2dj3,max2dj3  # @UnusedImport
from rasor.pd_metadata import MetaDataPD

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


from scannable.checkbeanscannables import checkrc, checktopup_time, checkfe, checkbeam, checkbeamcv, checkfe_cv, checkrc_cv, checktopup_time_cv, checkbeam4scan, checkbeam4cvscan # @UnusedImport
from scan.miscan import miscan; print miscan.__doc__  # @UndefinedVariable
from scan.flyscan_command import flyscannable, FlyScanPositionsProvider, flyscan  # @UnusedImport
from  scan import flyscan_command; print flyscan_command.__doc__  # @UndefinedVariable

from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
import gdascripts
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()
from data_process.scanDataProcess import *  # @UnusedWildImport


from scannable.id_energys.idu_energy_gap import * # @UnusedWildImport
from scannable.id_energys.idd_energy_gap import *  # @UnusedWildImport
from scannable.id_energys.idu_energy_jawphase import *  # @UnusedWildImport
from scannable.id_energys.idd_lin_energy import * # @UnusedWildImport
from scannable.id_energys.idu_switchable import *  # @UnusedWildImport
from scan.trajectory_scans import trajcscan, trajrscan  # @UnusedImport
#Continuous Scan scannables and commands
from scannable.continuous.deprecated.continuous_energy_scannables import *  # @UnusedWildImport
from scan.cvscan import cvscan, cvscan2, cvscan_traj # @UnusedImport

#create 'smode', 'pol', and 'enenry'
from scannable.idcontrols.mode_polarisation_energy_instances import *  # @UnusedWildImport
idd,idu = SourceMode.SOURCE_MODES
pc,nc,lh,lv,la,lh3 = Polarisation.POLARISATIONS

from rasor.scannable.ThArea import thArea
from rasor.scannable.TthArea import tthArea
try:
    from startup.i10 import *  # @UnusedWildImport
except:
    localStation_exception(sys.exc_info(), "import diffcalc error.")
    
from rasor.positionWrapper import PositionWrapper
from i10commands.stopJythonScannables import stopJythonScannablesExceptExcluded  # @UnusedImport
STOP_ALL_EXCLUSIONS=[]  # @UndefinedVariable

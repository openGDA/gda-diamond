from os.path import os
from utils.ExceptionLogs import localStation_exception, localStation_exceptions
print "**************************************************"
print "Running the I10 startup script localStation.py..."
print ""

global ScriptBase, run, finder, MetaDataPD, PositionWrapper, DummyScannable, add_default
global idd_gap, idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, idd_jawphase, idd_sepphase, \
       idu_gap, idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, idu_jawphase, idu_sepphase, \
       pgm_energy, s4xgap, s4ygap, th, tth, thp, ttp, eta, sx, sy, sz
global tth, th, chi, dsu, dsd, eta, ttp, thp, py, pz, alpha, difx, lgf, lgb, lgm, sx, sy, sz
global RetTilt, RetRotation, AnaTilt ,AnaRotation, \
        AnaDetector, AnaTranslation,hpx, hpy, hpc, hpb
global mac116, mac117, mac118, mac119, mac120
global RASOR_SCALER, UI1, UJ1
global zebra

import sys, gda, java
#from rasor.init_scan_commands_and_processing import * 
from gda.configuration.properties import LocalProperties
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.pd import epics_pds

# setup standard scans with processing
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
import gdascripts.utils #@UnusedImport
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals() 

print "-----------------------------------------------------------------------------------------------------------------"
print "Set scan returns to the original positions on completion to false (0); default is 0."
print "   To set scan returns to its start positions on completion please do:"
print "      >>>scansReturnToOriginalPositions=1"
scansReturnToOriginalPositions=0;
print
#Please change the following lines to add default scannables to i11 GDA server engine
#print "-----------------------------------------------------------------------------------------------------------------"
#print "Adding default scannable objects to GDA system: Io, Te"
#add_default Io #@UndefinedVariable
#add_default Ie #@UndefinedVariable

print "-----------------------------------------------------------------------------------------------------------------"
print "commands for directory/file operations: "
print "   >>>pwd - return the current data directory"
print "   >>>lwf - return the full path of the last working data file"
print "   >>>nwf - return the full path of the next working data file"
print "   >>>nfn - return the next data file number to be collected"
print "   >>>setSubdirectory('test') - change data directory to a sub-directory named 'test', created first if not exist"
print "   >>>getSubdirectory() - return the current sub-directory setting if exist"
print "Please note: users can only create sub-directory within their permitted visit data directory via GDA, not themselves."
print "To create another sub-directory 'child-test' inside a sub-directory 'test', you must specify the full path as 'test/child-test' "
from gda.data import PathConstructor, NumTracker

# set up a nice method for getting the latest file path
i10NumTracker = NumTracker("i10");

# function to find the working directory
def pwd():
    '''return the working directory'''
    cwd = PathConstructor.createFromDefaultProperty()
    return cwd
    
alias("pwd")

# function to find the last working file path
def lwf():
    '''return the last working file path root'''
    cwd = PathConstructor.createFromDefaultProperty()
    filenumber = i10NumTracker.getCurrentFileNumber();
    return os.path.join(cwd,str(filenumber))
    
alias("lwf")

# function to find the next working file path
def nwf():
    '''query the next working file path root'''
    cwd = PathConstructor.createFromDefaultProperty()
    filenumber = i10NumTracker.getCurrentFileNumber();
    return os.path.join(cwd,str(filenumber+1))
    
alias("nwf")

# function to find the next scan number
def nfn():
    '''query the next file number or scan number'''
    filenumber = i10NumTracker.getCurrentFileNumber();
    return filenumber+1
    
alias("nfn")

# the subdirectory parts
def setSubdirectory(dirname):
    '''create a new sub-directory for data collection that follows'''
    finder.find("GDAMetadata").setMetadataValue("subdirectory",dirname)
    try:
        os.mkdir(pwd())
    except :
        pass
    
def getSubdirectory():
    return finder.find("GDAMetadata").getMetadataValue("subdirectory")

print

##setup metadata for the file
run("rasor/pd_metadata.py")
#MBB#rmotors=MetaDataPD("rmotors", [tth,th,chi,rasor_eta,rasor_ttp, rasor_thp, rasor_py,rasor_pz, rasor_dsu, rasor_dsd, rasor_difx, rasor_alpha, rasor_lgm, rasor_lgf, rasor_lgb])
rmotors=MetaDataPD("rmotors", [tth, th, chi, eta, ttp, thp, py, pz, dsu, dsd, difx, alpha, lgm, lgf, lgb])
#add_default rmotors

##Position Wrapper
#wherescannables=[rasor_tth,rasor_th,rasor_chi,h,k,l,energy]
#MBB#wascannables = [tth, th,chi,rasor_dsu,rasor_dsd,rasor_eta,rasor_ttp,rasor_thp,rasor_py,rasor_pz,rasor_alpha,rasor_difx,rasor_lgf,rasor_lgb,rasor_lgm,rasor_sx,rasor_sy,rasor_sz]
wascannables = [tth, th, chi, dsu, dsd, eta, ttp, thp, py, pz, alpha, difx, lgf, lgb, lgm, sx, sy, sz]
run("rasor/positionWrapper.py")
#wh=PositionWrapper(wherescannables) ##can only be used with diffcalc
wa=PositionWrapper(wascannables)
#alias('wh')
alias('wa')

###Save and reload positions
run("rasor/saveAndReload.py")

###delay scannable
from gdascripts.pd.time_pds import showtime,inctime,waittime,tictoc, showtimeClass, showincrementaltimeClass, waittimeClass2  # @UnusedImport
wait = waittime
showtime.setLevel(4) # so it is operated before anything else in a scan

try:
    print "creating 'dummy' & `denergy` scannables"
    print ""
    dummy = DummyScannable("dummy")
    denergy = pgm_energy
except:
    localStation_exception(sys.exc_info(), "creating 'dummy' & 'denergy' scannables")



try:
    ########diffcal####################
    diffcalcDir = LocalProperties.get("gda.diffcalc.path") + "/"
    sys.path = [diffcalcDir] + sys.path
    run("i10fourcircle.py")
    #execfile(diffcalcDir + "example/startup/i10fourcircle.py")
    
except:
    localStation_exception(sys.exc_info(), "initialising diffcalc")

try:
    run("rasor/scannable/polarisationAnalyser.py")
    # name, d_spacing (A), start_energy(eV), stop_energy(eV), thp_offset(deg), pos_z(mm), pos_y(mm)
    #ml = [
    #    Multilayer("mn", 13.7, 600, 700, 1.17, -14.5, 1.5),
    #    Multilayer("o",  16.2, 510, 550, 0,      0,   1.5)]
    # name, multilayer_list, pz_scannable, py_scannable
    #mss = MultilayerSelectorScannable("mss", ml, pz, py)
    # name, thp_scannable, ttp_scannable, multilayer_selector_scannable, energy_scannable
    #pa = PolarisationAnalyser("pa", thp, ttp, mss, idupgm_energy)
    #print "Usage: pos mss            to find out which MSS you are on"
    #print "Usage: pos mss <num>      to select MSS by number"
    #print "Usage: pos mss 'string'   to select MSS by name"
    #print "Usage: pos pa             to find out which PA you are on"
    #print "Usage: pos pa <num>       to set pa for a given energy in eV"
    #print "Usage: pos pa 0           to set pa for a the energy in configured energy scannable"
    #alias pa
except:
    localStation_exception(sys.exc_info(), "initialising polarisation analyser")

try:
    from high_field_magnet.scannable.intelligentPowerSupply import \
        IntelligentPowerSupplyFieldScannable, \
        IntelligentPowerSupplySweepRateScannable
    from dls_scripts.scannable.CryojetScannable import CryojetScannable
    
    ips_field = IntelligentPowerSupplyFieldScannable('ips_field', 'BL10J-EA-SMC-01:', field_tolerance=0.01)
    ips_sweeprate = IntelligentPowerSupplySweepRateScannable('ips_sweeprate', 'BL10J-EA-SMC-01:', sweeprate_tolerance=0.01)
    itc2 = CryojetScannable('itc2',pvroot='BL10J-EA-TCTRL-02:', temp_tolerance=1, stable_time_sec=60)
    ips_field.setLevel(6)
    ips_sweeprate.setLevel(6)
    itc2.setLevel(6)
    magj1yrot_off = epics_pds.EpicsReadWritePVClass('magj1yrot_off', 'BL10J-EA-MAG-01:INSERT:ROTY.OFF', 'deg', '%.6f')
except:
    localStation_exception(sys.exc_info(), "initialising high field magnet")

## temporary fix for inability to perform caput with callback on SR10I-MO-SERVC-01:BLGAPMTR.VAL
idd_gap_temp = epics_pds.SingleEpicsPositionerClass("idd_gap_temp",
                    "SR10I-MO-SERVC-01:BLGAPMTR.VAL", 
                    "SR10I-MO-SERVC-01:BLGAPMTR.RBV", 
                    "SR10I-MO-SERVC-01:BLGAPMTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLGAPMTR.STOP", "mm", "%.4f")

idu_gap_temp = epics_pds.SingleEpicsPositionerClass("idu_gap_temp",
                    "SR10I-MO-SERVC-21:BLGAPMTR.VAL", 
                    "SR10I-MO-SERVC-21:BLGAPMTR.RBV", 
                    "SR10I-MO-SERVC-21:BLGAPMTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLGAPMTR.STOP", "mm", "%.4f")

idd_rowphase1_temp = epics_pds.SingleEpicsPositionerClass("idd_rowphase1_temp",
                    "SR10I-MO-SERVC-01:BLRPQ1MTR.VAL", 
                    "SR10I-MO-SERVC-01:BLRPQ1MTR.RBV", 
                    "SR10I-MO-SERVC-01:BLRPQ1MTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLRPQ1MTR.STOP", "mm", "%.4f")

idu_rowphase1_temp = epics_pds.SingleEpicsPositionerClass("idu_rowphase1_temp",
                    "SR10I-MO-SERVC-21:BLRPQ1MTR.VAL", 
                    "SR10I-MO-SERVC-21:BLRPQ1MTR.RBV", 
                    "SR10I-MO-SERVC-21:BLRPQ1MTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLRPQ1MTR.STOP", "mm", "%.4f")

idd_rowphase2_temp = epics_pds.SingleEpicsPositionerClass("idd_rowphase2_temp",
                    "SR10I-MO-SERVC-01:BLRPQ2MTR.VAL", 
                    "SR10I-MO-SERVC-01:BLRPQ2MTR.RBV", 
                    "SR10I-MO-SERVC-01:BLRPQ2MTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLRPQ2MTR.STOP", "mm", "%.4f")

idu_rowphase2_temp = epics_pds.SingleEpicsPositionerClass("idu_rowphase2_temp",
                    "SR10I-MO-SERVC-21:BLRPQ2MTR.VAL", 
                    "SR10I-MO-SERVC-21:BLRPQ2MTR.RBV", 
                    "SR10I-MO-SERVC-21:BLRPQ2MTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLRPQ2MTR.STOP", "mm", "%.4f")

idd_rowphase3_temp = epics_pds.SingleEpicsPositionerClass("idd_rowphase3_temp",
                    "SR10I-MO-SERVC-01:BLRPQ3MTR.VAL", 
                    "SR10I-MO-SERVC-01:BLRPQ3MTR.RBV", 
                    "SR10I-MO-SERVC-01:BLRPQ3MTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLRPQ3MTR.STOP", "mm", "%.4f")

idu_rowphase3_temp = epics_pds.SingleEpicsPositionerClass("idu_rowphase3_temp",
                    "SR10I-MO-SERVC-21:BLRPQ3MTR.VAL", 
                    "SR10I-MO-SERVC-21:BLRPQ3MTR.RBV", 
                    "SR10I-MO-SERVC-21:BLRPQ3MTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLRPQ3MTR.STOP", "mm", "%.4f")

idd_rowphase4_temp = epics_pds.SingleEpicsPositionerClass("idd_rowphase4_temp",
                    "SR10I-MO-SERVC-01:BLRPQ4MTR.VAL", 
                    "SR10I-MO-SERVC-01:BLRPQ4MTR.RBV", 
                    "SR10I-MO-SERVC-01:BLRPQ4MTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLRPQ4MTR.STOP", "mm", "%.4f")

idu_rowphase4_temp = epics_pds.SingleEpicsPositionerClass("idu_rowphase4_temp",
                    "SR10I-MO-SERVC-21:BLRPQ4MTR.VAL", 
                    "SR10I-MO-SERVC-21:BLRPQ4MTR.RBV", 
                    "SR10I-MO-SERVC-21:BLRPQ4MTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLRPQ4MTR.STOP", "mm", "%.4f")

idd_jawphase_temp = epics_pds.SingleEpicsPositionerClass("idd_jawphase_temp",
                    "SR10I-MO-SERVC-01:BLJAWMTR.VAL", 
                    "SR10I-MO-SERVC-01:BLJAWMTR.RBV", 
                    "SR10I-MO-SERVC-01:BLJAWMTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLJAWMTR.STOP", "mm", "%.4f")

idu_jawphase_temp = epics_pds.SingleEpicsPositionerClass("idu_jawphase_temp",
                    "SR10I-MO-SERVC-21:BLJAWMTR.VAL", 
                    "SR10I-MO-SERVC-21:BLJAWMTR.RBV", 
                    "SR10I-MO-SERVC-21:BLJAWMTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLJAWMTR.STOP", "mm", "%.4f")

idd_sepphase_temp = epics_pds.SingleEpicsPositionerClass("idd_sepphase_temp",
                    "SR10I-MO-SERVC-01:BLSEPMTR.VAL", 
                    "SR10I-MO-SERVC-01:BLSEPMTR.RBV", 
                    "SR10I-MO-SERVC-01:BLSEPMTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLSEPMTR.STOP", "mm", "%.4f")

idu_sepphase_temp = epics_pds.SingleEpicsPositionerClass("idu_sepphase_temp",
                    "SR10I-MO-SERVC-21:BLSEPMTR.VAL", 
                    "SR10I-MO-SERVC-21:BLSEPMTR.RBV", 
                    "SR10I-MO-SERVC-21:BLSEPMTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLSEPMTR.STOP", "mm", "%.4f")

print " To move gap use idd_gap_temp as idd_gap etc."

try:
    xbpm1_x = epics_pds.DisplayEpicsPVClass(
        'xbpm1_x', 'FE10I-DI-PBPM-01:BEAMX', 'nm', '%f')
    xbpm1_y = epics_pds.DisplayEpicsPVClass(
        'xbpm1_y', 'FE10I-DI-PBPM-01:BEAMY', 'nm', '%f')
    xbpm2_x = epics_pds.DisplayEpicsPVClass(
        'xbpm2_x', 'FE10I-DI-PBPM-02:BEAMX', 'nm', '%f')
    xbpm2_y = epics_pds.DisplayEpicsPVClass(
        'xbpm2_y', 'FE10I-DI-PBPM-02:BEAMY', 'nm', '%f')
    xbpm_anglex = epics_pds.DisplayEpicsPVClass(
        'xbpm_anglex', 'FE10I-DI-BEAM-01:RM:ANGLEX', 'rad', '%f')
    xbpm_angley = epics_pds.DisplayEpicsPVClass(
        'xbpm_angley', 'FE10I-DI-BEAM-01:RM:ANGLEY', 'rad', '%f')
    xbpm_anglex_urad = epics_pds.DisplayEpicsPVClass(
        'xbpm_anglex_urad', 'FE10I-DI-BEAM-01:X:ANGLE', 'urad', '%f')
    xbpm_angley_urad = epics_pds.DisplayEpicsPVClass(
        'xbpm_angley_urad', 'FE10I-DI-BEAM-01:Y:ANGLE', 'urad', '%f')
    xbpm=gda.device.scannable.scannablegroup.ScannableGroup('xbpm', [
        xbpm1_x, xbpm1_y, xbpm2_x, xbpm2_y,
        xbpm_anglex, xbpm_angley, xbpm_anglex_urad, xbpm_angley_urad])
except:
    localStation_exception(sys.exc_info(), "initialising front end xbpm's")

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

try:
    from future.singleEpicsPositionerNoStatusClassDeadbandOrStop import SingleEpicsPositionerNoStatusClassDeadbandOrStop

    m1fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m1fpitch',
        'BL10I-OP-COL-01:FPITCH:DMD:AO', 'BL10I-OP-COL-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
    m3m5fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m3m5fpitch',
        'BL10I-OP-SWTCH-01:FPITCH:DMD:AO', 'BL10I-OP-SWTCH-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
    m4fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m4fpitch',
        'BL10I-OP-FOCS-01:FPITCH:DMD:AO', 'BL10I-OP-FOCS-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
    m6fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m6fpitch',
        'BL10J-OP-FOCA-01:FPITCH:DMD:AO', 'BL10J-OP-FOCA-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
except:
    localStation_exception(sys.exc_info(), "initialising fpitch scannables")

########setting up the diagnostic flea camera###############
run("diagnostic_cameras.py")

try:
    from future.EpicsPneumaticShutterFactory import EpicsPneumaticShutterFactory
    beamline = finder.find("Beamline")
    
    shtropen = EpicsPneumaticShutterFactory(beamline,
        "Branch Shutter", "-PS-SHTR-01", True)
    
    shtrclose = EpicsPneumaticShutterFactory(beamline,
        "Branch Shutter", "-PS-SHTR-01", False)
    
    gv12open = EpicsPneumaticShutterFactory(beamline,
        "GV 12", "I-VA-VALVE-12", True)
    
    gv12close = EpicsPneumaticShutterFactory(beamline,
        "GV 12", "I-VA-VALVE-12", False)
except:
    localStation_exception(sys.exc_info(), "creating shutter & valve objects")

try:
    th_off = epics_pds.EpicsReadWritePVClass('th_off', 'ME01D-MO-DIFF-01:THETA.OFF', 'deg', '%.6f')
    tth_off = epics_pds.EpicsReadWritePVClass('tth_off', 'ME01D-MO-DIFF-01:TWOTHETA.OFF', 'deg', '%.6f')
except:
    localStation_exception(sys.exc_info(), "creating th & tth offset and encoder offset scannables")

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
    add_default(meta)
    meta.quiet = True
    
except:
    localStation_exception(sys.exc_info(), "creating metadata objects")

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

###############################################################################
###                           Wait for beam device                          ###
###############################################################################
try:
    print "Adding checkbeam device (rc>190mA, 60s wait after beam back)"
    print "   (change threshold with checkrc.minumumThreshold=12345)"
    
    from gdascripts.scannable.beamokay import WaitWhileScannableBelowThreshold, WaitForScannableState
    from gda.device.scannable.scannablegroup import ScannableGroup
    
    checkrc = WaitWhileScannableBelowThreshold('checkrc', rc, 190, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5) #@UndefinedVariable
    checktopup_time = WaitWhileScannableBelowThreshold('checktopup_time', topup_time, 5, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5) #@UndefinedVariable
    checkfe = WaitForScannableState('checkfe', frontend, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=60) #@UndefinedVariable
    checkbeam = ScannableGroup('checkbeam', [checkrc, checkfe, checktopup_time])
    checkbeam.configure()
    
    checkrc_cv = WaitWhileScannableBelowThreshold('checkrc_cv', rc, 190, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5) #@UndefinedVariable
    checkrc_cv.setOperatingContinuously(True)
    checktopup_time_cv = WaitWhileScannableBelowThreshold('checktopup_time_cv', topup_time, 5, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5) #@UndefinedVariable
    checktopup_time_cv.setOperatingContinuously(True)
    checkfe_cv = WaitForScannableState('checkfe_cv', frontend, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=60) #@UndefinedVariable
    checkfe_cv.setOperatingContinuously(True)
    checkbeam_cv = ScannableGroup('checkbeam_cv', [checkrc_cv, checkfe_cv, checktopup_time_cv])
    checkbeam_cv.configure()
except:
    localStation_exception(sys.exc_info(), "creating checkbeam objects")

try:    
    print "Adding checkbeamcv device (add to cvscan to get checkbeam functionality)"

    from gda.device.scannable import PassthroughScannableDecorator
    
    class ZiePassthroughScannableDecorator(PassthroughScannableDecorator):

        def __init__(self, delegate):
            PassthroughScannableDecorator.__init__(self, delegate)  # @UndefinedVariable
    
        def getInputNames(self): 
            return []
    
        def getExtraNames(self): 
            return []
    
        def getOutputFormat(self):
            return []
    
        def getPosition(self):
            return None

    checkbeamcv = ZiePassthroughScannableDecorator(checkbeam_cv)
except:
    localStation_exception(sys.exc_info(), "creating checkbeamcv object")

try:
    from Diamond.PseudoDevices.EpicsDevices import EpicsDeviceClass
    gflow2=EpicsDeviceClass(name='gflow2', pvSet="BL10J-EA-TCTRL-02:GFLOW:SET", pvGet="BL10J-EA-TCTRL-02:GFLOW", pvStatus=None, strUnit="", strFormat="%.2f", timeout=None)
except:
    localStation_exception(sys.exc_info(), "creating gflow2 scannable")

from scan.miscan import miscan
alias("miscan")

print "*"*80
print "Attempting to run localStationUser.py from users script directory"
try:
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

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
from gdascripts.pd import epics_pds

# setup standard scans with processing
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
import gdascripts.utils #@UnusedImport
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals() 

def localStation_exception(exc_info, msg):
    typ, exception, traceback = exc_info
    handle_messages.simpleLog("! Failure %s !" % msg)
    handle_messages.log(None, "Error %s -  " % msg , typ, exception, traceback, False)

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
import gdascripts.pd.time_pds
wait = gdascripts.pd.time_pds.waittime

try:
    print "creating 'dummy' & `denergy` scannables"
    print ""
    dummy = DummyScannable("dummy")
    denergy = pgm_energy
except:
    localStation_exception(sys.exc_info(), "creating 'dummy' & 'denergy' scannables")

try:    
    # to delay scan points so they run afer a certain elapsed time
    from gdascripts.pd.time_pds import showtimeClass
    print ""
    print "creating scannable 'showtime' which will delay scan points until a time has been reached during a scan."
    print "usage of 'showtime' scan <motor> <start> <stop> <step> showtime 0 <delay between points in s>"
    print ""
    showtime = showtimeClass("showtime")
    showtime.setLevel(4) # so it is operated before anything else in a scan
except:
    localStation_exception(sys.exc_info(), "creating 'showtime' scannable")

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
    from high_field_magnet.scannable.intelligentTemperatureController import \
        IntelligentTemperatureControllerScannable
    #from scannable.CryojetScannable import CryojetScannable
    
    ips_field = IntelligentPowerSupplyFieldScannable('ips_field',
        'BL10J-EA-SMC-01:', field_tolerance=0.01)
    ips_sweeprate = IntelligentPowerSupplySweepRateScannable('ips_sweeprate',
        'BL10J-EA-SMC-01:', sweeprate_tolerance=0.01)
    #itc2 = CryojetScannable('itc2',
    itc2 = IntelligentTemperatureControllerScannable('itc2',
        'BL10J-EA-TCTRL-02:', temp_tolerance=1, stable_time_sec=60)
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

######## Import classes required for cameras ###############
from gdascripts.scannable.detector.ProcessingDetectorWrapper import \
      SwitchableHardwareTriggerableProcessingDetectorWrapper
from uk.ac.diamond.scisoft.analysis.io import TIFFImageLoader

######## Setting up the Andor Rasor camera ###############
andor_installed = False

if andor_installed:
    try: # Based in I16 configuration GDA-mt/configurations/i16-config/scripts/localStation.py at 3922edf
        global andor1det, andor1det_for_snaps, andor1GV12det, andor1GV12det_for_snaps

        # the andor has no hardware triggered mode configured. This class is used to hijack its DetectorSnapper implementation.
        andor = SwitchableHardwareTriggerableProcessingDetectorWrapper(
            'andor', andor1det, None, andor1det_for_snaps, [],
            panel_name=None, panel_name_rcp='Plot 1',
            toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
            fileLoadTimout=15, returnPathAsImageNumberOnly=True)
    
        #from scannable.adbase import ADTemperature
        #andortemp = ADTemperature('andortemp', andor1.getCollectionStrategy().getAdBase())
        #from scannable.andor import andor_trigger_output_enable, andor_trigger_output_disable
        #alias('andor_trigger_output_disable')
        #alias('andor_trigger_output_enable')
        #andor_trigger_output_enable()
    
        andorGV12 = SwitchableHardwareTriggerableProcessingDetectorWrapper(
            'andorGV12', andor1GV12det, None, andor1GV12det_for_snaps, [],
            panel_name=None, panel_name_rcp='Plot 1',
            toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
            fileLoadTimout=15, returnPathAsImageNumberOnly=True)
    
        def andorGV12openDelay(t_seconds = None):
            """Get or set the shutter close delay (in seconds) for the andor"""
            if t_seconds == None:
                return andor1GV12det.getCollectionStrategy().getShutterOpenDelay()
            andor1GV12det.getCollectionStrategy().setShutterOpenDelay(t_seconds)
        
        def andorGV12closeDelay(t_seconds = None):
            """Get or set the shutter close delay (in seconds) for the andor"""
            if t_seconds == None:
                return andor1GV12det.getCollectionStrategy().getShutterCloseDelay()
            andor1GV12det.getCollectionStrategy().setShutterCloseDelay(t_seconds)
        
        alias('andorGV12openDelay')
        alias('andorGV12closeDelay')
        
    except:
        localStation_exception(sys.exc_info(), "creating andor & andorGV12 objects")

######## Imports for the I10 Pimte and I06b Pixis cameras ###############
from gdascripts.scannable.detector.DetectorDataProcessor \
    import DetectorDataProcessor #, DetectorDataProcessorWithRoi

from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue \
    import SumMaxPositionAndValue

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak \
    import TwodGaussianPeak

######## Setting up the I10 Pimte camera ###############
pimte_installed = False

if pimte_installed:
    try: # Based in I16 configuration GDA-mt/configurations/i16-config/scripts/localStation.py at 3922edf
        global pimte1det, pimte1det_for_snaps

        # the pimte has no hardware triggered mode configured. This class is used to hijack its DetectorSnapper implementation.
        pimte = SwitchableHardwareTriggerableProcessingDetectorWrapper(
            'pimte', pimte1det, None, pimte1det_for_snaps, [],
            panel_name=None, panel_name_rcp='Plot 1',
            toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
            fileLoadTimout=15, returnPathAsImageNumberOnly=True)

        pimteSMPV = SwitchableHardwareTriggerableProcessingDetectorWrapper(
            'pimteSMPV', pimte1det, None, pimte1det_for_snaps,
            panel_name=None, panel_name_rcp='Plot 1',
            toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
            fileLoadTimout=15, returnPathAsImageNumberOnly=True)
        pimteSMPV.display_image = True
        #pimteSMPV.processors=[DetectorDataProcessorWithRoi('max', pimte1det, [SumMaxPositionAndValue()], False)]
        pimteSMPV.processors=[DetectorDataProcessor        ('max', pimte1det, [SumMaxPositionAndValue()], False)]

        pimte2d = SwitchableHardwareTriggerableProcessingDetectorWrapper(
            'pimte2d', pimte1det, None, pimte1det_for_snaps,
            panel_name=None, panel_name_rcp='Plot 1',
            toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
            fileLoadTimout=15, returnPathAsImageNumberOnly=True)
        pimte2d.display_image = True
        #pimteSMPV.processors=[DetectorDataProcessorWithRoi('max', pimte1det, [TwodGaussianPeak()], False)]
        pimte2d.processors=[DetectorDataProcessor        ('max', pimte1det, [TwodGaussianPeak()], False)]

    except:
        localStation_exception(sys.exc_info(), "creating pimte objects")

######## Setting up the I06 Pixis camera ###############
pixis_installed = True

if pixis_installed:
    try: # Based in I16 configuration GDA-mt/configurations/i16-config/scripts/localStation.py at 3922edf
        global pixis1det, pixis1det_for_snaps

        # the pixis has no hardware triggered mode configured. This class is used to hijack its DetectorSnapper implementation.
        pixis = SwitchableHardwareTriggerableProcessingDetectorWrapper(
            'pixis', pixis1det, None, pixis1det_for_snaps, [],
            panel_name=None, panel_name_rcp='Plot 1',
            toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
            fileLoadTimout=15, returnPathAsImageNumberOnly=True)
    
        pixisSMPV = SwitchableHardwareTriggerableProcessingDetectorWrapper(
            'pixisSMPV', pixis1det, None, pixis1det_for_snaps,
            panel_name=None, panel_name_rcp='Plot 1',
            toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
            fileLoadTimout=15, returnPathAsImageNumberOnly=True)
        pixisSMPV.display_image = True
        #pixisSMPV.processors=[DetectorDataProcessorWithRoi('max', pixis1det, [SumMaxPositionAndValue()], False)]
        pixisSMPV.processors=[DetectorDataProcessor        ('max', pixis1det, [SumMaxPositionAndValue()], False)]

        pixis2d = SwitchableHardwareTriggerableProcessingDetectorWrapper(
            'pixis2d', pixis1det, None, pixis1det_for_snaps,
            panel_name=None, panel_name_rcp='Plot 1',
            toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
            fileLoadTimout=15, returnPathAsImageNumberOnly=True)
        pixis2d.display_image = True
        #pixisSMPV.processors=[DetectorDataProcessorWithRoi('max', pixis1det, [TwodGaussianPeak()], False)]
        pixis2d.processors=[DetectorDataProcessor        ('max', pixis1det, [TwodGaussianPeak()], False)]

    except:
        localStation_exception(sys.exc_info(), "creating pixis objects")

######## Setting up the semi-automatic Zebra triggered cameras ###############
zebra_triggered_pimte_detector_installed = False

if zebra_triggered_pimte_detector_installed:
    from future.scannable.ZebraTriggeredDetector import ZebraTriggeredDetector
    in4ttl=10
    in3ttl=7
    setCollectionTimeInstructions = """    In addition:
        On the Main tab, as well as setting the exposure time, make sure that:
            Number of images is set to 1
            CCD Readout is set to Full
            Accumulations is set to 1
        On the Data File tab make sure that:
            The Data file is set to a suitable name and that it
            will be written to your visit directory
        On the ADC tab make sure that:
            Rate is set to 1MHz
        On the Timing tab make sure that:
            Mode is set to External Sync
            The Continuous Cleans checkbox is checked
            Shutter Control is Normal
            Safe mode is selected
            Delay time is 0.5seconds
            Edge trigger is + edge
    Also make sure that:
        The Zebra TTL Out 4 is connected to the ST-133 Ext Sync input
        The Zebra TTL In 4  is connected to the ST-133 NOT SCAN output
        The Zebra TTL In 3  is connected to the ST-133 NOT READY output"""
    prepareForCollectionInstructions="Please ensure that all acquisition parameters are correct before pressing the Acquire button."
    pimte = ZebraTriggeredDetector('pimte', zebra=zebra, 
        notScanInput=in4ttl, notReadyInput=in3ttl, triggerOutSoftInput=4,
        setCollectionTimeInstructions=setCollectionTimeInstructions,
        prepareForCollectionInstructions=prepareForCollectionInstructions)

zebra_triggered_pco_detector_installed = True

if zebra_triggered_pco_detector_installed:
    from future.scannable.ZebraTriggeredDetector import ZebraTriggeredDetector
    zebra=finder.find('zebra')
    in4ttl=10
    setCollectionTimeInstructions = "Setting collection time in Zebra"
    prepareForCollectionInstructions=None
    scanStartInstructions="""
    If you are having problems, or you are stuck only able to see this text:
        On the CamWare screen, make sure that:
            In Camera Control, teh Trigger mode is set to External Exp. Ctrl
        Then File menu > Direct Record To File,
            Set number of images to store as number of points in scan +1 or greater
            Set the name of the file for this scan.
    On the Zebra EDM screen (Launchers > Beamlines > BL10I BLADE > ZEB1) ensure that:
        On the SYS tab:
            OUT4 TTL is 55 (PULSE4)
        On the PULSE tab, ensure that:
            PULSE4 input is 63 (SOFT_IN4) and Trigger on Rising Edge
    Also make sure that:
        The Zebra TTL Out 4 is connected to the Camera exp. trig (control in)
        The Zebra TTL In 4  is connected to the Camera busy (status out)
        Ensure that the dip switches beneath the control in sockets are all set to ON"""
    pco = ZebraTriggeredDetector('pco', zebra=zebra, 
        notScanInput=in4ttl, notReadyInput=None, triggerOutSoftInput=4,
        setCollectionTimeInstructions=setCollectionTimeInstructions,
        prepareForCollectionInstructions=prepareForCollectionInstructions,
        scanStartInstructions=scanStartInstructions, 
        gateNotTrigger=True, notScanInverted=True, zebraPulse=4)

######## Setting up the Zebra as a fast dicriosm counter ###############
zebra_fastdicr_installed = True

if zebra_fastdicr_installed:
    from scannable.detectors.fastDicroismZebraDetector import FastDichroismZebraDetector
    global zebraContinuousMoveController
    #fastDichroism=FastDichroismZebraDetector('fastDichroism', 'BL10I-EA-ZEBRA-01:', zebraContinuousMoveController)
    fastDichroism=FastDichroismZebraDetector('fastDichroism', 'BL10I-EA-ZEBRA-01:', None)

polarimeter_installed = False
if polarimeter_installed:
    try:
        run("polarimeter/hexapodAxises4.py")        # /dls_sw/i10/scripts/polarimeter
        run("polarimeter/rotationTemperature.py")   # /dls_sw/i10/scripts/polarimeter
        run("polarimeter/detector.py")              # /dls_sw/i10/scripts/polarimeter
        run("polarimeter/feScannables.py")          # i10-config/scripts/polarimeter/feScannables.py
    except:
        localStation_exception(sys.exc_info(), "initialising polarimeter")

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
    th_enc_off = epics_pds.EpicsReadWritePVClass('th_off', 'ME01D-MO-ENCDR-01:ENCTHETA.OFF', 'deg', '%.6f')
    tth_enc_off = epics_pds.EpicsReadWritePVClass('tth_enc_off', 'ME01D-MO-ENCDR-01:ENC2THETA.OFF', 'deg', '%.6f')
except:
    localStation_exception(sys.exc_info(), "creating th & tth offset and encoder offset scannables")

# meta should be created last to ensure we have all required scannables
try:
    print '-'*80
    from gdascripts.scannable.installStandardScannableMetadataCollection import * #@UnusedWildImport
    meta.rootNamespaceDict=globals()
    note.rootNamespaceDict=globals()

    def stdmeta():
        stdmetadatascannables = (idd_gap, idd_rowphase1, idd_rowphase2,
                                 idd_rowphase3, idd_rowphase4, idd_jawphase,
                                 idd_sepphase,
                                 idu_gap, idu_rowphase1, idu_rowphase2,
                                 idu_rowphase3, idu_rowphase4, idu_jawphase,
                                 idu_sepphase,
                                 pgm_energy, s4xgap, s4ygap,
                                 th, tth, thp, ttp, eta, sx, sy, sz)
        
        if polarimeter_installed:
            stdmetadatascannables += (RetTilt, RetRotation, AnaTilt ,AnaRotation, 
                                 AnaDetector, AnaTranslation,hpx, hpy, hpc, hpb)
        stdmetadatascannables += (th_off, tth_off, th_enc_off, tth_enc_off)
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
    checktopup_time = WaitWhileScannableBelowThreshold('checktopup_time', rc, 30, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=30) #@UndefinedVariable
    checkfe = WaitForScannableState('checkfe', frontend, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=60) #@UndefinedVariable
    checkbeam = ScannableGroup('checkbeam', [checkrc, checkfe, checktopup_time])
    checkbeam.configure()
except:
    localStation_exception(sys.exc_info(), "creating checkbeam objects")

try:
    from Diamond.PseudoDevices.EpicsDevices import EpicsDeviceClass
    gflow2=EpicsDeviceClass(name='gflow2', pvSet="BL10J-EA-TCTRL-02:GFLOW:SET", pvGet="BL10J-EA-TCTRL-02:GFLOW", pvStatus=None, strUnit="", strFormat="%.2f", timeout=None)
except:
    localStation_exception(sys.exc_info(), "creating gflow2 scannable")

print "Attempting to run localStationUser.py for users script directory"
try:
    run("localStationUser")
    print "localStationUser.py completed."
    print "**************************************************"
except java.io.FileNotFoundException, e:
    print "No localStationUser run"
except:
    localStation_exception(sys.exc_info(), "running localStationUser user script")

print "**************************************************"
print "localStation.py completed."
print "**************************************************"

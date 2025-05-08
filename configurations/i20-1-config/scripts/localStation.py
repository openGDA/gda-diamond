from uk.ac.gda.exafs.ui.data import EdeScanParameters
from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from gdascripts.utils import caget, caput

from gda.jython.commands.ScannableCommands import cv as cvscan
from run_in_try_catch import run_in_try_catch
vararg_alias("cvscan")

run("gdascripts/javajythonutil.py")
run 'gdascripts/metadata/metadata_commands.py'
run("ede_scan_runner.py")
run("turboxas_scan_runner.py")
run("frelon-kinetic-roi-settings.py")
run("frelon-adc-status.py")
run("run_in_try_catch.py")
run("scannable-restorer.py")

if LocalProperties.isDummyModeEnabled() == False:
    run("shutter_functions.py")
    run("d10CentroidScannables.py")
    run("continuous_detector_scan.py")

das = Finder.find("DAServer")
das4tfg=Finder.find("daserverForTfg")

#Set flag used by ConcurrentScan so that scannables return to their original position at end of scan. 24/2/2016
scansReturnToOriginalPositions=1

# These scannables are checked before any scan data point
# You may comment them out to remove the checking.
if LocalProperties.get("gda.mode") == "live":
    if "frelon" in globals().keys() :
        run("frelon-functions.py")
        resetFrelonToInternalTriggerMode();

    # to speed up step scans
    LocalProperties.set("gda.scan.concurrentScan.readoutConcurrently","true")
    LocalProperties.set("gda.scan.multithreadedScanDataPointPipeline.length","10")

    noBeam = ["Shutdown", "No Beam", "Mach. Dev."]
    print "Machine mode = ", machineModeMonitor.getPosition()
    
    if machineModeMonitor.getPosition() in noBeam :
        print "Removing absorber, shutter and topup checkers"
        remove_default([absorberChecker])
        remove_default([shutterChecker])
        remove_default([topupChecker])
    else:
        add_default([absorberChecker])
        add_default([shutterChecker])


else:
    remove_default([absorberChecker])

add_default detectorMonitorDataProvider

# Setup metashop for writing metadata into Nexus file (TurboXas scans). imh 29/7/2016
from gda.data.scan.datawriter import NexusDataWriter
# Local property used by NexusDataWriter to store name of metadata object
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME, "metashop")
metashop = Finder.find("metashop")

# Misc. TurboXAS related beans
zebra_gatePulsePreparer=Finder.find("zebra_gatePulsePreparer")
zebra_device=Finder.find("zebra_device")
zebra_device2=Finder.find("zebra_device2")
trajscan_preparer=Finder.find("trajscan_preparer")

# Set bi-directional trajectory to use fixed runup/down distance
trajscan_preparer.setUseFixedTurnaroundDistance(True)
trajscan_preparer.setTurnaroundDistance(0.1)

#Copy encoder positions to zebra (in case any motors have been re-homed)
def setupZebras() :
    print "Copying encoder motor positions in Zebras"
    for zebra in [ zebra_device , zebra_device2 ]:
        zebra.encCopyMotorPosToZebra(1)
        zebra.encCopyMotorPosToZebra(2)
        zebra.encCopyMotorPosToZebra(3)
        zebra.encCopyMotorPosToZebra(4)


def setupTfg() :
    print "Stopping tfg and setting it to use scaler64 collection mode"
    das4tfg.sendCommand("tfg stop")
    das4tfg.sendCommand("tfg setup-cc-mode scaler64");
    
    # -- DAserver options for triggering XSpress3 ((TTL VETO 0)
    print "Setting Veto options for XSpress3"
    # veto signal : high veto signal when input is high
    das4tfg.sendCommand("tfg setup-veto veto0-inv 0")
    # veto output termination (see manual)
    das4tfg.sendCommand("tfg setup-veto veto0-drive 1")
    
    # Output trigger for ADC (TTL VETO 1)
    das4tfg.sendCommand("tfg setup-veto veto1-inv 0")
    das4tfg.sendCommand("tfg setup-veto veto1-drive 1")
    
    # Scaler channel input 0 : Record when input level is high (topup signal for TurboXas)
    das4tfg.sendCommand("tfg setup-cc-chan 0 level")

run_in_try_catch(setupTfg)
run_in_try_catch(setupZebras)

xspress3Controller = Finder.find("xspress3Controller")
# xspress3 = Finder.get("xspress3")

swmrFrameFlush = 5

def setup_detectors() :
    if LocalProperties.isDummyModeEnabled() :
        return

    if xspress3Controller != None and xspress3Controller.isConfigured() :
        print "Setting up XSpress3 : "
        print "  Trigger mode = 'TTL Veto Only'"
        from uk.ac.gda.devices.detector.xspress3 import TRIGGER_MODE
        xspress3Controller.setTriggerMode(TRIGGER_MODE.TTl_Veto_Only)
        #Set input array port on HDF5 plugin to point to arrayport of Detector. imh 7/8/2017
        basePvName = xspress3Controller.getEpicsTemplate()
        detPort = caget(basePvName+":PortName_RBV")
        print "  HDF5 array port name = ", detPort
        caput(basePvName+":HDF5:NDArrayPort", detPort)
        
        print "  HDF5 SWMR mode = On" 
        caput(basePvName+":HDF5:SWMRMode", True) # Set SWMR mode on.
        
        print "  HDF5 SWMR : Flush on nth frame, NDAttribute flush = ", swmrFrameFlush
        caput(basePvName+":HDF5:NumFramesFlush", swmrFrameFlush)
        caput(basePvName+":HDF5:NDAttributeChunk", swmrFrameFlush)
        
        xspress3.setFilePath("")
    
    if "frelon" in globals().keys() :
        print "Adding continuous scan commands for alignment slit : \n\trun_slit_scan(start, stop, step, accumulation_time, num_accumulations)\n\tplot_last_data()"
        run('alignment_stage_scan5.py')

run_in_try_catch(setup_detectors)

def setSwmrMode(onoff):
    caput(basePvName+":HDF5:SWMRMode", onoff)

# Set turboslit positions to use when operating as a 'shutter'. imh 21/4/2017
def setup_fast_shutter():
    if LocalProperties.get("gda.mode") == "live":
        setTurboSlitShutterPositions(0, 1)
        configureFastShutter()

run_in_try_catch(setup_fast_shutter)

# Set name of shutter to be operated when collecting dark current on ionchambers. imh 21/4/2017
LocalProperties.set("gda.exafs.darkcurrent.shutter", turbo_slit_shutter.getName())

# Make version of scalers with 'user friendly' name
ionchambers = scaler_for_zebra

# After restarting GDA servers. first call of 'BufferedScaler.clearMemory()' fails ("Ghist scaler_memory_zebra clear failed")
# Do it here to avoid first scan from throwing exception.
try :
    print "Clearing scaler memory"
    scaler_for_zebra.clearMemory()
except :
    pass
 
# Remove 'air bearing' from some scannables, so air is not automatically switched on/off for motor moves. 10/7/2018
sample_z.setAirBearingScannable(None)
stage3_z.setAirBearingScannable(None)
det_z.setAirBearingScannable(None)
twotheta.setAirBearingScannable(None)

openCloseShutterDuringScan.setSleepTimeMs(500)

print "Setting up 'scan_end_processor' to process data at end of scans"
run "ScanEndScriptRunner.py"
scan_end_processor=ScanEndScriptRunner("scan_end_processor", '/dls_sw/apps/dawn_autoprocessing/autoprocess' )
scan_end_processor.setProcessingOnOffPositioner(run_scan_end_processing)
add_default scan_end_processor

# Setup stanford amplifier power supply switcher (live mode only)
if LocalProperties.get("gda.mode") == "live":
    run "stanfordPowerSupplyOnOff.py"
    powerSupply = StanfordPowerOnOff("powerSupply")
    add_default powerSupply


print "\nReconnect daserver command : reconnect_daserver() "
def reconnect_daserver() :
    mem = scaler_for_zebra.getScaler()
    mem.close()
    sleep(1)
    daserverForTfg.close()
    sleep(1)
    print "Trying to reconnect to DAServer..."
    daserverForTfg.reconfigure();sleep(1);mem.clear()

# industrialGasRigValve.configure()

def setup_traj_scan_objects() :
    global trajscan_preparer
    trajscan_preparer = Finder.find("trajscan_preparer")
    global trajscan_controller
    trajscan_controller = Finder.find("trajscan_controller")
           
def setup_trajectory_profile(turboxas_xml_file_name) :
    """
        Calculate and setup turbo slit trajectory for set of TurboXasParameters loaded from xml file.
        After running this function, use execute_trajectory_scan() to execute the trajectory scan.
        
        Parameters :
            turboxas_xml_file_name - name of xml file containing the parameters (absolute path)
        
    """

    params = TurboXasParameters.loadFromFile(turboxas_xml_file_name)
    
    trajscan_preparer.clearTrajectoryLists()
    trajscan_preparer.setTwoWayScan(params.isTwoWayScan())
    trajscan_preparer.addPointsForTimingGroups(params.getMotorParameters())
    
    print("Trajectory positions : ")
    print(trajscan_preparer.getTrajectoryPositionsList())
    
    print("Trajectory times : ")
    print(trajscan_preparer.getTrajectoryTimesList())
    
    print("Trajectory velocity modes : ")
    print(trajscan_preparer.getTrajectoryVelocityModesList())

def execute_trajectory_scan() :
    print("Building trajectory scan points...")
    trajscan_preparer.sendAppendProfileValues()
    print("Executing trajectory scan")
    trajscan_controller.setExecuteProfile()

setup_traj_scan_objects()

trajscan_preparer.setDefaults() # set the default trajectory scan options

help(setup_trajectory_profile)

# Setup the data directory to point to old comissioning folder (directories for 2024, 2025 have not been created)
dir_path="/dls/i20-1/data/2023/cm33897-5/tmp"
print("Setting data directory to : {}".format(dir_path))
LocalProperties.set(LocalProperties.GDA_DATAWRITER_DIR, dir_path)

# Create (java) PandA scannables
run("panda_scannables_java.py")

run("continuous_detector_scan.py")

run("signal_generator.py")

run("blueapi_control.py")

# Set SWMR writing to True - so tgat Datavis allows live visualisation of scan data
LocalProperties.set(NexusDataWriter.GDA_NEXUS_SWMR, "true")

print("\nRemoving defaults")
for d in absorberChecker, shutterChecker, scan_end_processor, powerSupply :
    remove_default(d)


print("\n---- Finished running localStation.py ----\n")
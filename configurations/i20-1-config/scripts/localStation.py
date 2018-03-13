from uk.ac.gda.exafs.ui.data import EdeScanParameters
from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from gdascripts.utils import caget, caput

run("roi_control.py")
run("gdascripts/javajythonutil.py")
run("shutter_functions.py")

run("frelon_scan_runner.py")
run("turboxas_scan_runner.py")


finder = Finder.getInstance()
das = finder.find("DAServer")
das4tfg=finder.find("daserverForTfg")

#Set flag used by ConcurrentScan so that scannables return to their original position at end of scan. 24/2/2016
scansReturnToOriginalPositions=1

def machineMode():
    return caget("CS-CS-MSTAT-01:MODE")
# These scannables are checked before any scan data point
# You may comment them out to remove the checking.
if LocalProperties.get("gda.mode") == "live":
    if frelon != None :
        run("frelon-functions.py")
        resetFrelonToInternalTriggerMode();

    # to speed up step scans
    LocalProperties.set("gda.scan.concurrentScan.readoutConcurrently","true")
    LocalProperties.set("gda.scan.multithreadedScanDataPointPipeline.length","10")
    if (machineMode() == "No Beam"):
        del(shutter2)
        from gda.device.enumpositioner import DummyPositioner
        shutter2 = DummyPositioner()
        shutter2.setName("shutter2")
        shutter2.setPositions(['In','Out'])
        shutter2('In')
        remove_default([absorberChecker])
        remove_default([shutterChecker])
        remove_default([topupChecker])
    else:
        add_default([absorberChecker])
        add_default([shutterChecker])


else:
    remove_default([absorberChecker])

add_default detectorMonitorDataProvider

xstrip.start() #Call start so data and timing handles are set correctly. imh 16/12/2015


# Setup metashop for writing metadata into Nexus file (TurboXas scans). imh 29/7/2016
from gda.data.scan.datawriter import NexusDataWriter
# Local property used bye NexusDataWriter to store name of metadata object
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME, "metashop")
metashop = Finder.getInstance().find("metashop")

# Misc. TurboXAS related beans
zebra_gatePulsePreparer=finder.find("zebra_gatePulsePreparer")
zebra_device=finder.find("zebra_device")
trajscan_preparer=finder.find("trajscan_preparer")

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

xspress3Controller = finder.find("xspress3Controller")
# xspress3 = finder.get("xspress3")

swmrFrameFlush = 5
if xspress3Controller != None and LocalProperties.isDummyModeEnabled() == False:
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
    
        # Set hdf filewriter path to nexus folder in visit directory
    from gda.data import PathConstructor
    # outputDir = PathConstructor.getVisitDirectory()+"/nexus/"
    outputDir = PathConstructor.createFromDefaultProperty()+"/nexus/"
    print "Visit directory ", PathConstructor.getVisitDirectory()
    print "Default data directory ", PathConstructor.createFromDefaultProperty()
    #if "0-0" in  outputDir :
    #    reset_namespace
    
    print "  HDF file writer output directory : ", outputDir
    xspress3.setFilePath(outputDir)
    xspress3Controller.setFilePath(outputDir)


def setSwmrMode(onoff):
    caput(basePvName+":HDF5:SWMRMode", onoff)

# Set turboslit positions to use when operating as a 'shutter'. imh 21/4/2017
if LocalProperties.get("gda.mode") == "live":
    setTurboSlitShutterPositions(0, 1)
    configureFastShutter()

# Set name of shutter to be operated when collecting dark current on ionchambers. imh 21/4/2017
LocalProperties.set("gda.exafs.darkcurrent.shutter", turbo_slit_shutter.getName())

xstrip.setSynchroniseToBeamOrbit(True)

from gda.jython.commands.ScannableCommands import cv as cvscan
vararg_alias("cvscan")

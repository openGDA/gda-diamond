from uk.ac.gda.exafs.ui.data import EdeScanParameters

from gda.configuration.properties import LocalProperties
from gdascripts.utils import caget

run("roi_control.py")
run("gdascripts/javajythonutil.py")
run("shutter_functions.py")

run("frelon_scan_runner.py")
run("turboxas_scan_runner.py")


das = finder.find("DAServer")
das4tfg=finder.find("daserverForTfg")

#Set flag used by ConcurrentScan so that scannables return to their original position at end of scan. 24/2/2016
scansReturnToOriginalPositions=1

def machineMode():
    return caget("CS-CS-MSTAT-01:MODE")
# These scannables are checked before any scan data point
# You may comment them out to remove the checking.
if LocalProperties.get("gda.mode") == "live":
    run("frelon-functions.py")
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

    resetFrelonToInternalTriggerMode();

else:
    remove_default([absorberChecker])

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

# Set turboslit positions to use when operating as a 'shutter'. imh 21/4/2017
if LocalProperties.get("gda.mode") == "live":
    setTurboSlitShutterPositions(0, 1)
    configureFastShutter()

# Set name of shutter to be operated when collecting dark current on ionchambers. imh 21/4/2017
LocalProperties.set("gda.exafs.darkcurrent.shutter", turbo_slit_shutter.getName())



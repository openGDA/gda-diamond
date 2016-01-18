from uk.ac.gda.exafs.ui.data import EdeScanParameters

from gda.configuration.properties import LocalProperties
from gdascripts.utils import caget

run("roi_control.py")
run("gdascripts/javajythonutil.py")

das = finder.find("DAServer")
das4tfg=finder.find("daserverForTfg")

def machineMode():
    return caget("CS-CS-MSTAT-01:MODE")
# These scannables are checked before any scan data point
# You may comment them out to remove the checking.
if LocalProperties.get("gda.mode") == "live":
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
    else:
        add_default([absorberChecker])
        add_default([shutterChecker])
else:
    remove_default([absorberChecker])

xstrip.start() #Call start so data and timing handles are set correctly. imh 16/12/2015
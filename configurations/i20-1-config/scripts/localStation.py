from uk.ac.gda.exafs.ui.data import EdeScanParameters
from gda.configuration.properties import LocalProperties

run "roi_control"

das = finder.find("DAServer")

# These scannables are checked before any scan data point
# You may comment them out to remove the checking.
if LocalProperties.get("gda.mode") == "live":
    # to speed up step scans
    LocalProperties.set("gda.scan.concurrentScan.readoutConcurrently","true")
    LocalProperties.set("gda.scan.multithreadedScanDataPointPipeline.length","10")
    if (machineMode() == "No Beam"):
        remove_default([absorberChecker])
        remove_default([shutterChecker])
    else:
        add_default([absorberChecker])
        add_default([shutterChecker])
else:
    remove_default([absorberChecker])

from gda.device.scannable import ScannableBase
from org.slf4j import LoggerFactory

from gda.device.detector.countertimer import TfgScaler, TfgScalerWithFrames, TfgScalerWithDarkCurrent
from java.lang import Exception
import math
import datetime
from gda.jython import InterfaceProvider

print("\nRunning 'test-ionchamber-output.py")

""" Scannable to be used as base that can be used in a scan but doesn't produce any output data.
    Override atScanStart atScanEnd etc with suitable implementations. atScanEnd is called if an exception is thrown during the scan
"""

run('ionchamber-checker.py')

print("Creating 'ionchamberChecker' scannable to test ionchamber output")
ionchamberChecker = TestIonchamberReadout("ionchamberChecker")
ionchamberChecker.setTfg(counterTimer01)
ionchamberChecker.setCollectionTime(0.5)
ionchamberChecker.setFirstPointCollectionTime(0.25)
ionchamberChecker.setNumPoints(10);
ionchamberChecker.setfixIonchamberFunction(reconnect_daserver)

## Generate new metadata entry to show the results of the ion chamber checker
print("Adding metadata entry for ionchamberChecker test results to Ascii writer and Nexus configuration")
ionchamberCheckerMetadata = createAsciiMetaDataEntry("Ion chamber status : %s", [ionchamberChecker])
addMetaDataEntry(datawriterconfig, ionchamberCheckerMetadata)

metashop = Finder.find("metashop")
metashop.remove(ionchamberChecker.getName())
metashop.add(ionchamberChecker)


print("")
from gda.device.scannable import ScannableBase
from org.slf4j import LoggerFactory

from gda.device.detector.countertimer import TfgScaler, TfgScalerWithFrames, TfgScalerWithDarkCurrent
from java.lang import Exception
import math
import datetime
from gda.jython import InterfaceProvider
from __builtin__ import False
from uk.ac.gda.server.exafs.scan import DetectorPreparer

print("\nRunning 'test-ionchamber-output.py")

run('ionchamber-checker.py')

print "New reconnect daserver command : reconnect_daserver_new() "
def reconnect_daserver_new() :
    print "Closing connection to DAServer..."
    mem = ionchambers.getScaler()
    mem.close()
    sleep(1)
    DAServer.close()
    sleep(1)
    
    print "Trying to reconnect to DAServer..."
    DAServer.reconfigure()
    sleep(1)
    mem.clear()
    sleep(1)
    print "Finished"
    
class IonchamberDetectorPreparer(DetectorPreparer) :

    def __init__(self, ionchamberChecker):
        self.logger = LoggerFactory.getLogger("IonchamberDetectorPreparer")
        self.ionchamberChecker = ionchamberChecker
        self.runChecker = False

    def configure(self, scanBean, detectorBean, outputBean, experimentFullPath) :
        pass

    def setRunIonchamberChecker(self, tf):
        self.runChecker = tf

    def isRunIonchamberChecker(self):
        return self.runChecker

    def beforeEachRepetition(self):
        if not self.runChecker :
            return
        try :
            self.ionchamberChecker.atScanStart()
        except Exception as e :
            self.logger.warn("Problem running ion chamber checker", e)

    def completeCollection(self):
        pass

    def getExtraDetectors(self):
        return []

print("Creating 'ionchamberChecker' scannable to test ionchamber output")
ionchamberChecker = TestIonchamberReadout("ionchamberChecker")
ionchamberChecker.setTfg(ionchambers)
ionchamberChecker.setCollectionTime(0.5)
ionchamberChecker.setFirstPointCollectionTime(0.25)
ionchamberChecker.setNumPoints(10);
ionchamberChecker.setfixIonchamberFunction(reconnect_daserver_new)

## Generate new metadata entry to show the results of the ion chamber checker
print("Adding metadata entry for ionchamberChecker test results to Ascii writer and Nexus configuration")
ionchamberCheckerMetadata = createAsciiMetaDataEntry("Ion chamber status : %s", [ionchamberChecker])
addMetaDataEntry(datawriterconfig, ionchamberCheckerMetadata)
addMetaDataEntry(datawriterconfig_xes, ionchamberCheckerMetadata)

metashop.remove(ionchamberChecker.getName())
metashop.add(ionchamberChecker)


print("")
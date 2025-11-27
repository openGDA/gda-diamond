from gda.device.scannable import ScannableBase
from org.slf4j import LoggerFactory
from uk.ac.gda.server.exafs.scan import DetectorPreparerDelegate

from gda.device.detector.countertimer import TfgScaler, TfgScalerWithFrames, TfgScalerWithDarkCurrent
from java.lang import Exception
import math
import datetime
from gda.jython import InterfaceProvider
from __builtin__ import False
from uk.ac.gda.server.exafs.scan import DetectorPreparer

print("\nRunning 'ionchamber-checker.py")

run('ionchamber-checker.py')

print "New reconnect daserver command : reconnect_daserver_new() "
def reconnect_daserver_new() :
    print "Closing connection to DAServer..."
    mem = counterTimer01.getScaler()
    mem.close()
    sleep(1)
    mem.getDaServer().close()
    sleep(1)
    
    print "Trying to reconnect to DAServer..."
    mem.getDaServer().reconfigure()
    sleep(1)
    mem.clear()
    sleep(1)
    print "Finished"
    
class IonchamberDetectorPreparer(DetectorPreparer) :

    def __init__(self, ionchamberChecker):
        self.logger = LoggerFactory.getLogger("IonchamberDetectorPreparer")
        self.ionchamberChecker = ionchamberChecker
        self.runChecker = False
        self.rep_number = 0
        self.check_interval = 1 # 0 = off, 1 = run every rep,
        self.shutter = sample_shutter

    def configure(self, scanBean, detectorBean, outputBean, experimentFullPath) :
        self.rep_number = 0

    def setRunIonchamberChecker(self, tf):
        self.runChecker = tf

    def isRunIonchamberChecker(self):
        return self.runChecker

    def beforeEachRepetition(self):
        if self.check_interval <= 0 :
            return
        
        self.rep_number += 1

        if self.rep_number%self.check_interval != 1:
            return
        
        self.run_checker()
    
    def run_checker(self):
        try :
            self.move_shutter("Close")
            self.ionchamberChecker.atScanStart()
        except Exception as e :
            self.logger.warn("Problem running ion chamber checker", e)
        
        self.move_shutter("Open")
        
    def move_shutter(self,position):
        print("Moving {} to {}".format(self.shutter.getName(), position))
        #if beam_available() :
        self.shutter.moveTo(position)
        sleep(2)
        print("Shutter position : {}".format(self.shutter.getPosition()))
        
    def completeCollection(self):
        pass

    def getExtraDetectors(self):
        return []


print("Creating 'ionchamberChecker' scannable to test ionchamber output")
ionchamberChecker = TestIonchamberReadout("ionchamberChecker")
ionchamberChecker.setTfg(counterTimer01)
ionchamberChecker.setCollectionTime(0.5)
ionchamberChecker.setFirstPointCollectionTime(0.25)
ionchamberChecker.setNumPoints(5);
ionchamberChecker.setfixIonchamberFunction(reconnect_daserver_new)

checker_preparer = IonchamberDetectorPreparer(ionchamberChecker)
checker_preparer.check_interval = 1

det_preparer_delegates = DetectorPreparerDelegate()
det_preparer_delegates.setPreparers([checker_preparer])
det_preparer_delegates.setThrowExceptions(True)

detectorPreparer.setPreparerDelegates(det_preparer_delegates)

## Generate new metadata entry to show the results of the ion chamber checker
print("Adding metadata entry for ionchamberChecker test results to Ascii writer and Nexus configuration")
datawriterconfig = Finder.find("datawriterconfig")
metashop = Finder.find("metashop")

ionchamberCheckerMetadata = createAsciiMetaDataEntry("Ion chamber status : %s", [ionchamberChecker])
addMetaDataEntry(datawriterconfig, ionchamberCheckerMetadata)

metashop.remove(ionchamberChecker.getName())
metashop.add(ionchamberChecker)


print("")
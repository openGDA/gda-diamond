from gda.device.scannable import ScannableBase
from org.slf4j import LoggerFactory
from uk.ac.gda.server.exafs.scan import DetectorPreparerDelegate

from gda.device.detector.countertimer import TfgScaler, TfgScalerWithFrames, TfgScalerWithDarkCurrent
from java.lang import Exception
import math
import datetime
from gda.jython import InterfaceProvider
from uk.ac.gda.server.exafs.scan import DetectorPreparer

print("\nRunning 'ionchamber-checker.py")

run('ionchamber-checker.py')

print "New reconnect daserver command : reconnect_daserver_new() "
def reconnect_daserver_new() :
    print("Reconnecting to DAServer")
 
    print("Closing current connection to DAServer...")
    mem = counterTimer01.getScaler()
    mem.close()
    sleep(1)
    mem.getDaServer().close()
    sleep(1)
    
    print("Trying to reconnect to DAServer...")
    mem.getDaServer().reconfigure()
    sleep(1)
    mem.clear()
    sleep(1)
    print("Finished")

from time import time

class IonchamberDetectorPreparer(DetectorPreparer) :

    def __init__(self, ionchamberChecker):
        self.logger = LoggerFactory.getLogger("IonchamberDetectorPreparer")
        self.ionchamberChecker = ionchamberChecker
        self.runChecker = False
        self.rep_number = 0
        self.check_interval_mins = 30 # time interval between successive runs of the checker (minutes)
        self.time_of_last_check =  0.0
        self.shutter = sample_shutter

    def configure(self, scanBean, detectorBean, outputBean, experimentFullPath) :
        self.rep_number = 0

    def setRunIonchamberChecker(self, tf):
        self.runChecker = tf

    def isRunIonchamberChecker(self):
        return self.runChecker

    def beforeEachRepetition(self):
        if self.check_last_run_time():
            self.run_checker()
            self.time_of_last_check = time()
        
    def check_last_run_time(self): 
        time_since_last_check = (time() - self.time_of_last_check)/60.0
        print("Since since last check : %.1f minutes (check interval = %.0f minutes)"%(time_since_last_check, self.check_interval_mins))
        return time_since_last_check > self.check_interval_mins

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
checker_preparer.check_interval_mins = 30

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

from gda.device.scannable import TopupChecker

from org.slf4j import LoggerFactory
from gda.device.enumpositioner import ValvePosition


class TopupCheckerWithShutter(TopupChecker):
    
    def __init__(self, topupChecker):
        # Copy formatting from a topup checker
        self.copySettings(topupChecker)
        self.shutter = None
        self.logger = LoggerFactory.getLogger("TopupCheckerWithShutter")
    
    #Set the scannable to be closed during topup (and opened again aftwerwards)
    def setShutter(self, shutter):
        self.shutter = shutter
        
    # Copy setttings from another topupchecker
    def copySettings(self, topupChecker):
        self.setMachineModeMonitor(topupChecker.getMachineModeMonitor())
        self.setScannableToBeMonitored(topupChecker.getScannableToBeMonitored())

        self.setPauseBeforeScan(topupChecker.isPauseBeforeScan())
        self.setPauseBeforeLine(topupChecker.isPauseBeforeLine())
        self.setPauseBeforePoint(topupChecker.isPauseBeforePoint())
        
        self.setOutputFormat(topupChecker.getOutputFormat())
        self.setInputNames(topupChecker.getInputNames())
        self.setExtraNames(topupChecker.getExtraNames())
        self.setLevel(topupChecker.getLevel())
        
        self.setTimeout(topupChecker.getTimeout())
        self.setTolerance(topupChecker.getTolerance())
        self.setWaittime(topupChecker.getWaittime())
        self.setCollectionTime(topupChecker.getCollectionTime())
            
    def moveShutter(self, position):
        if self.shutter != None :
            self.sendAndPrintMessage("Moving "+self.shutter.getName()+" to '"+position+"' position")
            self.shutter.moveTo(position)
            self.sendAndPrintMessage(self.shutter.getName()+" move finished (position = "+str(self.shutter.getPosition())+")")
        
    def atPointStart(self):
        if self.pauseBeforePoint and self.machineIsRunning() and self.topupImminent() :
            
            self.sendAndPrintMessage("Preparing for topup ...")
            self.moveShutter(ValvePosition.CLOSE)
            self.testShouldPause()
            self.moveShutter(ValvePosition.OPEN)
            

topupChecker2 = TopupCheckerWithShutter(topupChecker)
topupChecker2.setName("topupChecker2")
topupChecker2.setShutter(photonshutter)
topupChecker2.configure()

for scn in get_defaults() :
    if scn.getName() == topupChecker2.getName() :
        remove_default(scn)

# Replace original topupChecker with the new one
remove_default(topupChecker)
add_default(topupChecker2)



# For testing in dummy mode
#topup.setFillTime(5.0)
#topup.setTopupInterval(30.0)
#machineModeMonitor.moveTo("User")

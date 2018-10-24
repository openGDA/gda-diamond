from gdascripts.scan import trajscans
from gdascripts.scan.scanListener import ScanListener
from org.slf4j import LoggerFactory

class TrajectoryControllerHelper(ScanListener):
    def __init__(self): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("TrajectoryControllerHelper")

    def prepareForScan(self):
        self.logger.info("prepareForScan()")

    def update(self, scanObject):
        self.logger.info("update(%r)" % scanObject)

 
trajscans.DEFAULT_SCANNABLES_FOR_TRAJSCANS = [meta] # @UndefinedVariable

trajectory_controller_helper = TrajectoryControllerHelper()

print "Creating gda cvscan commands:"
cvscan=trajscans.CvScan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
alias('cvscan') #@UndefinedVariable
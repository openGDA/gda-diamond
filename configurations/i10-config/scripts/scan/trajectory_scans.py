'''
Extracted from i10-config/scripts/scannable/continuous/try_continuous_energy.py in GDA 9.8
Created on 13 Apr 2018

@author: fy65
'''
from gdascripts.scan.scanListener import ScanListener
from org.slf4j import LoggerFactory
from gdascripts.scan import trajscans
from gdascripts.scannable.installStandardScannableMetadataCollection import meta
from gdascripts.scan.installStandardScansWithProcessing import scan_processor
from gda.jython.commands.GeneralCommands import alias 

class TrajectoryControllerHelper(ScanListener):
    def __init__(self): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("TrajectoryControllerHelper")

    def prepareForScan(self):
        self.logger.info("prepareForTracjectoryScan()")

    def update(self, scanObject):
        self.logger.info("update(%r)" % scanObject)

trajscans.DEFAULT_SCANNABLES_FOR_TRAJSCANS = [meta]

trajectory_controller_helper = TrajectoryControllerHelper()

print "-"*100
print "Creating I10 GDA 'trajcscan' and 'trajrscan' commands:"
trajcscan=trajscans.TrajCscan([scan_processor, trajectory_controller_helper]) 
trajrscan=trajscans.TrajRscan([scan_processor, trajectory_controller_helper]) 
alias('trajcscan')
alias('trajrscan')

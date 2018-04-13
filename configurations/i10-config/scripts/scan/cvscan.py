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
        self.logger.info("prepareForCVScan()")

    def update(self, scanObject):
        self.logger.info("update(%r)" % scanObject)


trajscans.DEFAULT_SCANNABLES_FOR_TRAJSCANS = [meta]

trajectory_controller_helper = TrajectoryControllerHelper()

print "-"*100
print "Creating I10 GDA cvscan commands:"
cvscan=trajscans.CvScan([scan_processor, trajectory_controller_helper]) 
alias('cvscan')

# E.g. cvscan egy 695 705 1 mcs1 2 mcs17 2 mcs16 2

""" Tests Results:
    10ev at 2 seconds per 1ev 'step & 10ev at .2 seconds per .1ev 'step:

    scan pgm_energy 695 705 1 macr1 macr16 macr17 2       11 points, 28 seconds (18:32:36 to 18:33:24)
    scan pgm_energy 695 705 .1 macr1 macr16 macr17 .2    101 points, 3 minutes 15 seconds (18:35:57 to 18:39:12
    
    cvscan egy 695 705 1 mcs1 mcs16 mcs17 2                11 points, 34 seconds (18:41:48 to 18:42:22)
    cvscan egy 695 705 .1 mcs1 mcs16 mcs17 .2            101? points, 36 seconds (18:45:09 to 18:45:45)
"""
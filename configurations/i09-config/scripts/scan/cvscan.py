'''
Extracted from i10-config/scripts/scannable/continuous/try_continuous_energy.py in GDA 9.8
Created on 13 Apr 2018

@author: fy65
'''
from gdascripts.scan.scanListener import ScanListener
from org.slf4j import LoggerFactory
from gdascripts.scan import trajscans
from gdascripts.scan.installStandardScansWithProcessing import scan_processor
from gda.jython.commands.GeneralCommands import alias 
from scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from numbers import Number

from utils.ExceptionLogs import localStation_exception
import sys

class TrajectoryControllerHelper(ScanListener):
    def __init__(self): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("TrajectoryControllerHelper")
        self.original_default_scannables=[]
        self.energy=None
        self.wfs=None

    def prepareForScan(self):
        self.logger.info("prepareForCVScan()")
        #remove default scannables as they cannot work with cvscan
        from gda.jython.commands.ScannableCommands import get_defaults, remove_default
        default_scannables = get_defaults()
        self.logger.debug("remove original default scannables: %r from default" % default_scannables)
        for scn in default_scannables:
            self.original_default_scannables.append(scn)
            remove_default(scn)
            
    def update(self, scanObject):
        self.logger.info("update(%r)" % scanObject)
        # restore default scannables after cvscan completed.
        if self.original_default_scannables is not None:
            from gda.jython.commands.ScannableCommands import add_default
            self.logger.debug("add original default scannables %r to default" % self.original_default_scannables)
            for scn in self.original_default_scannables:
                add_default(scn)
        else:
            self.logger.debug("original default scannables is empty!")
                              
trajectory_controller_helper = TrajectoryControllerHelper()
cvscan_traj=trajscans.CvScan([scan_processor, trajectory_controller_helper]) 

print "-"*100
print "Creating I09 GDA 'cvscan' commands: "

def cvscan(c_energy, start, stop, step, *args):
    ''' cvscan that checks if there is enough time to collect data before topup when 'checkbeamcv' is used.
    '''
    wfs=[]
    dwell=[]
    others=[]
    beam_checker=None
    newargs=[c_energy, start, stop, step]
    try:
        for arg in args:
            if isinstance(arg, WaveformChannelScannable):
                wfs.append(arg)
            elif isinstance(arg, Number):
                dwell.append(arg)
            elif arg.getName() == "checkbeam":
                beam_checker=arg
            else:
                others.append(arg)
        if not checkContentEqual(dwell):
            raise Exception("dwell time specified must be equal for all detectors!")
        for each in wfs:
            newargs.append(each)
            newargs.append(dwell[0]) #the pull stream code require every channel have dwell time even they are on the same EPICS scaler
        for other in others:
            newargs.append(other)
        if beam_checker is not None:
            #check if there is enough time for the cvscan before top_up
            scanTime=abs((stop-start)/step*dwell[0])
            topup_checker=beam_checker.getGroupMember("checktopup_time")
            topup_checker.setOperatingContinuously(True) #only check at scan start
            topup_checker.minimumThreshold=scanTime + 5
    #         print "topup_checker.minimumThreshold = %r" % (topup_checker.minimumThreshold)
            newargs.append(beam_checker)

        trajectory_controller_helper.energy=c_energy
        trajectory_controller_helper.wfs=wfs
        cvscan_traj([e for e in newargs])
    except:
        localStation_exception(sys.exc_info(), "cvscan exits with Error.")

alias('cvscan')
   
def checkContentEqual(lst):
    return lst[1:] == lst[:-1]


# E.g. cvscan cenergy 695 705 0.1 mcs3 0.1 mcs4 0.1 mcs5 0.1

""" Tests Results from I10:
    10ev at 2 seconds per 1ev 'step & 10ev at .2 seconds per .1ev 'step:

    scan pgm_energy 695 705 1 macr1 macr16 macr17 2       11 points, 28 seconds (18:32:36 to 18:33:24)
    scan pgm_energy 695 705 .1 macr1 macr16 macr17 .2    101 points, 3 minutes 15 seconds (18:35:57 to 18:39:12
    
    cvscan egy 695 705 1 mcs1 mcs16 mcs17 2                11 points, 34 seconds (18:41:48 to 18:42:22)
    cvscan egy 695 705 .1 mcs1 mcs16 mcs17 .2            101? points, 36 seconds (18:45:09 to 18:45:45)
"""
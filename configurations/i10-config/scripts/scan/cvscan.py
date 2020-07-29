'''
A simplified version of cvscan - which does not support old 'egy_g' and 'egy' scannable any more.

Created on 28 July 2020

@author: fy65
'''
from numbers import Number
import sys

from gda.jython.commands.GeneralCommands import alias 
from gdascripts.scan import trajscans
from gdascripts.scan.installStandardScansWithProcessing import scan_processor
from gdascripts.scan.scanListener import ScanListener
from org.slf4j import LoggerFactory
from scannable.checkbeanscannables import ZiePassthroughScannableDecorator
from scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from utils.ExceptionLogs import localStation_exception


class TrajectoryControllerHelper(ScanListener):
    def __init__(self): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("TrajectoryControllerHelper")
        self.original_default_scannables=[]

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

print("-"*100)
print("Creating I10 GDA 'cvscan' commands: - dwell time must apply to all waveform scannables individually!")

def cvscan(c_energy, start, stop, step, *args):
    ''' parse arguments and set scan time required to collect data before topup when 'checkbeamcv' is used.
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
            elif isinstance(arg, ZiePassthroughScannableDecorator):
                beam_checker=arg
            else:
                others.append(arg)
        if not checkContentEqual(dwell):
            raise ValueError("dwell time specified must be equal for all detectors!")
        for each in wfs:
            newargs.append(each)
            newargs.append(dwell[0]) #the pull stream code require every channel have dwell time even they are on the same EPICS scaler
        for other in others:
            newargs.append(other)
        if beam_checker is not None:
            #set time required for cvscan before topup
            scan_time=abs((stop-start)/step*dwell[0])
            topup_checker=beam_checker.getDelegate().getGroupMember("checktopup_time_cv")
            topup_checker.minimumThreshold=scan_time + 5
            newargs.append(beam_checker)

        cvscan_traj([e for e in newargs])
    except:
        localStation_exception(sys.exc_info(), "cvscan exits with Error.")

alias('cvscan')
   
def checkContentEqual(lst):
    return lst[1:] == lst[:-1]


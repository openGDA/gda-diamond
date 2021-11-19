'''
define 'cvscan' that parses input arguments and setup topup checker if present before scanning

@author: fy65
@since: 25 August 2020
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
from gdascripts.utils import caput
import installation

EPICS_FEEDBACK_PV = "BL21I-OP-MIRR-01:FBCTRL:MODE"

class TrajectoryControllerHelper(ScanListener):
    def __init__(self, pvName=None): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("TrajectoryControllerHelper")
        self.original_default_scannables=[]
        self.pvName = pvName

    def prepareForScan(self):
        self.logger.info("prepareForCVScan()")
        #remove default scannables as they cannot work with cvscan
        from gda.jython.commands.ScannableCommands import get_defaults, remove_default
        default_scannables = get_defaults()
        self.logger.debug("remove original default scannables: %r from default" % default_scannables)
        for scn in default_scannables:
            self.original_default_scannables.append(scn)
            remove_default(scn)
        if self.pvName:
            caput(self.pvName, 0) 
            
    def update(self, scan_object):
        self.logger.info("update(%r)" % scan_object)
        # restore default scannables after cvscan completed.
        if self.original_default_scannables is not None:
            from gda.jython.commands.ScannableCommands import add_default
            self.logger.debug("add original default scannables %r to default" % self.original_default_scannables)
            for scn in self.original_default_scannables:
                add_default(scn)
        else:
            self.logger.debug("original default scannables is empty!")
        if self.pvName:
            caput(self.pvName, 4) 
            
if installation.isLive():
    trajectory_controller_helper = TrajectoryControllerHelper(pvName=EPICS_FEEDBACK_PV)
else:
    trajectory_controller_helper = TrajectoryControllerHelper()
    
cvscan_traj=trajscans.CvScan([scan_processor, trajectory_controller_helper]) 

print("-"*100)
print("Creating I21 GDA 'cvscan' commands: ")

def cvscan(c_energy, start, stop, step, *args):
    ''' cvscan that checks if there is enough time to collect data before topup when 'checkbeam' is used.
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
            raise RuntimeError("dwell time specified must be equal for all detectors!")
        for each in wfs:
            newargs.append(each)
            newargs.append(dwell[0]) #the pull stream code require every channel have dwell time even they are on the same EPICS scaler
        for other in others:
            newargs.append(other)
        if beam_checker is not None:
            #check if there is enough time for the cvscan before top_up
            scan_time=abs((stop-start)/step*dwell[0])
            topup_checker=beam_checker.getGroupMember("checktopup_time")
            topup_checker.setOperatingContinuously(True) #only check at scan start
            topup_checker.minimumThreshold=scan_time + 5
            newargs.append(beam_checker)
        cvscan_traj([e for e in newargs])
    except:
        localStation_exception(sys.exc_info(), "cvscan exits with Error.")

alias('cvscan')
   
def checkContentEqual(lst):
    return lst[1:] == lst[:-1]

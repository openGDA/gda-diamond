'''
create functions to parse cvscan commands for continuous energy moving scan.

@author: fy65
'''
from gdascripts.scan.scanListener import ScanListener
from org.slf4j import LoggerFactory
from gdascripts.scan import trajscans
from gdascripts.scan.installStandardScansWithProcessing import scan_processor
from gda.jython.commands.GeneralCommands import alias # @UnresolvedImport
from i09shared.scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from numbers import Number

from i09shared.utils.ExceptionLogs import localStation_exception
import sys

from gda.configuration.properties import LocalProperties # @UnresolvedImport
BEAMLINE = LocalProperties.get("gda.beamline.name")
if BEAMLINE == "i09" or BEAMLINE == "i09-2":
    from i09_2_shared.scannable.continuous.jenergy_scannable_instances import jenergy_move_controller # @UnresolvedImport
if BEAMLINE == "i09" or BEAMLINE == "i09-1":
    from i09_1_shared.scannable.continuous.ienergy_scannable_instances import ienergy_move_controller # @UnresolvedImport

class TrajectoryControllerHelper(ScanListener):
    def __init__(self): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("TrajectoryControllerHelper")
        self.original_default_scannables=[]

    def prepareForScan(self):
        self.logger.info("prepareForCVScan()")
        #remove default scannables as they cannot work with cvscan
        from gda.jython.commands.ScannableCommands import get_defaults, remove_default # @UnresolvedImport
        default_scannables = get_defaults()
        self.logger.debug("remove original default scannables: %r from default" % default_scannables)
        for scn in default_scannables:
            self.original_default_scannables.append(scn)
            remove_default(scn)
            
    def update(self, scan_object):
        self.logger.info("update(%r)" % scan_object)
        # restore default scannables after cvscan completed.
        if self.original_default_scannables is not None:
            from gda.jython.commands.ScannableCommands import add_default # @UnresolvedImport
            self.logger.debug("add original default scannables %r to default" % self.original_default_scannables)
            for scn in self.original_default_scannables:
                add_default(scn)
        else:
            self.logger.debug("original default scannables is empty!")
                              
trajectory_controller_helper = TrajectoryControllerHelper()
cvscan_traj=trajscans.CvScan([scan_processor, trajectory_controller_helper]) 

print ("-"*100)
print ("Creating I09 GDA 'cvscan' command")
print("")

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
                if c_energy.getName() == 'jenergy':
                    arg.setHardwareTriggerProvider(jenergy_move_controller)
                elif c_energy.getName() == 'ienergy':
                    arg.setHardwareTriggerProvider(ienergy_move_controller)
                else:
                    raise RuntimeError("cvscan only works with 'ienergy' or 'jenergy' for continuous energy moving scan!")
            elif isinstance(arg, Number):
                dwell.append(arg)
            elif arg.getName() == "checkbeam":
                beam_checker=arg
            else:
                others.append(arg)
        if not check_content_equal(dwell):
            raise RuntimeError("dwell time specified must be equal for all detectors!")
        
        print(wfs, dwell)
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
   
def check_content_equal(lst):
    return lst[1:] == lst[:-1]

'''
'cvscan' - constant velocity scanning of energy. 
It parses input parameters and setup topup checker if present before scanning before delegating the scanning to trajscans.

It is specialized to including control of feedback PV before and after the continuous energy motion.

@author: fy65
@since: 25 August 2020
'''
from numbers import Number
import sys

from gda.jython.commands.GeneralCommands import alias 
from gdascripts.scan import trajscans
from gdascripts.scan.installStandardScansWithProcessing import scan_processor
from gdascripts.scan.scanListener import ScanListener
from org.slf4j import LoggerFactory
from gda.device.scannable.scannablegroup import ScannableGroup
from scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from utils.ExceptionLogs import localStation_exception
from gda.factory import Finder
from gda.observable import IObserver
from gdascripts.utils import caput
import installation
from gda.device import Scannable
from types import FloatType, IntType
from time import sleep
from gdascripts.metadata.nexus_metadata_class import meta

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
            self.original_default_scannables =[]
        else:
            self.logger.debug("original default scannables is empty!")
        if self.pvName:
            caput(self.pvName, 4) 
            
if installation.isLive():
    trajectory_controller_helper = TrajectoryControllerHelper(pvName=EPICS_FEEDBACK_PV)
else:
    trajectory_controller_helper = TrajectoryControllerHelper()
    
cvscan_traj=trajscans.CvScan([scan_processor, trajectory_controller_helper]) 

id_access_control = Finder.find("idblena")

from gda.epics.IAccessControl import Status 
class IDAccessObserver(IObserver):
    def __init__(self, id_access_control):
        self.id_control = id_access_control
        self.status = Status.ENABLED  # @UndefinedVariable
        id_access_control.addIObserver(self)

    def update(self, source, arg):
        if source == self.id_control:
            self.status = arg

    def getStatus(self):
        return self.status

id_access_observer = IDAccessObserver(id_access_control)

print("-"*100)
print("Creating I21 GDA 'cvscan' commands. ")

def cvscan(c_energy, start, stop, step, *args):
    ''' cvscan that checks if there is enough time to collect data before topup when 'checkbeam' is used.
    '''
    command = "cvscan "
    wfs=[]
    dwell=[]
    others=[]
    beam_checker=None
    newargs=[c_energy, start, stop, step]
    command += c_energy.getName() + " " + " ".join(map(str, newargs[1:])) + " "
    for arg in args:
        if isinstance(arg, WaveformChannelScannable):
            wfs.append(arg)
        elif isinstance(arg, Number):
            dwell.append(arg)
        elif isinstance(arg, ScannableGroup) and arg.getName() == "checkbeam":
            beam_checker=arg
        else:
            others.append(arg)
    if not checkContentEqual(dwell):
        raise ValueError("dwell time specified must be equal for all detectors!")
    for each in wfs:
        newargs.append(each)
        command += each.getName() + " "
        newargs.append(dwell[0]) #the pull stream code require every channel have dwell time even they are on the same EPICS scaler
        command += str(dwell[0]) + " "
    for other in others:
        newargs.append(other)
        if isinstance(other, Scannable):
            command += other.getName() + " "
        if type(other)==IntType or type(other)== FloatType:
            command += str(other) + " "
    if beam_checker is not None:
        #check if there is enough time for the cvscan before top_up
        scan_time=abs((stop-start)/step*dwell[0])
        topup_checker=beam_checker.getGroupMember("checktopup_time")
        topup_checker.setOperatingContinuously(True) #only check at scan start
        topup_checker.minimumThreshold=scan_time + 5
        newargs.append(beam_checker)
        command += beam_checker.getName()
        
        first_time = True
        while id_access_observer.getStatus() == Status.DISABLED:  # @UndefinedVariable
            if first_time:
                print("Waiting for ID access from beamline to be enabled by Main Control Room, Tel: 8899")
                first_time = False
            sleep(5)
               
    meta.addScalar("user_input", "command", command)
    try:
        cvscan_traj([arg for arg in newargs])
    except Exception as e:
        localStation_exception(sys.exc_info(), "cvscan exits with Error: %s" % (e))
    finally:
        meta.rm("user_input", "command")

alias('cvscan')
   
def checkContentEqual(lst):
    return lst[1:] == lst[:-1]

#cvscan testing 
# cvscan energy 695 705 1 draincurrent_c 0.1 diff1_c 0.1 m4c1_c 0.1 fy2_c 0.1
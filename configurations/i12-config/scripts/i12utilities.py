from gdascripts.messages import handle_messages
from gda.data import NumTracker
import os
from gda.data import PathConstructor
from gda.factory import Finder
import sys
import gda.device.scannable.DummyScannable
from gda.configuration.properties import LocalProperties
import subprocess
from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names, vararg_alias
from time import sleep
from gda.jython.commands import GeneralCommands
from gda.epics import CAClient
from epics_scripts.pv_scannable_utils import caputStringAsWaveform
from gdascripts.metadata.metadata_commands import meta_add, meta_ll, meta_ls, meta_rm
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gda.jython.commands import ScannableCommands
from gda.jython import Jython
from gdascripts.utils import caput, caget

# set up a nice method for getting the latest file path
i12NumTracker = NumTracker("i12");
finder = Finder.getInstance()
ca=CAClient()

def wd():
    dir = PathConstructor.createFromDefaultProperty()
    return dir
    


# function to find the last file path
def pwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i12NumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber))
    


# function to find the next file path
def nwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i12NumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber + 1))
    
# function to find the next scan number
def nfn():
    filenumber = i12NumTracker.getCurrentFileNumber();
    return filenumber + 1
    
# function to find the next scan number
def cfn():
    filenumber = i12NumTracker.getCurrentFileNumber();
    return filenumber
    

# the subdirectory parts
def setSubdirectory(dirname):
    try:
        finder.find("GDAMetadata").setMetadataValue("subdirectory", dirname)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem setting metadata value for 'subdirectory' to " + dirname, exceptionType, exception, traceback, False)
        print "Failed to set metadata value for 'subdirectory' to:", dirname, exception
        

def getSubdirectory():
    try:
        return finder.find("GDAMetadata").getMetadataValue("subdirectory")
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem getting metadata value for 'subdirectory' ", exceptionType, exception, traceback, False)
        print "Failed to get metadata value for 'subdirectory':", exception
        return None
        

from gda.data.metadata import GDAMetadataProvider
def getVisit():
    """
    Returns string representing current visit ID, eg cm4963-2
    """
    try:
        gdaMetaProvider=GDAMetadataProvider.getInstance()
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem getting GDA metadata provider", exceptionType, exception, traceback, False)
        print "Failed to get GDA metadata provider:", exception
    return gdaMetaProvider.getMetadataValue(GDAMetadataProvider.EXPERIMENT_IDENTIFIER)

def rreplace(s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

def getVisitRootPath():
    """
    Returns string representing current visit root path, eg /dls/i12/data/2014/cm4963-2
    """
    try:
        subDirname = finder.find("GDAMetadata").getMetadataValue("subdirectory")
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem getting metadata value for 'subdirectory' ", exceptionType, exception, traceback, False)
        print "Failed to get metadata value for subdirectory:", exception
    workDirpath = wd()
    if (subDirname is not None) and (subDirname != ""):
        visitRootpath = rreplace(workDirpath, os.sep+subDirname,"",1)
    else:
        visitRootpath = workDirpath
    return visitRootpath
    
    
def setDataWriterToNexus():
    oldDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusDataWriter")
    newDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    print "Old DataWriter: ", oldDW
    print "New DataWriter: ", newDW
    
def setDataWriterToSrs():
    oldDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    LocalProperties.set("gda.data.scan.datawriter.dataFormat", "SrsDataFile")
    newDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    print "Old DataWriter: ", oldDW
    print "New DataWriter: ", newDW
    
def getDataWriter():
    return LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    
class DocumentationScannable(gda.device.scannable.DummyScannable):
    def __init__(self, name, mesg, url=None):
        super(DocumentationScannable, self).__init__(name)
        self.mesg = mesg
        self.url = url
        pass
    
    def __doc__(self):
        hSC = finder.find("helpScriptController")
        if self.url != None and hSC != None:
            #subprocess.Popen(['python2.6', '-m', 'webbrowser', '-t', self.url])
            hSC.update(hSC, "URL:" + `self.url`)
        return self.mesg

def ls_scannables():
    ls_names(Scannable)
    

def setUpCopyPluginForPCO():
    print "setting up cpy plugin for PCO"
    ca.caput( "BL12I-EA-DET-02:COPY:Run", 0)
    ca.caputStringAsWaveform( "BL12I-EA-DET-02:COPY:SourceFilePath", "d:\\i12\\data\\2014")
    ca.caputStringAsWaveform( "BL12I-EA-DET-02:COPY:DestFilePath", "t:\\i12\\data\\2014")
    ca.caput ("BL12I-EA-DET-02:COPY:Run", 1)


def setUpCopyPluginForPIXIUM():
    print "setting up cpy plugin for PIXIUM"
    ca.caput( "BL12I-EA-DET-10:FILECOPY:Run", 0)
    ca.caputStringAsWaveform( "BL12I-EA-DET-10:FILECOPY:SourceFilePath", "d:\\i12\\data\\2014")
    ca.caputStringAsWaveform( "BL12I-EA-DET-10:FILECOPY:DestFilePath", "t:\\i12\\data\\2014")
    ca.caput ("BL12I-EA-DET-10:FILECOPY:Run", 1)

from gda.jython import InterfaceProvider
from gda.device.scannable import EpicsScannable
def createScannableFromPV( name, pv, addToNameSpace=True, getAsString=True, hasUnits=False):
    """
    Description:
        utility function to create a scannable from a given PV
    Arguments:
        name - user-specified name of a scannable to be created, e.g. pixium10_DataType
        pv - EPICS identifier of pv to be used by the scannable, e.g. BL12I-EA-DET-10:CAM:DataType
        addToNameSpace = if True, the scannable is accessible from the commandline after the call
        getAsString - If True, output value is a string (useful for enum pv, in which case set getAsString=True, and set hasUnits=False)
        hasUnits - If False, output value is not converted to units - useful for enum pv with getAsString=True
    
    For example,
        createScannableFromPV("pixium10_DataType", "BL12I-EA-DET-10:CAM:DataType", True, True, False)
    creates a scannable for pv with the following enums:
    caget -d 31 BL12I-EA-DET-10:CAM:DataType
        BL12I-EA-DET-10:CAM:DataType
        Native data type: DBF_ENUM
        Request type:     DBR_CTRL_ENUM
        Element count:    1
        Value:            UInt32
        Status:           NO_ALARM
        Severity:         NO_ALARM
        Enums:            ( 8)
                          [ 0] Int8
                          [ 1] UInt8
                          [ 2] Int16
                          [ 3] UInt16
                          [ 4] Int32
                          [ 5] UInt32
                          [ 6] Float32
                          [ 7] Float64
    """
    sc = EpicsScannable()
    sc.setName(name)
    sc.setPvName(pv)
    sc.setUseNameAsInputName(True)
    sc.setGetAsString(getAsString)
    sc.setHasUnits(hasUnits)
    sc.afterPropertiesSet()
    sc.configure()
    if addToNameSpace:
        commandServer = InterfaceProvider.getJythonNamespace()
        commandServer.placeInJythonNamespace(name,sc)
    return sc

try:
    s4 = finder.find("s4")
    t5 = finder.find("t5")
    ss2 = finder.find("ss2")    #t6
    t7 = finder.find("t7")
    t8 = finder.find("t8")
#    t9 = finder.find("t9")
except:
    exceptionType, exception, traceback = sys.exc_info()
    msg = "Unable to find an EH2-specific scannable: "
    handle_messages.log(None, msg, exceptionType, exception, traceback, False)

_meta_scannables_EH2 = []
_meta_scannables_EH2.append(s4)
_meta_scannables_EH2.append(t5)
_meta_scannables_EH2.append(ss2) #t6
_meta_scannables_EH2.append(t7)
_meta_scannables_EH2.append(t8)


def meta_add_EH2():
    """
    Function to add EH2-specific objects to meta scannables: s4, t5, ss2 (t6), t7, t8.
    """
    for s in _meta_scannables_EH2:
        print s.name
        meta_add(s)
    #print "\n ***List of all currently selected meta scannables (to be recorded once per scan in the 'before_scan' group of scan Nexus file):"
    #infoAllMetaScannables_i12 = meta_ls()
    #print infoAllMetaScannables_i12

def meta_rm_EH2():
    """
    Function to remove EH2-specific objects from meta scannables: s4, t5, ss2 (t6), t7, t8.
    """
    for s in _meta_scannables_EH2:
        meta_rm(s)
    #print "\n ***List of all currently selected meta scannables (to be recorded once per scan in the 'before_scan' group of scan Nexus file):"
    #infoAllMetaScannables_i12 = meta_ls()
    #print infoAllMetaScannables_i12

_hostname_EH2 = []
_hostname_EH2.append("i12-ws008.diamond.ac.uk")
_hostname_EH2.append("i12-ws009.diamond.ac.uk")
_hostname_EH2.append("i12-ws0010.diamond.ac.uk")

#from socket import gethostname

#def get_hostname():
#    return os.getenv('HOSTNAME')
#    return socket.gethostname()

#def is_hostname_in_EH2():
#    return get_hostname() in _hostname_EH2

def isLive():
    mode = LocalProperties.get("gda.mode")
    return mode =="live" or mode =="live_localhost"


def clear_defaults():
    """To clear all current default scannables."""
    srv = finder.findSingleton(Jython)
    all_vec = srv.getDefaultScannables()
    all_arr = all_vec.toArray()
    for s in all_arr:
        #srv.removeDefault(s)
        ScannableCommands.remove_default(s)
    return all_arr
alias("clear_defaults")

def i12tomoFlyScan(description="Hello World", inBeamPosition=0.,outOfBeamPosition=1., exposureTime=.05, start=0., stop=180., step=.1, imagesPerDark=20, imagesPerFlat=20, extraFlatsAtEnd=False, closeShutterAfterScan=False, vetoFlatsDarksAtStart=False, helical_axis_stage=None):
    """
    Function to perform a tomography continuous-rotation scan on i12
     Arguments:
    description - description of the scan (or the sample that is being scanned. This is generally user-specific information that may be used to map to this scan later and is available in the NeXus file)
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds ( default = 1)
    start - first rotation angle (default=0.)
    stop  - last rotation angle (default=180.)
    step - rotation step size (default = 0.1)
    imagesPerDark - number of images to be taken for each dark (default=20)
    imagesPerFlat - number of images to be taken for each flat (default=20)
    extraFlatsAtEnd - if true, flats are taken after the flyscan as well as before
    closeShutterAfterScan - if true, shutter is closed after the flyscan
    """
    print "Running i12tomoFlyScan"
    import i13tomographyScan
#    from gda.factory import Finder
#    finder = Finder.getInstance()
#    zebra1=finder.find("zebra")
    #remove_default(ring)
    #remove_default(actualTime)
    #caput("BL12I-EA-ZEBRA-01:M1:SETPOS.PROC", 1)    # copy motor position to Zebra 1 (on POS1 of ENC tab)
    caput("BL12I-EA-ZEBRA-01:SYS_RESET.PROC", 1)
    defaults_save = clear_defaults()
    atTomoFlyScanStart()
    try:
        i13tomographyScan.tomoFlyScan(description=description, inBeamPosition=inBeamPosition, outOfBeamPosition=outOfBeamPosition, exposureTime=exposureTime, start=start, stop=stop, step=step, imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat, extraFlatsAtEnd=extraFlatsAtEnd, closeShutterAfterScan=closeShutterAfterScan, beamline="I12", vetoFlatsDarksAtStart=vetoFlatsDarksAtStart, helical_axis_stage=helical_axis_stage)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Exception in i12tomoFlyScan", exceptionType, exception, traceback, False)
    finally:
        #zebra1.pcDisarm()
        # set to step-scan
        #import zebra_utilities
        #zebra_utilities.setZebra2Mode(1)
        #_p2rcvmc.gap = _p2rcvmc_gap_saved
        for s in defaults_save:
            ScannableCommands.add_default(s)
            
        atTomoFlyScanEnd()
    print "Finished running i12tomoFlyScan"

def _make_subdir(dirname="rawdata"):
    """
    To create a given sub-directory in the current visit directory (if this sub-directory does not already exist).
    
    Note(s):
        (1) This is NOT the same as setSubdirectory(dirname) as scan files will NOT automatically be saved in this sub-directory 
        UNLESS one additionally executes setSubdirectory(dirname)
        (2) The input sub-directory's name must be specified relative to the current visit directory, ie to /dls/i12/data/yyyy/visit
        rather then, eg, /dls/i12/data/yyyy/visit/rawdata (the latter being i12's default sub-directory for saving scan files)
    Example(s): 
        (1) _make_subdir("test12/noname")
        will, if necessary, create a new sub-directory whose path is /dls/i12/data/yyyy/visit/test12/noname
        (2) _make_subdir("rawdata")
        will, if necessary, create a new sub-directory whose path is /dls/i12/data/yyyy/visit/rawdata
    """
    dirpath = os.path.join(getVisitRootPath(), dirname)
    if (dirname is not None) and (len(dirname)>0) and (not os.path.exists(dirpath)):
        try:
            os.makedirs(dirpath)
        except Exception, e:
            msg="Failed to create sub-directory %s: " %(dirpath)
            raise Exception(msg + str(e))
    else:
        msg="Directory %s already exists!" %(dirpath)
        print msg
        
        
from gdascripts.parameters import beamline_parameters

def atTomoFlyScanStart():
    print "atTomoFlyScanStart"
    jns = beamline_parameters.JythonNameSpaceMapping(InterfaceProvider.getJythonNamespace())
    tomography_theta=jns.tomography_theta
    if tomography_theta is None:
        raise NameError("tomography_theta is not defined in Jython namespace")
    tomography_theta_name = tomography_theta.name
    #print tomography_theta_name
    tomography_flyscan_det = jns.tomography_flyscan_det
    if tomography_flyscan_det is None:
        raise NameError("tomography_flyscan_det is not defined in Jython namespace")
    tomography_flyscan_det_name = tomography_flyscan_det.name
    #print tomography_flyscan_det_name
    isUsingP2R = ("p2r" in tomography_flyscan_det_name) or ("p2r" in tomography_theta_name)
    _p2rcvmc_gap_saved = None
    if isUsingP2R:
        try:
            _p2rcvmc = finder.find("p2rcvmc")
            _p2rcvmc_gap_saved = _p2rcvmc.gap
            _p2rcvmc.gap = False
        except:
            print("Unable to find p2rcvmc!")
    return _p2rcvmc_gap_saved

def atTomoFlyScanEnd():
    print "atTomoFlyScanEnd"
    """
    Function to tidy up anything that needs tidying up after a fly scan, eg
    setting the angular speed of p2r to 30 deg/sec 
    """
    jns = beamline_parameters.JythonNameSpaceMapping(InterfaceProvider.getJythonNamespace())
    tomography_theta=jns.tomography_theta
    if tomography_theta is None:
        raise NameError("tomography_theta is not defined in Jython namespace")
    tomography_theta_name = tomography_theta.name
    #print tomography_theta_name
    tomography_flyscan_det = jns.tomography_flyscan_det
    if tomography_flyscan_det is None:
        raise NameError("tomography_flyscan_det is not defined in Jython namespace")
    tomography_flyscan_det_name = tomography_flyscan_det.name
    #print tomography_flyscan_det_name
    if ("p2r" in tomography_flyscan_det_name) or ("p2r" in tomography_theta_name):
        tomography_flyscan_theta = jns.tomography_flyscan_theta
        _p2r_telnet = tomography_flyscan_theta.motor.smc.getBidiAsciiCommunicator()
        try:
            #stop all movement
            #print "AB"
            #_p2r_telnet.sendCmdNoReply("AB")        # abort all current movement
            # set angular speed to some decent value
            tomography_flyscan_theta.setSpeed(30)
            _p2r_telnet.sendCmdNoReply("MMPOSITION")
        except:
            tomography_flyscan_theta.motor.smc.bidiAsciiCommunicator.closeConnection()
            try:
                #stop all movement
                #print "AB"
                #_p2r_telnet.sendCmdNoReply("AB")    # abort all current movement
                # the 1st attempt is usually unsuccessful
                tomography_flyscan_theta.setSpeed(30)
                _p2r_telnet.sendCmdNoReply("MMPOSITION")
            except:
                # the 2nd attempt is usually successful
                tomography_flyscan_theta.setSpeed(30)
                _p2r_telnet.sendCmdNoReply("MMPOSITION")

def atTomoStepScanEnd():
    """
    Function to tidy up anything that needs tidying up after a step scan, eg
    setting the angular speed of p2r to 30 deg/sec 
    """
    jns = beamline_parameters.JythonNameSpaceMapping(InterfaceProvider.getJythonNamespace())
    tomography_theta=jns.tomography_theta
    if tomography_theta is None:
        raise NameError("tomography_theta is not defined in Jython namespace")
    tomography_theta_name = tomography_theta.name
    #print tomography_theta_name
    tomography_detector = jns.tomography_detector
    if tomography_detector is None:
        raise NameError("tomography_flyscan_det is not defined in Jython namespace")
    tomography_detector_name = tomography_detector.name
    #print tomography_detector_name
    if ("p2r" in tomography_detector_name) or ("p2r" in tomography_theta_name):
        p2r_rot_motor=finder.find("p2r_rot_motor")
        _p2r_telnet = p2r_rot_motor.smc.getBidiAsciiCommunicator()
        try:
            # set angular speed to some decent value
            p2r_rot_motor.setSpeed(30)
        except:
            #p2r_rot_motor.smc.bidiAsciiCommunicator.closeConnection() # setSpeed below opens the connection if not present
            from p2r_utilities import p2r_telnet
            p2r_telnet.reset()
            try:
                # the 1st attempt is usually unsuccessful
                p2r_rot_motor.setSpeed(30)
            except:
                # the 2nd attempt is usually successful
                p2r_rot_motor.setSpeed(30)                                 

from gda.device.scannable import ScannableBase, SimpleScannable
from gda.jython.commands.ScannableCommands import inc, scan, pos, createConcurrentScan
from gda.scan import ConstantVelocityScanLine, MultiScanItem, MultiScanRunner, ConcurrentScan
from gdascripts.metadata.metadata_commands import setTitle
from java.lang import Runnable
from gda.commandqueue import JythonScriptProgressProvider
from gda.util import OSCommandRunner
import time
from gda.data.scan.datawriter.DefaultDataWriterFactory import createDataWriterFromFactory
from gda.data.scan.datawriter import *
from gda.device.scannable import ScannableBase, ScannableUtils
image_key_dark=2
image_key_flat=1 # also known as bright
image_key_project=0 # also known as sample

def updateProgress( percent, msg):
    JythonScriptProgressProvider.sendProgress( percent, msg)
    print "percentage %d %s" % (percent, msg)


class PreScanRunnable(Runnable):
    def __init__(self, msg, percentage, shutter, shutterPosition, xMotor, xMotorPosition, image_key, image_key_value,
                 zebraTriggerMode=None, alreadyPrepared=False):
        self.msg = msg
        self.percentage = percentage
        self.shutter=shutter
        self.shutterPosition = shutterPosition
        self.xMotor = xMotor
        self.xMotorPosition =xMotorPosition
        self.image_key =image_key
        self.image_key_value =image_key_value
        self.zebraTriggerMode = zebraTriggerMode
        self.alreadyPrepared = alreadyPrepared
        
    def run(self):
        if not self.alreadyPrepared:
            updateProgress(self.percentage, self.msg)
            self.shutter.moveTo(self.shutterPosition)
            self.xMotor.moveTo(self.xMotorPosition)
            self.image_key.moveTo(self.image_key_value)
            if self.zebraTriggerMode is not None:
                import zebra_utilities
                zebra_utilities.setZebra2Mode(self.zebraTriggerMode)
                #zebra_utilities.setZebra3AfterPixiumFlyScan()

def addFlyScanNXTomoSubentry(scanObject, tomography_detector_name, tomography_theta_name, externalhdf=True):
    if scanObject is None:
        raise ValueError("Input scanObject must not be None")
   
    nxLinkCreator = NXTomoEntryLinkCreator()
   
    # detector independent items
    nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/source:NXsource/current:NXdata")
    nxLinkCreator.setInstrument_detector_image_key_target("entry1:NXentry/instrument:NXinstrument/image_key:NXpositioner/image_key:NXdata")
    nxLinkCreator.setInstrument_source_target("entry1:NXentry/instrument:NXinstrument/source:NXsource")
   
    sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/" + tomography_theta_name + ":NXpositioner/"
    sample_rotation_angle_target += tomography_theta_name + ":NXdata"
    nxLinkCreator.setSample_rotation_angle_target(sample_rotation_angle_target);
    
    #currently no clear value for sample x,y,z so use a dummy default value
    default_placeholder_target = "entry1:NXentry/scan_identifier:NXdata"    
    nxLinkCreator.setSample_x_translation_target(default_placeholder_target)
    nxLinkCreator.setSample_y_translation_target(default_placeholder_target)
    nxLinkCreator.setSample_z_translation_target(default_placeholder_target)
       
    nxLinkCreator.setTitle_target("entry1:NXentry/title:NXdata")
   
    # detector dependent items
    if externalhdf:
        # external file
        instrument_detector_data_target = "!entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "data:SDS"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
    else:
        # image filenames
        instrument_detector_data_target = "entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "image_data:NXdata"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
   
    nxLinkCreator.afterPropertiesSet()
   
    dataWriter = createDataWriterFromFactory()
    subEntryWriter = NXSubEntryWriter(nxLinkCreator)
    dataWriter.addDataWriterExtender(subEntryWriter)
    scanObject.setDataWriter(dataWriter)
                   
#def tomoFlyScan(description, inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
#              imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=True, extraFlatsAtEnd=False, closeShutterAfterScan=False, beamline="I12", autoAnalyse=True):
#def i12tomoFlyScan(description="Hello World", inBeamPosition=0.,outOfBeamPosition=1., exposureTime=.05, start=0., stop=180., step=.1, imagesPerDark=20, imagesPerFlat=20, extraFlatsAtEnd=False, closeShutterAfterScan=False):                  
def tomoTRFlyScan(description="Hello World", inBeamPosition=0., outOfBeamPosition=1., exposureTime=.05, start=10., tomoRange=180., step=.1, ntomo=1, nrot=0, locked=None, imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=True, extraFlatsAtEnd=False, closeShutterAfterScan=False, sendTriggers=True, beamline="I12", autoAnalyse=True):
    """
    Function to collect a series of tomography frames, where each frame is a continuous-rotation scan
     Arg(s):
    description - description of the scan (or the sample that is being scanned. This is generally user-specific information that may be used to map to this scan later and is available in the NeXus file)
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds (default = 1)
    start - first rotation angle (default=0.)
    tomoRange - angular range over which a single tomography frame is collected (default=180.)
    step - angular step size (default = 0.1)
    ntomo - the total number of tomography frames, each being collected over the same angular range specified by tomoRange (default = 1)
    nrot - integer number of full (360 deg) rotations between the start angles of any two consecutive tomography frames (default = 0)
           Note: if nrot = 0, a single tomography frame is collected over the angular range specified by tomoRange 
    locked - if None, no action is taken
             if True, p2r's Move Mode is set to MMPOSITION, ie linear and rotational axes are locked to move together
             if False, p2r's Move Mode is set to MMPOSITION-JOG, ie linear and rotational axes move independently from one another
             (default = None)
    imagesPerDark - integer number of images to be taken in each dark-field collection (default=20)
    imagesPerFlat - integer number of images to be taken in each flat-field collection (default=20)
    extraFlatsAtEnd - if True, flats are taken after the main scan has finished as well as before it
    closeShutterAfterScan - if True, shutter is closed at the end of this function
    sendTriggers - if True, triggers will be sent over telnet to P2R (default: True)
    """
    _fname = tomoTRFlyScan.__name__
    print "Running %s" %(_fname,)
    ntomo = int(ntomo)
    if ntomo < 1:
        msg = "ntomo must be larger than 0 - exiting!" %(ntomo)
        raise ValueError(msg)
    nrot = int(nrot)
    
    if nrot > 0:
        if tomoRange >= nrot * 360.0:
            msg = "The condition: tomoRange < nrot * 360.0 is violated as %s >= %s * 360.0 - no scan will be run!" %(tomoRange, nrot)
            raise ValueError(msg)
        #stop = ((tomoRange - tomoRange % 360) + 360)*ntomo
        stop = 360.0*(nrot*ntomo - nrot + 1)
        ngates = ntomo
    else:
        # assume nrot == 0, which is interpreted as single tomography acquisition from start to start + tomoRange * ntomo
        stop = start + tomoRange * ntomo
        ngates = 1
        
    print "start = %f, stop = %f, step = %f" %(start, stop, step)
    
    _p2rcvmc = finder.find("p2rcvmc")
    _p2rcvmc.gap = True
    p2r_rot = finder.find("p2r_rot")
    adiff_large = 3.0
    pos_curr = None #p2r_rot.getPosition()
    if (False and abs(pos_curr - start) > adiff_large):
        #p2r_rot_motor=finder.find("p2r_rot_motor")
        p2r_rot.moveTo(start)
        sleep(0.5)
        speed_curr = p2r_rot.getSpeed()
        print "Moving p2r_rot to start = %f (with current (instantaneous) speed of %s)..." %(start, speed_curr)
        tol = 0.01
        pos_curr = p2r_rot.getPosition()
        wait_sec = 1
        veto = False
        while(not veto):
            sleep(wait_sec)
            pos_prev = pos_curr
            pos_curr = p2r_rot.getPosition()
            adiff = abs(start - pos_curr)
            adelta_iter = abs(pos_prev - pos_curr)
            if adiff < tol:
                veto = True
                print "pos_curr = %.3f and start = %.3f are within tolerance tol = %.3f (adiff = %.3f)" %(pos_curr,start,tol,adiff)
            elif adelta_iter < tol:
                veto = True
                print "p2r_rot appears to have stopped moving because \n\t the most recent relative displacement is within tolerance tol = %.3f (adelta_iter = %f)!" %(tol,adelta_iter)
                print "Current (instantaneous) speed = %s" %(p2r_rot.getSpeed())
        print "Finished moving p2r_rot to start = %f (with current (instantaneous) speed of %s)" %(start, p2r_rot.getSpeed())
    #i12tomoFlyScan(description=description, \
    #               inBeamPosition=inBeamPosition, outOfBeamPosition=outOfBeamPosition, \
    #               exposureTime=exposureTime, \
    #               start=start, stop=stop, step=step, \
    #               imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat, \
    #               extraFlatsAtEnd=extraFlatsAtEnd, \
    #               closeShutterAfterScan=closeShutterAfterScan)    

    is_p2r_used = False
    jns = beamline_parameters.JythonNameSpaceMapping(InterfaceProvider.getJythonNamespace())
    tomography_theta=jns.tomography_theta
    if tomography_theta is None:
        raise NameError("tomography_theta is not defined in Jython namespace")
    tomography_theta_name = tomography_theta.name
    #print tomography_theta_name
    tomography_flyscan_det = jns.tomography_flyscan_det
    if tomography_flyscan_det is None:
        raise NameError("tomography_flyscan_det is not defined in Jython namespace")
    tomography_flyscan_det_name = tomography_flyscan_det.name
    #print tomography_flyscan_det_name
    p2r_locked = None
    from p2r_utilities import p2r_telnet
    p2r_telnet.reset()
    if ("p2r" in tomography_flyscan_det_name) or ("p2r" in tomography_theta_name):
        is_p2r_used = True
        tomography_flyscan_theta = jns.tomography_flyscan_theta
        _p2r_telnet = tomography_flyscan_theta.motor.smc.getBidiAsciiCommunicator()
       # _p2r_telnet.sendCmdNoReply("MMPOSITION") # always make sure this is set at the begining
        print "It appears (from jythonNamespaceMapping_live) that p2r is used!"
        #p2r_move_mode_admissible = ["MMPOSITION", "MMPOSITION-JOG"]
        if not locked is None:
            _p2r_telnet = tomography_flyscan_theta.motor.smc.getBidiAsciiCommunicator()
            print _p2r_telnet.address
            print _p2r_telnet.port
            if not locked is None:      #if locked: 
                print "requested move mode for p2r is: locked (MMPOSITION)"
                p2r_locked = locked     #p2r_locked = True
                p2r_movemode = locked
                print "requested move mode for p2r is: %d" %(p2r_movemode)
                #_p2r_telnet.sendCmdNoReply("MMPOSITION") #done in Java coz this must be done after pos to lead-in position
            else:
                print "requested move mode for p2r is: NOT locked (MMPOSITION-JOG)"
                pass                    #p2r_locked = False
                #_p2r_telnet.sendCmdNoReply("MMPOSITION-JOG")
        
                  
    #jns=beamline_parameters.JythonNameSpaceMapping()
    tomography_flyscan_flat_dark_det=jns.tomography_flyscan_flat_dark_det
    savename=tomography_flyscan_flat_dark_det.name
    try:
        tomodet=jns.tomodet
        if tomodet is None:
            if beamline == "I13":
                raise NameError("tomodet is not defined in Jython namespace")
        tomography_flyscan_theta=jns.tomography_flyscan_theta
        if tomography_flyscan_theta is None:
            raise NameError("tomography_flyscan_theta is not defined in Jython namespace")

        tomography_flyscan_det=jns.tomography_flyscan_det
        if tomography_flyscan_det is None:
            raise NameError("tomography_flyscan_det is not defined in Jython namespace")
        
        tomography_translation=jns.tomography_translation
        if tomography_translation is None:
            raise NameError("tomography_translation is not defined in Jython namespace")
        

        tomography_shutter=jns.tomography_shutter
        if tomography_shutter is None:
            raise NameError("tomography_shutter is not defined in Jython namespace")
        
        meta_add = jns.meta_add
        if meta_add is None:
            raise NameError("meta_add is not defined in Jython namespace")

        if beamline == "I13":
            camera_stage = jns.cs1
            if camera_stage is None:
                raise NameError("camera_stage is not defined in Jython namespace")
    
            sample_stage = jns.sample_stage
            if sample_stage is None:
                raise NameError("sample_stage is not defined in Jython namespace")
            
            meta_add( camera_stage)
            meta_add( sample_stage)

            ionc_i = jns.ionc_i
            if ionc_i is None:
                raise NameError("ionc_i is not defined in Jython namespace")
            ionc_i_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(ionc_i)

        print "imagesPerDark = %i, imagesPerFlat = %i" %(imagesPerDark, imagesPerFlat)
        nother = imagesPerDark + imagesPerFlat
        nother += (imagesPerFlat if extraFlatsAtEnd else 0)
        nprojs = ScannableUtils.getNumberSteps(tomography_flyscan_theta, start, start+tomoRange, step) + 1
        print "ngates = %i, nprojs = %i, nother = %i" %(ngates, nprojs, nother)
        #return
        #if is_p2r_used:
        _p2rcvmc = finder.find("p2rcvmc")
        _p2rcvmc_gap_saved = _p2rcvmc.gap
        _p2rcvmc.gap = True
        _p2rcvmc.setNumberOfGates(ngates)
        _p2rcvmc.setNprojs(nprojs)
        _p2rcvmc.setNother(nother)
        _p2rcvmc.setP2R_start(start)
        _p2rcvmc.setP2R_end(start+tomoRange)
        _p2rcvmc.setP2R_step(step)
        _p2rcvmc.setP2R_end_eff(stop)
        _p2rcvmc.setTomoRange(tomoRange)
        _p2rcvmc.setNrot(nrot)
        _p2rcvmc.setP2R_gap(True)
        _p2rcvmc.setZindex(0)
        _p2rcvmc.setSendTriggers(sendTriggers)
        if not p2r_locked is None: 
            _p2rcvmc.setP2R_locked(p2r_locked)
            _p2rcvmc.setP2r_movemode(p2r_movemode)
        
        index=SimpleScannable()
        index.setCurrentPosition(0.0)
        index.setName(tomography_flyscan_theta.name)
        index.inputNames = tomography_flyscan_theta.inputNames
        index.extraNames = tomography_flyscan_theta.extraNames
        index.configure()

#        index_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(index)


        image_key=SimpleScannable()
        image_key.setCurrentPosition(0.0)
        image_key.setInputNames(["image_key"])
        image_key.setName("image_key")
        image_key.configure()
        image_key_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(image_key)


#        ss=SimpleScannable()
#        ss.name = tomography_flyscan_theta.name
#        ss.currentPosition=0.
#        ss.inputNames = tomography_flyscan_theta.inputNames
#        ss.extraNames = tomography_flyscan_theta.extraNames
#        ss.configure()

        ss1=SimpleScannable()
        ss1.name = tomography_flyscan_theta.getContinuousMoveController().name
        ss1.currentPosition=0.
        ss1.inputNames = tomography_flyscan_theta.getContinuousMoveController().inputNames
        ss1.extraNames = tomography_flyscan_theta.getContinuousMoveController().extraNames
        ss1.configure()
        
        

        
        tomography_flyscan_flat_dark_det.name = tomography_flyscan_det.name
        
#        scanBackward=ConstantVelocityScanLine([tomography_flyscan_theta, stop, start, step, index_cont, image_key_cont, ionc_i_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
#        scanObject3=ConstantVelocityScanLine([tomography_flyscan_theta, start, stop, step,ix, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
        if tomodet is not None:
            tomodet.stop()
        
#        multiScanObj = MultiScan([darkFlatScan, scanObject, scanObject2,scanObject3])
        multiScanItems = []

#darks before
        if imagesPerDark > 0:
            if beamline == "I13":
                darkScan=ConcurrentScan([index, 0, imagesPerDark-1, 1, image_key, ionc_i, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
            else:
                #darkScan=ConcurrentScan([index, 0, imagesPerDark-1, 1, image_key, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
                darkScan=ConcurrentScan([index, (start,)*imagesPerDark, image_key, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
            multiScanItems.append(MultiScanItem(darkScan, PreScanRunnable("Preparing for darks", 0, tomography_shutter, "Close", tomography_translation, inBeamPosition, image_key, image_key_dark, zebraTriggerMode=1)))
        else:
            print "No darkScan at start requested."

#flats before

        if imagesPerFlat > 0:
            if beamline == "I13":
                flatScan=ConcurrentScan([index, 0, imagesPerFlat-1, 1, image_key, ionc_i, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
            else:
                #flatScan=ConcurrentScan([index, 0, imagesPerFlat-1, 1, image_key, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
                flatScan=ConcurrentScan([index, (start,)*imagesPerFlat, image_key, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
            multiScanItems.append(MultiScanItem(flatScan, PreScanRunnable("Preparing for flats",10, tomography_shutter, "Open", tomography_translation, outOfBeamPosition, image_key, image_key_flat, zebraTriggerMode=1)))
        else:
            print "No flatScan at start requested."
        
#flyscan
        if beamline == "I13":
            scanForward=ConstantVelocityScanLine([tomography_flyscan_theta, start, stop, step,image_key_cont, ionc_i_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
        else:
            #alreadyPrepared_lst = [False, True, True]
            #start_sub = start
            #for i in range(ntomo):
            #    stop_sub = start_sub + tomoRange
            #    print "i = %i, start_sub = %f, stop_sub = %f, step = %f" %(i, start_sub, stop_sub, step) 
                #scanForward=ConstantVelocityScanLine([tomography_flyscan_theta, start_sub, stop_sub, step,image_key_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
                #multiScanItems.append(MultiScanItem(scanForward, PreScanRunnable("Preparing for projections",20, tomography_shutter, "Open",tomography_translation, inBeamPosition, image_key, image_key_project, zebraTriggerMode=2, alreadyPrepared=alreadyPrepared_lst[i])))
            #    start_sub = start + 360*nrot * (i+1)
            scanForward=ConstantVelocityScanLine([tomography_flyscan_theta, start, stop, step,image_key_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
        multiScanItems.append(MultiScanItem(scanForward, PreScanRunnable("Preparing for projections",20, tomography_shutter, "Open",tomography_translation, inBeamPosition, image_key, image_key_project, zebraTriggerMode=2)))

#flats after
        if extraFlatsAtEnd:
            if imagesPerFlat > 0:
                if beamline == "I13":
                    flatScan=ConcurrentScan([index, 0, imagesPerFlat-1, 1, image_key, ionc_i, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
                else:
                    flatScan=ConcurrentScan([index, 0, imagesPerFlat-1, 1, image_key, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
                multiScanItems.append(MultiScanItem(flatScan, PreScanRunnable("Preparing for flats",10, tomography_shutter, "Open", tomography_translation, outOfBeamPosition, image_key, image_key_flat, zebraTriggerMode=1)))
        else:
            print "No flatScan at end requested."
        
        if not description == None: 
            setTitle(description)
        else :
            setTitle("undefined")
        
        multiScanObj = MultiScanRunner(multiScanItems)
        #multiScanObj.veto = True
        #must pass first scan to be run
        
        addFlyScanNXTomoSubentry(multiScanItems[0].scan, tomography_flyscan_det.name, tomography_flyscan_theta.name, externalhdf=(tomography_flyscan_det.name != "flyScanDetectorTIF"))
        multiScanObj.runScan()
        time.sleep(2)
        if extraFlatsAtEnd:
            print "Moving sample to in-beam position after taking flat-field images at end of scan."
            tomography_translation.moveTo(inBeamPosition)
        #turn camera back on
        tomography_flyscan_flat_dark_det.name = savename
        if setupForAlignment:
            if tomodet is not None:
                tomodet.setupForAlignment()
            
        if autoAnalyse:
            lsdp=jns.lastScanDataPoint()
            OSCommandRunner.runNoWait(["/dls_sw/apps/tomopy/tomopy/bin/gda/tomo_at_scan_end_kz", lsdp.currentFilename], OSCommandRunner.LOGOPTION.ALWAYS, None)
    
        return multiScanObj;
    except :
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Error in tomoFlyScanScan", exceptionType, exception, traceback, False)
        tomography_flyscan_flat_dark_det.name = savename
    finally:
        if beamline == "I12" or beamline == "i12":
            import zebra_utilities
            zebra_utilities.setZebra2Mode(1)

        if closeShutterAfterScan:
            print "Closing the shutter after the flyscan."
            tomography_shutter.moveTo("Close")    
        
        _p2rcvmc.gap = _p2rcvmc_gap_saved
        p2r_telnet.reset()
    print "Finished running %s" %(_fname,)
    

#def tomoTRFlyScan(description="Hello World", inBeamPosition=0., outOfBeamPosition=1., exposureTime=.05, start=0., tomoRange=180., step=.1, ntomo=1, nrot=0, locked=None, imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=True, extraFlatsAtEnd=False, closeShutterAfterScan=False, beamline="I12", autoAnalyse=True):
def i12tomoTRFlyScan(description="Hello World", inBeamPosition=0.,outOfBeamPosition=1., exposureTime=.05, start=10., tomoRange=180., step=.1, ntomo=1, nrot=0, locked=None, imagesPerDark=20, imagesPerFlat=20, extraFlatsAtEnd=False, closeShutterAfterScan=False, sendTriggers=True, z1config="/dls_sw/i12/epics/zebra/count_opulse_p2r_z1.zeb", z2config="/dls_sw/i12/epics/zebra/edge_p2r_z2.zeb"):
    """
    Function to collect a series of tomography frames, where each frame is a continuous-rotation scan
     Arg(s):
    description - description of the scan (or the sample that is being scanned. This is generally user-specific information that may be used to map to this scan later and is available in the NeXus file)
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds (default = 1)
    start - first rotation angle (default=0.)
    tomoRange - angular range over which a single tomography frame is collected (default=180.)
    step - angular step size (default = 0.1)
    ntomo - the total number of tomography frames, each being collected over the same angular range specified by tomoRange (default = 1)
    nrot - integer number of full (360 deg) rotations between the start angles of any two consecutive tomography frames (default = 0)
           Note: if nrot = 0, a single tomography frame is collected over the angular range specified by tomoRange 
    locked - if None, no action is taken
             if True, p2r's Move Mode is set to MMPOSITION, ie linear and rotational axes are locked to move together
             if False, p2r's Move Mode is set to MMPOSITION-JOG, ie linear and rotational axes move independently from one another
             (default = None)
    imagesPerDark - integer number of images to be taken in each dark-field collection (default=20)
    imagesPerFlat - integer number of images to be taken in each flat-field collection (default=20)
    extraFlatsAtEnd - if True, flats are taken after the main scan has finished as well as before it
    closeShutterAfterScan - if True, shutter is closed at the end of this function
    sendTriggers - if True, triggers will be sent over telnet to P2R (default: True)
    z1config - NOT YET IMPLEMENTED
    z2config - NOT YET IMPLEMENTED
    """
    _fname = i12tomoTRFlyScan.__name__
    print "Running %s" %(_fname,)
    
    from p2r_utilities import p2r_telnet
    p2r_telnet.reset()
    #import i13tomographyScan
#    from gda.factory import Finder
#    finder = Finder.getInstance()
#    zebra1=finder.find("zebra")
    #remove_default(ring)
    #remove_default(actualTime)
    #caput("BL12I-EA-ZEBRA-01:M1:SETPOS.PROC", 1)    # copy motor position to Zebra 1 (on POS1 of ENC tab)
    defaults_save = clear_defaults()
    caput("BL12I-EA-ZEBRA-01:SYS_RESET.PROC", 1)
    caput("BL12I-EA-DET-02:CAM:ArrayCounter", 0)
    
    try:
#def tomoTRFlyScan(description="Hello World", inBeamPosition=0., outOfBeamPosition=1., exposureTime=.05, start=0., tomoRange=180., step=.1, ntomo=1, nrot=0, locked=None, imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=True, extraFlatsAtEnd=False, closeShutterAfterScan=False, beamline="I12", autoAnalyse=True):
        tomoTRFlyScan(description=description, \
                      inBeamPosition=inBeamPosition, outOfBeamPosition=outOfBeamPosition, \
                      exposureTime=exposureTime, \
                      start=start, tomoRange=tomoRange, step=step, ntomo=ntomo, nrot=nrot, locked=locked, \
                      imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat, extraFlatsAtEnd=extraFlatsAtEnd, \
                      closeShutterAfterScan=closeShutterAfterScan, sendTriggers=sendTriggers, beamline="I12")
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Exception in %s" %(_fname), exceptionType, exception, traceback, False)
    finally:
        #zebra1.pcDisarm()
        # set to step-scan
        #import zebra_utilities
        #zebra_utilities.setZebra2Mode(1)
        for s in defaults_save:
            ScannableCommands.add_default(s)
            
        atTomoFlyScanEnd();
    print "Finished running %s" %(_fname,)
    

from gdascripts.scannable.beamokay import WaitWhileScannableBelowThresholdMonitorOnly, WaitForScannableState

class WaitWhileScannableBelowRelativeThresholdMonitorOnly(WaitWhileScannableBelowThresholdMonitorOnly):
    def __init__(self, name, scannableToMonitor, minimumThresholdPct, minimumThresholdHard, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=0):
        minimumThreshold = scannableToMonitor.getPosition() * minimumThresholdPct
        super(WaitWhileScannableBelowRelativeThresholdMonitorOnly, self).__init__(name, scannableToMonitor, minimumThreshold, secondsBetweenChecks, secondsToWaitAfterBeamBackUp)
        self.minimumThresholdPct = minimumThresholdPct
        self.minimumThresholdHard = minimumThresholdHard
    
    def atScanStart(self):
        self.minimumThreshold = max(scannableToMonitor.getPosition() * self.minimumThresholdPct, self.minimumThresholdHard)
        super(WaitWhileScannableBelowRelativeThresholdMonitorOnly, self).atScanStart()

#tomoScan(description="tomoScan", inBeamPosition=0, outOfBeamPosition=0, exposureTime=0.1, start=0.0, stop=5.0, step=1.0, darkFieldInterval=0, flatFieldInterval=0, imagesPerDark=2, imagesPerFlat=3, optimizeBeamInterval=0, pattern='default', tomoRotationAxis=0, addNXEntry=True, autoAnalyse=True, additionalScannables=[])
#i13tomographyScan.tomoScanX(description="tomoScanX", inBeamPosition=0, outOfBeamPosition=0, exposureTimeDark=0.3, exposureTimeFlat=0.2, exposureTime=0.1, start=0.0, stop=5.0, step=1.0, darkFieldInterval=0, flatFieldInterval=0, imagesPerDark=2, imagesPerFlat=3, optimizeBeamInterval=0, pattern='default', tomoRotationAxis=0, addNXEntry=True, autoAnalyse=True, additionalScannables=[])

def setZebra1And2ForP2RGapScan(z1config="/dls_sw/i12/epics/zebra/count_opulse_p2r_z1.zeb", z2config="/dls_sw/i12/epics/zebra/edge_p2r_z2.zeb"):
    print "Awaiting implementation!"


class BeamlineStorage:
    def __init__(self, name, ixx='i12', windowsSubString = {"na": "d:\\i12\\data\\", "gpfs": "t:\\i12\\data\\"}, windowsSubString_rvr = {"d": "NetApp", "t": "GPFS01"}, emails=[]):
        self.name = name
        self.ixx = ixx
        self.emails = emails # lst, eg ['kaz.wanelik@diamond.ac.uk', 'frederik.ferner@diamond.ac.uk', 'andy.wilson@diamond.ac.uk']
        self.emails_enabled = False
        self.windowsSubString_dct = windowsSubString #dct, eg {"na": "d:\\i12\\data\\", "gpfs": "t:\\i12\\data\\"}
        self. windowsSubString_rvr = windowsSubString_rvr #dct, eg {"d": "NetApp", "t": "GPFS01"}
        self.verbose = False

    def use(self, storage_name):
        use_storage(storage_name)
        
    def report(self):
        report_storage()
        
    
def use_storage(storage_name):
    """
    Desc:
    Fn to select storage for saving scan files on the beamline. Note: this command needs to be executed each time GDA servers get restarted.
    
    Arg(s):
    storage_name (str) - name of storage to be used for saving any subsequent scan files: NetApp (local) or GPFS01 (central):
        "na" - NetApp local storage 
        "gpfs" - GPFS central storage
    """
    #assert na or gpfs
    storage_name_ = storage_name.lower()
    print "\n * Configuring beamline storage to %s...\n" %(storage_name_)
    windowsSubString_dct = {"na": "d:\\i12\\data\\", "gpfs": "t:\\i12\\data\\"}
    windowsSubString_rvr_dct = {"d": "NetApp", "t": "GPFS01"}

    storage = windowsSubString_dct[storage_name_]
    curr_out_str = "Current windowsSubString for %s is %s (%s).\n"
    
    # PIXIUM TIFF detector objects
    pixium10_tif = finder.find("pixium10_tif")
    det_name = pixium10_tif.getName()
    print "Setting windowsSubString for %s to %s... " %(det_name, storage)
    pixium10_tif.getAdditionalPluginList()[0].getNdFile().getFilePathConverter().setWindowsSubString(storage)
    #pixium10_tif.pluginList[1].ndFileHDF5.file.filePathConverter.setWindowsSubString(storage)
    print "Finished setting windowsSubString for %s to %s." %(det_name, storage)
    det_cfg = pixium10_tif.getAdditionalPluginList()[0].getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)
    #print "Current windowsSubString = %s" %(flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString())

    # PIXIUM HDF detector objects
    pixium10_hdf = finder.find("pixium10_hdf")
    det_name = pixium10_hdf.getName()
    print "Setting windowsSubString for %s to %s... " %(det_name, storage)
    pixium10_hdf.getAdditionalPluginList()[0].getNdFile().getFilePathConverter().setWindowsSubString(storage)
    print "Finished setting windowsSubString for %s to %s." %(det_name, storage)
    det_cfg = pixium10_hdf.getAdditionalPluginList()[0].getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)
    
    # PCO TIFF detector objects
    pco4000_dio_tif = finder.find("pco4000_dio_tif")
    det_name = pco4000_dio_tif.getName()
    print "Setting windowsSubString for %s to %s... " %(det_name, storage)
    pco4000_dio_tif.getNdFile().getFilePathConverter().setWindowsSubString(storage)
    print "Finished setting windowsSubString for %s to %s." %(det_name, storage)
    det_cfg = pco4000_dio_tif.getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)
    
    flyScanDetectorTIF = finder.find("flyScanDetectorTIF")
    det_name = flyScanDetectorTIF.getName()
    print "Setting windowsSubString for %s to %s... " %(det_name, storage)
    flyScanDetectorTIF.pluginList[1].getNdFile().getFilePathConverter().setWindowsSubString(storage)
    print "Finished setting windowsSubString for %s to %s." %(det_name, storage)
    det_cfg = flyScanDetectorTIF.pluginList[1].getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)
    
    flyScanFlatDarkDetectorTIF = finder.find("flyScanFlatDarkDetectorTIF")
    det_name = flyScanFlatDarkDetectorTIF.getName()
    print "Setting windowsSubString for %s to %s... " %(det_name, storage)
    flyScanFlatDarkDetectorTIF.pluginList[1].getNdFile().getFilePathConverter().setWindowsSubString(storage)
    print "Finished setting windowsSubString for %s to %s." %(det_name, storage)
    det_cfg = flyScanFlatDarkDetectorTIF.pluginList[1].getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)
    
    # PCO HDF detector objects
    flyScanDetector = finder.find("flyScanDetector")
    det_name = flyScanDetector.getName()
    print "Setting windowsSubString for %s to %s... " %(det_name, storage)
    flyScanDetector.pluginList[1].ndFileHDF5.file.filePathConverter.setWindowsSubString(storage)
    print "Finished setting windowsSubString for %s to %s." %(det_name, storage)
    det_cfg = flyScanDetector.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    flyScanFlatDarkDetector = finder.find("flyScanFlatDarkDetector")
    det_name = flyScanFlatDarkDetector.getName()
    print "Setting windowsSubString for %s to %s... " %(det_name, storage)
    flyScanFlatDarkDetector.pluginList[1].ndFileHDF5.file.filePathConverter.setWindowsSubString(storage)
    print "Finished setting windowsSubString for %s to %s." %(det_name, storage)
    det_cfg = flyScanFlatDarkDetector.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)
    
    pco4000_dio_hdf = finder.find("pco4000_dio_hdf")
    det_name = pco4000_dio_hdf.getName()
    print "Setting windowsSubString for %s to %s... " %(det_name, storage)
    pco4000_dio_hdf.pluginList[1].ndFileHDF5.file.filePathConverter.setWindowsSubString(storage)
    print "Finished setting windowsSubString for %s to %s." %(det_name, storage)
    det_cfg = pco4000_dio_hdf.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)
    
    #old pco?
    
    #p2r...
    
    # need to undo .tmp and suppressing some GDA error messages

    if storage_name_ == "na":
        #print "disable 'waiting for file to be created'"
        pixium10_tif.pluginList[1].waitForFileArrival=False
        #print "disable 'Path does not exist on IOC'"
        pixium10_tif.pluginList[1].pathErrorSuppressed=True

        pco4000_dio_tif.setCheckFileExists(False)
        pco4000_dio_tif.fileWriter.pathErrorSuppressed=True
        pco4000_dio_hdf.pluginList[1].pathErrorSuppressed=True

        flyScanDetector.getAdditionalPluginList()[0].pathErrorSuppressed=True
        flyScanFlatDarkDetector.getAdditionalPluginList()[0].pathErrorSuppressed=True
    elif storage_name_ == "gpfs":
        #print "enable 'waiting for file to be created'"
        pixium10_tif.pluginList[1].waitForFileArrival=True
        #print "enable 'Path does not exist on IOC'"
        pixium10_tif.pluginList[1].pathErrorSuppressed=False

        pco4000_dio_tif.setCheckFileExists(False) # was True 5 x 17 kz
        pco4000_dio_tif.fileWriter.pathErrorSuppressed=False
        pco4000_dio_hdf.pluginList[1].pathErrorSuppressed=False

        flyScanDetector.getAdditionalPluginList()[0].pathErrorSuppressed=False
        flyScanFlatDarkDetector.getAdditionalPluginList()[0].pathErrorSuppressed=False
    else:
        msg = "Unsupported storage option: %s!" %(storage_name_)
        print msg

    print "\n * Finished configuring beamline storage to %s!" %(storage_name_)
    
def report_storage():
    """
    Desc:
    Fn to report current storage configuration for saving scan files on the beamline.
    """
    windowsSubString_rvr_dct = {"d": "NetApp", "t": "GPFS01"}
    
    #curr_out_str = "Current windowsSubString for %s is %s (%s)."
    curr_out_str = " %s is currently configured to use the %s storage (on %s)."
    
    # PIXIUM TIFF detector objects
    pixium10_tif = finder.find("pixium10_tif")
    det_name = pixium10_tif.getName()
    det_cfg = pixium10_tif.getAdditionalPluginList()[0].getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)
    
    # PIXIUM HDF detector objects
    pixium10_hdf = finder.find("pixium10_hdf")
    det_name = pixium10_hdf.getName()
    det_cfg = pixium10_hdf.getAdditionalPluginList()[0].getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)
    
    # PCO TIFF detector objects
    pco4000_dio_tif = finder.find("pco4000_dio_tif")
    det_name = pco4000_dio_tif.getName()
    det_cfg = pco4000_dio_tif.getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[detreport_storage_drv], det_cfg)

    flyScanDetectorTIF = finder.find("flyScanDetectorTIF")
    det_name = flyScanDetectorTIF.getName()
    det_cfg = flyScanDetectorTIF.pluginList[1].getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    flyScanFlatDarkDetectorTIF = finder.find("flyScanFlatDarkDetectorTIF")
    det_name = flyScanFlatDarkDetectorTIF.getName()
    det_cfg = flyScanFlatDarkDetectorTIF.pluginList[1].getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    # PCO HDF detector objects
    flyScanDetector = finder.find("flyScanDetector")
    det_name = flyScanDetector.getName()
    det_cfg = flyScanDetector.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    flyScanFlatDarkDetector = finder.find("flyScanFlatDarkDetector")
    det_name = flyScanFlatDarkDetector.getName()
    det_cfg = flyScanFlatDarkDetector.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    pco4000_dio_hdf = finder.find("pco4000_dio_hdf")
    det_name = pco4000_dio_hdf.getName()
    det_cfg = pco4000_dio_hdf.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    #p2r...
    
i12storage = BeamlineStorage('i12storage')


from gda.device.scannable import PseudoDevice

class SleepAtScanStart(PseudoDevice):
    # c'tor
    def __init__(self, name, sleep_sec=1, verbose=True):
        self.setName(name) 
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%5.5g"])
        self.sleep_sec = sleep_sec	# position
        self.verbose = verbose
        self.scan_pt = 0
    
    def reset(self):
        self.scan_pt = 0
    
    # returns the value this scannable represents
    def rawGetPosition(self):
        return self.sleep_sec
    
    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        self.sleep_sec = new_position
    
    # Returns the status of this Scannable
    def rawIsBusy(self):
        return False
    
#    def atScanStart(self):
#        print "sleeping..."
#        sleep(self.sleep_sec)
#        print "finished sleeping"
    
    def atPointStart(self):
        self.scan_pt += 1
        if self.scan_pt == 1:
            if self.verbose:
                print "Sleeping at scan point %i for %s s" %(self.scan_pt, self.sleep_sec)
            sleep(self.sleep_sec)
            if self.verbose:
                print "Finished sleeping at scan point %i for %s s" %(self.scan_pt, self.sleep_sec)

    def stop(self):
        self.reset()
    
    def atScanEnd(self):
        self.reset()
    
    def atCommandFailure(self):
        self.reset()

sleepy_start=SleepAtScanStart("sleepy_start",1)



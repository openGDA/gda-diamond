import os
import time 
import datetime
import subprocess
import csv
import socket
from time import sleep
from gda.data import NumTracker
from gdascripts.messages import handle_messages
from gda.jython import InterfaceProvider
from gda.factory import Finder
from gda.commandqueue import JythonCommandCommandProvider
from gdascripts.metadata.metadata_commands import setTitle, getTitle, meta_add, meta_ll, meta_ls, meta_rm
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from gda.device.scannable.scannablegroup import ScannableGroup
from epics_scripts.pv_scannable_utils import createPVScannable, caput, caget, caputStringAsWaveform
from gda.configuration.properties import LocalProperties
from gda.device.scannable import EpicsScannable
from gda.jython import InterfaceProvider, Jython
from gda.jython.commands import GeneralCommands
from tomographyScan import tomoFlyScan

print "Running i13i_utilities.py..."

# set up a nice method for getting the latest file path
i13iNumTracker = NumTracker("i13i")
finder = Finder.getInstance()

# to get working directory, eg /dls/i13/data/2015/cm12165-1/raw/
def wd():
    """
    Method to get working directory for the current visit in GDA
    """
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    return dir

# to get the current file (scan) number
def cfn():
    """
    Method to get the last file (scan) number used by GDA
    """
    filenumber = i13iNumTracker.getCurrentFileNumber()
    return filenumber

# to get the next file (scan) number
def nfn():
    """
    Method to get the next file (scan) number, eg 61192
    """
    filenumber = i13iNumTracker.getCurrentFileNumber()
    return filenumber + 1

# to get the last file path, eg /dls/i13/data/2015/cm12165-1/raw/61191
def pwd():
    """
    Method to get the last file path used by GDA, eg /dls/i13/data/2015/cm12165-1/raw/61192
    """
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i13iNumTracker.getCurrentFileNumber()
    return os.path.join(dir, str(filenumber))

# to get the next file path, eg /dls/i13/data/2015/cm12165-1/raw/61192
def nwd():
    """
    Method to get the next file path, eg /dls/i13/data/2015/cm12165-1/raw/61192
    """
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i13iNumTracker.getCurrentFileNumber()
    return os.path.join(dir, str(filenumber + 1))

# to change the sub-directory of the GDA current working directory
def setSubdirectory(dirname):
    """
    Method to add a sub-directory to the GDA current working directory, eg setSubdirectory('X/Y') sets the path to /dls/i13/data/2015/cm12165-1/X/Y/
    and setSubdirectory('') sets the path back to /dls/i13/data/2015/cm12165-1/
    """
    try:
        finder.find("GDAMetadata").setMetadataValue("subdirectory", dirname)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem setting metadata value for 'subdirectory' to " + dirname, exceptionType, exception, traceback, False)
        print "Failed to set metadata value for 'subdirectory' to:", dirname, exception
        

# to get the sub-directory of the GDA current working directory
def getSubdirectory():
    """
    Method to get the sub-directory of the GDA current working directory, eg 'X/Y' is returned if setSubdirectory('X/Y') was executed earlier to set
    the path to /dls/i13/data/2015/cm12165-1/X/Y/.
    For the default sub-directory on i13i, getSubdirectory outputs 'raw'. 
    """
    try:
        return finder.find("GDAMetadata").getMetadataValue("subdirectory")
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem getting metadata value for 'subdirectory' ", exceptionType, exception, traceback, False)
        print "Failed to get metadata value for 'subdirectory':", exception
        return None

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

def getVisitPath():
    data_path = LocalProperties.get("gda.data.scan.datawriter.datadir")
    data_path_split = data_path.rsplit('/')
    visit_path = '/'
    for i in range(1,6):
        visit_path = os.path.join(visit_path, data_path_split[i])
    return visit_path
    
import smtplib
from email.mime.text import MIMEText
def send_email(whoto, subject, body, verbose=False):
    """
    To send an e-mail from the beamline's GDA server to one or more recipients
    
    whoto - the list of e-mail addresses of the intended recipients (list of strings, eg ['user_name@diamond.ac.uk'] or ["user_name_one@diamond.ac.uk", "user_name_two@gmail.com"])
    subject - the subject of the e-mail to be send (string)
    body - the content of the e-mail to be send (string)
    verbose - if True, a short message is displayed when e-mail is successful sent  
    
    Example:
    send_email(["user_name_one@diamond.ac.uk", "user_name_two@gmail.com"], "Update on myscript's relentless progress...", "myscript completed without errors - hurrah!")
    
    The e-mail message sent by the above command will show up in the relevant mail boxes as follows:   
        From:		gda@i13-control.diamond.ac.uk
        Subject:	Update on myscript's relentless progress...
        Content:	myscript completed without errors - hurrah!
    """
    whofrom = "gda"
    if not type(whoto) is list:
        msg = "'whoto' must be a list, eg ['user_name@diamond.ac.uk'] or ['user_name_one@diamond.ac.uk', 'user_name_two@gmail.com']"
        raise Exception(msg)
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = whofrom
    msg['To'] = ", ".join(whoto)
     
    try:
        s = smtplib.SMTP('localhost')
        s.sendmail(whofrom, whoto, msg.as_string())
        s.quit()
        if verbose:
            print "E-mail successfully sent!"
    except smtplib.SMTPException, ex:
        print "Failed to send e-mail: %s!" %(str(ex))

def clear_defaults():
    """To clear all current default scannables."""
    srv = finder.findSingleton(Jython)
    all_vec = srv.getDefaultScannables()
    all_arr = all_vec.toArray()
    for s in all_arr:
        remove_default(s)
    return all_arr
alias("_clear_defaults")


def clear_meta_data():
    """To clear all current meta-data."""
    ls_str = meta_ls()
    all_lst = []
    all_kv_lst = []
    if len(ls_str) > len("meta:"):
        ls_str_ = ls_str.split("meta:")[1]
        all_lst = ls_str_.split("\n")[1:]
        print all_lst
        ll_str = meta_ll()
        ll_str_ = ll_str.split("meta:")[1]
        all_ll_lst = ll_str_.split("\n")[1:]
        print all_ll_lst
        for m in all_lst:
            m_ = m.strip().split(".")[0]
            print "m_ = %s" %(m_)
            try:
                scn_m = finder.find(m_)
                if scn_m is not None:
                    all_kv_lst.append((m_, None))
                    meta_rm(scn_m)
                else:
                    for x in all_ll_lst:
                        if m_ in x:
                            m_v = x.split(" = ")[1]
                            print "m_v = %s, x = %s" %(m_v, x)
                            all_kv_lst.append((m_, m_v))
                    meta_rm(m_)
            except Exception, ex:
                print "Excepting... " + str(ex)
    else:
        print "No meta-data found to clear!"
    return all_lst, all_kv_lst
alias("clear_meta_data")

def createScannableFromPV( name, pv, addToNameSpace=True, getAsString=True, hasUnits=False):
    """
    Description:
        Utility function to create a scannable from a given PV
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

class StringDisplayEpicsPVClass(ScannableMotionBase):
    '''Create PD to display single EPICS PV which returns a string (label)'''
    def __init__(self, name, pvstring):
        self.pvstring = pvstring
        self.setName(name);
        self.setInputNames([name])
        self.setLevel(8)
        self.outcli=CAClient(pvstring)
    
    def rawGetPosition(self):
        output = "rawGetPosition: unknown position"
        try:
            if not self.outcli.isConfigured():
                self.outcli.configure()
            output=str(self.outcli.caget())
        except Exception, ex:
            output="caget failed"
            print "Error in rawGetPosition: ", ex
        finally:
            return output
    
    def rawAsynchronousMoveTo(self,position):
        return
    
    def rawIsBusy(self):
        return 0
    
    def set_pvstring(self, pvstring):
        if self.outcli.isConfigured():
            self.outcli.clearup()
        self.pvstring = pvstring
    
class StringListDisplayEpicsPVClass(ScannableMotionBase):
    '''Create PD to display single EPICS PV which returns a string (label)'''
    def __init__(self, name, name_lst, pvstring_lst):
        self.setName(name);
        self.setInputNames(name_lst)
        self.setLevel(8)
        self.outcli_lst=[]
        for n, pv in zip(name_lst, pvstring_lst):
            self.outcli_lst.append((n, pv, CAClient(pv)))
    
    def configureAll(self):
        for n_pv_cac in self.outcli_lst:
            if not n_pv_cac[2].isConfigured():
                n_pv_cac[2].configure()
    
    def clearupAll(self):
        for n_pv_cac in self.outcli_lst:
            if n_pv_cac[2].isConfigured():
                n_pv_cac[2].clearup()
    
    def rawGetPosition(self):
        try:
            output = []
            self.configureAll()
            for n_pv_cac in self.outcli_lst:
                try:
                    output.append(str(n_pv_cac[2].caget()))
                except Exception, ex:
                    output.append("caget failed")
                    print "Trouble for %s with pv %s" %(n_pv_cac[0], n_pv_cac[1]), ex
        except Exception, ex:
            output=[None]*len(self.outcli_lst)
            print "Another trouble", ex
        return output
    
    def rawAsynchronousMoveTo(self,position):
        return
    
    def rawIsBusy(self):
        return 0

pco_cam_model = StringDisplayEpicsPVClass("pco_cam_model", "BL13I-EA-DET-01:CAM:Model_RBV")

pco_focus_prefix = "BL13I-MO-CAM-02:FOCUS"
pco_edge_focus_label = StringDisplayEpicsPVClass("focus_pco_edge_label", pco_focus_prefix + ":MP:RBV:CURPOS")
pco_edge_focus = StringDisplayEpicsPVClass("focus_pco_edge", pco_focus_prefix + ".RBV")
pco_edge_turret = StringDisplayEpicsPVClass("turret_pco_edge", "BL13I-MO-CAM-02:TURRET:P:UPD.D")

pco_4000_focus_label = StringDisplayEpicsPVClass("focus_pco_4000_label", "BL13I-MO-STAGE-01:FOCUS:MP:RBV:CURPOS")
pco_4000_focus = StringDisplayEpicsPVClass("focus_pco_4000", "BL13I-MO-STAGE-01:FOCUS.RBV")
pco_4000_turret = StringDisplayEpicsPVClass("turret_pco_4000", "BL13I-MO-CAM-01:TURRET:P:UPD.D")

filter_stick_1 = finder.find("f1_Stick1")
filter_stick_2 = finder.find("f1_Stick2")
filter_stick_3 = finder.find("f1_Stick3")
filter_stick_4 = finder.find("f1_Stick4")
filter_stick_5 = finder.find("f1_Stick5")

dcm_mode = finder.find("dcm_mode")

ionc_A_over_V_gain = createScannableFromPV("ionc_A_over_V_gain", "BL13I-DI-FEMTO-06:GAIN", addToNameSpace=True, getAsString=True, hasUnits=False)
ionc_gainmode = createScannableFromPV("ionc_gainmode", "BL13I-DI-FEMTO-06:GAINMODE", addToNameSpace=True, getAsString=True, hasUnits=False)
ionc_acdc = finder.find("ionc_acdc")

try:
    ionc_cfg = ScannableGroup()
    ionc_cfg.setName("ionc_cfg")        
    ionc_cfg.addGroupMember(ionc_A_over_V_gain)
    ionc_cfg.addGroupMember(ionc_gainmode)
    ionc_cfg.addGroupMember(ionc_acdc)
    ionc_cfg.configure()
except Exception, ex:
    print "Failed to create the ionc_prm group: ", str(ex)
    
try:
    pco_edge_agg = ScannableGroup()
    pco_edge_agg.setName("pco_edge_agg")
    pco_edge_agg.addGroupMember(pco_cam_model)
    pco_edge_agg.addGroupMember(pco_edge_focus_label)
    pco_edge_agg.addGroupMember(pco_edge_focus)
    pco_edge_agg.configure()
except Exception, ex:
    print "Failed to create the pco_edge_agg group: ", str(ex)

try:
    pco_4000_agg = ScannableGroup()
    pco_4000_agg.setName("pco_4000_agg")
    pco_4000_agg.addGroupMember(pco_cam_model)
    pco_4000_agg.addGroupMember(pco_4000_focus_label)
    pco_4000_agg.addGroupMember(pco_4000_focus)
    pco_4000_agg.configure()
except Exception, ex:
    print "Failed to create the pco_4000_agg group: ", str(ex)
    
try:
    filter_sticks = ScannableGroup()
    filter_sticks.setName("filter_sticks")
    filter_sticks.addGroupMember(filter_stick_1)
    filter_sticks.addGroupMember(filter_stick_2)
    filter_sticks.addGroupMember(filter_stick_3)
    filter_sticks.addGroupMember(filter_stick_4)
    filter_sticks.addGroupMember(filter_stick_5)
    filter_sticks.configure()
except Exception, ex:
    print "Failed to create the filter_sticks group: ", str(ex)



def isLive():
    mode = LocalProperties.get("gda.mode")
    return mode =="live" or mode =="live_localhost"



def stressTest(nScans=100, pathToVisit="/dls/i13/data/2016/cm14467-4", filesys="na"):
    """
    Function to run a sequence of tomography fly scans to test the performance of the file system. 
    
    Args:
        nScans - initial number of scans, which is then repeated ad infinitum
        pathToVisit - path to the visit directory
        filesys - "na" for NetApp and "gpfs" for GPFS03
         
    Notes: 
        (1) all scan files will be saved in the tmp sub-directory of the input visit directory
        (2) execute reportTomo to see which stages and detectors will be used in these scans
        (3) it is recommended to use a dummy tomography_translation
        (4) make sure that Command Queue is not paused! 
    """
    print "Executing stressTest..."
    datadir_saved = LocalProperties.get("gda.data.scan.datawriter.datadir")
    
    windowsSubString_dct = {"na": "d:\\i13\\data\\", "gpfs": "g:\\i13\\data\\"}
    flyScanDetectorNoChunking = finder.find("flyScanDetectorNoChunking")
    #windowsSubString_saved = flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    #print "windowsSubString_saved = %s" %(windowsSubString_saved)
    print "Setting windowsSubString to %s..." %(windowsSubString_dct[filesys])
    flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.setWindowsSubString(windowsSubString_dct[filesys])
    print "Current windowsSubString = %s" %(flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString())
    
    title_saved = getTitle()
    setTitle("stressTest")
    try:
        cqp=finder.find("commandQueueProcessor")
        datadir = os.path.join(pathToVisit, "tmp")
        LocalProperties.set("gda.data.scan.datawriter.datadir", datadir)    # this does not seem to work from inside this fn as files go to raw, not tmp!
        LocalProperties.set("gda.data", datadir)                            # this does not seem to work from inside this fn as files go to raw, not tmp!
        print "All scan files will be saved in %s" %(LocalProperties.get("gda.data.scan.datawriter.datadir"))
        for i in range(nScans):
            cmd="tomographyScan.tomoFlyScan(2.3,2.3,exposureTime=.01, start=-90, stop=90., step=0.1, imagesPerDark=0, imagesPerFlat=0, setupForAlignment=False)"
            cqp.addToTail(JythonCommandCommandProvider(cmd, "StressTest "+`i`,None))
        cqp.addToTail(JythonCommandCommandProvider("stressTest()", "Add stressTest to the queue",None))
    except Exception, e:
        print "Trouble running stressTest: " +str(e)
    finally:
        LocalProperties.set("gda.data.scan.datawriter.datadir", datadir_saved)
        setTitle(title_saved)
        flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.setWindowsSubString(windowsSubString_dct[filesys])
    print "Finished executing stressTest - bye!"
    
    
    
def stressfly13(nscans, exposureTime, start, stop, step, pathToVisitDir="/dls/i13/data/2019/cm22976-3", filesys="gpfs"):
    """
    Fn to collect a series of fly scans for testing purposes with the following:
	dummy translation stage is expected to be used!
	no flats and darks
	all scan files going to the tmp sub-directory of the input pathToVisitDir
 
    nscans = tot number of scans to be run
    exposureTime = exposure time in seconds
    start = first rotation angle
    stop = last rotation angle
    step = rotation step size
    pathToVisitDir = path to a directory which GDA can use for writing log files, ie /dls/i13/data/2016/cm14467-4
    filesys = 'na' for NetApp and 'gpfs' for GPFS03
    """
    _fn = stressfly13.__name__
    windowsSubString_dct = {"na": "d:\\i13\\data\\", "gpfs": "g:\\i13\\data\\"} 	# was "t:\\i13\\data\\"} for GPFS01
    flyScanDetectorNoChunking = finder.find("flyScanDetectorNoChunking")
    #windowsSubString_saved = flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    #print "windowsSubString_saved = %s" %(windowsSubString_saved)
    print "Setting windowsSubString to %s..." %(windowsSubString_dct[filesys])
    flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.setWindowsSubString(windowsSubString_dct[filesys])
    print "Current windowsSubString = %s" %(flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString())
    
    pv_after_scan = {"HDF5:IOSpeed": "BL13I-EA-DET-01:HDF5:IOSpeed", "HDF5:DroppedArrays": "BL13I-EA-DET-01:HDF5:DroppedArrays_RBV", "HDF5:RunTime": "BL13I-EA-DET-01:HDF5:RunTime"}
    log_subdir_path = "raw/testout"
    log_dir_path = os.path.join(pathToVisitDir, log_subdir_path)  # it appears GDA can't save files in tmp or processing
    print "log_dir_path = %s" %(log_dir_path)
    if (not os.path.exists(log_dir_path)):
        try:
            os.makedirs(log_dir_path)
        except Exception, e:
            msg="Failed to create sub-directory %s: " %(log_dir_path)
            raise Exception(msg + str(e))
    log_file_name = _fn
    timestr_template = "%Y-%m-%dT%H-%M-%S"
    timestr = time.strftime(timestr_template)
    log_file_name += ("_%s_" %(filesys))
    log_file_name += timestr
    #log_file_name += ".log"
    log_file_name += ".csv"
    log_file_path = os.path.join(log_dir_path,log_file_name)
    fh = open(log_file_path, 'wt')
    print "Saving log file in: %s\n" %(log_file_path)
    
    title_saved = getTitle()
    title = _fn +"_" + filesys
    msg = wd()
    print "Saving data in: " + msg
    try:
        i =-1
        timestr_template_HMS = "%H:%M:%S"
        csv_writer = csv.writer(fh)
        #msg = "scan iter \t scan number \t start time \t end time \t elapsed (min) \t HDF5:IOSpeed \t HDF5:RunTime \t HDF5:Dropped"
        #fh.write(msg+"\n")
        csv_writer.writerow(('scan iter', 'scan number', 'start time', 'end time', 'elapsed (min)', 'HDF5:IOSpeed', 'HDF5:RunTime', 'HDF5:Dropped'))
        for i in range(nscans):
            interruptable()             # for breaking this loop when GDA Abort button is pressed
            title_tmp = title
            title_tmp += "_%d/%d" %((i+1), nscans)
            setTitle(title_tmp)
            timestr_start = time.strftime(timestr_template_HMS)
            print "Starting scan iter %d (of %d), start time: %s." %(i+1, nscans, timestr_start)
            #msg = "scan iter: %d/%d, scan number: %d, start time: %s" %((i+1), nscans, nfn(), timestr_start)
            #fh.write(msg+"\n")
            start_time = time.time()
            tomoFlyScan(inBeamPosition=0., outOfBeamPosition=1., exposureTime=exposureTime, \
                                       start=start, stop=stop, step=step, \
                                       imagesPerDark=0, imagesPerFlat=0)
            end_time = time.time()
            elapsed_min = (end_time - start_time)/60.0
            timestr_end = time.strftime(timestr_template_HMS)
            #msg = "scan iter: %d/%d, scan number: %d, start time: %s, end time: %s, elapsed (min): %f, HDF5:IOSpeed: %s, HDF5:Dropped: %s" %((i+1), nscans, cfn(), timestr_start, timestr_end, elapsed_min, str(caget(pv_after_scan["HDF5:IOSpeed"])), str(caget(pv_after_scan["HDF5:DroppedArrays"])))
            #msg = "%d/%d \t %d \t %s \t %s \t %f \t %s \t %s \t %s" %((i+1), nscans, cfn(), timestr_start, timestr_end, elapsed_min, str(caget(pv_after_scan["HDF5:IOSpeed"])), str(caget(pv_after_scan["HDF5:RunTime"])), str(caget(pv_after_scan["HDF5:DroppedArrays"])))
            #fh.write(msg+"\n")
            csv_writer.writerow(("%d/%d" %((i+1), nscans), cfn(), timestr_start, timestr_end, elapsed_min, str(caget(pv_after_scan["HDF5:IOSpeed"])), str(caget(pv_after_scan["HDF5:RunTime"])), str(caget(pv_after_scan["HDF5:DroppedArrays"]))))
            fh.flush()
            print "Finished scan iter %d (of %d), end time: %s." %(i+1, nscans, timestr_end)
            interruptable()             # for breaking this loop when GDA Abort button is pressed
    except Exception, e:
        msg = "Scan %d (of %d) has failed: " %(i+1, nscans)
        print msg + str(e)
    finally:
        fh.close()
        setTitle(title_saved)
    print "\n Finished executing %s - bye!" %(_fn)

def interruptable():
    """
    Fn to facilitate making for-loops interruptable in GDA: need to call this fn in the 1st or the last line of a for-loop
    """
    GeneralCommands.pause()

def use_storage(storage_name, notify=False, comment='', verbose=False):
    """
    Fn to select a storage place, NetApp or GPGS01, for saving GDA scan files. After executing this command, any subsequent GDA scans will save their scan files on the selected storage.
    Note: this command needs to be excuted again if GDA servers are re-started
    
    Arg(s)
    storage_name (String) - short name of the storage place to be used for GDA saving scan files:
        "na" - NetApp local storage 
        "gpfs" - GPFS03 central storage
    notify (boolean) - if True, an e-mail notification is sent to relevant stakelders
    comment (String) - a user-provided justification for changing storage, to be included in all e-mail notifications to stakeholders
    verbose (String) - if True, e-mail addresses are reported at the time e-mail notifications are sent out      
    """
    #assert na or gpfs

    now = time.strftime("%c")
    notify = True
    emails = []
    emails.append('kaz.wanelik@diamond.ac.uk')
#    emails.append('frederik.ferner@diamond.ac.uk')
#    emails.append('andy.wilson@diamond.ac.uk')
#    christoph on i13 / michael on i12?

    detector_objs = {}
    detector_objs.update({'flyScanDetectorNoChunking': 'flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.setWindowsSubString(%s)'})

    storage_name_ = storage_name.lower()
    windowsSubString_dct = {"na": "d:\\i13\\data\\", "gpfs": "g:\\i13\\data\\"}
    windowsSubString_rvr_dct = {"d": "NetApp", "g": "GPFS03"}

    storage_path = windowsSubString_dct[storage_name_]
    setn_out_str = "Setting %s to use %s (%s)..."
    fin_out_str = "Finished setting %s to use %s (%s)."
    curr_out_str = "%s is now set to use %s (%s).\n"

    # loop over objects in detectors_obj, finding each obj and then executing the corresponding command (handle failures gracefully without aborting the loop)

    # PCO HDF detectors
    flyScanDetectorNoChunking = finder.find("flyScanDetectorNoChunking")
    det_name = flyScanDetectorNoChunking.getName()
    det_drv = storage_path.split(':')[0]
    print setn_out_str %(det_name, windowsSubString_rvr_dct[det_drv], storage_path)
    flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.setWindowsSubString(storage_path)
    print fin_out_str %(det_name, windowsSubString_rvr_dct[det_drv], storage_path)
    det_cfg = flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    flyScanFlatDarkDetectorNoChunking = finder.find("flyScanFlatDarkDetectorNoChunking")
    det_name = flyScanFlatDarkDetectorNoChunking.getName()
    det_drv = storage_path.split(':')[0]
    print setn_out_str %(det_name, windowsSubString_rvr_dct[det_drv], storage_path)
    flyScanFlatDarkDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.setWindowsSubString(storage_path)
    print fin_out_str %(det_name, windowsSubString_rvr_dct[det_drv], storage_path)
    det_cfg = flyScanFlatDarkDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    # PCO TIFF detectors 
    flyScanDetectorTIF = finder.find("flyScanDetectorTIF")
    det_name = flyScanDetectorTIF.getName()
    det_drv = storage_path.split(':')[0]
    print setn_out_str %(det_name, windowsSubString_rvr_dct[det_drv], storage_path)
    flyScanDetectorTIF.pluginList[1].getNdFile().getFilePathConverter().setWindowsSubString(storage_path)
    print fin_out_str %(det_name, windowsSubString_rvr_dct[det_drv], storage_path)
    det_cfg = flyScanDetectorTIF.pluginList[1].getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    flyScanFlatDarkDetectorTIF = finder.find("flyScanFlatDarkDetectorTIF")
    det_name = flyScanFlatDarkDetectorTIF.getName()
    det_drv = storage_path.split(':')[0]
    print setn_out_str %(det_name, windowsSubString_rvr_dct[det_drv], storage_path)
    flyScanFlatDarkDetectorTIF.pluginList[1].getNdFile().getFilePathConverter().setWindowsSubString(storage_path)
    print fin_out_str %(det_name, windowsSubString_rvr_dct[det_drv], storage_path)
    det_cfg = flyScanFlatDarkDetectorTIF.pluginList[1].getNdFile().getFilePathConverter().getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    #pco1_aux_tif.pluginList[1].getNdFile().getFilePathConverter().setWindowsSubString(storage_path)

    # pco_hw_hdf, pco_hw_hdf_nochunking, pco_hw_tif, pco1_tif?  
    # pco1_hw_hdf.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    # pco1_hw_hdf_nochunking.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    # pco1_hw_tif.pluginList[1].getNdFile().getFilePathConverter().getWindowsSubString()

    # need to undo .tmp (rsync) and suppressing some GDA error messages
    # need to undo .tmp and suppressing some GDA error messages

    if storage_name_ == "na":
        #print "disable 'waiting for file to be created'"
        #pixium10_tif.pluginList[1].waitForFileArrival=False
        #print "disable 'Path does not exist on IOC'"
        #pixium10_tif.pluginList[1].pathErrorSuppressed=True

        #pco4000_dio_tif.setCheckFileExists(False)
        #pco4000_dio_tif.fileWriter.pathErrorSuppressed=True
        #pco4000_dio_hdf.pluginList[1].pathErrorSuppressed=True
        
        # i13
        #pco1_hw_tif.pluginList[1].waitForFileArrival=False
        #pco1_tif.pluginList[1].waitForFileArrival=False

        flyScanDetectorNoChunking.getAdditionalPluginList()[0].pathErrorSuppressed=True
        flyScanFlatDarkDetectorNoChunking.getAdditionalPluginList()[0].pathErrorSuppressed=True
        
        caput("BL13I-EA-DET-01:HDF5:TempSuffix", ".tmp")
        caput("BL13I-EA-DET-01:TIFF:TempSuffix", ".tmp")
    elif storage_name_ == "gpfs":
        #print "enable 'waiting for file to be created'"
        #pixium10_tif.pluginList[1].waitForFileArrival=True
        #print "enable 'Path does not exist on IOC'"
        #pixium10_tif.pluginList[1].pathErrorSuppressed=False
        
        # i13
        #pco1_hw_tif.pluginList[1].waitForFileArrival=True
        #pco1_tif.pluginList[1].waitForFileArrival=True

        #pco4000_dio_tif.setCheckFileExists(True)
        #pco4000_dio_tif.fileWriter.pathErrorSuppressed=False
        #pco4000_dio_hdf.pluginList[1].pathErrorSuppressed=False

        flyScanDetectorNoChunking.getAdditionalPluginList()[0].pathErrorSuppressed=False
        flyScanFlatDarkDetectorNoChunking.getAdditionalPluginList()[0].pathErrorSuppressed=False
        
        caput("BL13I-EA-DET-01:HDF5:TempSuffix", "")
        caput("BL13I-EA-DET-01:TIFF:TempSuffix", "")
    else:
        msg = "Unsupported storage mode: %s!" %(storage_name_)
        print msg


    pretty_print_dct = {'na': 'NetApp', 'gpfs': 'GPFS03'}

    if notify and len(emails)>0:
        if verbose:
            print('Sending an e-mail notification to:')
            for eml in emails:
                print(eml) 
        #send e-mail, specifying: time, visit's path (with beamline id)
        storage_name = pretty_print_dct[storage_name_]
        hst = socket.gethostname()
        beamline = 'i13'
        sbj = '%s storage changed to %s.' %(beamline, storage_name)
        filepath = pwd()+'.nxs'
        visit_id = filepath
        bdy = '%s: storage changed to %s for visit %s at %s.' %(beamline, storage_name, visit_id, now)
        if len(comment)>0:
            bdy += '\n' + comment
        else:
            bdy += ' No comment provided.'
        send_email(emails, subject=sbj, body=bdy, verbose=verbose)

    print "\n * Finished configuring beamline storage to %s!" %(storage_name_)
    


def report_storage():
    """
    Desc:
    Fn to report current storage configuration for saving scan files on the beamline.
    """
    windowsSubString_rvr_dct = {"d": "NetApp", "g": "GPFS03"}
    
    #curr_out_str = "Current windowsSubString for %s is %s (%s)."
    curr_out_str = "%s is currently configured to use the %s storage (on %s)."
    
    # PCO TIFF detector objects
    #pco4000_dio_tif = finder.find("pco4000_dio_tif")
    #det_name = pco4000_dio_tif.getName()
    #det_cfg = pco4000_dio_tif.getNdFile().getFilePathConverter().getWindowsSubString()
    #det_drv = det_cfg.split(':')[0]
    #print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

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
    flyScanDetectorNoChunking = finder.find("flyScanDetectorNoChunking")
    det_name = flyScanDetectorNoChunking.getName()
    det_cfg = flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    flyScanFlatDarkDetectorNoChunking = finder.find("flyScanFlatDarkDetectorNoChunking")
    det_name = flyScanFlatDarkDetectorNoChunking.getName()
    det_cfg = flyScanFlatDarkDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    det_drv = det_cfg.split(':')[0]
    print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    #pco4000_dio_hdf = finder.find("pco4000_dio_hdf")
    #det_name = pco4000_dio_hdf.getName()
    #det_cfg = pco4000_dio_hdf.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    #det_drv = det_cfg.split(':')[0]
    #print curr_out_str %(det_name, windowsSubString_rvr_dct[det_drv], det_cfg)

    #flyScanDetector, flyScanDetectorTIF
    # pco1_hw_hdf_nochunking

from gdascripts.scannable.beamokay import WaitWhileScannableBelowThresholdMonitorOnly, reprtime

class WaitWhileScannableBelowThresholdMonitorOnlyWithEmailFeedback(WaitWhileScannableBelowThresholdMonitorOnly):
    
    def __init__(self, name, scannableToMonitor, minimumThreshold, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=0, emails=None):
        WaitWhileScannableBelowThresholdMonitorOnly.__init__(self, name, scannableToMonitor, minimumThreshold, secondsBetweenChecks, secondsToWaitAfterBeamBackUp)
        self.emails = emails
        self.feedback_reqd_ = True 
        
    def handleStatusChange(self,status):
        ixx = "i13" 
        ## check for status change to provide feedback:
        if status and self.lastStatus:
            pass # still okay
        if status and not self.lastStatus:
            msg = "*** " + self.name + ": Beam back up at: " + reprtime() + ". Resuming scan in " + str(self.secondsToWaitAfterBeamBackUp) + "s..."
            print(msg)
            if len(self.emails) : send_email(whoto=self.emails, subject=ixx+": "+msg, body=msg)
            self.lastStatus = True
            sleep(self.secondsToWaitAfterBeamBackUp)
            msg = "*** " + self.name + ":  Resuming scan now at " + reprtime()
            if len(self.emails) : send_email(whoto=self.emails, subject=ixx+": "+msg, body=msg)
            print(msg)
        if not status and not self.lastStatus:
            pass # beam still down
        if not status and self.lastStatus:
            msg = "*** " + self.name + ": Beam down at: " + reprtime() + " . Pausing scan..."
            print(msg)
            self.lastStatus = False
            if len(self.emails) : send_email(whoto=self.emails, subject=ixx+": "+msg, body=msg)
  
from gda.device.scannable import TopupChecker
class TopupProtector(TopupChecker):
    """
    For example, scan ix 0 20 1 pco_det 0.1 topup_protec [0.1, 10, 2]
    """ 

    def __init__(self, name, machCountdownMonitor, machModeMonitor, level=1):
        self.setName(name)
        #self.setInputNames(["collectionTime", "tolerance", "waittime"])
        self.setInputNames(["collection_interval_sec", "before_interval_sec", "after_interval_sec"])
        self.setOutputFormat(["%.3f"])
        self.setScannableToBeMonitored(machCountdownMonitor)
        self.setMachineModeMonitor(machModeMonitor)

    def rawAsynchronousMoveTo(self, position):
        self.collectionTime = position[0]
        self.tolerance = position[1]
        self.waittime = position[2]

    def rawGetPosition(self):
        return [self.collectionTime, self.tolerance, self.waittime]
        
#bm = WaitWhileScannableBelowThresholdMonitorOnly("bm", ring_current, minimumThreshold=200.0, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=1)


from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider
from gda.epics import CAClient

class PseudoScannable(ScannableBase):
    def __init__(self, name, obj):
        self.name = name
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ["%s"]
        self.obj = obj
        
    def getPosition(self):
        return str(self.obj)
    
    def isBusy(self):
        return False
    
class DetCfg(ScannableBase):
    _dct = {}
    _dct.update({'BL13I-EA-DET-01': {}}) # pco 4000
    _dct['BL13I-EA-DET-01'].update({'model': ('BL13I-EA-DET-01:CAM:Model_RBV', "%s")})
    _dct['BL13I-EA-DET-01'].update({'focus_name': ('BL13I-MO-CAM-01:FOCUS:MP:RBV:CURPOS',"%s")})
    _dct['BL13I-EA-DET-01'].update({'focus': ('BL13I-MO-CAM-01:FOCUS.RBV',"%s")})
    _dct['BL13I-EA-DET-01'].update({'turret': ('BL13I-MO-CAM-01:TURRET:P:UPD.D',"%s")})
    _dct['BL13I-EA-DET-01'].update({'turret': ('BL13I-MO-CAM-01:TURRET:P:UPD.D',"%s")})
    _dct['BL13I-EA-DET-01'].update({'pixel_rate': ('BL13I-EA-DET-01:CAM:PIX_RATE',"%s")})
    _dct['BL13I-EA-DET-01'].update({'adc_mode': ('BL13I-EA-DET-01:CAM:ADC_MODE',"%s")})

    _dct.update({'BL13I-EA-DET-02': {}}) # pco EDGE
    _dct['BL13I-EA-DET-02'].update({'model': ('BL13I-EA-DET-02:CAM:Model_RBV',"%s")})
    _dct['BL13I-EA-DET-02'].update({'focus_name': ('BL13I-MO-CAM-02:FOCUS:MP:RBV:CURPOS',"%s")})
    _dct['BL13I-EA-DET-02'].update({'focus': ('BL13I-MO-CAM-02:FOCUS.RBV',"%s")})
    _dct['BL13I-EA-DET-02'].update({'turret': ('BL13I-MO-CAM-02:TURRET:P:UPD.D',"%s")})
    _dct['BL13I-EA-DET-02'].update({'pixel_rate': ('BL13I-EA-DET-02:CAM:PIX_RATE',"%s")})
    _dct['BL13I-EA-DET-02'].update({'adc_mode': ('BL13I-EA-DET-02:CAM:ADC_MODE',"%s")})
    
    def __init__(self, name):
        self.name = name
        self.inputNames = []
        self.extraNames = []
        self.outputFormat = []
        self.det_base_pv = None
        self.cac_dct = {}
        
    def atScanStart(self):
        print("***************** atScanStart")
        inputNames = []
        outputFormat = []
        det_names = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation().getDetectorNames()
        if len(det_names)>0:
            det_name = det_names[0]
            try:
                det_obj = finder.find(det_name)
                self.det_base_pv = det_obj.getCollectionStrategy().getAdBase().getBasePVName()
                print self.det_base_pv
            except Exception, e:
                print("Error in atScanStart: %s" %(str(e)))
            for k, v in type(self)._dct[self.det_base_pv].iteritems():
                print k, v #, v[0], v[1]
                self.cac_dct.update({k: CAClient(v[0])})
                #self.extraNames.append(k)
                inputNames.append(k)
                #self.outputFormat.append(v[1])
                outputFormat.append(v[1])
            #self.extraNames = kzkz
            #print kzkz
            print inputNames
            print outputFormat
            self.inputNames = inputNames
            self.outputFormat = outputFormat
            self.configure()
                
    def configure(self):
        for k, v in self.cac_dct.iteritems():
            self.cac_dct[k].configure()
    
    def isBusy(self):
        return False
    
    def getPosition(self):
        pos_out = []
        for k, cac in self.cac_dct.iteritems():
            pos_out.append(cac.caget())
        return pos_out
            

# simultaneous cameras 
def set_sim_cam_step(mode):
    det = finder.find("pco1_hw_hdf_nochunking")
    cs = det.getCollectionStrategy()
    if mode == 0:
        # original set-up
        cs.setNoLongerBusyTriggerSetupCommand('tfg setup-trig start adc5 alternate 1')
        cs.setExposeTriggerOutVal(64)
        cs.setNoLongerBusyTriggerInVal(39) #dead port for the old cam
    else:
        cs.setNoLongerBusyTriggerSetupCommand('tfg setup-trig start adc2 alternate 1')
        cs.setExposeTriggerOutVal(16) # 80 to send triggers to both cameras at the same time
        cs.setNoLongerBusyTriggerInVal(34) #dead port for the new cam (CLHS/maxipix)

def get_sim_cam_step():
    det = finder.find("pco1_hw_hdf_nochunking")
    cs = det.getCollectionStrategy()
    cmdBusy = cs.getNoLongerBusyTriggerSetupCommand()
    exposeOut = cs.getExposeTriggerOutVal()
    busyIn = cs.getNoLongerBusyTriggerInVal()
    print "(cmdBusy, exposeOut, busyIn) = ('%s', %s, %s)"%(cmdBusy, exposeOut, busyIn)

def set_sim_cam_fly(mode, exposeTriggerOut=16, noLongerBusyTriggerIn=34):
    det = finder.find("flyScanDetectorNoChunking")
    cs = det.getCollectionStrategy()
    if mode == 0:
        # original set-up
        cs.setExposeTriggerOutVal(64)
        cs.setNoLongerBusyTriggerInVal(39)
    else:
        cs.setExposeTriggerOutVal(exposeTriggerOut) # 80 to send triggers to both cameras at the same time
        cs.setNoLongerBusyTriggerInVal(0) #(noLongerBusyTriggerIn) #set dead port to 0 if waiting for cam busy signal to go down is not required (appears to be needed for fly scans in the switchable/swappable simultaneous-cameras set-up, otherwise some triggers appear to be missed (eg zebra says it issued 1801 but the cam says it collected only 1687 

def get_sim_cam_fly():
    det = finder.find("flyScanDetectorNoChunking")
    cs = det.getCollectionStrategy()
    exposeOut = cs.getExposeTriggerOutVal()
    busyIn = cs.getNoLongerBusyTriggerInVal()
    print "(exposeOut, busyIn) = (%s, %s)"%(exposeOut, busyIn)
    
    
print "Finished running i13i_utilities.py!"

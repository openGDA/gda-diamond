import os
import subprocess
from time import sleep
from gda.data import NumTracker
from gdascripts.messages import handle_messages
from gda.data import PathConstructor
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
from gda.jython import InterfaceProvider

print "Running i13i_utilities.py..."

# set up a nice method for getting the latest file path
i13iNumTracker = NumTracker("i13i")
finder = Finder.getInstance()

# to get working directory, eg /dls/i13/data/2015/cm12165-1/raw/
def wd():
    """
    Method to get working directory for the current visit in GDA
    """
    dir = PathConstructor.createFromDefaultProperty()
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
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i13iNumTracker.getCurrentFileNumber()
    return os.path.join(dir, str(filenumber))

# to get the next file path, eg /dls/i13/data/2015/cm12165-1/raw/61192
def nwd():
    """
    Method to get the next file path, eg /dls/i13/data/2015/cm12165-1/raw/61192
    """
    dir = PathConstructor.createFromDefaultProperty()
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


import smtplib
from email.mime.text import MIMEText
def send_email(whoto, subject, body):
    """
    To send an e-mail from the beamline's GDA server to one or more recipients
    
    whoto - the list of e-mail addresses of the intended recipients (list of strings, eg ['user_name@diamond.ac.uk'] or ["user_name_one@diamond.ac.uk", "user_name_two@gmail.com"])
    subject - the subject of the e-mail to be send (string)
    body - the content of the e-mail to be send (string)
    
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
     
    # send the message via our own SMTP server, but don't include the envelope header
    try:
        s = smtplib.SMTP('localhost')
        s.sendmail(whofrom, whoto, msg.as_string())
        s.quit()
        print "E-mail successfully sent!"
    except smtplib.SMTPException, ex:
    #except Exception, ex:
        print "Failed to send e-mail: %s!" %(str(ex))

def clear_defaults():
    """To clear all current default scannables."""
    srv = finder.find(JythonServer.SERVERNAME)
    all_vec = srv.getDefaultScannables()
    all_arr = all_vec.toArray()
    for s in all_arr:
        #srv.removeDefault(s)
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
        #txt_lst = []
        #scn_lst = []
        #for m in all_lst:
        #    m.strip()
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
                #meta_rm(m_)
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
            #print output
            #sleep(10)
            #self.outcli.clearup()
        except Exception, ex:
            output="caget failed"
            print "Error in rawGetPosition: ", ex
        finally:
            return output
    
    def rawAsynchronousMoveTo(self,position):
        return
    
    def rawIsBusy(self):
        return 0
    
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
                    #print ex
        except Exception, ex:
            output=[None]*len(self.outcli_lst)
            print "Another trouble", ex
        return output
    
    def rawAsynchronousMoveTo(self,position):
        return
    
    def rawIsBusy(self):
        return 0

#pco_cam_model = StringDisplayEpicsPVClass("pco_cam_model", "BL13I-EA-DET-01:CAM:Model_RBV")

pco_cam_model = StringDisplayEpicsPVClass("pco_cam_model", "BL13I-EA-DET-01:CAM:Model_RBV")

pco_edge_focus_label = StringDisplayEpicsPVClass("focus_pco_edge_label", "BL13I-MO-STAGE-02:FOCUS2:MP:RBV:CURPOS")
pco_edge_focus = StringDisplayEpicsPVClass("focus_pco_edge", "BL13I-MO-STAGE-02:FOCUS2.RBV")

pco_4000_focus_label = StringDisplayEpicsPVClass("focus_pco_4000_label", "BL13I-MO-STAGE-02:FOCUS:MP:RBV:CURPOS")
pco_4000_focus = StringDisplayEpicsPVClass("focus_pco_4000", "BL13I-MO-STAGE-02:FOCUS.RBV")

#filter_stick_1 = StringDisplayEpicsPVClass("filter_stick_1", "BL13I-OP-ATTN-01:STICK1:MP:RBV:CURPOS")
#filter_stick_2 = StringDisplayEpicsPVClass("filter_stick_2", "BL13I-OP-ATTN-01:STICK2:MP:RBV:CURPOS")
#filter_stick_3 = StringDisplayEpicsPVClass("filter_stick_3", "BL13I-OP-ATTN-01:STICK3:MP:RBV:CURPOS")
#filter_stick_4 = StringDisplayEpicsPVClass("filter_stick_4", "BL13I-OP-ATTN-01:STICK4:MP:RBV:CURPOS")
#filter_stick_5 = StringDisplayEpicsPVClass("filter_stick_5", "BL13I-OP-ATTN-01:STICK5:MP:RBV:CURPOS")
filter_stick_1 = createScannableFromPV("filter_stick_1", "BL13I-OP-ATTN-01:STICK1:MP:RBV:CURPOS", addToNameSpace=True, getAsString=True, hasUnits=False)
filter_stick_2 = createScannableFromPV("filter_stick_2", "BL13I-OP-ATTN-01:STICK2:MP:RBV:CURPOS", addToNameSpace=True, getAsString=True, hasUnits=False)
filter_stick_3 = createScannableFromPV("filter_stick_3", "BL13I-OP-ATTN-01:STICK3:MP:RBV:CURPOS", addToNameSpace=True, getAsString=True, hasUnits=False)
filter_stick_4 = createScannableFromPV("filter_stick_4", "BL13I-OP-ATTN-01:STICK4:MP:RBV:CURPOS", addToNameSpace=True, getAsString=True, hasUnits=False)
filter_stick_5 = createScannableFromPV("filter_stick_5", "BL13I-OP-ATTN-01:STICK5:MP:RBV:CURPOS", addToNameSpace=True, getAsString=True, hasUnits=False)

#beamline_xray_mode = StringDisplayEpicsPVClass("beamline_xray_mode", "BL13I-OP-DCM-01:MODE:RBV")
beamline_xray_mode = createScannableFromPV("beamline_xray_mode", "BL13I-OP-DCM-01:MODE:RBV", addToNameSpace=True, getAsString=True, hasUnits=False)

ionc_A_over_V_gain = createScannableFromPV("ionc_A_over_V_gain", "BL13I-DI-FEMTO-06:GAINHIGHSPEED", addToNameSpace=True, getAsString=True, hasUnits=False)
ionc_gainmode = createScannableFromPV("ionc_gainmode", "BL13I-DI-FEMTO-06:GAINMODE", addToNameSpace=True, getAsString=True, hasUnits=False)
ionc_acdc = createScannableFromPV("ionc_acdc", "BL13I-DI-FEMTO-06:ACDC", addToNameSpace=True, getAsString=True, hasUnits=False)
    
try:
    pco_edge_agg = ScannableGroup()
    pco_edge_agg.setName("pco_edge_agg")
    pco_edge_agg.addGroupMember(pco_cam_model)
    pco_edge_agg.addGroupMember(pco_edge_focus_label)
    pco_edge_agg.addGroupMember(pco_edge_focus)
    pco_edge_agg.configure()
except Exception, ex:
    #print "Failed to create %s due to %s: " %(pco_edge_agg.getName(), str(ex))
    print "Failed to create the pco_edge_agg group: ", str(ex)

try:
    pco_4000_agg = ScannableGroup()
    pco_4000_agg.setName("pco_4000_agg")
    pco_4000_agg.addGroupMember(pco_cam_model)
    pco_4000_agg.addGroupMember(pco_4000_focus_label)
    pco_4000_agg.addGroupMember(pco_4000_focus)
    pco_4000_agg.configure()
except Exception, ex:
    #print "Failed to create %s due to %s: " %(pco_edge_agg.getName(), str(ex))
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
    #print "Failed to create %s due to %s: " %(pco_edge_agg.getName(), str(ex))
    print "Failed to create the filter_sticks group: ", str(ex)


#pco_edge_aggregate = StringListDisplayEpicsPVClass("pco_edge_aggregate", ["pco_cam_model", "pco_edge_focus_label", "pco_edge_focus"], ["BL13I-EA-DET-01:CAM:Model_RBV", "BL13I-MO-STAGE-02:FOCUS2:MP:RBV:CURPOS", "BL13I-MO-STAGE-02:FOCUS2.RBV"])
#pco_4000_aggregate = StringListDisplayEpicsPVClass("pco_4000_aggregate", ["pco_cam_model", "pco_4000_focus_label", "pco_4000_focus"], ["BL13I-EA-DET-01:CAM:Model_RBV", "BL13I-MO-STAGE-02:FOCUS:MP:RBV:CURPOS", "BL13I-MO-STAGE-02:FOCUS.RBV"])

def isLive():
    mode = LocalProperties.get("gda.mode")
    return mode =="live" or mode =="live_localhost"



def stressTest(nScans=100, pathToVisit="/dls/i13/data/2016/cm14467-4", filesys="na"):
    """
    Function to run a sequence of tomography fly scans to test the response of the file system. 
    
    Args:
        nScans - initial number of scans, which is then repeated ad infinitum
        pathToVisit - path to the visit directory
        filesys - "na" for NetApp and "gpfs" for GPFS01
         
    Notes: 
        (1) all scan files will be saved in the tmp sub-directory of the input visit directory
        (2) execute reportTomo to see which stages and detectors will be used in these scans
        (3) it is recommended to use a dummy tomography_translation
        (4) make sure that Command Queue is not paused! 
    """
    print "Executing stressTest..."
    datadir_saved = LocalProperties.get("gda.data.scan.datawriter.datadir")
    
    windowsSubString_dct = {"na": "d:\\i13\\data\\", "gpfs": "t:\\i13\\data\\"}
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
    
print "Finished running i13i_utilities.py!"

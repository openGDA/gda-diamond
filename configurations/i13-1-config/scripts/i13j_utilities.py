from gda.data import NumTracker
import os
from gda.data import PathConstructor
from gda.factory import Finder
from gda.jython import InterfaceProvider
from gda.device.scannable import EpicsScannable
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gda.configuration.properties import LocalProperties

# set up a nice method for getting the latest file path
i13jNumTracker = NumTracker("i13j");
finder = Finder.getInstance()

# function to output the current scan number
def csn():
    return cfn()

# function to output the current file number
def cfn():
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return filenumber

# function to output the next scan number
def nsn():
    return nfn()

# function to output the next file number
def nfn():
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return filenumber + 1

# function to output the last file path
def pwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber))
    

# function to output the next file path
def nwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber + 1))

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
        From:       gda@i13-1-control.diamond.ac.uk
        Subject:    Update on myscript's relentless progress...
        Content:    myscript completed without errors - hurrah!
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

def clear_defaults():
    """To clear all current default scannables."""
    srv = finder.find(JythonServer.SERVERNAME)
    all_vec = srv.getDefaultScannables()
    all_arr = all_vec.toArray()
    for s in all_arr:
        #srv.removeDefault(s)
        ScannableCommands.remove_default(s)
    return all_arr
alias("clear_defaults")

def isLive():
    mode = LocalProperties.get("gda.mode")
    return mode =="live" or mode =="live_localhost"

from gda.device.scannable import TopupChecker 
from gda.device.monitor import EpicsMonitor

machineTopupMonitor = EpicsMonitor()
machineTopupMonitor.setName("machineTopupMonitor")
machineTopupMonitor.setPvName("SR-CS-FILL-01:COUNTDOWN")
machineTopupMonitor.configure()

machineModeMonitor = EpicsMonitor()
machineModeMonitor.setName("machineModeMonitor")
machineModeMonitor.setPvName("CS-CS-MSTAT-01:MODE")
machineModeMonitor.configure()

topupMonitor = TopupChecker()
topupMonitor.setName("topupMonitor")
topupMonitor.setTolerance(2.0)
topupMonitor.setWaittime(10.0)
topupMonitor.setTimeout(600.0)
topupMonitor.setMachineModeMonitor(machineModeMonitor)
topupMonitor.setScannableToBeMonitored(machineTopupMonitor)
topupMonitor.setLevel(999) # so this is the last thing to be called before data is collected, to save time for motors to move
topupMonitor.configure() 

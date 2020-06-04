from gda.data import NumTracker
import os
from time import sleep, strftime
from gda.jython import InterfaceProvider
from gda.factory import Finder
from gda.jython import InterfaceProvider, Jython
from gda.device.scannable import EpicsScannable
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gda.configuration.properties import LocalProperties
from gda.device.scannable.scannablegroup import ScannableGroup

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
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i13jNumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber))
    

# function to output the next file path
def nwd():
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
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
    srv = finder.findSingleton(Jython)
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


from gdascripts.scannable.beamokay import WaitWhileScannableBelowThresholdMonitorOnly, reprtime

class WaitWhileScannableBelowThresholdMonitorOnlyWithEmailFeedback(WaitWhileScannableBelowThresholdMonitorOnly):
    
    def __init__(self, name, scannableToMonitor, minimumThreshold, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=0, ixx="i13-1", emails=None):
        WaitWhileScannableBelowThresholdMonitorOnly.__init__(self, name, scannableToMonitor, minimumThreshold, secondsBetweenChecks, secondsToWaitAfterBeamBackUp)
        self.emails = emails # list
        self.emails_enabled = True
        self.ixx = ixx   
        
    def handleStatusChange(self,status):
        send_emails = self.emails_enabled and len(self.emails)
        ## check for status change to provide feedback:
        if status and self.lastStatus:
            pass # still okay
        if status and not self.lastStatus:
            msg = "*** " + self.name + ": Beam back up at: " + reprtime() + ". Resuming scan in " + str(self.secondsToWaitAfterBeamBackUp) + "s..."
            print(msg)
            if send_emails : send_email(whoto=self.emails, subject=self.ixx+": "+msg, body=msg)
            self.lastStatus = True
            sleep(self.secondsToWaitAfterBeamBackUp)
            msg = "*** " + self.name + ":  Resuming scan now at " + reprtime()
            if send_emails : send_email(whoto=self.emails, subject=self.ixx+": "+msg, body=msg)
            print(msg)
        if not status and not self.lastStatus:
            pass # beam still down
        if not status and self.lastStatus:
            msg = "*** " + self.name + ": Beam down at: " + reprtime() + ". Pausing scan..."
            print(msg)
            self.lastStatus = False
            if len(self.emails) : send_email(whoto=self.emails, subject=self.ixx+": "+msg, body=msg)
        

from gda.device.scannable import ScannableBase
class ShutterDirector(ScannableBase):
    """
    Class that opens the shutter before detector exposes and then shuts this shutter afterwards
    """
    def __init__(self, name, delegate, delay_after_open_sec=0, delay_after_close_sec=0):
        self.name = name
        self.inputNames = [name]
        self.delegate = delegate        # the shutter Scannable to direct
        self.delay_after_open_sec = delay_after_open_sec        # optional delay after issuing the open command
        self.delay_after_close_sec = delay_after_close_sec      # optional delay after issuing the close command
    
    def _do_open_shutter(self):
        self.delegate.moveTo('Open')
        sleep(self.delay_after_open_sec)

    def _do_close_shutter(self):
        self.delegate.moveTo('Closed')
        sleep(self.delay_after_close_sec) 
        
    def atLevelMoveStart(self):         # see atLevelMoveStart in Scannable
        #print("atLevelMoveStart")
        self._do_open_shutter()
        
    def isBusy(self):
        #print("isBusy")
        return self.delegate.isBusy()
    
    def atPointStart(self):             
        #print("atPointStart")
        #self._do_close_shutter()
        self._do_open_shutter()
        pass
        
    def atPointEnd(self):             # Called on every Scannable at the end of every data point...
        #print("atPointEnd")
        self._do_close_shutter()
        pass

    def atScanStart(self):
        #print("atScanStart")
        self.setLevel(self.delegate.getLevel())
        self._do_open_shutter()
        
    def atScanEnd(self):
        #print("atScanEnd")
        self._do_close_shutter()
        
    def getPosition(self):
        #print("getPosition")
        if self.delegate.getPosition()=="Open":
            return 0
        else:
            return 1
    
    def rawAsynchronousMoveTo(self,new_position):
        #print("rawAsynchronousMoveTo")
        pass

from epics_scripts.pv_scannable_utils import caput, caget
class CAShutterDirector(ScannableBase):
    """
    Class that opens the shutter before detector exposes and then shuts this shutter afterwards
    """
    def __init__(self, name, delegatePV, to_open_int=5, to_close_int=0, delay_after_open_sec=0, delay_after_close_sec=0):
        self.name = name
        self.inputNames = [name]
        self.delegate = delegatePV        # the shutter Scannable to direct
        self.to_open_int = to_open_int
        self.to_close_int = to_close_int   
        self.delay_after_open_sec = delay_after_open_sec        # optional delay after issuing the open command
        self.delay_after_close_sec = delay_after_close_sec      # optional delay after issuing the close command
    
    def _do_open_shutter(self):
        #self.delegate.moveTo('Open')
        caput(self.delegate, self.to_open_int)
        sleep(self.delay_after_open_sec)

    def _do_close_shutter(self):
        #self.delegate.moveTo('Closed')
        caput(self.delegate, self.to_close_int)
        sleep(self.delay_after_close_sec) 
        
    def atLevelMoveStart(self):         # see atLevelMoveStart in Scannable
        #print("atLevelMoveStart")
        self._do_open_shutter()
        
    def isBusy(self):
        #print("isBusy")
        #return self.delegate.isBusy()
        return False
    
    def atPointStart(self):             
        #print("atPointStart")
        #self._do_close_shutter()
        self._do_open_shutter()
        pass
        
    def atPointEnd(self):             # Called on every Scannable at the end of every data point...
        #print("atPointEnd")
        self._do_close_shutter()
        pass

    def atScanStart(self):
        #print("atScanStart")
        #self.setLevel(self.delegate.getLevel())
        self._do_open_shutter()
        
    def atScanEnd(self):
        #print("atScanEnd")
        self._do_close_shutter()
        
    def getPosition(self):
        #print("getPosition")
        out = caget(self.delegate)
        #if self.delegate.getPosition()=="Open":
        if out=='Open' or out==str(int(self.to_open_int)) or out==str(float(self.to_open_int)):
            return 0
        else:
            return 1
    
    def rawAsynchronousMoveTo(self,new_position):
        #print("rawAsynchronousMoveTo")
        pass

from gda.device.scannable import ScannableMotionBase
class StepScanMinder(ScannableBase):
    """
    Class that...
    """
    def __init__(self, name, ixx="i13-1", every=3, emails=None):
        self.name = name
        self.inputNames = [name]
        self.ixx = ixx
        self.emails = emails                # list
        self.emails_enabled = True
        self.every = every
        self.current_scan_pt_idx = 0
        self.is_on = False		# is_minding
        
    def rawGetPosition(self):
        return self.current_scan_pt_idx + 1
    
    def rawAsynchronousMoveTo(self, new_position):
        self.every = int(-new_position) if new_position < 0 else int(new_position) 
    
    def isBusy(self):
        return False   
    
    def atPointEnd(self):
        self.current_scan_pt_idx += 1
        send_emails = self.emails_enabled and len(self.emails) and (self.current_scan_pt_idx % self.every == 0)
        if send_emails:
            msg = "At scan point %i." %(self.current_scan_pt)
            send_email(whoto=self.emails, subject=self.ixx+": "+msg, body=msg)
        
    def atScanStart(self):
        self.current_scan_pt_idx = 0
        
    def atScanEnd(self):
        # is this going to send a repeat e-mail?
        msg = msg = "At scan point %i." %(self.current_scan_pt)
        send_email(whoto=self.emails, subject=self.ixx+": "+msg, body=msg)
        
    def getPosition(self):
        return self.delegate.getPosition()


from gda.epics import CAClient
class StepScanMinderPCO(ScannableBase):
    """
    Class that...
    """
    def __init__(self, name, delay_sec=10, mode="stepscan", ixx="i13-1", pv_prefix="BL13J-EA-DET-01:CAM:", emails=None):
        self.name = name
        self.inputNames = [name]
        self.emails = ["kaz.wanelik@diamond.ac.uk"] #emails                # list of e-mail addresses of subscribers
        self.emails_enabled = True
        self.ixx = ixx
        self.current_scan_pt_idx = 0
        self.pv_prefix=pv_prefix
        self.mode_int = self.get_mode_from_str(mode)

        self.is_minder_on = False
        self.minder_check_delay_sec = delay_sec # max(delay_sec, float(caget(self.cam_acquire_priod_pv))*2) # there could be waittime as well!
        self.previous_minded_val = None
        self.minded_val = None
        self.failed_attempts_min = 3
        self.failed_attempts_count = 0
        self.failed_attempts_max = 3*10 # before automatically turning OFF
        self.is_mindee_ok = True
        self.has_unfavourable_alert_been_sent = False

        self.cac_minded_val_rbv = CAClient("BL13J-EA-DET-01:TIFF:FileNumber") #CAClient("BL13J-EA-DET-01:CAM:NumImagesCounter_RBV") BL13J-EA-DET-01:CAM:ArrayCounter_RBV
        self.cac_cam_acquire_period_rbv = CAClient("BL13J-EA-DET-01:CAM:AcquirePeriod_RBV")
        self.cac_cam_acquire = CAClient("BL13J-EA-DET-01:CAM:Acquire")				# 0=Done 1=Acquire
        self.cac_cam_acquire_rbv = CAClient("BL13J-EA-DET-01:CAM:Acquire_RBV")			# 0=Done 1=Acquiring
        self.cac_cam_arm_state_rbv = CAClient("BL13J-EA-DET-01:CAM:ARM_MODE_RBV")		# 0=Disarmed 1=Armed
        self.cac_tiff_enable_callbacks = CAClient("BL13J-EA-DET-01:TIFF:EnableCallbacks") 	# 0=Disable 1=Enable
        self.cac_tiff_capture = CAClient("BL13J-EA-DET-01:TIFF:Capture")			# 0=Done 1=Capture
        self.remedy_delay_sec = 2

        self._setup_sys()

    def get_mode_from_str(self, mode_str):
        if mode_str=='stepscan':
            mode_int = 0
        elif mode_str=='repscan':
            mode_int = 1
        else:
            mode_int = None
            print("Unsupported input mode: %s!" %(mode_str))
        return mode_int

    def set_mode_from_int(self, mode_int):
        self.mode_int = mode_int 

    def _setup_sys(self):
        # populate ixx from prefix?
        if self.mode_int==0:
            self.cac_minded_val_rbv = CAClient("BL13J-EA-DET-01:TIFF:FileNumber")
        elif self.mode_int==1:
            self.cac_minded_val_rbv = CAClient("BL13J-EA-DET-01:TIFF:FileNumber")
        else:
            print("Unsupported mode: %s!" %(self.mode_int)) 

    def configureAll(self):
        if not self.cac_minded_val_rbv.isConfigured():
            self.cac_minded_val_rbv.configure()
        if not self.cac_cam_acquire_period_rbv.isConfigured():
            self.cac_cam_acquire_period_rbv.configure()
        if not self.cac_cam_acquire.isConfigured():
            self.cac_cam_acquire.configure()
        if not self.cac_cam_acquire_rbv.isConfigured():
            self.cac_cam_acquire_rbv.configure()
        if not self.cac_cam_arm_state_rbv.isConfigured():
            self.cac_cam_arm_state_rbv.configure()
        if not self.cac_tiff_enable_callbacks.isConfigured():
            self.cac_tiff_enable_callbacks.configure()
        if not self.cac_tiff_capture.isConfigured():
            self.cac_tiff_capture.configure()


    def clearupAll(self):
        if self.cac_minded_val_rbv.isConfigured():
            self.cac_minded_val_rbv.clearup()
        if self.cac_cam_acquire_period_rbv.isConfigured():
            self.cac_cam_acquire_period_rbv.clearup()
        if self.cac_cam_acquire.isConfigured():
            self.cac_cam_acquire.clearup()
        if self.cac_cam_acquire_rbv.isConfigured():
            self.cac_cam_acquire_rbv.clearup()         
        if self.cac_cam_arm_state_rbv.isConfigured():
            self.cac_cam_arm_state_rbv.clearup()         
        if self.cac_tiff_enable_callbacks.isConfigured():
            self.cac_tiff_enable_callbacks.clearup()
        if self.cac_tiff_capture.isConfigured():
            self.cac_tiff_capture.clearup()

    def rawGetPosition(self):
        return self.current_scan_pt_idx + 1
    
    def rawAsynchronousMoveTo(self, new_position):
        self.every = int(-new_position) if new_position < 0 else int(new_position) 
    
    def isBusy(self):
        return False   
    
    def atPointEnd(self):
        self.current_scan_pt_idx += 1
        send_emails = self.emails_enabled and len(self.emails) and (self.current_scan_pt_idx % self.every == 0)
        if send_emails:
            msg = "At scan point %i." %(self.current_scan_pt)
            send_email(whoto=self.emails, subject=self.ixx+": "+msg, body=msg)
        
    def atScanStart(self):
        self.configureAll()
        self.is_mindee_ok = True
        self.current_scan_pt_idx = 0
        
    def atScanEnd(self):
        # is this going to send a repeat e-mail?
        msg = msg = "At scan point %i." %(self.current_scan_pt)
        send_email(whoto=self.emails, subject=self.ixx+": "+msg, body=msg)
        
    def getPosition(self):
        return self.delegate.getPosition()

    def stop(self):
        self.clearupAll()
    
    def atScanEnd(self):
        self.clearupAll()
    
    def atCommandFailure(self):
        self.clearupAll()

    def add_subscriber(self, email):
        if not email in self.emails:
            self.emails.append(email)

    def remove_subscriber(self, email):
        self.emails=list(filter(lambda e: e != email, self.emails))

    def remove_all_subscribers(self, email):
        self.emails=[]

    def reset(self):
        self.configureAll()
        # don't change current self.is_on ???
        # don't change current self.emails_enabled
        # don't change self.emails
        self.is_mindee_ok = True
        self.failed_attempts_count = 0
        self.previous_minded_val = -1 #int(self.cac_minded_val_rbv.caget())
        self.has_unfavourable_alert_been_sent = False
        #self.minder_check_delay_sec = max(self.minder_check_delay_sec, float(self.cac_cam_acquire_period_rbv.caget())*2)

    def mind(self):
        #if self.is_mindee_acquiring ???
        self._setup_sys()
        self.reset()
        if self.is_minder_on:
            print("WARNING: This StepScanMinderPCO is turned ON!")
        else:
            print("WARNING: This StepScanMinderPCO is turned OFF!")
        dbg_loop_count =0
        while (self.is_minder_on):
            #print("dbg_loop_count = %i" %(dbg_loop_count))
            #need_minding = self.does_mindee_need_minding()	# this is to ensure that the minder does not run forever...
            #if not need_minding:
            #    self.is_minder_on = need_minding
            #    print("PCO does NOT appear to be scanning, so this StepScanMinderPCO will now automatically turn itself OFF - bye!")
            #    break
            if self.failed_attempts_count > self.failed_attempts_max:
                self.is_minder_on = False
                msg ="Maximum number of attempts (%i) to revive PCO has been exceeded, and this StepScanMinderPCO will now automatically turn itself OFF - bye!" %(self.failed_attempts_max)
                print(msg)
                self.handle_emails(msg)
                self.clearupAll()
                break
            try:
                curr_minded_val = int(self.cac_minded_val_rbv.caget())
                print("curr = %i, prev = %i" %(curr_minded_val, self.previous_minded_val)) 
                if curr_minded_val > self.previous_minded_val:
                    self.previous_minded_val = curr_minded_val
                    self.failed_attempts_count = 0
                    if not self.is_mindee_ok:
                        #email favourable news to subscribers
                        msg ="Current PCO scan appears to have recovered from a stall!"
                        print(msg)
                        self.handle_emails(msg)
                        self.is_mindee_ok = True
                else:
                    self.failed_attempts_count += 1
                    if self.failed_attempts_count > self.failed_attempts_min:
                        self.is_mindee_ok = False
                        if not self.has_unfavourable_alert_been_sent:
                            # email unfavourable news to subscribers
                            msg ="Current PCO scan appears to have stalled!"
                            print(msg)
                            self.handle_emails(msg)
                            self.has_unfavourable_alert_been_sent = True
                        self.revive()
            except Exception, e:
                # differentiate btwn different Exception types and actions that follow them?
                print("Failed on caget %s"%(self.cac_minded_val_rbv.getPvName())) 
            sleep(self.minder_check_delay_sec)
            dbg_loop_count += 1
            
    def revive(self):
        print("This StepScanMinderPCO is now making an attempt to revive PCO by switching it OFF and then ON: attempt %i (min=%i, max=%i)"%(self.failed_attempts_count, self.failed_attempts_min, self.failed_attempts_max)) 
        # stop the camera
        self.cac_cam_acquire.caput(0)
        sleep(self.remedy_delay_sec)
        # start the camera again, and hope for the best
        self.cac_cam_acquire.caput(1)

    def set_on(self):
        self.is_minder_on = True

    def set_off(self):
        self.is_minder_on = False

    def toggle_op(self):
        self.is_minder_on = (not self.is_minder_on)

    def is_on(self):
        return self.is_minder_on

    def handle_emails(self, msg):
        any_emails_to_be_sent = self.emails_enabled and len(self.emails)
        if any_emails_to_be_sent : send_email(whoto=self.emails, subject=self.ixx+": "+msg, body=msg)

    def is_mindee_acquiring(self):
        out = None
        try:
            #out = int(caget(self.cam_acquire_pv))==1 # 0=Done 1=Acquire; this will be continuously ON and OFF during scan, so not a good indicator
            out = int(self.cli_arm_state_rbv.caget())==1 and int(self.cli_arm_state_rbv.caget())==1 #0=Disarmed 1=Armed 0=done 1=Acquiring
        except Exception, e:
            print("Failed on caget: %s"%(self.cam_acquire_pv)) # and tiff plugin set up?
        return out

    def is_mindee_potentially_stalling(self):
        out = None
        try:
            out = int(self.cac_cam_arm_state_rbv.caget())==1 and int(self.cac_cam_arm_state_rbv.caget())==1 #0=Disarmed 1=Armed 0=done 1=Acquiring
        except Exception, e:
            print("Failed on caget %s or %s"%(self.cac_cam_arm_state_rbv.getPvName(), self.cac_cam_arm_state_rbv())) # and tiff plugin set up?
        return out

    def does_mindee_need_minding(self):
        out = False
        try:
            if self.mode_int==0: # step scan
                out = int(self.cac_tiff_enable_callbacks.caget())==1  # 0=Disable 1=Enable
            elif self.mode==1:   # repscan
                out = int(self.cac_cam_arm_state_rbv.caget())==1 and int(self.cac_tiff_enable_callbacks.caget())==1  # 0=Disarmed 1=Armed; 0=Disable 1=Enable # and tiff plugin set up?
            else:
                print("Unsupported mode: %i!" %(self.mode_int))
        except Exception, e:
            print("Failed on caget %s or %s"%(self.cac_cam_arm_state_rbv.getPvName(), self.cac_tiff_enable_callbacks.getPvName())) 
        return out

        
pcotif_minder=StepScanMinderPCO("pcotif_minder")




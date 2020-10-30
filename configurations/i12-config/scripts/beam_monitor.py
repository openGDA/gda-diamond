from gda.device.scannable import ScannableMotionBase
from gda.jython import JythonServerFacade
from gda.jython.JythonStatus import RUNNING
from gda.jython.commands.ScannableCommands import pos, scan
from gdascripts.utils import caput, caget, caput_wait

from time import sleep, strftime
from datetime import datetime
from gda.device import DeviceException


def open_shutter(sh_obj, wait_after_reset=0.5, wait_after_open=4.0):
    name = sh_obj.getName()
    pre_state = sh_obj.getPosition()
    if pre_state == "Open":  #  '0' is open, '1' is closed and '2' is reset. 
        print("Shutter %s is already open." %(name))
    else:
        #print("Pre-state is %s" %(pre_state))
        print("Opening shutter %s..." %(name))
        pos(sh_obj, "Reset")
        sleep(wait_after_reset)
        pos(sh_obj, "Open")
        sleep(wait_after_open)
        post_state = sh_obj.getPosition()
        print "Finished opening shutter %s - current state: %s" %(name, post_state)

def reprtime(fmt='%H:%M:%S'):
    return strftime(fmt)

class WaitWhileScannableBelowThresholdMonitorOnly(ScannableMotionBase):
    '''
    Can be configured with any monitor-like scannable and a minimum threshold.
    This scannable's getPosition method will not return until the monitor-like scannable
    returns a number above the threshold.
    
    When it does return getPosition returns 1 if okay or zero to indicate that during the last point a
    beamdump occured.
    
    getPosition reports status changes and time.
    '''

    def __init__(self, name, scannableToMonitor, minimumThreshold, secondsBetweenChecks=1.0, secondsToWaitAfterBeamBackUp=0.0, shtr_obj=None):
        self.scannableToMonitor = scannableToMonitor
        self.minimumThreshold = minimumThreshold
        self.secondsBetweenChecks = secondsBetweenChecks
        self.secondsToWaitAfterBeamBackUp = secondsToWaitAfterBeamBackUp
        
        self.setName(name);
        self.setInputNames([])
        self.setExtraNames([name+"_beamok"]);

        self.Units=[]
        self.setOutputFormat(['%.0f'])
        self.setLevel(6)
        
        self.lastStatus = True # Good
        self._operating_continuously=False
        
        self.shtr_obj = shtr_obj
        self.shtr_opening_enabled = False
        
        self.time_fmt = '%H:%M:%S'
        self.beamDownStartTm = None         # str
        self.beamDownEndTm = None           # str
        self.beamDownElapsedInterval = None # datetime obj
        
        self.extra_conditions_dct = {'FE12I-PS-SHTR-01:STA': 3, 'FE12I-PS-SHTR-02:STA': 3, 'FE12I-RS-ABSB-01:STA': 3}
        self.extra_conditions_enabled = False
        
    def setOperatingContinuously(self, b):
        '''when set to True, no topup monitor will be active. Default is False.
        '''
        self._operating_continuously = b

    def isOperatingContinously(self):
        return self._operating_continuously

    def atScanStart(self):
        print '=== Beam checking enabled: '+self.scannableToMonitor.getName()+' must exceed '+str(self.minimumThreshold)+', currently '+str(self._getStatus())+'; and the FE absorber and the port shutter be opened'
        self.statusRemainedGoodSinceLastGetPosition = True
        if self._operating_continuously:
            while not self._getStatusAndHandleChange():  
                # not okay, so wait here
                sleep(self.secondsBetweenChecks)
                self._collectNewMonitorValue()  
            

    def isBusy(self):
        '''This can't be used as isBusy is not checked unless the scannable
        is 'moved' by passing in a number'''
        return False

    def waitWhileBusy(self):
        if not self._operating_continuously:
            if JythonServerFacade.getInstance().getScanStatus()==RUNNING:
                # loop until okay
                while not self._getStatusAndHandleChange():  
                    # not okay
                    sleep(self.secondsBetweenChecks)
                    self._collectNewMonitorValue()  
                # now okay
        
    def getPosition(self):
        '''If scan is running then pauses until status is okay and returning False
        if the scan was not okay. If scan is not running, return the current state
        and print a warning that the scan is not being paused.
        This only works if scan is not continuous.
        '''
        self.statusRemainedGoodSinceLastGetPosition = 1.0
        
        if not self._operating_continuously:
            if JythonServerFacade.getInstance().getScanStatus()==RUNNING:
                # loop until okay
                while not self._getStatusAndHandleChange():  
                    # not okay
                    self.statusRemainedGoodSinceLastGetPosition = 0.0
                    sleep(self.secondsBetweenChecks)
                    self._collectNewMonitorValue()  
                # now okay
            else: # scan not running
                currentStatus = self._getStatus()
                if not currentStatus: # bad
                    print self.name + " not holding read-back as no scan is running"
                self.statusRemainedGoodSinceLastGetPosition = currentStatus
        
        return self.statusRemainedGoodSinceLastGetPosition

    def _getStatus(self):
        val = self.scannableToMonitor.getPosition()
        if type(val) in (type(()), type([])):
            val = val[0]
        #ensure scan continues when topup is shutdown. 
        if val==-1 and self.scannableToMonitor.getName()=="topup_time":
            return True
        #status = (val >= self.minimumThreshold)
        status = (val >= self.minimumThreshold) and (int(caget('FE12I-RS-ABSB-01:STA'))==1) and (int(caget('FE12I-PS-SHTR-01:STA'))==1)
        return status

    def _getStatusAndHandleChange(self):
        ## Check current status, reports and returns it
        status = self._getStatus()
        self.handleStatusChange(status) 
        return status
        
    def handleStatusChange(self,status):
        ## check for status change to provide feedback:
        if status and self.lastStatus:
            pass # still okay
        if status and not self.lastStatus:
            self.beamDownEndTm = reprtime(self.time_fmt)
            self.beamDownElapsedInterval = datetime.strptime(self.beamDownEndTm, self.time_fmt) - datetime.strptime(self.beamDownStartTm, self.time_fmt)
            print "*** " + self.name + ": Beam back up at " + self.beamDownEndTm + " (elapsed downtime = " + str(self.beamDownElapsedInterval) + " [" + self.time_fmt.replace('%','') +"]). Will resume scan in " + str(self.secondsToWaitAfterBeamBackUp) + "s..."
            self.lastStatus = True
            sleep(self.secondsToWaitAfterBeamBackUp)
            # handle extra conditions
            if self.extra_conditions_enabled:
                cond_sgl = self._concatenateExtraConditions()
                while not eval(cond_sgl):
                    print "*** " + self.name + ": Waiting for port shutter, front-end optics shutter, and front-end absorber to be open!"
                    sleep(self.secondsBetweenChecks)
            
            if self.shtr_opening_enabled and (self.shtr_obj is not None):
                print "*** " + self.name + ": Opening shutter %s" %(self.shtr_obj)
                open_shutter(self.shtr_obj)
            print "*** " + self.name + ":  Resuming scan now at " + reprtime(self.time_fmt)
        if not status and not self.lastStatus:
            pass # beam still down
        if not status and self.lastStatus:
            self.beamDownStartTm = reprtime(self.time_fmt)
            print "*** " + self.name + ": Beam down at " + self.beamDownStartTm + ". Pausing scan..."
            self.lastStatus = False
            
    def _collectNewMonitorValue(self):
        pass

    def _concatenateExtraConditions(self):
        cond_sgl = ''
        for i, (k,v) in enumerate(self.extra_conditions_dct.iteritems()):
            cond_sgl += 'int(caget("%s"))==%d' %(k,v)
            cond_sgl += ' and ' if i<len(self.extra_conditions_dct)-1 else ''
        return cond_sgl
            

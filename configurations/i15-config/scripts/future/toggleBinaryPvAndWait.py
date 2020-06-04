""" Based on b16/scripts/pd_toggleBinaryPvAndWait.py r15228
"""
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from gdascripts.pd.time_pds import tictoc
from gdascripts.messages.handle_messages import simpleLog
from time import sleep


class ToggleBinaryPvAndWait(ScannableMotionBase):
    """ 
    Useful for triggering detectors which have been setup to record images on 
    hardware triggers.
    
    When asked to move, toggles a binary PV from normalLevel to !normalLevel and
    then back to normalLevel. Remains busy until the single exposure+readout time
    is reached.
    """
    def __init__(self, name, pvstring, normalLevel='on', triggerLevel='off'):
        self.name = name
        self.cli = CAClient(pvstring)
        self.setInputNames(['t'])
        self.setOutputFormat(['%5.5f'])
        self.setLevel(9)        
        self.timer=tictoc()
        self.waitfortime=0
        self.cli.configure()
        self.normalLevel = normalLevel
        self.triggerLevel = triggerLevel
        self.verbose=False
        self.setNormal()
        self.lastExposureTime=0

    def setNormal(self):
        if self.verbose:
            simpleLog("self.cli.caput(%r)" % self.normalLevel)
        self.cli.caput(self.normalLevel)

    def setTrigger(self): 
        if self.verbose:
            simpleLog("self.cli.caput(%r)" % self.triggerLevel)
        self.cli.caput(self.triggerLevel)
            
    def trigger(self, exposureTime):
        self.setTrigger()
        sleep(exposureTime)
        self.setNormal()

    def atScanStart(self):
        self.setNormal()

    def isBusy(self):
        if self.timer()<self.waitfortime:
            return 1
        else:
            return 0

    def getState(self):    
        # If the CA client has already had a channel configured by atStart())
        
        val=self.cli.caget()
        if val=='1':
            return 1
        elif val=='0':
            return 0
        else:
            raise Exception

    def getPosition(self):
        return self.lastExposureTime

    def asynchronousMoveTo(self,waittime=0):
        if waittime <= 0: # Ignore invalid wait times. This also fixes the
            #               the problem of return to start no wait toggles.
            if self.verbose:
                simpleLog("ToggleBinaryPvAndWait return move ignored.")
            return        
        if self.verbose:
            simpleLog("ToggleBinaryPvAndWait.asynchronousMoveTo(%r)" % waittime)
        self.lastExposureTime = waittime
        self.waitfortime=self.timer()+waittime
        self.trigger(waittime)
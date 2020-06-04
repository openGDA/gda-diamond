from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from gdascripts.pd.time_pds import tictoc
from time import sleep


class ToggleBinaryPvAndWait(ScannableMotionBase):
    """ 
    Useful for triggering detectors which have been setup to record images on 
    hardware triggers.
    
    When asked to move, toggles a binary PV from normalLevel to !normalLevel and
    then back to normalLevel. Remains busy until the single exposure+readout time
    is reached.
    """
    def __init__(self, name, pvstring, normalLevel=True):
        self.name = name
        self.cli = CAClient(pvstring)
        self.setInputNames(['t'])
        self.setOutputFormat(['%5.5f'])
        self.setLevel(9)        
        self.timer=tictoc()
        self.waitfortime=0
        self.currenttime=0
        self.cli.configure()
        self.normalLevel = normalLevel
        self.triggerLength=0
        self.lastExposureTime=0

    def setNormal(self): 
        if self.normalLevel==True:
            self.cli.caput(1)
        else:
            self.cli.caput(0)            

    def setTrigger(self): 
        if self.normalLevel==True:
            self.cli.caput(0)
        else:
            self.cli.caput(1)
            
    def trigger(self):
        self.setTrigger()
        sleep(self.triggerLength)
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
        self.lastExposureTime = waittime
        self.currenttime=self.timer()
        self.waitfortime=self.currenttime+waittime
        self.trigger()


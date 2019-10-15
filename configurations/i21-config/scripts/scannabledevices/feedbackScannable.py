'''
Created on 10 Oct 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase
from gda.epics import CAClient
rootPV="BL21I-OP-MIRR-01:FBCTRL:"

class FeedbackScannable(ScannableBase):
    '''
    During a scan 
    1. atScanStart:
        1.1 cache current EPICS mode;
        1.2. switch it to "Post-Capture AutoPV mode";
    2. atPointStart call 'Start Feedback" once;
    3. atScanEnd switch back to the mode found before stScan Start;
    4. get and set the feedback time in EPICS

    '''

    PV_END_POINT={"Mode":":MODE","Start":":START.PROC","Time":":FBTIME"}

    def __init__(self, name, pvroot=rootPV):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.mode=CAClient(pvroot+FeedbackScannable.PV_END_POINT["Mode"])
        self.mode.configure()
        self.start=CAClient(pvroot+FeedbackScannable.PV_END_POINT["Start"])
        self.start.configure()
        self.time=CAClient(pvroot+FeedbackScannable.PV_END_POINT["Time"])
        self.time.configure()
        self.exisitingMode=int(self.mode.caget())
        
    def atScanStart(self):
        self.exisitingMode=int(self.mode.caget()) #cache existing EPICS mode
        if self.exisitingMode!=3:
            self.mode.caput(3) #set to "Post-Capture AutoPV mode" during scan
            self.IChangedMode=True
    
    def atScanEnd(self):
        if self.IChangedMode:
            self.mode.caput(self.exisitingMode) #put the mode back to what I found before scan
    
    def atPointStart(self):
        self.start.caputWait(1) #Start Feedback and wait callback
        
    def getPosition(self):
        ''' retrieve feedback time value from EPICS
        '''
        return self.time.caget()
        
    def asynchronousMoveTo(self, value):
        ''' change feedback time in EPICS
        '''
        value=float(value)
        self.time.caput(value)
        
    def isBusy(self):
        return False
    
#fbs=FeedbackScannable("fbs", pvroot="BL21I-OP-MIRR-01:FBCTRL:")

class FeedbackOffScannable(ScannableBase):
    '''
    switch off feedback during a scan

    '''

    PV_END_POINT={"Mode":":MODE"}

    def __init__(self, name, pvroot=rootPV):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.mode=CAClient(pvroot+FeedbackScannable.PV_END_POINT["Mode"])
        self.mode.configure()
        self.exisitingMode=int(self.mode.caget())
        self.IChangedMode=False
        
    def atScanStart(self):
        self.exisitingMode=int(self.mode.caget()) #cache existing EPICS mode
        if self.exisitingMode!=0:
            self.mode.caput(0) #set to off
            self.IChangedMode=True
    
    def atScanEnd(self):
        if self.IChangedMode:
            self.mode.caput(self.exisitingMode) #put tne mode back to what I found before scan
    
    def getPosition(self):
        ''' retrieve mode value
        '''
        return self.mode.caget()
        
    def asynchronousMoveTo(self, value):
        pass
        
    def isBusy(self):
        return False
        
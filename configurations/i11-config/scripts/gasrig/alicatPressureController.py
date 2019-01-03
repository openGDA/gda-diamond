'''
scannable for Alicat pressure controller to provide access to its properties, i.e. 
get and set methods.
Build in default flow tolerance is 0.01, and reading precision is 3 decimals.

usage example:
    bpr=AlicatPressureController("bpr","BL11I-EA-GIR-01:SYSTEM:","%.3f")
    
Created on 6 Dec 2013
updated on 16 June 2014

@author: fy65
'''
from gda.epics import CAClient
from time import sleep
#ROOT_PV="BL11I-EA-GIR-01:BPR:"
READ_MODE="MODE:RD"
SET_MODE="MODE:WR"
READ_PRESSURE="P:RD"
READ_TARGET="SETPOINT:RD"
SET_TARGET="SETPOINT:WR"
READ_PROPORTIONAL_GAIN="PGAIN:RD"
SET_PROPORTIONAL_GAIN="PGAIN:WR"
READ_DERIVATIVE_GAIN="DGAIN:RD"
SET_DERIVATIVE_GAIN="DGAIN:WR"

modes={0:"Control",1:"Hold"}

from gda.device.scannable import ScannableMotionBase

class AlicatPressureController(ScannableMotionBase):
    '''
    construct a scannable for pressure control. It also provides access to other properties.
    '''
    def __init__(self,name, rootPV, tolerance=0.01, formatstring="%.3f"):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat([formatstring])
        self.setLevel(3)
        self.readmodecli=CAClient(rootPV+READ_MODE)
        self.setmodecli=CAClient(rootPV+SET_MODE)
        self.readpressurecli=CAClient(rootPV+READ_PRESSURE)
        self.settargetcli=CAClient(rootPV+SET_TARGET)
        self.readtargetcli=CAClient(rootPV+READ_TARGET)
        self.setproportionalgaincli=CAClient(rootPV+SET_PROPORTIONAL_GAIN)
        self.readproportionalgaincli=CAClient(rootPV+READ_PROPORTIONAL_GAIN)
        self.setderivativegaincli=CAClient(rootPV+SET_DERIVATIVE_GAIN)
        self.readderivativegaincli=CAClient(rootPV+READ_DERIVATIVE_GAIN)
        self.mytolerance=tolerance
        self.isConfigured=False
        
    def configure(self):
        if not self.isConfigured:
            if not self.readmodecli.isConfigured():
                self.readmodecli.configure()
            if not self.setmodecli.isConfigured():
                self.setmodecli.configure()
            if not self.settargetcli.isConfigured():
                self.settargetcli.configure()
            if not self.readtargetcli.isConfigured():
                self.readtargetcli.configure()
            if not self.readpressurecli.isConfigured():
                self.readpressurecli.configure()
            self.isConfigured=True
            
    def deconfigure(self):
        if self.isConfigured:
            if self.readmodecli.isConfigured():
                self.readmodecli.clearup()
            if self.setmodecli.isConfigured():
                self.setmodecli.clearup()
            if self.settargetcli.isConfigured():
                self.settargetcli.clearup()
            if self.readtargetcli.isConfigured():
                self.readtargetcli.clearup()
            if self.readpressurecli.isConfigured():
                self.readpressurecli.clearup()
            self.isConfigured=False
            
    def getMode(self):
        try:
            if not self.readmodecli.isConfigured():
                self.readmodecli.configure()
                output=int(self.readmodecli.caget())
                self.readmodecli.clearup()
            else:
                output=int(self.readmodecli.caget())
            return modes[output]
        except:
            print "Error returning current mode"
            return 0

    def setMode(self, mode):
        try:
            if not self.setmodecli.isConfigured():
                self.setmodecli.configure()
                self.setmodecli.caput(mode)
                self.setmodecli.clearup()
            else:
                self.setmodecli.caput(mode)
        except:
            print "error set to mode"

    def setTarget(self, target):
        try:
            if not self.settargetcli.isConfigured():
                self.settargetcli.configure()
                self.settargetcli.caput(target)
                self.settargetcli.clearup()
            else:
                self.settargetcli.caput(target)
        except:
            print "error set to target flow value"

    def getTarget(self):
        try:
            if not self.settargetcli.isConfigured():
                self.settargetcli.configure()
                output=float(self.settargetcli.caget())
                self.settargetcli.clearup()
            else:
                output=float(self.settargetcli.caget())
            return output
        except:
            print "Error returning target value"
            return 0

    def getPressure(self):
        try:
            if not self.readpressurecli.isConfigured():
                self.readpressurecli.configure()
                output=float(self.readpressurecli.caget())
                self.readpressurecli.clearup()
            else:
                output=float(self.readpressurecli.caget())
            return output
        except:
            print "Error returning pressure"
            return 0
        
    def getProportionalGain(self):
        try:
            if not self.readproportionalgaincli.isConfigured():
                self.readproportionalgaincli.configure()
                output=float(self.readproportionalgaincli.caget())
                self.readproportionalgaincli.clearup()
            else:
                output=float(self.readproportionalgaincli.caget())
            return output
        except:
            print "Error returning Proportional Gain"
            return 0

    def setProportionalGain(self, gain):
        try:
            if not self.setproportionalgaincli.isConfigured():
                self.setproportionalgaincli.configure()
                self.setproportionalgaincli.caput(gain)
                self.setproportionalgaincli.clearup()
            else:
                self.setproportionalgaincli.caput(gain)
        except:
            print "error set to proportional gain"

    def getDerivativeGain(self):
        try:
            if not self.readderivativegaincli.isConfigured():
                self.readderivativegaincli.configure()
                output=float(self.readderivativegaincli.caget())
                self.readderivativegaincli.clearup()
            else:
                output=float(self.readderivativegaincli.caget())
            return output
        except:
            print "Error returning Derivative Gain"
            return 0

    def setDerivativeGain(self, gain):
        try:
            if not self.setderivativegaincli.isConfigured():
                self.setderivativegaincli.configure()
                self.setderivativegaincli.caput(gain)
                self.setderivativegaincli.clearup()
            else:
                self.setderivativegaincli.caput(gain)
        except:
            print "error set to derivative gain"
            
            
    def getTolerance(self):
        return self.mytolerance
    
    def setTolerance(self, value):
        self.mytolerance=value

#### methods for scannable 
    def getPosition(self):
        return self.getPressure()
    
    def asynchronousMoveTo(self, posi):
        self.setTarget(float(posi))

    def moveTo(self, posi, sleepdelta=0.5):
        self.asynchronousMoveTo(posi)
        while self.isBusy():
            sleep(sleepdelta)

    def isBusy(self):
        return (abs(float(self.getPosition())-float(self.getTarget()))>float(self.getTolerance()))

    def atScanStart(self):
        pass
    def atPointStart(self):
        pass
    def stop(self):
        pass
    def atPointEnd(self):
        pass
    def atScanEnd(self):
        pass
    



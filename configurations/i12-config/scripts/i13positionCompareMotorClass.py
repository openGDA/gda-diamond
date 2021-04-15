'''
filename: positionCompareMotorClass.py

This class uses position compare to determine motor status. It does not use low level Motor Status directly.
Only 3 PVs - set, readback, and stop - are required. No other motor status are handled by this class.
The motor's positional tolerance must be set, that is the same as the retry deadband value of the Motor Record.

Created on 27 Oct 2010

@author: fy65
'''
from time import sleep
from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase

class PositionCompareMotorClass(ScannableMotionBase):
    '''Create a scannable for a single motor'''
    def __init__(self, name, pvinstring, pvoutstring, pvstopstring, tolerance, unitstring, formatstring, wait_sec=1):
        self.setName(name);
        self.setInputNames([name])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(3)
        self.incli=CAClient(pvinstring)
        self.outcli=CAClient(pvoutstring)
        self.stopcli=CAClient(pvstopstring)
        self._tolerance=tolerance
        self.wait=wait_sec
        self.wait_enabled = False
        
    def atScanStart(self):
        if not self.incli.isConfigured():
            self.incli.configure()
        if not self.outcli.isConfigured():
            self.outcli.configure()
        if not self.stopcli.isConfigured():
            self.stopcli.configure()
         
    def rawGetPosition(self):
        try:
            if not self.outcli.isConfigured():
                #print "rawGetPosition: not configured, so needs to be first configured"
                self.outcli.configure()
                output=float(self.outcli.caget())
                self.outcli.clearup()
            else:
                #print "rawGetPosition: already configured!"
                output=float(self.outcli.caget())
            return output
        except Exception, ex:
            #print "Error returning current position: ", ex
            return float('nan')

    def getTargetPosition(self):
        try:
            if not self.incli.isConfigured():
                #print "getTargetPosition: not configured, so needs to be first configured"
                self.incli.configure()
                target=float(self.incli.caget())
                self.incli.clearup()
            else:
                #print "getTargetPosition: already configured!"
                target=float(self.incli.caget())
            return target
        except Exception, ex:
            #print "Error returning target position: ", ex
            return 0
       
    def rawAsynchronousMoveTo(self,new_position):
        if new_position == self.getTargetPosition():
            return
        try:
            if not self.incli.isConfigured():
                #print "rawAsynchronousMoveTo: not configured, so needs to be first configured"
                self.incli.configure()
                self.incli.caput(new_position)
                self.incli.clearup()
            else:
                #print "rawAsynchronousMoveTo: already configured!"
                self.incli.caput(new_position)
        except Exception, ex:
            print "error moving to position: ", ex

    def isBusy(self):
        if self.wait_enabled:
            sleep(self.wait)
        return ( not abs(self.rawGetPosition() - self.getTargetPosition()) < self._tolerance)

    def atScanEnd(self):
        if self.incli.isConfigured():
            self.incli.clearup()
        if self.outcli.isConfigured():
            self.outcli.clearup()
        if self.stopcli.isConfigured():
            self.stopcli.clearup()
            
    def stop(self):
        if not self.stopcli.isConfigured():
            self.stopcli.configure()
            self.stopcli.caput(1)
            self.stopcli.clearup()
        else:
            self.stopcli.caput(1)

    def toString(self):
        return self.name + " : " + str(self.getPosition())
              
    def setTolerance(self,new_tolerance):
        self._tolerance=new_tolerance
    
    def getTolerance(self):
        return self._tolerance
    
    # override the below two base class functions because they are ignored anyway
    def setTolerances(self,new_tolerance):
        self._tolerance=new_tolerance
    
    def getTolerances(self):
        return self._tolerance
    
    def configureAll(self):
        if not self.incli.isConfigured():
            self.incli.configure()
        if not self.outcli.isConfigured():
            self.outcli.configure()
        if not self.stopcli.isConfigured():
            self.stopcli.configure()
    
    def clearupAll(self):
        if self.incli.isConfigured():
            self.incli.clearup()
        if self.outcli.isConfigured():
            self.outcli.clearup()
        if self.stopcli.isConfigured():
            self.stopcli.clearup()

    def setWaitTimeSec(self,wait_sec):
        self.wait=wait_sec
    
    def getWaitTimeSec(self):
        return self.wait

    def setWaitEnabled(self,enabled):
        self.wait_enabled=enabled
    
    def isWaitEnabled(self):
        return self.wait_enabled


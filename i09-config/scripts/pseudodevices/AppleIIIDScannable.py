'''
Created on 15 Aug 2012

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
#from time import sleep


class Apple2IDScannableClass(ScannableMotionBase):
    '''Create PD for Apple II ID controls'''
    def __init__(self, name, pvinstring, pvoutstring, pvexecutestring, unitstring, formatstring, tolerance=0.01):
        self.setName(name);
        self.setInputNames([name])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(5)
        self.incli=CAClient(pvinstring)
        self.outcli=CAClient(pvoutstring)
        self.execli=CAClient(pvexecutestring)
        self._tolerance=tolerance
       
    def setTolerance(self,tolerance):
        self._tolerance=tolerance 

    def getTolerance(self):
        return self._tolerance
    
    def atStart(self):
        if not self.incli.isConfigured():
            self.incli.configure()
        if not self.outcli.isConfigured():
            self.outcli.configure()
        if not self.execli.isConfigured():
            self.execli.configure()
         
    def getPosition(self):
        try:
            if not self.outcli.isConfigured():
                self.outcli.configure()
                output=float(self.outcli.caget())
                self.outcli.clearup()
            else:
                output=float(self.outcli.caget())
            return output
        except:
            print "Error returning current position"
            return 0

    def getDemandPosition(self):
        try:
            if not self.incli.isConfigured():
                self.incli.configure()
                target=float(self.incli.caget())
                self.incli.clearup()
            else:
                target=float(self.incli.caget())
            return target
        except:
            print "Error returning target position"
            return 0
       
    def asynchronousMoveTo(self,new_position):
        try:
            if not self.incli.isConfigured():
                self.incli.configure()
                self.incli.caputWait(float(new_position))
                self.incli.clearup()
            if not self.execli.isConfigured():
                self.execli.configure()
                self.execli.caput(1)
                self.execli.clearup()
            else:
                self.incli.caputWait(float(new_position))
                #sleep(1.0)
                self.execli.caput(1)
                #self.execli.caput(1)
        except:
            print "error moving to position"

    def isBusy(self):
        return (abs(float(self.getPosition()) - float(self.getDemandPosition()))>float(self._tolerance))

    def atEnd(self):
        if self.incli.isConfigured():
            self.incli.clearup()
        if self.outcli.isConfigured():
            self.outcli.clearup()
        if self.execli.isConfigured():
            self.execli.clearup()
            
    def toString(self):
        return self.name + " : " + str(self.getPosition())


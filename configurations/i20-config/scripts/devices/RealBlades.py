# coding=UTF-8

from gda.device.scannable import ScannableMotionBase
from gda.factory import Finder

# If changing this scannable, either call reset_namespace to reload the 
# script or restart the server using the servers.sh command.

class BladeAngle(ScannableMotionBase):

    def __init__(self, name, rName, off, dist, observerName=None):
        self.pseudoName  = name
        self.realName    = rName
        self.offset      = off
        self.distance    = dist
        self.observerName = observerName
        self.isBusy      = False

    def rawIsBusy(self):
        return self.isBusy

    def rawGetPosition(self):
        realValue = Finder.getInstance().find(self.realName).getPosition()
        self.currentposition = (realValue - self.offset) / self.distance
        return self.currentposition

    def rawAsynchronousMoveTo(self,new_position):
        
        # Important set isBusy in try finally block.
        try:
            self.isBusy = True;
            self.currentposition = new_position
        
            # Move realMotor
            realMotor = Finder.getInstance().find(self.realName)
            realValue = (self.currentposition*self.distance)+self.offset
            print "Setting the value of "+realMotor.getName()+" to "+str(realValue)
            realMotor.moveTo(realValue)
         
            # We send the value string to the observers so that the Dashboard receives the new
            # value for instance. Note that the value string is in the same format as that returned by the
            # pos command.
            if self.observerName!=None:
                observer = Finder.getInstance().findNoWarn(self.observerName)
                if observer!=None:
                    observer.notifyIObservers("Move", self.getName()+" : value: "+str(self.currentposition))
        finally:
            self.isBusy = False; 
        
    def getName(self):
        return self.pseudoName
    
    # In order for the dash to work, the unit must be returned here 
    # for a script defined scannable.
    def getAttribute(self, attributeName):
        if attributeName=="userunits":
            return "mrad"
        return super.getAttribute(attributeName)

class SubtractAngle(ScannableMotionBase):

    def __init__(self, name, a, b, observerName=None):
        self.pseudoName  = name
        self.a       = a
        self.b       = b
        self.observerName = observerName
       
    def setRef(self, ref):
        self.ref     = ref

    def rawIsBusy(self):
        return False

    def rawGetPosition(self):
        bValue = self.b.getPosition()
        aValue = self.a.getPosition()
        self.currentposition = bValue - aValue
        return self.currentposition
    
    def rawAsynchronousMoveTo(self,new_position):
        
        # Important set isBusy in try finally block.
        try:
            self.isBusy = True;
            self.currentposition = new_position
        
            # Move realMotors
            aValue = self.ref.getPosition() - self.currentposition/2.0
            print "Setting the value of "+self.a.getName()+" to "+str(aValue)
            
            bValue = self.ref.getPosition() + self.currentposition/2.0
            print "Setting the value of "+self.b.getName()+" to "+str(bValue)

            self.b.moveTo(bValue)
            self.a.moveTo(aValue)

            # We send the value string to the observers so that the Dashboard receives the new
            # value for instance. Note that the value string is in the same format as that returned by the
            # pos command.
            if self.observerName!=None:
                observer = Finder.getInstance().findNoWarn(self.observerName)
                if observer!=None:
                    observer.notifyIObservers("Move", self.getName()+" : value: "+str(self.currentposition))
        finally:
            self.isBusy = False; 
        
    def getName(self):
        return self.pseudoName
    
    def getAttribute(self, attributeName):
        if attributeName=="userunits":
            return "mrad"
        return super.getAttribute(attributeName)

class AverageAngle(ScannableMotionBase):

    def __init__(self, name, a, b, observerName=None):
        self.pseudoName  = name
        self.a       = a
        self.b       = b
        self.observerName = observerName

    def setRef(self, ref):
        self.ref     = ref

    def rawIsBusy(self):
        return False

    def rawGetPosition(self):
        bValue = self.b.getPosition()
        aValue = self.a.getPosition()
        self.currentposition = (bValue + aValue) / 2.0
        return self.currentposition
        
    def rawAsynchronousMoveTo(self,new_position):
        
        # Important set isBusy in try finally block.
        try:
            self.isBusy = True;
            self.currentposition = new_position
        
            # Move realMotors
            aValue = self.currentposition - self.ref.getPosition()/2.0
            print "Setting the value of "+self.a.getName()+" to "+str(aValue)
            
            bValue = self.currentposition + self.ref.getPosition()/2.0
            print "Setting the value of "+self.b.getName()+" to "+str(bValue)
            
            self.b.moveTo(bValue)
            self.a.moveTo(aValue)

            # We send the value string to the observers so that the Dashboard receives the new
            # value for instance. Note that the value string is in the same format as that returned by the
            # pos command.
            if self.observerName!=None:
                observer = Finder.getInstance().findNoWarn(self.observerName)
                if observer!=None:
                    observer.notifyIObservers("Move", self.getName()+" : value: "+str(self.currentposition))
        finally:
            self.isBusy = False; 

    def getName(self):
        return self.pseudoName
    
    def getAttribute(self, attributeName):
        if attributeName=="userunits":
            return "mrad"
        return super.getAttribute(attributeName)

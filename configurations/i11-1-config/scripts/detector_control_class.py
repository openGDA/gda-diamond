from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase

class DetectorControlClass(ScannableMotionBase):
    '''Create PD for single EPICS ETL detector'''
    def __init__(self, name, pvinstring, pvoutstring, unitstring, formatstring):
        self.setName(name);
        self.setInputNames([name])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(3)
        self.incli=CAClient(pvinstring)
        self.outcli=CAClient(pvoutstring)
        
    def atStart(self):
        if not self.incli.isConfigured():
            self.incli.configure()
        if not self.outcli.isConfigured():
            self.outcli.configure()
         
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

    def getTargetPosition(self):
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
                self.incli.caput(new_position)
                self.incli.clearup()
            else:
                self.incli.caput(new_position)
        except:
            print "error moving to position"

    def isBusy(self):
        return (self.getPosition() != self.getTargetPosition())

    def atEnd(self):
        if self.incli.isConfigured():
            self.incli.clearup()
        if self.outcli.isConfigured():
            self.outcli.clearup()
            
    def toString(self):
        return self.name + " : " + str(self.getPosition())
              

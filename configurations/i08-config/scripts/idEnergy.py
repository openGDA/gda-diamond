from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import ScannableMotor
from gda.device.scannable import ScannableUtils
from gda.factory import Finder

class my_energy_class1(ScannableMotionBase):
    def __init__(self, name):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%5.5g"])
        my_pgm_energy = Finder.find("pgm_energy")
        self.currentposition = (float)(my_pgm_energy.getPosition()) # this template scannable represents a single number
        self.iambusy = 0 # flag to hold the status of the scannable
        
    def getPosition(self):
        print "Begin getPosition"
        return self.currentposition
    
    def asynchronousMoveTo(self, new_e):
        """Performs the operation this Scannable represents."""
        self.iambusy = 1
        self.SetEnergy(new_e)
        self.currentposition = new_e
        self.iambusy = 0
         
    def isBusy(self):
        """Returns the status of this Scannable."""
        return self.iambusy
    
    def SetEnergy(self, e):
        gap = self.CalcGap(e)
        my_idgap = Finder.find("idgap")
        #my_pgm_energy = Finder.find("pgm_energy")
        my_idgap.moveTo(gap)        
        #my_pgm_energy.moveTo(e)
        
    def CalcGap(self, e):
        gap = 3.6887 + 0.10002*e - 0.00019451*e*e + e*e*e*2.5652*10**(-7)
        gap += -e*e*e*e*1.8887*10**(-10) + e*e*e*e*e*7.0713*10**(-14) - e*e*e*e*e*e*9.5723*10**(-18)
        #gap += 0.02
        return gap
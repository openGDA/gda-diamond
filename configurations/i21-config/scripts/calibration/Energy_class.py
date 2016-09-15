from gda.device.scannable import ScannableMotionBase
import gda.factory.Finder as Finder
import sys
#from gda.function.lookupTable import LookupTable
import math
from time import sleep
from lookup.LookupTables import readLookupTable
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.configuration.properties import LocalProperties


class BeamEnergy(ScannableMotionBase):
    '''Create beam energy scannable that encapsulates and fan-outs control to ID gap and PGM energy.
    
        This pseudo device requires a lookupTable table object to provide ID parameters for calculation of ID gap from beam 
        energy required and harmonic order. The lookupTable table object must be created before the instance creation of this class.
        The child scannables or pseudo devices must exist in jython's global namespace prior to any method call of this class 
        instance.
        '''
        
    def __init__(self, name, idctrl, gap, pgm, lut="IDCalibrationTable.txt"):
        '''Constructor - Only succeed if it find the lookupTable table, otherwise raise exception.'''
        self.lut=readLookupTable(LocalProperties.get("gda.config")+"/lookupTables/"+lut)
        self.gap=gap
        self.pgm=pgm
        self.idcontroller=idctrl
        self.scannables=ScannableGroup(name, [pgm, gap])
        self._busy=0
        self.setName(name)
        self.setLevel(3)
        self.setOutputFormat(["%10.6f"])
        self.inputNames=[name]
        self.order=1
        self.polarisation='LH'
    
    def setPolarisation(self, value, rowPhase=None):
        if self.getName() == "dummyenergy":
            print "'dummyenergy' does not simulate polarisation"
            return
        if value == "LH":
            self.idcontroller.moveTo([float(self.gap.getPosition()), "LH", 0]) 
            self.polarisation=value
        elif value == "LV":
            self.idcontroller.moveTo([float(self.gap.getPosition()), "C", 28]) 
            self.polarisation=value
        elif value == "C":
            if rowPhase is None:
                raise Exception("Motor position for Row Phase is not provided for Circular mode as 2nd parameter.") 
            self.idcontroller.moveTo([float(self.gap.getPosition()), "C", rowPhase]) 
            self.polarisation=value
        elif value == "L1":
            if rowPhase is None:
                raise Exception("Motor position for Row Phase is not provided for Linear 1 mode as 2nd parameter.") 
            self.idcontroller.moveTo([float(self.gap.getPosition()), "L1", rowPhase]) 
            self.polarisation=value
        elif value == "L2":
            if rowPhase is None:
                raise Exception("Motor position for Row Pahse is not provided for Linear 2 mdoe as 2nd parameter.") 
            self.idcontroller.moveTo([float(self.gap.getPosition()), "L2", rowPhase]) 
            self.polarisation=value
        else:
            raise ValueError("Input "+str(value)+" invalid. Valid values are 'LH', 'LV', 'C', 'L1' and 'L2'.")

    def getPolarisation(self):
        if self.getName() == "dummyenergy":
            print "'dummyenergy' does not simulate polarisation"
            return
        result=list(self.idcontroller.getPosition())
        self.polarisation=str(result[1])
        return self.polarisation
    
    def HarmonicEnergyRanges(self):
        print ("%s\t%s\t%s" % ("Harmonic", "Min Energy", "Max Energy"))
        keys=[int(key) for key in self.lut.keys()]
        for key in sorted(keys):
            print ("%8.0d\t%10.2f\t%10.2f" % (key,self.lut[key][2],self.lut[key][3]))
            
    def eneryRangeForOrder(self, order):
        return [self.lut[order][2],self.lut[order][3]]
        
    def setOrder(self,n):
        self.order=n
        
    def getOrder(self):
        return self.order
    
    def idgap(self, Ep, n):
        gap=20.0
        # Linear Horizontal
        if (self.getPolarisation()=="LH"):
            if (Ep<600 or Ep > 1000):
                raise ValueError("Demanding energy must lie between 600 and 1000eV!")
            gap = 12.063 + 0.031329*Ep
            if (gap<20 or gap>70):
                raise ValueError("Required Soft X-Ray ID gap is out side allowable bound (20, 70)!")
        
        # Linear Vertical
        elif self.getPolarisation()=="LV":
            raise ValueError("LV polarisation is not yet implemented!")
        # Circular left
        elif self.getPolarisation()=="C":
            raise ValueError("C polarisation is not yet implemented")
        
        # Circular right
        elif self.getPolarisation()=="L1":
            raise ValueError("L1 polarisation is not yet implemented")
      
        # Unsupported        
        else:
            raise ValueError("Unsupported polarisation mode")
        return gap
        
    def rawGetPosition(self):
        '''returns the current position of the beam energy.'''
        self.energy=self.pgm.getPosition()
        return self.energy;
    
    def calc(self, energy, order):
        return self.idgap(energy, order)

    def rawAsynchronousMoveTo(self, new_position):
        '''move beam energy to specified value.
        At the background this moves both ID gap and PGM energy to the values corresponding to this energy.
        If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''
        self.energy = float(new_position)
        gap = 7
        try:
            if self.getName() == "dummyenergy":
                gap=self.energy
            else:
                gap=self.idgap(self.energy, self.order)
        except:
            raise

        for s in self.scannables.getGroupMembers():
            if s.getName() == "idgap":
                try:
                    s.asynchronousMoveTo(gap)
                except:
                    print "cannot set " + s.getName() + " to " + str(gap)
                    raise
            else:
                try:
                    s.asynchronousMoveTo(self.energy)
                except:
                    print "cannot set " + s.getName() + " to " + str(self.energy)
                    raise
               
    def rawIsBusy(self):
        '''checks the busy status of all child scannable.
        
        If and only if all child scannable are done this will be set to False.'''  
        self._busy=0      
        for s in self.scannables.getGroupMembers():
            try:
                self._busy += s.isBusy()
            except:
                print s.getName() + " isBusy() throws exception ", sys.exc_info()
                raise
        if self._busy == 0:
            return 0
        else:
            return 1

    def toString(self):
        '''formats what to print to the terminal console.'''
        return self.name + " : " + str(self.rawGetPosition())
    
   


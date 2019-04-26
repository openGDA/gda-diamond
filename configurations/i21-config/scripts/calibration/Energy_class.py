from gda.device.scannable import ScannableMotionBase
import gda.factory.Finder as Finder
import sys
#from gda.function.lookupTable import LookupTable
import math
from time import sleep
from lookup.twoKeysLookupTable import loadLookupTable
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.configuration.properties import LocalProperties
from calibration.Energy2Gap4ID import idgap_calc
#from localStation import pgmGratingPitch_UserOffset


class BeamEnergy(ScannableMotionBase):
    '''Create beam energy scannable that encapsulates and fan-outs control to ID idgap and PGM energy.
    
        This pseudo device requires a lookupTable table object to provide ID parameters for calculation of ID idgap from beam 
        energy required and harmonic order. The lookupTable table object must be created before the instance creation of this class.
        The child scannables or pseudo devices must exist in jython's global namespace prior to any method call of this class 
        instance.
        '''
        
    def __init__(self, name, idctrl, idgap, pgmenergy, pgmgratingselect, lut="IDEnergy2GapCalibrations.txt"):  # @UndefinedVariable
        '''Constructor - Only succeed if it find the lookupTable table, otherwise raise exception.'''
        self.lut=loadLookupTable(LocalProperties.get("gda.config")+"/lookupTables/"+lut)
        self.idgap=idgap
        self.pgmenergy=pgmenergy
        self.idscannable=idctrl
        self.scannables=ScannableGroup(name, [pgmenergy, idgap])
        self._busy=0
        self.setName(name)
        self.setLevel(3)
        self.setOutputFormat(["%10.6f"])
        self.inputNames=[name]
        self.order=1
        self.polarisationMode='LH'
        self.pgmgratingselect=pgmgratingselect
        
    def setPolarisation(self, value, rowPhase=None):
        if self.getName() == "dummyenergy":
            print "'dummyenergy' does not simulate polarisationMode"
            return
        if value == "LH":
            self.idscannable.moveTo([float(self.idgap.getPosition()), "LH", 0]) 
            self.polarisationMode=value
        elif value == "LV":
            self.idscannable.moveTo([float(self.idgap.getPosition()), "LV", 28]) 
            self.polarisationMode=value
        elif value == "CR":
            if rowPhase is None:
                raise Exception("Motor position for Row Phase is not provided for Circular Right mode as 2nd parameter.") 
            self.idscannable.moveTo([float(self.idgap.getPosition()), "CR", rowPhase]) 
            self.polarisationMode=value
        elif value == "CL":
            if rowPhase is None:
                raise Exception("Motor position for Row Phase is not provided for Circular Left mode as 2nd parameter.") 
            self.idscannable.moveTo([float(self.idgap.getPosition()), "CL", rowPhase]) 
            self.polarisationMode=value
        elif value == "L1":
            if rowPhase is None:
                raise Exception("Motor position for Row Phase is not provided for Linear 1 mode as 2nd parameter.") 
            self.idscannable.moveTo([float(self.idgap.getPosition()), "L1", rowPhase]) 
            self.polarisationMode=value
        elif value == "L2":
            if rowPhase is None:
                raise Exception("Motor position for Row Pahse is not provided for Linear 2 mdoe as 2nd parameter.") 
            self.idscannable.moveTo([float(self.idgap.getPosition()), "L2", rowPhase]) 
            self.polarisationMode=value
        else:
            raise ValueError("Input "+str(value)+" invalid. Valid values are 'LH', 'LV', 'CR','CL', 'L1' and 'L2'.")

    def getPolarisationMode(self):
        if self.getName() == "dummyenergy":
            print "'dummyenergy' does not simulate polarisationMode"
            return
        result=list(self.idscannable.getPosition())
        self.polarisationMode=str(result[1])
        return self.polarisationMode
    
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
    
    def idgap_fn(self, Ep, n):
        gap=19.9
        # Linear Horizontal
        if (self.getPolarisationMode()=="LH"):
            gap=idgap_calc(Ep, "LH")
        # Linear Vertical
        elif self.getPolarisationMode()=="LV":
            gap=idgap_calc(Ep, "LV")
        # Circular left
        elif self.getPolarisationMode()=="CL":
            gap=idgap_calc(Ep, "CL")
        # Circular right
        elif self.getPolarisationMode()=="CR":
            gap=idgap_calc(Ep, "CR")
        #linear arbitrary
        elif self.getPolarisationMode()=="L1":
            gap=idgap_calc(Ep, "L1")
        return gap
        
    def rawGetPosition(self):
        '''returns the current position of the beam energy.'''
        return self.pgmenergy.getPosition()
    
    def calc(self, energy, order):
        return self.idgap(energy, order)

    def rawAsynchronousMoveTo(self, new_position):
        '''move beam energy to specified value.
        At the background this moves both ID idgap and PGM energy to the values corresponding to this energy.
        If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''
        energy = float(new_position)
        gap = 7
        try:
            if self.getName() == "dummyenergy":
                gap=energy
            else:
                gap=self.idgap_fn(energy, self.order)
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
                    s.asynchronousMoveTo(energy)
                except:
                    print "cannot set " + s.getName() + " to " + str(energy)
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
    
   


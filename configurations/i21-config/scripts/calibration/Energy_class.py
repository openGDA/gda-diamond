from gda.device.scannable import ScannableMotionBase
import gda.factory.Finder as Finder
import sys
#from gda.function.lookupTable import LookupTable
import math
from time import sleep
from lookup.twoKeysLookupTable import loadLookupTable
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.configuration.properties import LocalProperties
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
        elif value == "C":
            if rowPhase is None:
                raise Exception("Motor position for Row Phase is not provided for Circular mode as 2nd parameter.") 
            self.idscannable.moveTo([float(self.idgap.getPosition()), "C", rowPhase]) 
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
            raise ValueError("Input "+str(value)+" invalid. Valid values are 'LH', 'LV', 'C', 'L1' and 'L2'.")

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
            if (Ep>900 and Ep < 970):
                if self.pgmgratingselect.getPosition()=="VPG1":
                    gap = 19.086332 + 0.02336597*Ep #Corrected for VPG1 on 2017/02/15
                    #gap = 23.271 + 0.01748*Ep #Corrected for VPG1 on 2016/10/06
                elif self.pgmgratingselect.getPosition()=="VPG2":
                    #gap = 17.3845068 + 0.02555917*Ep #Corrected for VPG2 on 2017/02/15
                    #gap = 12.338 + 0.03074*Ep  #Corrected for VPG2 on 2016/10/06
                    gap = 18.669193 + 0.02350180*Ep  #Corrected for VPG2 at 930 eV on 2017/08/08
                elif self.pgmgratingselect.getPosition()=="VPG3":
                    gap = 18.5611846 + 0.02369966*Ep #Corrected for VPG3 on 2017/09/20
                else:
                    raise ValueError("Unknown Grating select in LH polarisationMode")
            elif (Ep>500 and Ep<600):
                if self.pgmgratingselect.getPosition()=="VPG1":
                    gap = 19.086332 + 0.02336597*Ep #Corrected for VPG1 on 2017/02/15
                    #gap = 23.271 + 0.01748*Ep #Corrected for VPG1 on 2016/10/06
                elif self.pgmgratingselect.getPosition()=="VPG2":
                    #gap = 17.3845068 + 0.02555917*Ep #Corrected for VPG2 on 2017/02/15
                    #gap = 12.338 + 0.03074*Ep  #Corrected for VPG2 on 2016/10/06
                    gap = 18.669193 + 0.02350180*Ep  #Corrected for VPG2 at 930 eV on 2017/08/08
                elif self.pgmgratingselect.getPosition()=="VPG3":
                    gap = 11.4731251 + 0.01873832*Ep #Corrected for VPG3 on 2017/09/20
                else:
                    raise ValueError("Unknown Grating select in LH polarisationMode")
            elif (Ep>690 and Ep<750):
                if self.pgmgratingselect.getPosition()=="VPG1":
                    gap = 19.2998231 + 0.02285595*Ep #Corrected for VPG1 on 2017/02/15
                    #raise Exception("No calibration available for VPG1 in LV mode")
                elif self.pgmgratingselect.getPosition()=="VPG2":
                    #gap = 12.2144937 + 0.01746779*Ep  #Corrected for VPG2 on 2017/11/30
                    raise Exception("No calibration available for VPG2 in LH mode")
                elif self.pgmgratingselect.getPosition()=="VPG3":
                    #gap = 11.4731251 + 0.01873832*Ep #Corrected for VPG3 on 2017/09/20
                    raise Exception("No calibration available for VPG3 in LH mode")
                else:
                    raise ValueError("Unknown Grating select in LH polarisationMode")    
            else:
                raise ValueError("Energy demand %feV is outside calibrated ranges") % (Ep)
        # Linear Vertical
        elif self.getPolarisationMode()=="LV":
            if (Ep>900 and Ep < 970):
                if self.pgmgratingselect.getPosition()=="VPG1":
                    # gap = 11.1441137 + 0.01881376*Ep #Corrected for VPG1 on 2017/07/31 ---> Linear Vertical
                    # gap = 11.6401974 + 0.01819208*Ep #Corrected for VPG1 on 2017/07/07 ---> Linear Vertical
                    gap = 11.0806699 + 0.01891585*Ep #Corrected for VPG1 at 930 eV on 2017/08/03 ---> Linear Vertical
                elif self.pgmgratingselect.getPosition()=="VPG2":
                    # gap = 11.3014613 + 0.01856236*Ep #Corrected for VPG2 on 2017/08/02 ---> Linear Vertical
    #                 gap = 11.2363888 + 0.01864200*Ep #Corrected for VPG2 at 930 eV on 2017/08/03 ---> Linear Vertical
                    gap = 11.3838749 + 0.01844212*Ep #Corrected for VPG2 at 930 eV on 2017/10/08 ---> Linear Vertical
                elif self.pgmgratingselect.getPosition()=="VPG3":
                    # gap = 11.2972185 + 0.01862358*Ep #Corrected for VPG3 on 2017/07/27 ---> Linear Vertical
                    gap = 11.3218637 + 0.01860144*Ep #Corrected for VPG3 at 930 eV on 2017/08/03 ---> Linear Vertical
                else:
                    raise ValueError("Unknown Grating select in LV polarisationMode")
            elif (Ep>500 and Ep<600):
                if self.pgmgratingselect.getPosition()=="VPG1":
                    gap = 19.086332 + 0.02336597*Ep #Corrected for VPG1 on 2017/02/15
                    #gap = 23.271 + 0.01748*Ep #Corrected for VPG1 on 2016/10/06
                elif self.pgmgratingselect.getPosition()=="VPG2":
                    #gap = 17.3845068 + 0.02555917*Ep #Corrected for VPG2 on 2017/02/15
                    #gap = 12.338 + 0.03074*Ep  #Corrected for VPG2 on 2016/10/06
                    gap = 18.669193 + 0.02350180*Ep  #Corrected for VPG2 at 930 eV on 2017/08/08
                elif self.pgmgratingselect.getPosition()=="VPG3":
                    gap = 11.4731251 + 0.01873832*Ep #Corrected for VPG3 on 2017/10/09
                else:
                    raise ValueError("Unknown Grating select in LV polarisationMode")
            elif (Ep>690 and Ep<750):
                if self.pgmgratingselect.getPosition()=="VPG1":
                    gap = 12.1996757 + 0.01755656*Ep #Corrected for VPG1 on 2017/02/15
                    #raise Exception("No calibration available for VPG1 in LV mode")
                elif self.pgmgratingselect.getPosition()=="VPG2":
                    gap = 12.2144937 + 0.01746779*Ep  #Corrected for VPG2 on 2017/11/30
                elif self.pgmgratingselect.getPosition()=="VPG3":
                    #gap = 11.4731251 + 0.01873832*Ep #Corrected for VPG3 on 2017/09/20
                    raise Exception("No calibration available for VPG1 in LV mode")
                else:
                    raise ValueError("Unknown Grating select in LV polarisationMode")
            else:
                raise ValueError("Energy demand %feV is outside calibrated ranges") % (Ep)
        # Circular left
        elif self.getPolarisationMode()=="C":
            raise ValueError("C polarisationMode is not yet implemented")
        
        # Circular right
        elif self.getPolarisationMode()=="L1":
            raise ValueError("L1 polarisationMode is not yet implemented")
      
        # Unsupported        
        else:
            raise ValueError("Unsupported polarisationMode mode")
           
        if (gap<20 or gap>70):
            raise ValueError("Required Soft X-Ray ID idgap is out side allowable bound (20, 70)!")
        return gap
        
    def rawGetPosition(self):
        '''returns the current position of the beam energy.'''
        self.energy=self.pgmenergy.getPosition()
        return self.energy;
    
    def calc(self, energy, order):
        return self.idgap(energy, order)

    def rawAsynchronousMoveTo(self, new_position):
        '''move beam energy to specified value.
        At the background this moves both ID idgap and PGM energy to the values corresponding to this energy.
        If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''
        self.energy = float(new_position)
        gap = 7
        try:
            if self.getName() == "dummyenergy":
                gap=self.energy
            else:
                gap=self.idgap_fn(self.energy, self.order)
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
    
   


import sys
import csv
from time import sleep
import logging
from gdascripts.utils import caput
import installation
logger = logging.getLogger('__main__')

from gda.configuration.properties import LocalProperties
from gda.device.scannable import ScannableMotionBase
from gda.device.scannable.scannablegroup import ScannableGroup
from lookup.fourKeysLookupTable import loadLookupTable
import numbers

def getFittingCoefficents(polarisation_mode, Ep, vpg, lut={}):
    lowEnergies=sorted([e[1] for e in lut.keys() if (e[0]==polarisation_mode and e[3]==vpg)])
    #print lowEnergies
    highEnergies=sorted([e[2] for e in lut.keys() if (e[0]==polarisation_mode and e[3]==vpg)])
    #print highEnergies
    minEnergy=min(lowEnergies)
    maxEnergy=max(highEnergies)
    limits=zip(lowEnergies, highEnergies)
    #print "Calibrated energy ranges: %s" % (limits)   
    if (Ep<minEnergy or Ep > maxEnergy):
        raise ValueError("Demanding energy must lie between %s and %s eV!"%(minEnergy, maxEnergy))
    else:
        for low, high in limits:
            if (Ep>=low and Ep<high): 
                return lut[(polarisation_mode, low, high, vpg)]

def loadDataset(filename):
    '''loads a CSV with the provided filename 
    '''
    with open(filename, 'rb') as csvfile:
        lines = csv.reader(csvfile)
        dataset = list(lines)[1:] #skip the header line
        for x in range(len(dataset)-1):
            for y in range(4):
                dataset[x][y] = float(dataset[x][y])
    return dataset

class BeamEnergyPolarisationClass(ScannableMotionBase):
    '''Coupled beam energy and polarisation scannable that encapsulates and fan-outs control to ID gap, row phase, and PGM energy.
    
        This pseudo device requires a lookupTable table object to provide ID parameters for calculation of ID idgap from beam 
        energy required and harmonic order. The lookupTable table object must be created before the instance creation of this class.
        The child scannables or pseudo devices must exist in jython's global namespace prior to any method call of this class 
        instance.
        '''
        
    def __init__(self, name, idctrl, pgmenergy, pgmgratingselect, idlamlookup, lut="IDEnergy2GapCalibrations.cvs", energyConstant=False, polarisationConstant=False, feedbackPV=None):
        '''Constructor - Only succeed if it find the lookupTable table, otherwise raise exception.'''
        self.lut,self.header=loadLookupTable(LocalProperties.get("gda.config")+"/lookupTables/"+lut)
        self.idscannable=idctrl
        self.pgmenergy=pgmenergy
        self.idlamlookup=idlamlookup
        self.scannables=ScannableGroup(name, [pgmenergy, idctrl])
        self.pgmgratingselect=pgmgratingselect
        self.feedbackPV=feedbackPV
        self._busy=0
        self.setName(name)
        self.setLevel(3)
        self.setOutputFormat(["%10.6f"])
        self.setInputNames([name])
        self.setExtraNames([])
        self.order=1
        self.polarisation=0.0
        self.gap=50
        self.polarisationMode='UNKNOWN'
        self.phase=0
        self.energyConstant=energyConstant
        self.polarisationConstant=polarisationConstant
        self.SCANNING=False 
        if self.energyConstant and self.polarisationConstant:
            raise Exception("Cannot create an instance with both energy and polarisation being constant.")
        self.isConfigured=False
        self.inputSignSwitched=False
        self.logger = logger.getChild(self.__class__.__name__)
    
    def configure(self):
        if self.idscannable is not None:
            self.maxGap=self.idscannable.getController().getMaxGapPos()
            self.minGap=self.idscannable.getController().getMinGapPos()
            self.maxPhase=self.idscannable.getController().getMaxPhaseMotorPos()
        self.isConfigured=True
    
    def getIDPositions(self):
        '''get gap and phase from ID hardware controller, and set polarisation mode in GDA 'idscannable' instance
        This method sync current object states with ID state in EPICS IOC.
        '''
        result=list(self.idscannable.getPosition())
        self.gap=float(result[0])
        self.polarisationMode=str(result[1])
        self.phase=float(result[2])
        return (self.gap, self.polarisationMode, self.phase)
    
    def showFittingCoefficentsLookupTable(self):
        formatstring="%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s"
        print (formatstring % ("Mode", "Min Energy", "Max Energy", "Grating", "Coefficent0", "Coefficent1", "Coefficent2", "Coefficent3", "Coefficent4", "Coefficent5", "Coefficent6", "Coefficent7"))
        for key, value in sorted(self.lut.iteritems()):
            print (formatstring % (key[0],key[1],key[2],key[3],value[0],value[1],value[2],value[3],value[4],value[5],value[6],value[7]))
    
    def showLinearAngleLookupTable(self):
        dataset=loadDataset(self.idlamlookup.lut)
        formatstring="%12s\t%12s\t%18s\t%12s"
        print (formatstring % ("Gap (mm)", "Phase (mm)", "Polarisation (deg)", "energy (eV)"))
        for value in dataset:
            print (formatstring % (value[0],value[1],value[2],value[3]))
               
    def setHarmonic(self,n):
        self.order=n
        
    def getHarmonic(self):
        return self.order
    
    def get_ID_gap_phase_at_current_polarisation(self, energy):
        self.getIDPositions() # update cached value from hardware positions
        return self.idgapphase(Ep=energy, mode=self.polarisationMode, n=self.order)

    def idgapphase(self, Ep=None, polar=None, mode='LH',n=1):
        '''coverts energy and polarisation to  gap and phase. It supports polarisation modes: LH, LV, CR, CL, LAP, LAN.
        Harmonic order is not yet implemented.
        '''
        Ep=Ep/n
        gap=20.0
        phase=0 #phase value for LH and LV is ignored by self.idscannable
        if mode in ["LH", "LV", "CR", "CL"]:
            #polarisation is constant in these modes
            coef=getFittingCoefficents(mode, Ep, str(self.pgmgratingselect.getPosition()), self.lut)
            gap = coef[0] + coef[1]*Ep + coef[2]*Ep**2 +coef[3]*Ep**3 + coef[4]*Ep**4 + coef[5]*Ep**5 + coef[6]*Ep**6 + coef[7]*Ep**7
            
            if (gap<self.minGap or gap>self.maxGap): #IDGroup Excel table only cover this range
                raise ValueError("Required Soft X-Ray ID gap is %s out side allowable bound (%s, %s)!" % (gap, self.minGap, self.maxGap))
            
            if mode == "LH":
                phase = 0.0
            elif mode == "LV":
                phase=self.maxPhase
            elif mode in ["CR", "CL"]:
                phase = 12.92907548 +  0.37353288*gap + -0.00614332*gap**2 + 5.3209E-06*gap**3 + 2.00631E-06*gap**4 + -3.9185E-08*gap**5 + 3.17986E-10*gap**6 + -9.93646E-13*gap**7
                
        elif mode in ["LAP","LAN"]:
            if self.polarisationConstant: 
                #move energy only
                #print self.phase, self.gap
                if (self.phase<0): #row phase can be negative in EPICS but lookup table only has positive phase values.
                    polarisation,energy = self.idlamlookup.getEnergyPolarisation(self.gap, -self.phase)
                else:
                    polarisation,energy = self.idlamlookup.getEnergyPolarisation(self.gap, self.phase)  # @UnusedVariable
                #print polarisation,energy
                if (polarisation>0):
                    polarisation=-polarisation #lookup table only contains negative polarisation angle!
                    self.inputSignSwitched=True
                gap, phase = self.idlamlookup.getGapPhase(Ep, polarisation) #only energy changes, keep existing polarisation
                #print gap, phase
            elif self.energyConstant:
                #move polarisation angle only
                #print self.phase, self.gap
                if (self.phase<0):
                    polarisation,energy = self.idlamlookup.getEnergyPolarisation(self.gap, -self.phase)
                else:
                    polarisation,energy = self.idlamlookup.getEnergyPolarisation(self.gap, self.phase)  # @UnusedVariable
                #print polarisation,energy, polar
                if (polar>0):
                    polar=-polar #lookup table only contains negative polarisation angle!
                    self.inputSignSwitched=True
                gap, phase = self.idlamlookup.getGapPhase(energy, polar) #only polarisation changes, keep existing energy
                #print gap, phase
            elif Ep is not None and polar is not None:
                #print Ep, polar
                if (polar>0):
                    polar=-polar #lookup table only contains negative polarisation angle!
                    self.inputSignSwitched=True
                gap, phase = self.idlamlookup.getGapPhase(Ep, polar) # both energy and polarisation change
                #print gap, phase
            else:
                raise ValueError("Both energy and polarisation are missing.")
            if (gap<self.minGap or gap>self.maxGap): #IDGroup Excel table only cover this range
                raise ValueError("Required Soft X-Ray ID gap is %s out side allowable bound (%s, %s!" % (gap, self.minGap,self.maxGap))
        else:
            raise ValueError("Unsupported polarisationMode mode")
        if phase<0 or phase>self.maxPhase: #Physical limits of ID Row Phase
            raise ValueError("Required Soft X-Ray ID phase is %s out side allowable bound (%s, %s)!" % (phase, 0, self.maxPhase))
        return (gap, phase)
        
    def rawGetPosition(self):
        '''returns the current beam energy, or polarisation, or both.'''
        if self.getName() == "dummyenergy":
            return self.energy
        elif self.getName() == "dummypolarisation":
            return self.polarisation
        else:
            gap, polarisationMode, phase = self.getIDPositions()
            energy=self.pgmenergy.getPosition()
            polarisation=polarisationMode
            if polarisationMode in ["LH","LV","CR","CL"]:
                if self.polarisationConstant:
                    return energy
                elif self.energyConstant:
                    self.setOutputFormat(["%s"])
                    self.polarisation=polarisation
                    return polarisation
                else:
                    self.setOutputFormat(["%10.6f","%s"])
                    self.polarisation=polarisation
                    return energy, polarisation
                    
            elif polarisationMode in ["LAP", "LAN"]:
                polarisation = self.idlamlookup.getEnergyPolarisation(gap, phase)[0]
                if self.inputSignSwitched:
                    polarisation=-polarisation
                    self.inputSignSwitched=False
                if self.polarisationConstant:
                    return energy
                elif self.energyConstant:
                    self.setOutputFormat(["%5.2f"])
                    self.polarisation=polarisation
                    return polarisation
                else:
                    self.setOutputFormat(["%10.6f","%5.2f"])
                    self.polarisation=polarisation
                    return energy, polarisation
            

    def validatePolarisation(self, polarisation):
        newPolarisationMode="UNKNOWN"
        if polarisation < -90 or polarisation > 90:
            raise ValueError("polarisation input is outside supported range (-90, 90)!")
        elif polarisation < 0:
            newPolarisationMode = "LAN"
        else:
            newPolarisationMode = "LAP"
        self.polarisationMode=newPolarisationMode
        return newPolarisationMode

    def rawAsynchronousMoveTo(self, new_position):
        '''move beam energy, polarisation, or both to specified value.
        At the background this moves both ID gap, phase, and PGM energy to the values corresponding to this energy, polarisation or both.
        If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''
        gap=20
        newPolarisationMode=None
        phase=0
        try:
            if self.getName() == "dummyenergy":
                self.energy = float(new_position)
            elif self.getName == "dummypolarisation":
                self.polaristion=float(new_position)
            else:
                if not self.SCANNING:  #ensure ID hardware in sync in 'pos' command
                    self.rawGetPosition()
                    
                #parse arguments as it could be 1 or 2 inputs, string or number type, depending on polarisation mode and instance attribute value
                if not isinstance(new_position, list): # single argument
                    if isinstance(new_position, basestring):
                        if self.polarisationConstant: #input must be for energy
                            raise ValueError("Input value must be a number.")
                        newPolarisationMode=str(new_position)
                        if not newPolarisationMode in ["LH", "LV","CR", "CL"]:
                            raise ValueError('Input value must be one of valid polarisation mode: "LH", "LV","CR", "CL"')
                        self.energy=self.pgmenergy.getPosition()
                    elif isinstance(new_position, numbers.Number):
                        if self.polarisationConstant: #input must be for energy
                            self.energy=float(new_position) #energy validation is done in getFittingCoefficent() method
                            newPolarisationMode=self.polarisationMode  #using existing polarisation mode
                        if self.energyConstant:       #input must be for polarisation
                            self.polarisation=float(new_position)
                            newPolarisationMode = self.validatePolarisation(self.polarisation)                            
                    else:
                        raise ValueError("Input value must be a string or number.")
                else: #2 arguments
                    args = list(new_position)
                    if len(args) != 2:
                        raise ValueError("Expect 2 arguments but got %s" % len(args))
                    if isinstance(args[0], numbers.Number):
                        self.energy=float(args[0]) #range validation is done later
                    else:
                        raise ValueError("1st input for energy must be a number")
                    if isinstance(args[1], numbers.Number):
                        self.polarisation=float(args[1])
                        newPolarisationMode = self.validatePolarisation(self.polarisation)
                    elif isinstance(args[1], basestring):
                        newPolarisationMode=args[1]
                    else:
                        raise ValueError("2nd input for polarisation must be a number")
                    
                if self.polarisationConstant:
                    gap, phase = self.idgapphase(Ep=self.energy, mode=newPolarisationMode, n=self.order)
                elif self.energyConstant:
                    gap, phase = self.idgapphase(Ep=self.energy, polar=self.polarisation, mode=newPolarisationMode, n=self.order) 
                else:
                    #print self.energy,self.polarisation,newPolarisationMode
                    gap, phase=self.idgapphase(Ep=self.energy, polar=self.polarisation, mode=newPolarisationMode, n=self.order)
        except:
            raise #re-raise any exception from above try block

        for s in self.scannables.getGroupMembers():
            #print s.getName(), self.idscannable.getName()
            if str(s.getName()) == str(self.idscannable.getName()):
                try:
                    if self.feedbackPV is not None and not self.SCANNING:
                        #change polarisation, need to stop feedback
                        caput(self.feedbackPV, 0)
                        s.moveTo([gap, newPolarisationMode, phase])
                        caput(self.feedbackPV, 4)
                    else:
                        s.asynchronousMoveTo([gap, newPolarisationMode, phase])
                    #print "moving %s to [%f, %s,%f]" % (s.getName(), gap, newPolarisationMode, phase)
                except:
                    print "cannot set %s to [%f, %s, %f]" % (s.getName(), gap, newPolarisationMode, phase)
                    raise
            else:
                if self.energyConstant: #polarisation change only
                    continue #do not need to move PGM energy
                else:
                    try:
                        beamlinename=LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME)
                        if (beamlinename=="i09" or beamlinename=="i09-2"):
                            s.asynchronousMoveTo(self.energy*1000)
                        else:
                            s.asynchronousMoveTo(self.energy)
                    except:
                        print "cannot set %s to %f." % (s.getName(), self.energy)
                        raise
               
    def rawIsBusy(self):
        '''checks the busy status of all child scannables.        
        If and only if all child scannables are done this will be set to False.
        '''
        if self.getName() == "dummyenergy" or self.getName()=="dummypolarisation":
            sleep(0.1)
            return False
        else: #real hardware
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

    def stop(self):
        self.pgmenergy.stop()
        if installation.isLive():
            print("ID motion stop is not supported according to ID-Group instruction. Please wait for the Gap motion to complete!")
        else:  
            self.idscannable.stop()
            
    def atScanStart(self):
        if self.getName() == "dummyenergy" or self.getName()=="dummypolarisation":
            return;
        else: # real hardware
            self.rawGetPosition() #ensure ID hardware in sync at start of scan
            self.SCANNING=True
            if self.feedbackPV is not None:
                #during scan, stop feedback
                caput(self.feedbackPV, 0)
            
        
    def atScanEnd(self):
        self.SCANNING=False
        if self.feedbackPV is not None:
            #restore feedback
            caput(self.feedbackPV, 4)
         

# lookup_file='/dls_sw/i21/software/gda/config/lookupTables/LinearAngle.csv' #theoretical table from ID group
#  
# idlamlookup=IDLookup4LinearAngleMode("idlamlookup", lut=lookup_file) 
# energy=BeamEnergyPolarisationClass("energy", idscannable, pgmEnergy, pgmGratingSelect, idlamlookup, lut="IDEnergy2GapCalibrations.csv", polarisationConstant=True)  # @UndefinedVariable
# energy.configure()
# polarisation=BeamEnergyPolarisationClass("polarisation", idscannable, pgmEnergy, pgmGratingSelect, idlamlookup, lut="IDEnergy2GapCalibrations.csv", energyConstant=True,feedbackPV="BL21I-OP-MIRR-01:FBCTRL:MODE")  # @UndefinedVariable
# polarisation.configure()
# energypolarisation=BeamEnergyPolarisationClass("energypolarisation", idscannable, pgmEnergy, pgmGratingSelect, idlamlookup, lut="IDEnergy2GapCalibrations.csv",feedbackPV="BL21I-OP-MIRR-01:FBCTRL:MODE")  # @UndefinedVariable
# energypolarisation.configure()
# energypolarisation.setInputNames(["energy"])
# energypolarisation.setExtraNames(["polarisation"])


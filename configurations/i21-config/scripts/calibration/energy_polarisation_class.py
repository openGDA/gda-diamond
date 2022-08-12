import sys
import csv
from time import sleep
import logging
import installation
from uk.ac.diamond.daq.concurrent import Async
from gda.configuration.properties import LocalProperties
from gda.device.scannable import ScannableMotionBase, ScannableStatus
from gda.device.scannable.scannablegroup import ScannableGroup
from lookup.fourKeysLookupTable import load_lookup_table, get_fitting_coefficents
import numbers
from gda.device.MotorProperties import MotorEvent
from gda.observable import IObserver
from org.apache.commons.lang3.builder import EqualsBuilder, HashCodeBuilder

logger = logging.getLogger('__main__')

def load_dataset(filename):
    '''loads a CSV with the provided filename 
    '''
    with open(filename, 'rb') as csvfile:
        lines = csv.reader(csvfile)
        dataset = list(lines)[1:] #skip the header line
        for x in range(len(dataset)-1):
            for y in range(4):
                dataset[x][y] = float(dataset[x][y])
    return dataset

X_RAY_POLARISATIONS = ["LH", "LV", "CR", "CL", "LH3", "LV3", "LH5", "LV5", "LAN", "LAP"]


# cannot use python 'lambda source, change : updateFunction(source, change)' for annonymouse IObserver as you cannot delete it after added it, which results in 'reset_namespace' add more observer agaia
class GenericObserver(IObserver):
    def __init__(self, name, update_function):
        self.name =name
        self.updateFunction = update_function # a function point
        
    def update(self, source, change):
        self.updateFunction(source, change)
    
    #both equals and hashCode method required by addIObserver and deleteIOberser in Java observers set.        
    def equals(self, other):
        return EqualsBuilder.reflectionEquals(self, other, True)
      
    def hashCode(self):
        # Apache lang3 org.apache.commons.lang3.builder.HashCodeBuilder
        return HashCodeBuilder.reflectionHashCode(self, True)
    
class BeamEnergyPolarisationClass(ScannableMotionBase):
    '''Coupled beam energy and polarisation scannable that encapsulates and fan-outs control to ID gap, row phase, and PGM energy.
    
        This pseudo device requires a lookupTable table object to provide ID parameters for calculation of ID idgap from beam 
        energy required and harmonic order. The lookupTable table object must be created before the instance creation of this class.
        The child scannables or pseudo devices must exist in jython's global namespace prior to any method call of this class 
        instance.
        '''

    harmonicOrder = 1
        
    def __init__(self, name, idctrl, pgmenergy, pgmgratingselect, idlamlookup, lut="IDEnergy2GapCalibrations.cvs", energyConstant=False, polarisationConstant=False, feedbackPV=None):
        '''Constructor - Only succeed if it find the lookupTable table, otherwise raise exception.'''
        self.lut,self.header=load_lookup_table(LocalProperties.get("gda.config")+"/lookupTables/"+lut)
        self.idscannable = idctrl
        self.pgmenergy = pgmenergy
        self.idlamlookup = idlamlookup
        self.scannables = ScannableGroup(name, [pgmenergy, idctrl])
        self.pgmgratingselect = pgmgratingselect
        self.feedbackPV = feedbackPV
        self._busy = 0
        self.setName(name)
        self.setLevel(3)
        self.setOutputFormat(["%10.6f"])
        self.setInputNames([name])
        self.setExtraNames([])
        self.polarisation = 'LH'
        self.gap = 50
        self.phase = 0
        self.energyConstant = energyConstant
        self.polarisationConstant = polarisationConstant
        self.SCANNING = False 
        if self.energyConstant and self.polarisationConstant:
            raise RuntimeError("Cannot create an instance with both energy and polarisation being constant.")
        self.isConfigured = False
        self.inputSignSwitched = False
        self.submit = None
        self.energyObserver = None
        self.polarisationObserver =  None
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
        gap=float(result[0])
        polarisation=str(result[1])
        if BeamEnergyPolarisationClass.harmonicOrder > 1: # support other harmonic
            polarisation = str(polarisation)+str(BeamEnergyPolarisationClass.harmonicOrder)
        phase=float(result[2])
        return (gap, polarisation, phase)
    
    def showFittingCoefficentsLookupTable(self):
        formatstring="%4s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s"
        print(formatstring % tuple([x for x in self.header]))
        for key, value in sorted(self.lut.iteritems()):
            print(formatstring % tuple([x for x in key] + [x for x in value]))
    
    def showLinearAngleLookupTable(self):
        dataset=load_dataset(self.idlamlookup.lut)
        formatstring="%12s\t%12s\t%18s\t%12s"
        print (formatstring % ("Gap (mm)", "Phase (mm)", "Polarisation (deg)", "energy (eV)"))
        for value in dataset:
            print (formatstring % (value[0],value[1],value[2],value[3]))
               
    def setHarmonic(self,n):
        BeamEnergyPolarisationClass.harmonicOrder = n
        
    def getHarmonic(self):
        return BeamEnergyPolarisationClass.harmonicOrder
    
    def get_ID_gap_phase_at_current_polarisation(self, energy):
        gap, polarisation, phase = self.getIDPositions()  # @UnusedVariable
        gap, phase = self.idgapphase(Ep=energy, mode=polarisation)
        return gap, polarisation, phase

    def idgapphase(self, Ep=None, polar=None, mode='LH'):
        '''coverts energy and polarisation to  gap and phase. It supports polarisation modes: LH, LV, CR, CL, LH3, LH5, LV3, LV5, LAP, LAN.
        '''

        phase=0 #phase value for LH and LV is ignored by self.idscannable
        if mode in X_RAY_POLARISATIONS[:-2]:
            # polarisation is constant in these modes
            coef=get_fitting_coefficents(mode, Ep, str(self.pgmgratingselect.getPosition()), self.lut)
            gap = coef[0] + coef[1]*Ep + coef[2]*Ep**2 +coef[3]*Ep**3 + coef[4]*Ep**4 + coef[5]*Ep**5 + coef[6]*Ep**6 + coef[7]*Ep**7
            
            if (gap<self.minGap or gap>self.maxGap): #IDGroup Excel table only cover this range
                raise ValueError("Required Soft X-Ray ID gap is %s out side allowable bound (%s, %s)!" % (gap, self.minGap, self.maxGap))
            
            if mode == "LH":
                phase = 0.0
                BeamEnergyPolarisationClass.harmonicOrder = 1
            elif mode == "LH3":
                phase = 0.0
                BeamEnergyPolarisationClass.harmonicOrder = 3
            elif mode == "LH5":
                phase = 0.0
                BeamEnergyPolarisationClass.harmonicOrder = 5              
            elif mode == "LV":
                phase=self.maxPhase
                BeamEnergyPolarisationClass.harmonicOrder = 1
            elif mode == "LV3":
                phase=self.maxPhase
                BeamEnergyPolarisationClass.harmonicOrder = 3
            elif mode == "LV5":
                phase=self.maxPhase
                BeamEnergyPolarisationClass.harmonicOrder = 5
            elif mode in ["CR", "CL"]:
                phase = 12.92907548 +  0.37353288*gap + (-0.00614332*gap**2) + 5.3209E-06*gap**3 + 2.00631E-06*gap**4 + (-3.9185E-08*gap**5) + 3.17986E-10*gap**6 + (-9.93646E-13*gap**7)
                
        elif mode in X_RAY_POLARISATIONS[-2:]:
            BeamEnergyPolarisationClass.harmonicOrder = 1
            gap, polarisation, phase = self.getIDPositions() # get Current ID position
            print("Current ID Gap, Polarisation, Phase = %f, %s, %f before lookup calculation" % (gap, polarisation, phase))
            if self.polarisationConstant or self.energyConstant:
                if (phase<0): #row phase can be negative in EPICS but lookup table only has positive phase values.
                    polarisation_angle,energy = self.idlamlookup.getEnergyPolarisation(gap, -phase)
                else:
                    polarisation_angle,energy = self.idlamlookup.getEnergyPolarisation(gap, phase)  
                print("Polarisation_Angle, Energy = %f, %f at current Gap, Phase = %f, %f" % (polarisation_angle, energy, gap, phase))
                if self.polarisationConstant:       #move energy only
                    if (polarisation_angle>0):
                        polarisation_angle=-polarisation_angle #lookup table only contains negative polarisation angle!
                        self.inputSignSwitched=True
                    gap, phase = self.idlamlookup.getGapPhase(Ep, polarisation_angle) #only energy changes, keep existing polarisation
                    print("Gap, Phase = %f, %f at Energy, Polarisation_Angle = %f, %f after lookup calculation" % (gap, phase, Ep, polarisation_angle))
                elif self.energyConstant:      #move polarisation angle only
                    if (polar>0):
                        polar=-polar #lookup table only contains negative polarisation angle!
                        self.inputSignSwitched=True
                    gap, phase = self.idlamlookup.getGapPhase(energy, polar) #only polarisation changes, keep existing energy
                    print("Gap, Phase = %f, %f at Energy, Polarisation_Angle = %f, %f after lookup calculation" % (gap, phase, energy, polar))
            elif not self.polarisationConstant and not self.energyConstant:
                if Ep is not None and polar is not None:
                    if (polar>0):
                        polar=-polar #lookup table only contains negative polarisation angle!
                        self.inputSignSwitched=True
                    gap, phase = self.idlamlookup.getGapPhase(Ep, polar) # both energy and polarisation change
                    print("Gap, Phase = %f, %f at Energy, Polarisation_Angle = %f, %f after lookup calculation" % (gap, phase, Ep, polar))
                else:
                    raise ValueError("Both energy and polarisation angle are required!")
            if (gap<self.minGap or gap>self.maxGap): #IDGroup Excel table only cover this range
                raise ValueError("Required Soft X-Ray ID gap is %s out side allowable bound (%s, %s!" % (gap, self.minGap,self.maxGap))
        else:
            raise ValueError("Unsupported polarisation mode %s is requested!" % (mode))
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
            gap, polarisation, phase = self.getIDPositions()
            energy=float(self.pgmenergy.getPosition())
                    
            if polarisation in X_RAY_POLARISATIONS[-2:]:
                polarisation_angle = self.idlamlookup.getEnergyPolarisation(gap, phase)[0]
                if self.inputSignSwitched:
                    polarisation_angle = -polarisation_angle
                    self.inputSignSwitched=False
                if self.polarisationConstant:
                    return energy
                elif self.energyConstant:
                    self.setOutputFormat(["%5.2f"])
                    self.polarisation = polarisation_angle
                    return polarisation_angle
                else:
                    self.setOutputFormat(["%10.6f", "%3.2f"])
                    self.polarisation = polarisation_angle
                    return energy, polarisation_angle
            else:
                if self.polarisationConstant:
                    return energy
                elif self.energyConstant:
                    self.setOutputFormat(["%s"])
                    self.polarisation = polarisation
                    return polarisation
                else:
                    self.setOutputFormat(["%10.6f","%s"])
                    self.polarisation = polarisation
                    return energy, polarisation
            

    def validatePolarisation(self, polarisation_angle):
        new_polarisation = None
        if polarisation_angle < -90 or polarisation_angle > 90:
            raise ValueError("polarisation_angle input is outside supported range (-90, 90)!")
        elif polarisation_angle < 0:
            new_polarisation = "LAN"
        else:
            new_polarisation = "LAP"
        return new_polarisation

    def moveDevices(self, gap, new_polarisation, phase, energy):
        for s in self.scannables.getGroupMembers():
            if str(s.getName()) == str(self.idscannable.getName()):
                try:
                    if new_polarisation in ["LH3", "LH5"]:
                        new_polarisation = "LH" # Java class does not explicitly support Harmonic
                    elif new_polarisation in ["LV3", "LV5"]:
                        new_polarisation = "LV"
                    s.asynchronousMoveTo([gap, new_polarisation, phase])
                except:
                    print("cannot set %s to [%f, %s, %f]" % (s.getName(), gap, new_polarisation, phase))
                    raise
            elif not self.energyConstant:
                try:
                    s.asynchronousMoveTo(energy)
                except:
                    print("cannot set %s to %f." % (s.getName(), energy))
                    raise
    
    def rawAsynchronousMoveTo(self, new_position):
        '''move beam energy, polarisation, or both to specified values.
        At the background this moves both ID gap, phase, and PGM energy to the values corresponding to this energy, polarisation or both.
        If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''
        gap=20
        new_polarisation = None
        polarisation_angle =  None
        phase=0

        if self.getName() == "dummyenergy":
            self.energy = float(new_position)
        elif self.getName == "dummypolarisation":
            self.polaristion=float(new_position)
        else:
            if not self.SCANNING:  #ensure ID hardware in sync in 'pos' command
                self.rawGetPosition()
                #required for Live Control GUI update when 'pos'
                self.addIObservers()
                
            #parse arguments as it could be 1 or 2 inputs, string or number type, depending on polarisation mode and instance attribute value
            if not isinstance(new_position, list): # single argument
                if isinstance(new_position, basestring):
                    if self.polarisationConstant: #input must be for energy
                        raise ValueError("Input value must be a number.")
                    new_polarisation=str(new_position)
                    if not new_polarisation in X_RAY_POLARISATIONS[:-2]:
                        raise ValueError("Input value must be one of valid polarisation mode: %s" % str(X_RAY_POLARISATIONS[:-2]) )
                    energy=self.pgmenergy.getPosition()
                elif isinstance(new_position, numbers.Number):
                    if self.polarisationConstant: #input must be for energy
                        energy=float(new_position) #energy validation is done in getFittingCoefficent() method
                        gap, new_polarisation, phase = self.getIDPositions()  #get existing polarisation mode
                    if self.energyConstant:       #input must be for polarisation angle in Linear Arbitrary mode
                        polarisation_angle=float(new_position)
                        new_polarisation = self.validatePolarisation(polarisation_angle)
                        energy=self.pgmenergy.getPosition()                         
                else:
                    raise ValueError("Input value must be a string or number.")
            else: #2 arguments
                args = list(new_position)
                if len(args) != 2:
                    raise ValueError("Expect 2 arguments but got %s" % len(args))
                if isinstance(args[0], numbers.Number):
                    energy=float(args[0]) #range validation is done later
                else:
                    raise ValueError("1st input for energy must be a number")
                if isinstance(args[1], numbers.Number):
                    polarisation_angle=float(args[1])
                    new_polarisation = self.validatePolarisation(polarisation_angle)
                elif isinstance(args[1], basestring):
                    new_polarisation=str(args[1])
                    if not new_polarisation in X_RAY_POLARISATIONS[:-2]:
                        raise ValueError("Input value must be one of valid polarisation mode: %s" % str(X_RAY_POLARISATIONS[:-2]) )
                else:
                    raise ValueError("2nd input for polarisation must be a number or string")
                
            gap, phase = self.idgapphase(Ep=energy, polar=polarisation_angle, mode=new_polarisation) 

        if self.feedbackPV is not None and not self.SCANNING:
            #stop feedback
            from gdascripts.utils import caput
            caput(self.feedbackPV, 0)        
            self.moveDevices(gap, new_polarisation, phase, energy)
            self.waitWhileBusy()
            caput(self.feedbackPV, 4)
        else:
            self.moveDevices(gap, new_polarisation, phase, energy)
            
          
    def isBusy(self):
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
                    print("%s: isBusy() throws exception\n, %s " % (s.getName(), sys.exc_info()))
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
        if self.submit is not None:
            self.submit.cancel(self.isBusy())
        self.removeIObservers()
            
    def atScanStart(self):
        if self.getName() == "dummyenergy" or self.getName()=="dummypolarisation":
            return;
        else: # real hardware
            self.rawGetPosition() #ensure ID hardware in sync at start of scan
            self.SCANNING=True
            #setup IObserver (cannot be called in configure() method as reset_namespace will add them again
            self.addIObservers()

       
    def atScanEnd(self):
        if self.getName() == "dummyenergy" or self.getName()=="dummypolarisation":
            return;
        else: # real hardware
            self.SCANNING=False
            #remove IOberser when finished scan
            self.removeIObservers()
    
    def updateValue(self):
        sleep(0.2)
        while self.pgmenergy.isBusy() or self.idscannable.isBusy():
            sleep(0.1)
            self.notifyIObservers(self, self.rawGetPosition())
    
    def updatePolarisation(self, source, change):
        if self.energyConstant and change == MotorEvent.MOVE_COMPLETE:  # @UndefinedVariable
            self.logger.debug("source is %s, change is %s" % (source, change))
            self.notifyIObservers(self, self.rawGetPosition())
        
    def updateEnergy(self, source, change):
        if self.polarisationConstant and change == ScannableStatus.BUSY:
            self.logger.debug("source is %s, change is %s" % (source, change))
            self.submit = Async.submit(lambda : self.updateValue(), "Updating value from %1$s", self.getName())

    def addIObservers(self):
        if self.energyConstant and self.polarisationObserver is None: # check required to stop multiple add
            self.polarisationObserver = GenericObserver("polarisationObserver", self.updatePolarisation)
            self.idscannable.addIObserver(self.polarisationObserver)
        if self.polarisationConstant and self.energyObserver is None:
            self.energyObserver = GenericObserver("energyObserver", self.updateEnergy)
            self.pgmenergy.addIObserver(self.energyObserver)
        if not self.energyConstant and not self.polarisationConstant:
            if self.polarisationObserver is None:
                self.polarisationObserver = GenericObserver("polarisationObserver", self.updatePolarisation)
                self.idscannable.addIObserver(self.polarisationObserver)
            if self.energyObserver is None:
                self.energyObserver = GenericObserver("energyObserver", self.updateEnergy)
                self.pgmenergy.addIObserver(self.energyObserver)
        
    def removeIObservers(self):
        '''delete observer from observed object'''
        if self.energyConstant and self.polarisationObserver is not None:
            self.idscannable.deleteIObserver(self.polarisationObserver)
            self.polarisationObserver = None
        if self.polarisationConstant and self.energyObserver is not None:
            self.pgmenergy.deleteIObserver(self.energyObserver)
            self.energyObserver = None
        if not self.energyConstant and not self.polarisationConstant:
            if self.polarisationObserver is None:
                self.idscannable.deleteIObserver(self.polarisationObserver)
                self.polarisationObserver = None
            if self.energyObserver is None:
                self.pgmenergy.deleteIObserver(self.energyObserver)
                self.energyObserver = None
        

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


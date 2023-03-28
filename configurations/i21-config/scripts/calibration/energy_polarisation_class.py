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
from gda.observable import IObserver
from org.apache.commons.lang3.builder import EqualsBuilder, HashCodeBuilder
from gda.device import MotorStatus

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
        result = list(self.idscannable.getPosition())
        gap = float(result[0])
        polarisation = str(result[1])
        if self.getHarmonic() > 1: # support other harmonic
            polarisation = str(polarisation)+str(self.getHarmonic())
        phase = float(result[2])
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
        polarisation_angle = None
        if polarisation in X_RAY_POLARISATIONS[-2:]:
            polarisation_angle = self.idlamlookup.getEnergyPolarisation(gap, phase if phase > 0 else -phase)[0]
        gap, phase = self.idgapphase(Ep=energy, polar=polarisation_angle, mode=polarisation)
        return gap, polarisation, phase


    def get_gap_use_theoretical_coefficients(self, Ep):
        '''calculate gap from energy using coefficients derived from ID group theoretical data.
        see https://confluence.diamond.ac.uk/x/OY8QAw for the data used here.
        '''
        if Ep >= 322 and Ep <= 1200:
            gap = 9.507261813 + 0.040972013 * Ep + (-2.99623E-05 * Ep ** 2) + 1.31482E-08 * Ep ** 3
        elif Ep > 1200 and Ep <= 1400:
            gap = 1521.627122 + (-4.841605377 * Ep) + 0.0058961 * Ep ** 2 + (-3.19241E-06 * Ep ** 3) + 6.52333E-10 * Ep ** 4
        elif Ep > 1400 and Ep <= 1500:
            gap = 157668.674 + (-442.4995757 * Ep) + 0.465963424 * Ep ** 2 + (-0.000218165 * Ep ** 3) + 3.8326E-08 * Ep ** 4
        elif Ep > 1500 and Ep <= 1535:
            gap = -1173703.108 + 2333.596119 * Ep + (-1.546647824 * Ep ** 2) + 0.000341725 * Ep ** 3
        elif Ep > 1535 and Ep <= 1541:
            gap = 3093760.122 + (-4026.212272 * Ep) + 1.309955533 * Ep ** 2
        else:
            raise ValueError("Energy %f requested outside range (322, 1541) supported in CR or CL polarisation!" % Ep)
        print("\nID gap is calculated based on ID group's theoretical data!")
        self.logger.info("Use theoretical coefficients for gap calculation from energy in CR/CL polarisation mode.")
        return gap


    def get_phase_and_set_harmonic_order(self, mode, gap):
        n = 1
        if mode == "LH":
            phase = 0.0
            n = 1
        elif mode == "LH3":
            phase = 0.0
            n = 3
        elif mode == "LH5":
            phase = 0.0
            n = 5
        elif mode == "LV":
            phase = self.maxPhase
            n = 1
        elif mode == "LV3":
            phase = self.maxPhase
            n = 3
        elif mode == "LV5":
            phase = self.maxPhase
            n = 5
        elif mode in ["CR", "CL"]:
            phase = 12.92907548 + 0.37353288 * gap + (-0.00614332 * gap ** 2) + 5.3209E-06 * gap ** 3 + 2.00631E-06 * gap ** 4 + (-3.9185E-08 * gap ** 5) + 3.17986E-10 * gap ** 6 + (-9.93646E-13 * gap ** 7)
            n = 1
        self.setHarmonic(n)
        return phase


    def get_gap_and_phase_in_linear_arbitrary_polarisation(self, requested_energy, requested_angle):
        gap, polarisation, phase = self.getIDPositions() # get Current ID position
        self.logger.debug("Current ID Gap, Polarisation, Phase = %f, %s, %f before lookup calculation" % (gap, polarisation, phase))
        polarisation_angle, energy = self.idlamlookup.getEnergyPolarisation(gap, phase if phase > 0 else -phase) #row phase can be negative in EPICS but lookup table only has positive phase values.
        self.logger.debug("Current Polarisation_Angle, Energy = %f, %f before lookup calculation" % (polarisation_angle, energy))
        if self.polarisationConstant: # move energy and keep polarisation angle
            angle = polarisation_angle if polarisation_angle < 0 else -polarisation_angle #lookup table only contains negative polarisation angle!
            self.inputSignSwitched = True if polarisation_angle > 0 else False
            energy = requested_energy
        else:
            angle =  requested_angle if requested_angle < 0 else -requested_angle #lookup table only contains negative polarisation angle!
            self.inputSignSwitched = True if requested_angle > 0 else False
            if not self.energyConstant and not self.polarisationConstant: #move energy only or both energy and polarisation angle
                energy = requested_energy
        gap, phase = self.idlamlookup.getGapPhase(energy, angle) #only polarisation changes, keep existing energy
        self.logger.debug("Gap, Phase = %f, %f at Energy, Polarisation_Angle = %f, %f after lookup calculation" % (gap, phase, requested_energy, requested_angle))
        return gap, phase

    def idgapphase(self, Ep=None, polar=None, mode='LH'):
        '''converts energy and polarisation to  gap and phase. It supports polarisation modes: LH, LV, CR, CL, LH3, LH5, LV3, LV5, LAP, LAN.
        '''

        phase=0 #phase value for LH and LV is ignored by self.idscannable
        if mode in X_RAY_POLARISATIONS[:-2]:
            # polarisation is constant in these modes
            try:
                coef = get_fitting_coefficents(mode, Ep, str(self.pgmgratingselect.getPosition()), self.lut)
                gap = coef[0] + coef[1]*Ep + coef[2]*Ep**2 +coef[3]*Ep**3 + coef[4]*Ep**4 + coef[5]*Ep**5 + coef[6]*Ep**6 + coef[7]*Ep**7
            except (KeyError, ValueError) as e:
                if mode not in ["CR", "CL"]:
                    raise e
                gap = self.get_gap_use_theoretical_coefficients(Ep)
            
            phase = self.get_phase_and_set_harmonic_order(mode, gap)
                
        elif mode in X_RAY_POLARISATIONS[-2:]:
            self.setHarmonic(1)
            gap, phase = self.get_gap_and_phase_in_linear_arbitrary_polarisation(Ep, polar)
        else:
            raise ValueError("Unsupported polarisation mode %s is requested!" % (mode))
        
        if (gap<self.minGap or gap>self.maxGap): #IDGroup Excel table only cover this range
            raise ValueError("Required Soft X-Ray ID gap is %s out side allowable bound (%s, %s!" % (gap, self.minGap,self.maxGap))
        if phase < 0 or phase > self.maxPhase: #Physical limits of ID Row Phase
            raise ValueError("Required Soft X-Ray ID phase is %s out side allowable bound (%s, %s)!" % (phase, 0, self.maxPhase))
        
        return (gap, phase)
        
    def rawGetPosition(self):
        '''returns the current beam energy, or polarisation, or both.'''
        gap, polarisation, phase = self.getIDPositions()
        energy = float(self.pgmenergy.getPosition())
                
        if self.polarisationConstant:
            return energy
        if polarisation in X_RAY_POLARISATIONS[-2:]:
            polarisation_angle = self.idlamlookup.getEnergyPolarisation(gap, phase)[0]
            polarisation_angle = -polarisation_angle if self.inputSignSwitched else polarisation_angle
            self.polarisation = polarisation_angle
            if self.energyConstant:
                self.setOutputFormat(["%5.2f"])
                return polarisation_angle
            else:
                self.setOutputFormat(["%10.6f", "%3.2f"])
                return energy, polarisation_angle
        else:
            self.polarisation = polarisation
            if self.energyConstant:
                self.setOutputFormat(["%s"])
                return polarisation
            else:
                self.setOutputFormat(["%10.6f","%s"])
                return energy, polarisation
            

    def validatePolarisation(self, polarisation_angle):
        new_polarisation = None
        if polarisation_angle < -89.882 or polarisation_angle > 89.882:
            raise ValueError("polarisation_angle input is outside supported range (-89.882, 89.882)!")
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
                        n = 1
                        if new_polarisation == "LH3":
                            n = 3
                        if new_polarisation == "LH5":
                            n = 5
                        self.setHarmonic(n)
                        new_polarisation = "LH" # Java class does not explicitly support Harmonic
                    elif new_polarisation in ["LV3", "LV5"]:
                        n = 1
                        if new_polarisation == "LV3":
                            n = 3
                        if new_polarisation == "LV5":
                            n = 5
                        self.setHarmonic(n)
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
    

    def parse_arguments(self, new_position):
    #parse arguments as it could be 1 or 2 inputs, string or number type, depending on polarisation mode and instance attribute value
        if not isinstance(new_position, list): # single argument
            if isinstance(new_position, basestring):
                if self.polarisationConstant: #input must be for energy
                    raise ValueError("Input value must be a number.")
                polarisation_mode = str(new_position)
                if polarisation_mode not in X_RAY_POLARISATIONS[:-2]:
                    raise ValueError("Input value must be one of valid polarisation mode: %s" % str(X_RAY_POLARISATIONS[:-2]))
                energy = self.pgmenergy.getPosition()
                polarisation_angle = None
            elif isinstance(new_position, numbers.Number):
                if self.polarisationConstant: #input must be for energy
                    energy = float(new_position) #energy validation is done in getFittingCoefficent() method
                    gap, polarisation_mode, phase = self.getIDPositions() #get existing polarisation mode
                    if polarisation_mode in X_RAY_POLARISATIONS[:-2]:
                        polarisation_angle = None
                    else:
                        polarisation_angle = self.idlamlookup.getEnergyPolarisation(gap, phase if phase > 0 else -phase)[0]                        
                if self.energyConstant: #input must be for polarisation angle in Linear Arbitrary mode
                    polarisation_angle = float(new_position)
                    polarisation_mode = self.validatePolarisation(polarisation_angle)
                    self.inputSignSwitched = False
                    energy = self.pgmenergy.getPosition()
            else:
                raise ValueError("Input value must be a string or number.")
        else:
            args = list(new_position)
            if len(args) != 2:
                raise ValueError("Expect 2 arguments but got %s" % len(args))
            if isinstance(args[0], numbers.Number):
                energy = float(args[0]) #range validation is done later
            else:
                raise ValueError("1st input for energy must be a number")
            if isinstance(args[1], numbers.Number):
                polarisation_angle = float(args[1])
                polarisation_mode = self.validatePolarisation(polarisation_angle)
                self.inputSignSwitched = False
            elif isinstance(args[1], basestring):
                polarisation_mode = str(args[1])
                if polarisation_mode not in X_RAY_POLARISATIONS[:-2]:
                    raise ValueError("Input value must be one of valid polarisation mode: %s" % str(X_RAY_POLARISATIONS[:-2]))
                polarisation_angle = None
            else:
                raise ValueError("2nd input for polarisation must be a number or string") #2 arguments
        return energy, polarisation_angle, polarisation_mode

    def rawAsynchronousMoveTo(self, new_position):
        '''move beam energy, polarisation, or both to specified values.
        At the background this moves both ID gap, phase, and PGM energy to the values corresponding to this energy, polarisation or both.
        If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''

        if not self.SCANNING:  #ensure ID hardware in sync in 'pos' command
            self.rawGetPosition()
            #required for Live Control GUI update when 'pos'
            self.addIObservers()
            
        energy, polarisation_angle, polarisation_mode = self.parse_arguments(new_position)
            
        gap, phase = self.idgapphase(Ep=energy, polar=polarisation_angle, mode=polarisation_mode) 

        if self.feedbackPV is not None and not self.SCANNING:
            #stop feedback
            from gdascripts.utils import caput
            caput(self.feedbackPV, 0)        
            self.moveDevices(gap, polarisation_mode, phase, energy)
            self.waitWhileBusy()
            caput(self.feedbackPV, 4)
        else:
            self.moveDevices(gap, polarisation_mode, phase, energy)
            
          
    def isBusy(self):
        '''checks the busy status of all child scannables.        
        If and only if all child scannables are done this will be set to False.
        '''
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
        self.rawGetPosition() #ensure ID hardware in sync at start of scan
        self.SCANNING=True
        #setup IObserver (cannot be called in configure() method as reset_namespace will add them again
        self.addIObservers()

       
    def atScanEnd(self):
        self.SCANNING=False
        #remove IOberser when finished scan
        self.removeIObservers()
    
    def updateValue(self):
        sleep(0.2) # wait for motor to start moving
        while self.pgmenergy.isBusy() or self.idscannable.isBusy():
            sleep(0.1)
            self.notifyIObservers(self, self.rawGetPosition())
    
    def updatePolarisation(self, source, change):
        if self.energyConstant and change == MotorStatus.BUSY:
            self.logger.debug("source is %s, change is %s" % (source, change))
            self.submit = Async.submit(lambda : self.updateValue(), "Updating value from %1$s", self.getName())
        
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
        
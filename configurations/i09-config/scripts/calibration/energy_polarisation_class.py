'''
define class for control of soft X-ray beam energy and polarisation. 

Supported polarisations are limited to LH, LV, CR, CL, and LH3. Linear Arbitrary polarisation is not supported!
For polarisation CL and CR, the ID phase is set to 15 mm fixed at the requested of I09 PBS!

@author: Fajin Yuan
@since: 10 August 2020
'''
import sys
from time import sleep
import logging
logger = logging.getLogger('__main__')

from gda.configuration.properties import LocalProperties
from gda.device.scannable import ScannableMotionBase
from gda.device.scannable.scannablegroup import ScannableGroup
from lookup.threeKeysLookupTable_CSV import load_lookup_table, get_fitting_coefficents
import numbers

class BeamEnergyPolarisationClass(ScannableMotionBase):
    '''Coupled beam energy and polarisation scannable that encapsulates and fan-outs control to ID gap, row phase, and PGM energy.

        This pseudo device requires a lookupTable table object to provide ID parameters for calculation of ID idgap from beam
        energy required and harmonic order. The lookupTable table object must be created before the instance creation of this class.
        The child scannables or pseudo devices must exist in jython's global namespace prior to any method call of this class
        instance.
        '''

    def __init__(self, name, idctrl, pgmenergy, lut="JIDEnergy2GapCalibrations.csv", energyConstant=False, polarisationConstant=False, gap_offset=None, feedbackPV=None):
        '''Constructor - Only succeed if it find the lookupTable table, otherwise raise exception.'''
        self.lut,self.header = load_lookup_table(LocalProperties.get("gda.config")+"/lookupTables/"+lut)
        self.idscannable = idctrl
        self.pgmenergy = pgmenergy
        self.scannables = ScannableGroup(name, [pgmenergy, idctrl])
        self.detune = gap_offset
        self.feedbackPV = feedbackPV
        self._busy = 0
        self.setName(name)
        self.setLevel(3)
        self.setOutputFormat(["%10.6f"])
        self.setInputNames([name])
        self.setExtraNames([])
        self.order = 1  #default to 1st harmonic order
        self.polarisation = 'UNKNOWN'
        self.gap = 50
        self.phase = 0
        self.energyConstant = energyConstant
        self.polarisationConstant = polarisationConstant
        self.SCANNING = False
        if self.energyConstant and self.polarisationConstant:
            raise RuntimeError("Cannot create an instance with both energy and polarisation being constant.")
        self.isConfigured = False
        self.inputSignSwitched = False
        self.beamlinename = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME)
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
        phase = float(result[2])
        return (gap, polarisation, phase)

    def showFittingCoefficentsLookupTable(self):
        formatstring="%4s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s"
        print (formatstring % tuple([x for x in self.header]))
        for key, value in sorted(self.lut.iteritems()):
            print (formatstring % tuple([x for x in key] + [x for x in value]))

    def setHarmonic(self,n):
        self.order=n

    def getHarmonic(self):
        return self.order

    def idgapphase(self, Ep=None, mode='LH',n=1):
        '''coverts energy and polarisation to  gap and phase. It supports polarisation modes: LH, LV, CR, CL.
        '''

        phase = 0 #phase value for LH and LV is ignored by self.idscannable
        if mode in ["LH", "LV", "CR", "CL"]:
            Ep = Ep/n
            #polarisation is constant in these modes
            coef = get_fitting_coefficents(mode, Ep, self.lut)
            gap = coef[0] + coef[1]*Ep + coef[2]*Ep**2 +coef[3]*Ep**3 + coef[4]*Ep**4 + coef[5]*Ep**5 + coef[6]*Ep**6 + coef[7]*Ep**7 + coef[8]*Ep**8 + coef[9]*Ep**9
            #adjust gap
            if self.detune:
                gap = gap + float(self.detune.getPosition())

            if (gap<self.minGap or gap>self.maxGap): #IDGroup Excel table only cover this range
                raise ValueError("Required Soft X-Ray ID gap is %s out side allowable bound (%s, %s)!" % (gap, self.minGap, self.maxGap))

            if mode == "LV":
                phase = self.maxPhase

            if mode in ["CR", "CL"]:
                phase=15.0

        else:
            raise ValueError("Unsupported polarisation mode, only LH, LV, CR and CL are supported.")
        if phase < 0 or phase > self.maxPhase: #Physical limits of ID Row Phase
            raise ValueError("Required Soft X-Ray ID phase is %s out side allowable bound (%s, %s)!" % (phase, 0, self.maxPhase))
        return (gap, phase)

    def calc(self, energy, mode):
        return self.idgapphase(energy, mode, self.order)

    def rawGetPosition(self):
        '''returns the current beam energy, or polarisation, or both.'''

        gap, polarisation, phase = self.getIDPositions()
        energy=float(self.pgmenergy.getPosition()/1000.0) #energy unit is in keV

        if polarisation in ["LH","LV","CR","CL"]:
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

    def rawAsynchronousMoveTo(self, new_position):
        '''move beam energy, polarisation, or both to specified values.
        At the background this moves both ID gap, phase, and PGM energy to the values corresponding to this energy, polarisation or both.
        If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''
        gap = 20
        new_polarisation = None
        phase = 0
        try:
            if not self.SCANNING:  #ensure ID hardware in sync in 'pos' command
                self.rawGetPosition()
            #parse arguments as it could be 1 or 2 inputs, string or number type, depending on polarisation mode and instance attribute value
            if not isinstance(new_position, list): # single argument
                self.logger.debug("Single argument: {} given".format(type(new_position)))
                if isinstance(new_position, basestring):
                    #polarisation change requested
                    energy=float(self.pgmenergy.getPosition())/1000.0 #get existing energy
                    if self.polarisationConstant: #input must be for energy
                        raise ValueError("Input value must be a number.")
                    new_polarisation=str(new_position)
                    if not new_polarisation in ["LH", "LV","CR", "CL"]:
                        raise ValueError('Input value must be one of valid polarisation mode: "LH", "LV","CR", "CL"')
                elif isinstance(new_position, numbers.Number):
                    # energy change requested
                    if self.polarisationConstant: #input must be for energy
                        energy=float(new_position) 
                        gap, new_polarisation, phase = self.getIDPositions() #get existing polarisation
                    else:
                        raise ValueError("Polarisation is not constant, but a number: {} was given".format(new_position))
                else:
                    raise ValueError("Input value must be a string or number.")
            else: #2 arguments
                args = list(new_position)
                if len(args) != 2:
                    raise ValueError("Expect 2 arguments but got %s" % len(args))
                if isinstance(args[0], numbers.Number):
                    self.logger.debug("Two arguments given and first argument {} is a number".format(args[0]))
                    energy = float(args[0]) #range validation is done later
                else:
                    raise ValueError("1st input for energy must be a number")
                if isinstance(args[1], basestring):
                    new_polarisation = args[1]
                else:
                    raise ValueError("2nd input  for polarisation must be a string")
                
            gap, phase=self.idgapphase(Ep=energy, mode=new_polarisation, n=self.order)
        except:
            raise #re-raise any exception from above try block

        if self.feedbackPV is not None and not self.SCANNING:
            #stop feedback
            from gdascripts.utils import caput
            caput(self.feedbackPV, 1)
        
        for s in self.scannables.getGroupMembers():
            if str(s.getName()) == str(self.idscannable.getName()):
                try:
                    s.asynchronousMoveTo([gap, new_polarisation, phase])
                except:
                    print ("cannot set %s to [%f, %s, %f]" % (s.getName(), gap, new_polarisation, phase))
                    raise
            else:
                if self.energyConstant: #polarisation change only
                    continue #do not need to move PGM energy
                else:
                    try:
                        s.asynchronousMoveTo(energy*1000)
                    except:
                        print ("cannot set %s to %f." % (s.getName(), energy))
                        raise
                    
        if self.feedbackPV is not None and not self.SCANNING:           
            caput(self.feedbackPV, 0)

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
                    print (s.getName() + " isBusy() throws exception ", sys.exc_info())
                    raise
            if self._busy == 0:
                return 0
            else:
                return 1

    def atScanStart(self):
        self.rawGetPosition() #ensure ID hardware in sync at start of scan
        self.SCANNING=True
        if self.feedbackPV is not None:
            #during scan, stop feedback
            from gdascripts.utils import caput
            caput(self.feedbackPV, 1)

    def atScanEnd(self):
        self.SCANNING=False
        if self.feedbackPV is not None:
            #restore feedback
            from gdascripts.utils import caput
            caput(self.feedbackPV, 0)

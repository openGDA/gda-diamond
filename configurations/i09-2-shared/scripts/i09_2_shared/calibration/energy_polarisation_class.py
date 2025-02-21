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
from gdascripts import installation as installation
logger = logging.getLogger('__main__')

from gda.configuration.properties import LocalProperties
from gda.device.scannable import ScannableMotionBase, ScannableStatus
from gda.device.scannable.scannablegroup import ScannableGroup
from i09shared.lookup.threeKeysLookupTable_CSV import load_lookup_table, get_fitting_coefficents
import numbers

from gda.device import MotorStatus

from gda.observable import IObserver
from uk.ac.diamond.daq.concurrent import Async
from org.apache.commons.lang3.builder import EqualsBuilder, HashCodeBuilder

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
    '''
    Coupled beam energy and polarisation scannable that encapsulates and fan-outs control to ID gap, row phase, and PGM energy.

    This pseudo device requires a lookupTable table object to provide ID parameters for calculation of ID idgap from beam
    energy required and harmonic order. The lookupTable table object must be created before the instance creation of this class.
    The child scannables or pseudo devices must exist in jython's global namespace prior to any method call of this class
    instance.
    '''

    def __init__(self, name, harmonic_order_scannable, idctrl, pgmenergy, lut="JIDEnergy2GapCalibrations.csv", energyConstant=False, polarisationConstant=False, gap_offset=None, feedbackPV=None):
        '''Constructor - Only succeed if it find the lookupTable table, otherwise raise exception.'''
        self.lut,self.header = load_lookup_table(LocalProperties.get("gda.config")+"/../i09-2-shared/lookupTables/"+lut)
        self.idscannable = idctrl
        self.mono_energy = pgmenergy
        self.scannables = ScannableGroup(name, [pgmenergy, idctrl])
        self.detune = gap_offset
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
        self.beamlinename = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME)
        self.logger = logger.getChild(self.__class__.__name__)
        self.harmonic_order_scannable = harmonic_order_scannable

        self.submit = None
        self.energyObserver = None
        self.polarisationObserver =  None

    def configure(self):
        if self.idscannable is not None:
            self.maxGap=self.idscannable.getController().getMaxGapPos()
            self.minGap=self.idscannable.getController().getMinGapPos()
            self.maxPhase=self.idscannable.getController().getMaxPhaseMotorPos()


        self.addIObservers()
        self.isConfigured=True

    def getIDPositions(self):
        '''get gap and phase from ID hardware controller, and set polarisation mode in GDA 'idscannable' instance
        This method sync current object states with ID state in EPICS IOC.
        '''
        result = list(self.idscannable.getPosition())
        gap = float(result[0])
        polarisation = str(result[1])
        if self.harmonic_order_scannable.getPosition() > 1: # support other harmonic
            polarisation = str(polarisation)+str(self.harmonic_order_scannable.getPosition())
        phase = float(result[2])
        return (gap, polarisation, phase)

    def showFittingCoefficentsLookupTable(self):
        formatstring="%4s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s\t%11s"
        print (formatstring % tuple([x for x in self.header]))
        for key, value in sorted(self.lut.iteritems()):
            print (formatstring % tuple([x for x in key] + [x for x in value]))

    def setOrder(self,n):
        self.harmonic_order_scannable.rawAsynchronousMoveTo(n)

    def getOrder(self):
        return self.harmonic_order_scannable.getPosition()

    def idgap(self, energy):
        '''return gap for the given energy for current polarisation.
            used in cvscan where polarisation doesn't change during continuous energy moving.
        '''
        gap, polarisation, phase = self.getIDPositions()  # @UnusedVariable
        gap, phase = self.idgapphase(Ep=energy, mode=polarisation)  # @UnusedVariable
        return gap

    def idgapphase(self, Ep=None, mode='LH'):
        '''coverts energy and polarisation to  gap and phase. It supports polarisation modes: LH, LV, CR, CL, and LH3
        '''

        phase = 0 #phase value for LH and LV is ignored by self.idscannable
        if mode in ["LH", "LV", "CR", "CL", "LH3"]:
            #polarisation is constant in these modes
            coef = get_fitting_coefficents(mode, Ep, self.lut)
            gap = coef[0] + coef[1]*Ep + coef[2]*Ep**2 +coef[3]*Ep**3 + coef[4]*Ep**4 + coef[5]*Ep**5 + coef[6]*Ep**6 + coef[7]*Ep**7 + coef[8]*Ep**8 + coef[9]*Ep**9
            #adjust gap
            if self.detune:
                gap = gap + float(self.detune.getPosition())

            if (gap<self.minGap or gap>self.maxGap): #IDGroup Excel table only cover this range
                raise ValueError("Required Soft X-Ray ID gap is %s out side allowable bound (%s, %s)!" % (gap, self.minGap, self.maxGap))

            if mode == "LH3":
                self.harmonic_order_scannable.rawAsynchronousMoveTo(3)
            if mode == "LH":
                self.harmonic_order_scannable.rawAsynchronousMoveTo(1)

            if mode == "LV":
                self.harmonic_order_scannable.rawAsynchronousMoveTo(1)
                phase = self.maxPhase

            if mode in ["CR", "CL"]:
                self.harmonic_order_scannable.rawAsynchronousMoveTo(1)
                phase=15.0

        else:
            raise ValueError("Unsupported polarisation mode, only LH, LV, CR, CL, and LH3 are supported.")
        if phase < 0 or phase > self.maxPhase: #Physical limits of ID Row Phase
            raise ValueError("Required Soft X-Ray ID phase is %s out side allowable bound (%s, %s)!" % (phase, 0, self.maxPhase))
        return (gap, phase)

    def calc(self, energy, order=1):
        message = "'order' input is no longer required. this is now merged into polarisation mode in the calibration lookup table!"
        print(message)
        self.logger.warn(message)
        return self.idgap(energy)

    def rawGetPosition(self):
        '''returns the current beam energy, or polarisation, or both.'''

        gap, polarisation, phase = self.getIDPositions()  # @UnusedVariable
        energy=float(self.mono_energy.getPosition()/1000.0) #energy unit is in keV

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

    def moveDevices(self, gap, new_polarisation, phase, energy):
        for s in self.scannables.getGroupMembers():
            if str(s.getName()) == str(self.idscannable.getName()):
                try:
                    if new_polarisation == "LH3" :
                        new_polarisation = "LH"
                    s.asynchronousMoveTo([gap, new_polarisation, phase])
                except:
                    print("cannot set %s to [%f, %s, %f]" % (s.getName(), gap, new_polarisation, phase))
                    raise
            elif not self.energyConstant:
                try:
                    s.asynchronousMoveTo(energy * 1000)
                except:
                    print("cannot set %s to %f." % (s.getName(), energy))
                    raise

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
                    energy=float(self.mono_energy.getPosition())/1000.0 #get existing energy
                    if self.polarisationConstant: #input must be for energy
                        raise ValueError("Input value must be a number.")
                    new_polarisation=str(new_position)
                    if not new_polarisation in ["LH", "LV","CR", "CL", "LH3"]:
                        raise ValueError('Input value must be one of valid polarisation mode: "LH", "LV","CR", "CL", "LH3"')
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

            gap, phase=self.idgapphase(Ep=energy, mode=new_polarisation)
        except:
            raise #re-raise any exception from above try block

        if self.feedbackPV is not None and not self.SCANNING:
            #stop feedback
            from gdascripts.utils import caput
            caput(self.feedbackPV, 1)
            self.moveDevices(gap, new_polarisation, phase, energy)
            self.waitWhileBusy()
            caput(self.feedbackPV, 0)
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
                    print (s.getName() + " isBusy() throws exception ", sys.exc_info())
                    raise
            if self._busy == 0:
                return 0
            else:
                return 1

    def stop(self):
        self.mono_energy.stop()
        if installation.isLive():
            print("ID motion stop is not supported according to ID-Group instruction. Please wait for the Gap motion to complete!")
        else:
            self.idscannable.stop()
        if self.submit is not None:
            self.submit.cancel(self.isBusy())

    def atScanStart(self):
        self.rawGetPosition() #ensure ID hardware in sync at start of scan
        self.SCANNING=True

    def atScanEnd(self):
        self.SCANNING=False

    def updateValue(self):
        sleep(0.2) # wait for motor to start moving
        while self.mono_energy.isBusy() or self.idscannable.isBusy():
            sleep(0.1)
            self.notifyIObservers(self, self.rawGetPosition())
        #last update on not busy
        sleep(0.1)
        self.notifyIObservers(self, self.rawGetPosition())

    def updatePolarisationValue(self):
        sleep(0.2) # wait for motor to start moving
        while self.mono_energy.isBusy() or self.idscannable.isBusy():
            sleep(0.1)
            self.notifyIObservers(self, self.rawGetPosition()[1])
        #last update on not busy
        sleep(0.1)
        self.notifyIObservers(self, self.rawGetPosition()[1])

    def updateEnergyValue(self):
        sleep(0.2) # wait for motor to start moving
        while self.mono_energy.isBusy() or self.idscannable.isBusy():
            sleep(0.1)
            self.notifyIObservers(self, self.rawGetPosition()[0])
        #last update on stop
        sleep(0.1)
        self.notifyIObservers(self, self.rawGetPosition()[0])

    def updatePolarisation(self, source, change):
        self.logger.debug("source is %s, change is %s" % (source, change))
        if self.energyConstant and change == MotorStatus.BUSY:
            self.logger.debug("%s: submit updating polarisation value thread ! " % self.getName())
            self.submit = Async.submit(lambda : self.updateValue(), "Updating polarisation value from %1$s", self.getName())

    def updatePolarisationField(self, source, change):
        self.logger.debug("source is %s, change is %s" % (source, change))
        if not self.energyConstant and not self.polarisationConstant and change == MotorStatus.BUSY:
            self.logger.debug("%s: submit updating polarisation field thread ! " % self.getName())
            self.submit = Async.submit(lambda : self.updatePolarisationValue(), "Updating polarisation field from %1$s", self.getName())

    def updateEnergy(self, source, change):
        self.logger.debug("source is %s, change is %s" % (source, change))
        if self.polarisationConstant and change == ScannableStatus.BUSY:
            self.logger.debug("%s: submit updating energy value thread !" % self.getName())
            self.submit = Async.submit(lambda : self.updateValue(), "Updating energy value from %1$s", self.getName())

    def updateEnergyField(self, source, change):
        self.logger.debug("source is %s, change is %s" % (source, change))
        if not self.energyConstant and not self.polarisationConstant and change == ScannableStatus.BUSY:
            self.logger.debug("%s: submit updating energy field thread !" % self.getName())
            self.submit = Async.submit(lambda : self.updateEnergyValue(), "Updating energy field from %1$s", self.getName())

    def addIObservers(self):
        if self.energyConstant and self.polarisationObserver is None: # check required to stop multiple add
            self.logger.debug("%s: add polarisation observer to %s" % (self.getName(), self.idscannable.getName()))
            self.polarisationObserver = GenericObserver("polarisationObserver", self.updatePolarisation)
            self.idscannable.addIObserver(self.polarisationObserver)
        if self.polarisationConstant and self.energyObserver is None:
            self.logger.debug("%s: add energy observer to %s" % (self.getName(), self.mono_energy.getName()))
            self.energyObserver = GenericObserver("energyObserver", self.updateEnergy)
            self.mono_energy.addIObserver(self.energyObserver)
        if not self.energyConstant and not self.polarisationConstant:
            if self.polarisationObserver is None:
                self.logger.debug("%s: add polarisation observer to %s" % (self.getName(), self.idscannable.getName()))
                self.polarisationObserver = GenericObserver("polarisationObserver", self.updatePolarisationField)
                self.idscannable.addIObserver(self.polarisationObserver)
            if self.energyObserver is None:
                self.logger.debug("%s: add energy observer to %s" % (self.getName(), self.mono_energy.getName()))
                self.energyObserver = GenericObserver("energyObserver", self.updateEnergyField)
                self.mono_energy.addIObserver(self.energyObserver)

    def removeIObservers(self):
        '''delete observer from observed object'''
        if self.energyConstant and self.polarisationObserver is not None:
            self.logger.debug("%s: delete polarisation observer from %s" % (self.getName(), self.idscannable.getName()))
            self.idscannable.deleteIObserver(self.polarisationObserver)
            self.polarisationObserver = None
        if self.polarisationConstant and self.energyObserver is not None:
            self.logger.debug("%s: delete energy observer from %s" % (self.getName(), self.pgmenergy.getName()))
            self.pgmenergy.deleteIObserver(self.energyObserver)
            self.energyObserver = None
        if not self.energyConstant and not self.polarisationConstant:
            if self.polarisationObserver is not None:
                self.logger.debug("%s: delete polarisation observer from %s" % (self.getName(), self.idscannable.getName()))
                self.idscannable.deleteIObserver(self.polarisationObserver)
                self.polarisationObserver = None
            if self.energyObserver is not None:
                self.logger.debug("%s: delete energy observer from %s" % (self.getName(), self.pgmenergy.getName()))
                self.pgmenergy.deleteIObserver(self.energyObserver)
                self.energyObserver = None
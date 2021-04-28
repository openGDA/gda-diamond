'''
Class represents either polarisation, energy, or both energy and polarisation of the X-ray beam.
It provides control of Insertion Device energy or polarisation.

'''
import sys
from time import sleep
import logging
from calibrations.xraysource import X_RAY_SOURCE_MODES
import math
from utils.ExceptionLogs import localStation_exception
from gdascripts.messages.handle_messages import simpleLog
import installation
logger = logging.getLogger('__main__')

from gda.configuration.properties import LocalProperties
from gda.device.scannable import ScannableMotionBase
from lookups.fourKeysLookupTable import get_fitting_coefficents, load_lookup_table
import numbers

ROW_PHASE_MOTOR_TOLERANCE = 0.004
MAXIMUM_ROW_PHASE_MOTOR_POSITION = 24.0
X_RAY_POLARISATIONS = ['pc', 'nc', 'lh', 'lv', 'la', 'lh3', 'unknown']


class BeamEnergyPolarisationClass(ScannableMotionBase):
    '''Coupled beam energy and polarisation scannable that encapsulates and fan-outs control to ID gap, row phase, and PGM energy.
    
        This pseudo device requires 2 lookupTable table objects to provide ID parameters for calculation of ID gap and row phase from beam 
        energy and polarisation required, respectively. These lookupTable table objects must be created before the instance creation of this class.
        The child scannables or pseudo devices must exist in jython's global name_space prior to any method call of this class 
        instance.
        '''
    harmonicOrder = 1
       
    def __init__(self, name, source, pgmenergy, idd_controls, idu_controls, lut4gap="IDEnergy2GapCalibrations.csv", lut4phase="IDEnergy2PhaseCalibrations.csv", energyConstant=False, polarisationConstant=False, maxGap=200, minGap=16, maxPhase=24):
        '''Constructor - Only succeed if it find the lookupTable table, otherwise raise exception.'''
        self.lut4gap, self.header = load_lookup_table(LocalProperties.get("gda.config") + "/lookupTables/" + lut4gap)
        self.lut4phase, self.header = load_lookup_table(LocalProperties.get("gda.config") + "/lookupTables/" + lut4phase)
        self.source = source
        self.pgmenergy = pgmenergy
        self.idd = idd_controls
        self.idu = idu_controls
        self._busy = 0
        self.setName(name)
        self.setLevel(3)
        self.setOutputFormat(["%10.6f"])
        self.setInputNames([name])
        self.setExtraNames([])
        self.polarisation = X_RAY_POLARISATIONS[6]
        self.gap = 50
        self.phase = 0
        self.order = 1
        self.energyConstant = energyConstant
        self.polarisationConstant = polarisationConstant
        self.SCANNING = False 
        if self.energyConstant and self.polarisationConstant:
            raise ValueError("Cannot create an instance with both energy and polarisation being constant.")
        self.logger = logger.getChild(self.__class__.__name__)
        self.maxGap = maxGap
        self.minGap = minGap
        self.maxPhase = maxPhase
        
    def determinePhaseFromHardware(self, insertiondevice={}):
        rowphase1 = float(insertiondevice['rowphase1'].getPosition())
        rowphase2 = float(insertiondevice['rowphase2'].getPosition())
        rowphase3 = float(insertiondevice['rowphase3'].getPosition())
        rowphase4 = float(insertiondevice['rowphase4'].getPosition())
        gap = float(insertiondevice['gap'].getPosition())
        # determine polarisation and phase value using row phase motor position pattern, However there is no way to return lh3 polarisation
        if self._motorPositionEqual(rowphase1, 0.0) and self._motorPositionEqual(rowphase2, 0.0) and self._motorPositionEqual(rowphase3, 0.0) and self._motorPositionEqual(rowphase4, 0.0):
            #Linear Horizontal
            if float(self.pgmenergy.getPosition()) > 2*gap*gap:
                polarisation = X_RAY_POLARISATIONS[5]
            elif float(self.pgmenergy.getPosition()) < 2*gap*gap:
                polarisation = X_RAY_POLARISATIONS[2]
            phase = 0.0
            return polarisation, phase
        if self._motorPositionEqual(rowphase1, MAXIMUM_ROW_PHASE_MOTOR_POSITION) and self._motorPositionEqual(rowphase2, 0.0) and self._motorPositionEqual(rowphase3, MAXIMUM_ROW_PHASE_MOTOR_POSITION) and self._motorPositionEqual(rowphase4, 0.0):
            #Linear Vertical
            polarisation = X_RAY_POLARISATIONS[3]
            phase = MAXIMUM_ROW_PHASE_MOTOR_POSITION
            return polarisation, phase
        if self._motorPositionEqual(rowphase1, rowphase3) and rowphase1 > 0.0 and self._motorPositionEqual(rowphase2, 0.0) and self._motorPositionEqual(rowphase4, 0.0):
            #Positive Circular
            polarisation = X_RAY_POLARISATIONS[0]
            phase = rowphase1
            return polarisation, phase
        if self._motorPositionEqual(rowphase1, rowphase3) and rowphase1 < 0.0 and self._motorPositionEqual(rowphase2, 0.0) and self._motorPositionEqual(rowphase4, 0.0):
            #Negative Circular
            polarisation = X_RAY_POLARISATIONS[1]
            phase = rowphase1
            return polarisation, phase
        if self._motorPositionEqual(rowphase1, -rowphase3) and self._motorPositionEqual(rowphase2, 0.0) and self._motorPositionEqual(rowphase4, 0.0):
            #Positive Linear Arbitrary
            polarisation = X_RAY_POLARISATIONS[4]
            phase = rowphase1
            return polarisation, phase
        if self._motorPositionEqual(rowphase2, -rowphase4) and self._motorPositionEqual(rowphase1, 0.0) and self._motorPositionEqual(rowphase3, 0.0):
            #Negative Linear Arbitrary
            polarisation = X_RAY_POLARISATIONS[4]
            phase = rowphase2
            return polarisation, phase
        #UNKNOWN
        polarisation = X_RAY_POLARISATIONS[6]
        phase = 0.0
        return (polarisation, phase)
    
    def _motorPositionEqual(self, a, b):
        return math.fabs(a - b) < ROW_PHASE_MOTOR_TOLERANCE
    
    def getIDPositions(self):
        '''get gap and phase from ID hardware controller, and set polarisation mode in GDA 'idscannable' instance
        This method sync current object states with ID state in EPICS IOC.
        '''
        if self.source.getPosition() == X_RAY_SOURCE_MODES[0]:
            gap = float(self.idd['gap'].getPosition())
            polarisation, phase = self.determinePhaseFromHardware(self.idd)            
        elif self.source.getPosition() == X_RAY_SOURCE_MODES[1]:
            gap = float(self.idu['gap'].getPosition())
            polarisation, phase = self.determinePhaseFromHardware(self.idu)
        else:
            raise ValueError("Unknown X-ray Source Mode.")
        if polarisation == X_RAY_POLARISATIONS[5]:
            BeamEnergyPolarisationClass.harmonicOrder = 3
        else:
            BeamEnergyPolarisationClass.harmonicOrder = 1
        return (gap, polarisation, phase)
    
    def displayGapCalibrationData(self):
        formatstring = "%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s"
        print (formatstring % tuple(self.header))
        for key, value in sorted(self.lut4gap.iteritems()):
            print (formatstring % (key[0], key[1], key[2], key[3], value[0], value[1], value[2], value[3], value[4], value[5], value[6], value[7]))
            
    def displayPhaseCalibrationData(self):
        formatstring = "%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s\t%12s"
        print (formatstring % tuple(self.header))
        for key, value in sorted(self.lut4phase.iteritems()):
            print (formatstring % (key[0], key[1], key[2], key[3], value[0], value[1], value[2], value[3], value[4], value[5], value[6], value[7]))
    
    def setHarmonicsOrder(self, n):
        if not n in [1, 3]:
            raise ValueError("Only beam harmonics order 1 and 3 are supported!")
        self.order = n
        BeamEnergyPolarisationClass.harmonicOrder = n
        
    def getHarmonicsOrder(self):
        return self.order
    
    def get_ID_gap_phase_at_current_source_polarisation(self, energy):
        gap, polarisation, phase = self.getIDPositions()
        gap, phase = self.idgapphase(self.source, Ep=energy, polar=polarisation)
        return gap, phase
    
    def idgapphase(self, source, Ep=None, polar='lh'):
        '''converts energy and polarisation to  gap and phase. It supports polarisation modes: 'pc','nc', 'lh', 'lv', 'la', 'lh3'.
        '''
        if polar in X_RAY_POLARISATIONS[:-1] :
        # find ID gap from energy
            coef = get_fitting_coefficents(source.getPosition(), polar, Ep, self.lut4gap)
            gap = coef[0] + coef[1] * Ep + coef[2] * Ep ** 2 + coef[3] * Ep ** 3 + coef[4] * Ep ** 4 + coef[5] * Ep ** 5 + coef[6] * Ep ** 6 + coef[7] * Ep ** 7
            
            if (gap < self.minGap or gap > self.maxGap):  # IDGroup Excel table only cover this range
                raise ValueError("Required Soft X-Ray ID gap is %s out side allowable bound (%s, %s)!" % (gap, self.minGap, self.maxGap))
            
            if polar == "lh":
                BeamEnergyPolarisationClass.harmonicOrder = 1
                phase = 0.0
            elif polar == "lh3":
                BeamEnergyPolarisationClass.harmonicOrder = 3
                phase = 0.0                
            elif polar == "lv":
                BeamEnergyPolarisationClass.harmonicOrder = 1
                phase = self.maxPhase
            elif polar in ["pc", "nc", 'la']:
                BeamEnergyPolarisationClass.harmonicOrder = 1
                coef2 = get_fitting_coefficents(source.getPosition(), polar, Ep, self.lut4phase)
                phase = coef2[0] + coef2[1] * Ep + coef2[2] * Ep ** 2 + coef2[3] * Ep ** 3 + coef2[4] * Ep ** 4 + coef2[5] * Ep ** 5 + coef2[6] * Ep ** 6 + coef2[7] * Ep ** 7
        else:
            raise ValueError("Unsupported polarisation mode %s, only %s are supported." % (polar, X_RAY_POLARISATIONS[:-1]))
        if phase < -self.maxPhase or phase > self.maxPhase:  # Physical limits of ID Row Phase
            raise ValueError("Required Soft X-Ray ID phase is %s out side allowable bound (%s, %s)!" % (phase, -self.maxPhase, self.maxPhase))
        return (gap, phase)
        
    def rawGetPosition(self):
        '''returns the current beam energy, or polarisation, or both.'''
        if self.getName() == "dummyenergy":
            return self.energy
        elif self.getName() == "dummypolarisation":
            return self.polarisation
        else:
            polarisation = self.getIDPositions()[1]
            energy = self.pgmenergy.getPosition()

            if self.polarisationConstant:
                return energy
            elif self.energyConstant:
                self.setOutputFormat(["%s"])
                self.polarisation = polarisation
                return polarisation
            else:
                self.setOutputFormat(["%10.6f", "%s"])
                self.polarisation = polarisation
                return energy, polarisation

    def move_id_to_positions(self, idcontrol, gap, phase, polarisation):
        try:
            idcontrol['gap'].asynchronousMoveTo(gap)
            idcontrol['rowphase1'].asynchronousMoveTo(phase)
            idcontrol['rowphase2'].asynchronousMoveTo(0.0)
            if polarisation == X_RAY_POLARISATIONS[4]:
                phase = -phase
            idcontrol['rowphase3'].asynchronousMoveTo(phase)
            idcontrol['rowphase4'].asynchronousMoveTo(0.0)
            if not polarisation == X_RAY_POLARISATIONS[4]:
                idcontrol['jawphase'].asynchronousMoveTo(0.0) #set ID jawphase to 0 position except for la
        except:
            localStation_exception(sys.exc_info(), "Error move %s to position (%f, %s, %f)" % (self.source.getPosition(), gap, polarisation, phase))
            simpleLog(localStation_exception)
            raise
    
    def isIDBusy(self, idcontrol):
        return idcontrol['gap'].isBusy() or idcontrol['rowphase1'].isBusy() or idcontrol['rowphase2'].isBusy() or idcontrol['rowphase3'].isBusy() or idcontrol['rowphase4'].isBusy() or idcontrol['jawphase'].isBusy()
            
    def rawAsynchronousMoveTo(self, new_position):
        '''move beam energy, polarisation, or both to specified value.
        At the background this moves both ID gap, phase, and PGM energy to the values corresponding to this energy, polarisation or both.
        If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''
        gap = 20
        new_polarisation_mode = None
        phase = 0
        if self.getName() == "dummyenergy":
            self.energy = float(new_position)
        elif self.getName == "dummypolarisation":
            self.polaristion = float(new_position)
        else:
            if not self.SCANNING:  # ensure ID hardware in sync in 'pos' command
                self.getIDPositions()  # update self.gap, self.polarisation,self.phase in this object
                
            # parse arguments as it could be 1 or 2 inputs, string type for polarisation or number type for energy
            if not isinstance(new_position, list):  # single argument
                if isinstance(new_position, basestring): 
                    if self.polarisationConstant:  # input must be for energy
                        raise ValueError("Input value must be a number.")
                    new_polarisation_mode = str(new_position)
                    if not new_polarisation_mode in X_RAY_POLARISATIONS[:-1]:
                        raise ValueError('Input value must be one of valid polarisation mode in %s' % X_RAY_POLARISATIONS[:-1])
                    energy = self.pgmenergy.getPosition()  # polarisation change, keep the current energy
                elif isinstance(new_position, numbers.Number):
                    if self.polarisationConstant:  # input must be for energy
                        energy = float(new_position)  # energy validation is done in get_fitting_coefficent() method
                        new_polarisation_mode = self.getIDPositions()[1]  # energy change, keep existing polarisation mode
                    if self.energyConstant:  # input must be for polarisation
                        raise ValueError('Input value must be one of valid polarisation mode in %s' % X_RAY_POLARISATIONS[:-1])
                else:
                    raise ValueError("Input value must be a string or number.")
            else:  # 2 arguments
                args = list(new_position)
                if len(args) != 2:
                    raise ValueError("Expect 2 arguments but got %s" % len(args))
                if isinstance(args[0], numbers.Number):
                    energy = float(args[0])  # range validation is done later
                else:
                    raise ValueError("1st input for energy must be a number")

                if isinstance(args[1], basestring):
                    new_polarisation_mode = args[1]
                else:
                    raise ValueError("2nd input for polarisation must be a String")

            gap, phase = self.idgapphase(self.source, Ep=energy, polar=new_polarisation_mode)

            # move ID to positions
            if self.source.getPosition() == X_RAY_SOURCE_MODES[0]:
                self.move_id_to_positions(self.idd, gap, phase, new_polarisation_mode)
            elif self.source.getPosition() == X_RAY_SOURCE_MODES[1]:
                self.move_id_to_positions(self.idu, gap, phase, new_polarisation_mode)
            else:
                raise ValueError("Source mode %s is not supported!" % self.source.getPosition())
            
            # move PGM to position
            if self.polarisationConstant or not self.energyConstant :
                try:
                    self.pgmenergy.asynchronousMoveTo(energy)
                except:
                    print("cannot set %s to %f." % (self.pgmenergy.getName(), energy))
                    raise
                
    def isBusy(self):
        '''checks the busy status of all child scannables.        
        If and only if all child scannables are done this will be set to False.
        '''
        if self.getName() == "dummyenergy" or self.getName() == "dummypolarisation":
            sleep(0.1)
            return False
        else:  # real hardware
            return self.pgmenergy.isBusy() or self.isIDBusy(self.idd if self.source.getPosition() == X_RAY_SOURCE_MODES[0] else self.idu)

    def stop_id(self, idcontrol):
        try:
            idcontrol['gap'].stop()
            idcontrol['rowphase1'].stop()
            idcontrol['rowphase2'].stop()
            idcontrol['rowphase3'].stop()
            idcontrol['rowphase4'].stop()
            idcontrol['jawphase'].stop()
        except:
            localStation_exception(sys.exc_info(), "Error stop %s" % (self.source.getPosition()))
            simpleLog(localStation_exception)
            raise
        
    def stop(self):
        self.pgmenergy.stop()
        if installation.isLive():
            print("ID motion stop is not supported according to ID-Group instruction. Please wait for the Gap motion to complete!")
        else:  
            if self.source.getPosition() == X_RAY_SOURCE_MODES[0]:
                self.stop_id(self.idd)
            elif self.source.getPosition() == X_RAY_SOURCE_MODES[1]:
                self.stop_id(self.idu)
            else:
                raise ValueError("Source mode %s is not supported!" % self.source.getPosition())

    def atScanStart(self):
        if self.getName() == "dummyenergy" or self.getName() == "dummypolarisation":
            return;
        else:  # real hardware
            self.getIDPositions()  # ensure ID hardware in sync at start of scan
            self.SCANNING = True
        
    def atScanEnd(self):
        self.SCANNING = False


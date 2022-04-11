"""
A Controller for Continuous Energy moving of both PGM grating pitch motor and ID gap motor at Constant Velocity

@author: Fajin Yuan 27 July 2020
"""

from datetime import datetime, timedelta
from gda.device import DeviceBase
from gda.device.continuouscontroller import ConstantVelocityMoveController
from gdascripts.scannable.epics.PvManager import PvManager
from java.util.concurrent import Callable
from org.slf4j import LoggerFactory
from pgm.pgm import angles2energy, enecff2mirror, enemirror2grating #, enecff2grating @UnresolvedImport
import threading, time
import installation
from time import sleep
from calibrations.xraysource import X_RAY_SOURCE_MODES

class ContinuousPgmGratingIDGapMoveController(ConstantVelocityMoveController, DeviceBase):
    '''Controller for constant velocity scan moving both PGM Grating Pitch and ID Gap at same time at constant speed respectively.
        It works for both Live and Dummy mode.
    '''
    def __init__(self, name, pgm_grat_pitch, pgm_mirr_pitch, pgmpvroot, energy, polarisation, idupvroot, iddpvroot, move_pgm=True, move_id=True): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("ContinuousPgmGratingIDGapEnergyMoveController:%s" % name)
        self.verbose = False
        self.setName(name)
        self._start_event = threading.Event()
        self._movelog_time = datetime.now()
        #PGM
        self._pgm_grat_pitch = pgm_grat_pitch
        self._pgm_mirr_pitch = pgm_mirr_pitch
        self._pgm_grat_pitch_speed_orig = None
        self._pgm_runupdown_time = None
        self._move_pgm = move_pgm
        self._move_id  = move_id

        self.pvs = PvManager({'grating_density':                'NLINES',
                              'cff':                            'CFF',
                              'grating_offset':                 'GRTOFFSET',
                              'plane_mirror_offset':            'MIROFFSET',
                              'pgm_energy':                     'ENERGY',
                              'grating_pitch':                  'GRT:PITCH',
                              'mirror_pitch':                   'MIR:PITCH',
                              'energy_calibration_gradient':    'MX',
                              'energy_calibration_reference':   'REFERENCE'}, pgmpvroot)
        if installation.isLive():
            self.pvs.configure()
            
        #ID
        self.energy = energy
        self.polarisation = polarisation
        self.idd = energy.idd
        self.idu = energy.idu
        self._id_gap_speed_orig=None
        self._id_runupdown_time = None
        self.idupvs = PvManager({'vel':'BLGSETVEL',
                                'acc':'IDGSETACC'}, idupvroot)
        if installation.isLive():
            self.idupvs.configure()
            
        self.iddpvs = PvManager({'vel':'BLGSETVEL',
                                'acc':'IDGSETACC'}, iddpvroot)
        if installation.isLive():
            self.iddpvs.configure()
            
        self.grating_pitch_positions=[]
        self.mirror_pitch_positions=[]
        self.pgm_energy_positions=[]
        self._start_time = None
        self.idspeedfactor=1.0
        self.pgmspeedfactor=1.0
        self.idstartdelaytime=0.0
        self._move_start = 0.0
        self._move_end = 1.0
        self._move_step = 0.1
        self._triggerPeriod = 0.0
        self.idcontrols = None
        self.continuousMovingStarted = False
       
    def setIDStartDelayTime(self, t):
        self.idstartdelaytime=t
        
    def getIDStartDelayTime(self):
        return self.idstartdelaytime
     
    def setIDSpeedFactor(self, val):
        self.idspeedfactor=val
    
    def getIDSpeedFactor(self):
        return self.idspeedfactor
    
    def setPGMSpeedFactor(self, val):
        self.pgmspeedfactor=val
    
    def getPGMSpeedFactor(self):
        return self.pgmspeedfactor
        
    #https://jira.diamond.ac.uk/browse/I10-301
    def enableIDMove(self):
        self._move_id=True
    
    def disableIDMove(self):
        self._move_id=False
        
    def isIDMoveEnabled(self):
        return self._move_id

    def enablePGMMove(self):
        self._move_pgm=True
    
    def disablePGMMove(self):
        self._move_pgm=False
        
    def isPGMMoveEnabled(self):
        return self._move_pgm

    # Implement: public interface ConstantVelocityMoveController extends ContinuousMoveController

    def setStart(self, start): # double
        self._move_start = start
        if self.verbose: self.logger.info('setStart(%r)' % start)
    
    def setEnd(self, end): # double
        self._move_end = end
        if self.verbose: self.logger.info('setEnd(%r)' % end)
    
    def setStep(self, step): # double
        self._move_step = step
        if self.verbose: self.logger.info('setStep(%r)' % step)

    # Implement: public interface ContinuousMoveController extends HardwareTriggerProvider

    def getPgmEnergyParameters(self):
        grating_densityFromEnum = {'0' : 400., '1':400., '2':1200.}
        return (grating_densityFromEnum[self.pvs['grating_density'].caget()],
                float(self.pvs['cff'].caget()), 
                float(self.pvs['grating_offset'].caget()), 
                float(self.pvs['plane_mirror_offset'].caget()), 
                float(self.pvs['energy_calibration_gradient'].caget()), 
                float(self.pvs['energy_calibration_reference'].caget()))
        
    def getPgmEnergyParametersFixed(self):
        # Hard code these values until we can work out a nice way of getting at the PVs
        # TODO: Get the values from their Epics PVs
        """
        caget BL10I-OP-PGM-01:NLINES BL10I-OP-PGM-01:CFF BL10I-OP-PGM-01:GRTOFFSET BL10I-OP-PGM-01:MIROFFSET BL10I-OP-PGM-01:MX BL10I-OP-PGM-01:REFERENCE
        """
        grating_density                 = 400.              # caget BL10I-OP-PGM-01:NLINES
        cff                             = 2.25              # caget BL10I-OP-PGM-01:CFF
        grating_offset                  = -0.053747         # caget BL10I-OP-PGM-01:GRTOFFSET
        plane_mirror_offset             = 0.002514          # caget BL10I-OP-PGM-01:MIROFFSET
        energy_calibration_gradient     = 1.0178            # caget BL10I-OP-PGM-01:MX
        energy_calibration_reference    = 392.555           # caget BL10I-OP-PGM-01:REFERENCE

        return grating_density, cff, grating_offset, plane_mirror_offset, energy_calibration_gradient, energy_calibration_reference


    def PreparePGMForMove(self):
        self._pgm_grat_pitch_speed_orig = 0.018 #required this because EPICS energy change this speed depending on the size of change set
        self._pgm_grat_pitch.speed=self._pgm_grat_pitch_speed_orig
   
        # Calculate the energy midpoint
        energy_midpoint = (self._move_end + self._move_start) / 2.
        if self.verbose:
            self.logger.info('preparePGMForMove:energy_midpoint=%r ' % (energy_midpoint))

        if installation.isLive():
            self.grating_density, self.cff, self.grating_offset, self.plane_mirror_offset, self.energy_calibration_gradient, self.energy_calibration_reference = self.getPgmEnergyParameters()
        else:
            self.grating_density, self.cff, self.grating_offset, self.plane_mirror_offset, self.energy_calibration_gradient, self.energy_calibration_reference = self.getPgmEnergyParametersFixed()
            
        # Calculate plane mirror angle for given grating density, energy, cff and offsets
        self.mirr_pitch_midpoint = enecff2mirror(gd=self.grating_density, 
                                                 energy=energy_midpoint, 
                                                 cff=self.cff, 
                                                 groff=self.grating_offset, 
                                                 pmoff=self.plane_mirror_offset, 
                                                 ecg=self.energy_calibration_gradient, 
                                                 ecr=self.energy_calibration_reference)
        # Calculate grating angles for given grating density, energy, mirror angle and offsets
        self._grat_pitch_start = enemirror2grating(gd=self.grating_density, 
                                                   energy=self._move_start, 
                                                   pmang=self.mirr_pitch_midpoint, 
                                                   groff=self.grating_offset, 
                                                   pmoff=self.plane_mirror_offset, 
                                                   ecg=self.energy_calibration_gradient, 
                                                   ecr=self.energy_calibration_reference)
        self._grat_pitch_end = enemirror2grating(gd=self.grating_density, 
                                                 energy=self._move_end, 
                                                 pmang=self.mirr_pitch_midpoint, 
                                                 groff=self.grating_offset, 
                                                 pmoff=self.plane_mirror_offset, 
                                                 ecg=self.energy_calibration_gradient, 
                                                 ecr=self.energy_calibration_reference)
        ### Calculate main cruise moves & speeds from start/end/step
        self._pgm_grat_pitch_speed = (abs(self._grat_pitch_end - self._grat_pitch_start) / self.getTotalTime())*self.getPGMSpeedFactor()
        
        ### Calculate ramp distance from required speed and ramp times
        #check speed within limits
        if self._pgm_grat_pitch_speed<=0.000 or self._pgm_grat_pitch_speed>0.018:
            raise ValueError("Calculated PGM Grit Pitch motor speed %f is outside limits [%f, %f]!" % (self._pgm_grat_pitch_speed, 0.000, 0.018))
        
        # Set the speed before we read out ramp times in case it is dependent
        self._pgm_grat_pitch.speed = self._pgm_grat_pitch_speed 
        # Should really be / | | | | | \ not /| | | | |\
        self._pgm_runupdown_time = self._pgm_grat_pitch.timeToVelocity
        self._pgm_runupdown = self._pgm_grat_pitch_speed / 2 * self._pgm_runupdown_time
        ### Move motor at full speed to start position
        if self.verbose:
            self.logger.info('preparePGMForMove:_pgm_mirr_pitch.asynchronousMoveTo(%r) @ %r ' % (self.mirr_pitch_midpoint * 1000., self._pgm_mirr_pitch.speed))
        self._pgm_mirr_pitch.asynchronousMoveTo(self.mirr_pitch_midpoint * 1000.)
        self._pgm_grat_pitch.speed = self._pgm_grat_pitch_speed_orig
        if self.getGratingMoveDirectionPositive():
            if self.verbose:
                self.logger.info('preparePGMForMove:asynchronousMoveTo(%r) @ %r (+ve)' % ((self._grat_pitch_start - self._pgm_runupdown) * 1000., self._pgm_grat_pitch_speed_orig))
            self._pgm_grat_pitch.asynchronousMoveTo((self._grat_pitch_start - self._pgm_runupdown) * 1000.)
        else:
            if self.verbose:
                self.logger.info('preparePGMForMove:asynchronousMoveTo(%r) @ %r (-ve)' % ((self._grat_pitch_start + self._pgm_runupdown) * 1000., self._pgm_grat_pitch_speed_orig))
            self._pgm_grat_pitch.asynchronousMoveTo((self._grat_pitch_start + self._pgm_runupdown) * 1000.)

    def PrepareIDForMove(self):
        if self.energy.source.getPosition() == X_RAY_SOURCE_MODES[0]:
            self.idcontrols = self.idd
            self.idpvs = self.iddpvs
        elif self.energy.source.getPosition()== X_RAY_SOURCE_MODES[1]:
            self.idcontrols = self.idu
            self.idpvs = self.idupvs
        else:
            raise ValueError("X-ray source mode %s is not supported!" % self.energy.source.getPosition())
        self.prepareID(self.idcontrols, self.idpvs)
        
    def getIDGapFromEnergy(self, egy):
        return self.energy.get_ID_gap_phase_at_current_source_polarisation(egy)[0]
        
    def prepareID(self, idcontrols, idpvs):
        if installation.isLive():
            self._id_gap_speed_orig = float(idpvs['vel'].caget())
        else:
            self._id_gap_speed_orig = idcontrols['gap'].speed
            
        # Calculate the energy midpoint
        energy_midpoint = (self._move_end + self._move_start) / 2.
        if self.verbose:
            self.logger.info('prepareID: energy_midpoint = %r ' % (energy_midpoint))
        # Calculate phase position for current X-ray source and polarisation at energy midpoint
        gap_midpoint, phase_midpoint = self.energy.get_ID_gap_phase_at_current_source_polarisation(energy_midpoint)  # @UnusedVariable
        
        # Calculate ID gap at start energy and end energy for current X-ray source and polarisation
        self._id_gap_start, phase_start = self.energy.get_ID_gap_phase_at_current_source_polarisation(self._move_start)  # @UnusedVariable
        self._id_gap_end, phase_end = self.energy.get_ID_gap_phase_at_current_source_polarisation(self._move_end)  # @UnusedVariable
        
        ### Calculate main cruise move speed from start/end/step
        self._id_gap_speed = abs(self._id_gap_end - self._id_gap_start) / self.getTotalTime()*self.idspeedfactor
        
        ### Calculate ramp distance from required speed and ramp times
        # check to ensure speed within limits
        if self._id_gap_speed<0.004 or self._id_gap_speed>1.0:
            raise ValueError("Calculated ID gap speed %f is outside limits [%f, %f]!" % (self._id_gap_speed, 0.004, 1.0))
        
        if installation.isLive():
            # Cannot set id_gap.speed through soft motor which in EPICS is read-only 
            idpvs['vel'].caput(self._id_gap_speed)
        else:
            idcontrols['gap'].speed = self._id_gap_speed 
            
        #acceleration time per axis
        self._id_axis_speed=self._id_gap_speed/2
        self._id_runupdown_time_per_axis=self._id_axis_speed*4
        # Should really be / | | | | | \ not /| | | | |\
        self._id_runupdown_per_axis = self._id_axis_speed / 2 * self._id_runupdown_time_per_axis
        self._id_gap_runupdown = self._id_runupdown_per_axis * 2

        ### Move motor at full speed to start position
        if installation.isLive():
            idpvs['vel'].caput(self._id_gap_speed_orig)
        else:
            idcontrols['gap'].speed = self._id_gap_speed_orig 
            
        if self.getIDGapMoveDirectionPositive():
            if self.verbose:
                self.logger.info('prepareID:move_id_to_positions([%s, %f, %f, %s]) @ %r mm/sec (+ve)' % (self.energy.source.getPosition(), (self._id_gap_start - self._id_gap_runupdown), phase_midpoint, self.epolarisation.getPosition(), self._id_gap_speed_orig))
            self.energy.move_id_to_positions(idcontrols, self._id_gap_start - self._id_gap_runupdown, phase_midpoint, self.polarisation.getPosition())
        else:
            if self.verbose:
                self.logger.info('prepareID:move_id_to_positions([%s, %f, %f, %s]) @ %r mm/sec (-ve)' % (self.energy.source.getPosition(), (self._id_gap_start + self._id_gap_runupdown), phase_midpoint, self.polarisation.getPosition(), self._id_gap_speed_orig))
            self.energy.move_id_to_positions(idcontrols, self._id_gap_start + self._id_gap_runupdown, phase_midpoint, self.polarisation.getPosition())

    def prepareForMove(self):
        if self.verbose: self.logger.info('prepareForMove()...')
        self.continuousMovingStarted = False
        if self.isPGMMoveEnabled():
            self.PreparePGMForMove()
        else:
            if self.verbose:
                self.logger.info('PGM move is disabled in %r' % (self.getName()))

        if self.isIDMoveEnabled():
            self.PrepareIDForMove()
        else:
            if self.verbose:
                self.logger.info('ID move is disabled in %r' % (self.getName()))
            
        if not self.isPGMMoveEnabled() and not self.isIDMoveEnabled():
            raise RuntimeError("Both PGM and ID moves are disabled so no scan will occur!")
        
        self.waitWhileMoving()
        if self.verbose:
            self.logger.info('...prepareForMove')

    def startMove(self):
        if self.verbose: self.logger.info('startMove()...')
        
        # Notify all position callables to start waiting for their time
        self._start_time = datetime.now()
        self._start_event.set()
        # Start threads to start ID & PGM and at the correct times
        if self.isPGMMoveEnabled():
            self._pgm_grat_pitch.speed = self._pgm_grat_pitch_speed
        
        if self.isIDMoveEnabled():
            if installation.isLive():
                self.idpvs['vel'].caput(self._id_gap_speed)
            else:
                self.idcontrols['gap'].speed = self._id_gap_speed 
        
        if self.isPGMMoveEnabled():
            if self.getGratingMoveDirectionPositive():
                if self.verbose: self.logger.info('startMove PGM Grating Pitch: asynchronousMoveTo(%r) @ %r (+ve)' % (
                                                        (self._grat_pitch_end + self._pgm_runupdown)*1000., self._pgm_grat_pitch_speed))
                self._pgm_grat_pitch.asynchronousMoveTo((self._grat_pitch_end + self._pgm_runupdown)*1000.)
            else:
                if self.verbose: self.logger.info('startMove PGM Grating Pitch: asynchronousMoveTo(%r) @ %r (-ve)' % (
                                                        (self._grat_pitch_end - self._pgm_runupdown)*1000., self._pgm_grat_pitch_speed))
                self._pgm_grat_pitch.asynchronousMoveTo((self._grat_pitch_end - self._pgm_runupdown)*1000.)
                
        if self.isIDMoveEnabled():
            sleep(self.getIDStartDelayTime())
            if self.getIDGapMoveDirectionPositive():
                if self.verbose: self.logger.info('startMove ID Gap: asynchronousMoveTo(%r) @ %r (+ve)' % (
                                                        (self._id_gap_end + 0.05 + self._id_gap_runupdown), self._id_gap_speed))
                self.idcontrols['gap'].asynchronousMoveTo((self._id_gap_end + 0.05 + self._id_gap_runupdown))
            else:
                if self.verbose: self.logger.info('startMove ID Gap: asynchronousMoveTo(%r) @ %r (-ve)' % (
                                                        (self._id_gap_end - 0.05 - self._id_gap_runupdown), self._id_gap_speed))
                self.idcontrols['gap'].asynchronousMoveTo((self._id_gap_end - 0.05 - self._id_gap_runupdown))

        self.continuousMovingStarted = True
        if self.verbose: self.logger.info('...startMove')

    def isMoving(self):
        if self.isIDMoveEnabled():
            if self.verbose and (datetime.now() - self._movelog_time) > timedelta(seconds=1):
                self.logger.info('isMoving() _pgm_grat_pitch=%r @ %r, _pgm_mirr_pitch=%r @ %r, _id_gap=%r @ %r, _id_energy=%r @ %r' % (
                    self._pgm_grat_pitch.isBusy(), self._pgm_grat_pitch(),
                    self._pgm_mirr_pitch.isBusy(), self._pgm_mirr_pitch(),
                    self.idcontrols['gap'].isBusy(), self.idcontrols['gap'](),
                    self.energy.isIDBusy(self.idcontrols), self.energy()))
                self._movelog_time = datetime.now()
            return self._pgm_grat_pitch.isBusy() or self._pgm_mirr_pitch.isBusy() or self.idcontrols['gap'].isBusy() or self.energy.isIDBusy(self.idcontrols)
        else:
            if self.verbose and (datetime.now() - self._movelog_time) > timedelta(seconds=1):
                self.logger.info('isMoving() _pgm_grat_pitch=%r @ %r, _pgm_mirr_pitch=%r @ %r' % (
                    self._pgm_grat_pitch.isBusy(), self._pgm_grat_pitch(),
                    self._pgm_mirr_pitch.isBusy(), self._pgm_mirr_pitch()))
                self._movelog_time = datetime.now()
            return self._pgm_grat_pitch.isBusy() or self._pgm_mirr_pitch.isBusy()
            

    def waitWhileMoving(self):
        if self.verbose: self.logger.info('waitWhileMoving()...')
        while self.isMoving():
            time.sleep(1)
        if self.verbose: self.logger.info('...waitWhileMoving()')

    def stopAndReset(self):
        if self.verbose: self.logger.info('stopAndReset()...')
        self._start_time = None
        self._start_event.clear()
        if self.isPGMMoveEnabled():
            self._pgm_grat_pitch.stop()
            self._pgm_mirr_pitch.stop()
        if self.isIDMoveEnabled() and installation.isDummy() and self.idcontrols:
            # real ID hardware does not support stop method!
            self.idcontrols['gap'].stop()
        self._restore_orig_speed()

    # Implement: public interface HardwareTriggerProvider extends Device

    def setTriggerPeriod(self, seconds): # double
        self._triggerPeriod = seconds
        if self.verbose: self.logger.info('setTriggerPeriod(%r)' % seconds)

    def getNumberTriggers(self):
        triggers = self.getTotalMove() / abs(self._move_step)
        if self.verbose: self.logger.info('getNumberTriggers()=%r (%r)' % (int(triggers), triggers))
        return int(triggers)

    def getTotalTime(self):
        total_time = self.getNumberTriggers() * self._triggerPeriod
        if self.verbose: self.logger.info('getTotalTime()=%r' % total_time)
        return total_time

    def getTimeToVelocity(self):
        return self._pgm_runupdown_time

    # Override: public abstract class DeviceBase implements Device, ConditionallyConfigurable, Localizable

        # None needed

    # Other functions

    def getTotalMove(self):
        total_move = abs(self._move_end - self._move_start)
        if self.verbose: self.logger.info('getTotalMove()=%r' % total_move)
        return total_move

    def getGratingMoveDirectionPositive(self):
        return (self._grat_pitch_end - self._grat_pitch_start) > 0

    def getIDGapMoveDirectionPositive(self):
        return (self._id_gap_end - self._id_gap_start) > 0

    class DelayableCallable(Callable):
    
        def __init__(self, controller, demand_position):
            #self.start_event = threading.Event()
            self.start_event = controller._start_event
            self._controller, self._demand_position = controller, demand_position
            self.logger = LoggerFactory.getLogger("ContinuousPgmGratingIDGapEnergyMoveController:%s:DelayableCallable[%r]" % (controller.name, demand_position))
            if self._controller.verbose:
                self.logger.info('__init__(%r, %r)...' % (controller.name, demand_position))
    
        def call(self):
            if self._controller.verbose: self.logger.info('call...')
            # Wait for controller to start all motors moving and set start time
            if self._controller._start_time:
                if self._controller.verbose: self.logger.info('start_time=%r' % (self._controller._start_time))
            else:
                if self._controller.verbose: self.logger.info('wait()...')
                timeout=60
                self.start_event.wait(timeout)
                if not self.start_event.isSet():
                    raise RuntimeError("%rs timeout waiting for startMove() to be called on %s at position %r." % (timeout, self._controller.name, self._demand_position))
                if self._controller.verbose: self.logger.info('...wait()')
            # Wait for delay before actually move start and then a time given by
            # how far through the scan this point is
            
            grat_pitch = enemirror2grating(gd     = self._controller.grating_density,
                                           energy = self._demand_position,
                                           pmang  = self._controller.mirr_pitch_midpoint,
                                           groff  = self._controller.grating_offset,
                                           pmoff  = self._controller.plane_mirror_offset,
                                           ecg    = self._controller.energy_calibration_gradient,
                                           ecr    = self._controller.energy_calibration_reference)
            
            complete = abs( (grat_pitch - self._controller._grat_pitch_start) /
                            (self._controller._grat_pitch_end - self._controller._grat_pitch_start) )
            sleeptime_s = (self._controller._pgm_runupdown_time + (complete * self._controller.getTotalTime()))
            
            delta = datetime.now() - self._controller._start_time
            delta_s = delta.seconds + delta.microseconds/1000000.
            if delta_s > sleeptime_s:
                self.logger.warn('Sleep time already past!!! sleeptime_s=%r, delta_s=%r, sleeptime_s-delta_s=%r' % (sleeptime_s, delta_s, sleeptime_s-delta_s))
            else:
                if self._controller.verbose:
                    self.logger.info('sleeping... sleeptime_s=%r, delta_s=%r, sleeptime_s-delta_s=%r' % (sleeptime_s, delta_s, sleeptime_s-delta_s))
                time.sleep(sleeptime_s-delta_s)
            
            energy = angles2energy(gd       = self._controller.grating_density,
                                   grang    = self._controller._pgm_grat_pitch()/1000.,
                                   pmang    = self._controller._pgm_mirr_pitch()/1000.,
                                   groff    = self._controller.grating_offset,
                                   pmoff    = self._controller.plane_mirror_offset,
                                   ecg      = self._controller.energy_calibration_gradient,
                                   ecr      = self._controller.energy_calibration_reference)
            if self._controller.verbose:
                self.logger.info('...DelayableCallable:call returning %r, %r' % (self._demand_position, energy))
            return self._demand_position, energy

    def getPositionCallableExtraNames(self):
        return ['readback']

    def getPositionCallableFormat(self):
        return ['%f', '%f']

    # public Callable<T> getPositionCallable() throws DeviceException;
    def getPositionCallableFor(self, position):
        if self.verbose: self.logger.info('getPositionCallableFor(%r)...' % position)
        # TODO: return actual positions back calculated from energy positions
        return self.DelayableCallable(self, position)

    def _restore_orig_speed(self):
        if self.isPGMMoveEnabled() and self._pgm_grat_pitch_speed_orig:
                if self.verbose: self.logger.info('Restoring original PGM Grating Pitch speed %r, was %r' % (self._pgm_grat_pitch_speed_orig, self._pgm_grat_pitch.speed))
                self._pgm_grat_pitch.speed = self._pgm_grat_pitch_speed_orig
                self._pgm_grat_pitch_speed_orig = None
        if self.isIDMoveEnabled() and self._id_gap_speed_orig:
                if installation.isLive() and self.continuousMovingStarted:
                    while self.idcontrols['gap'].isBusy():
                        sleep(0.5)
                    if self.verbose: self.logger.info('Restoring original ID gap speed %r, was %r' % (self._id_gap_speed_orig, self.idpvs['vel'].caget()))
                    self.idpvs['vel'].caput(self._id_gap_speed_orig)
                else:
                    if self.verbose: self.logger.info('Restoring original ID gap speed %r, was %r' % (self._id_gap_speed_orig, self.idcontrols['gap'].speed))
                    self.idcontrols['gap'].speed = self._id_gap_speed_orig 
                self._id_gap_speed_orig = None

    def atScanEnd(self):
        if self.verbose: self.logger.info('atScanEnd()...')
        self._restore_orig_speed()
        if self.continuousMovingStarted:
            print("cvscan completed.")
#         self._pgm_grat_pitch.getController().setCollectingData(False)
        # Should we also move the pgm_energy to a known value too, such as the midpoint?

"""
Continuous Energy Scannable and Controller for using Constant Velocity on I10
for use with GDA at Diamond Light Source
"""

from datetime import datetime, timedelta
from gda.device import DeviceBase
from gda.device.continuouscontroller import ConstantVelocityMoveController
from gdascripts.scannable.epics.PvManager import PvManager
from java.util.concurrent import Callable
from org.slf4j import LoggerFactory
from pgm.pgm import angles2energy, enecff2mirror, enemirror2grating #, enecff2grating
import threading, time
import installation

class ContinuousPgmGratingEnergyMoveController(ConstantVelocityMoveController, DeviceBase):

    def __init__(self, name, pgm_grat_pitch, pgm_mirr_pitch, pgmpvroot): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("ContinuousPgmGratingEnergyMoveController:%s" % name)
        self.verbose = False
        
        self.name = name
        self._pgm_grat_pitch = pgm_grat_pitch
        self._pgm_mirr_pitch = pgm_mirr_pitch
        self._start_event = threading.Event()
        self._pgm_grat_pitch_speed_orig = None
        self._movelog_time = datetime.now()
        self._pgm_runupdown_time = None

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

        #pgm_energy                     = 712.300           # caget BL10I-OP-PGM-01:ENERGY
        #grating_pitch                  = 88.0151063265128  # caget -g15 BL10I-OP-PGM-01:GRT:PITCH
        #mirror_pitch                   = 88.2753263680692  # caget -g15 BL10I-OP-PGM-01:MIR:PITCH

        energy_calibration_gradient     = 1.0178            # caget BL10I-OP-PGM-01:MX
        energy_calibration_reference    = 392.555           # caget BL10I-OP-PGM-01:REFERENCE

        return grating_density, cff, grating_offset, plane_mirror_offset, energy_calibration_gradient, energy_calibration_reference

    def prepareForMove(self):
        if self.verbose: self.logger.info('prepareForMove()...')
        self._pgm_grat_pitch_speed_orig = self._pgm_grat_pitch.speed

        # Calculate the energy midpoint
        energy_midpoint = (self._move_end + self._move_start) / 2.
        if self.verbose: self.logger.info('prepareForMove:energy_midpoint=%r ' % (energy_midpoint))

        if installation.isLive():
            (self.grating_density, self.cff, self.grating_offset, self.plane_mirror_offset, self.energy_calibration_gradient,self.energy_calibration_reference) = self.getPgmEnergyParameters()
        else:
            (self.grating_density, self.cff, self.grating_offset, self.plane_mirror_offset, self.energy_calibration_gradient,self.energy_calibration_reference) = self.getPgmEnergyParametersFixed()
            
        # Calculate plane mirror angle for given grating density, energy, cff and offsets
        self.mirr_pitch_midpoint =   enecff2mirror(gd     = self.grating_density,
                                                   energy = energy_midpoint,
                                                   cff    = self.cff,
                                                   groff  = self.grating_offset,
                                                   pmoff  = self.plane_mirror_offset,
                                                   ecg    = self.energy_calibration_gradient,
                                                   ecr    = self.energy_calibration_reference)

        # Calculate grating angles for given grating density, energy, mirror angle and offsets
        self._grat_pitch_start = enemirror2grating(gd     = self.grating_density,
                                                   energy = self._move_start,
                                                   pmang  = self.mirr_pitch_midpoint,
                                                   groff  = self.grating_offset,
                                                   pmoff  = self.plane_mirror_offset,
                                                   ecg    = self.energy_calibration_gradient,
                                                   ecr    = self.energy_calibration_reference)

        self._grat_pitch_end   = enemirror2grating(gd     = self.grating_density,
                                                   energy = self._move_end,
                                                   pmang  = self.mirr_pitch_midpoint,
                                                   groff  = self.grating_offset,
                                                   pmoff  = self.plane_mirror_offset,
                                                   ecg    = self.energy_calibration_gradient,
                                                   ecr    = self.energy_calibration_reference)

        ### Calculate main cruise moves & speeds from start/end/step
        self._pgm_grat_pitch_speed = (abs(self._grat_pitch_end - self._grat_pitch_start) /
            self.getTotalTime())
        ### Calculate ramp distance from required speed and ramp times
        # Set the speed before we read out ramp times in case it is dependent
        self._pgm_grat_pitch.speed = self._pgm_grat_pitch_speed
        # Should really be / | | | | | \ not /| | | | |\
        self._pgm_runupdown_time = self._pgm_grat_pitch.timeToVelocity
        self._pgm_runupdown = self._pgm_grat_pitch_speed/2 * self._pgm_runupdown_time
        ### Move motor at full speed to start position
        if self.verbose: self.logger.info('prepareForMove:_pgm_mirr_pitch.asynchronousMoveTo(%r) @ %r ' % (
                                                self.mirr_pitch_midpoint*1000., self._pgm_mirr_pitch.speed))
        self._pgm_mirr_pitch.asynchronousMoveTo(self.mirr_pitch_midpoint*1000.)
        
        self._pgm_grat_pitch.speed = self._pgm_grat_pitch_speed_orig
        if self.getGratingMoveDirectionPositive():
            if self.verbose: self.logger.info('prepareForMove:asynchronousMoveTo(%r) @ %r (+ve)' % (
                                                    (self._grat_pitch_start - self._pgm_runupdown)*1000., self._pgm_grat_pitch_speed_orig))
            self._pgm_grat_pitch.asynchronousMoveTo((self._grat_pitch_start - self._pgm_runupdown)*1000.)
        else:
            if self.verbose: self.logger.info('prepareForMove:asynchronousMoveTo(%r) @ %r (-ve)' % (
                                                    (self._grat_pitch_start + self._pgm_runupdown)*1000., self._pgm_grat_pitch_speed_orig))
            self._pgm_grat_pitch.asynchronousMoveTo((self._grat_pitch_start + self._pgm_runupdown)*1000.)
        self.waitWhileMoving()
        ### Calculate trigger delays
        if self.verbose:
            self.logger.info('...prepareForMove')

    def startMove(self):
        if self.verbose: self.logger.info('startMove()...')
        
        # Notify all position callables to start waiting for their time
        self._start_time = datetime.now()
        self._start_event.set()
        # Start threads to start ID & PGM and at the correct times
        self._pgm_grat_pitch.speed = self._pgm_grat_pitch_speed
        if self.getGratingMoveDirectionPositive():
            if self.verbose: self.logger.info('startMove:asynchronousMoveTo(%r) @ %r (+ve)' % (
                                                    (self._grat_pitch_end + self._pgm_runupdown)*1000., self._pgm_grat_pitch_speed))
            self._pgm_grat_pitch.asynchronousMoveTo((self._grat_pitch_end + self._pgm_runupdown)*1000.)
        else:
            if self.verbose: self.logger.info('startMove:asynchronousMoveTo(%r) @ %r (-ve)' % (
                                                    (self._grat_pitch_end - self._pgm_runupdown)*1000., self._pgm_grat_pitch_speed))
            self._pgm_grat_pitch.asynchronousMoveTo((self._grat_pitch_end - self._pgm_runupdown)*1000.)
        # How do we trigger the detectors, since they are 'HardwareTriggerable'?
        if self.verbose: self.logger.info('...startMove')

    def isMoving(self):
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
        self._start_time = None
        self._start_event.clear()
        if self.verbose: self.logger.info('stopAndReset()')
        self._pgm_grat_pitch.stop()
        self._restore_orig_speed()

    # Implement: public interface HardwareTriggerProvider extends Device

    def setTriggerPeriod(self, seconds): # double
        self._triggerPeriod = seconds
        if self.verbose: self.logger.info('setTriggerPeriod(%r)' % seconds)

    def getNumberTriggers(self):
        triggers = self.getTotalMove() / self._move_step
        if self.verbose: self.logger.info('getNumberTriggers()=%r (%r)' % (int(triggers), triggers))
        return int(triggers)

    def getTotalTime(self):
        totalTime = self.getNumberTriggers() * self._triggerPeriod
        if self.verbose: self.logger.info('getTotalTime()=%r' % totalTime)
        return totalTime

    def getTimeToVelocity(self):
        return self._pgm_runupdown_time

    # Override: public abstract class DeviceBase extends ConfigurableBase implements Device

        # None needed

    # Other functions

    def getTotalMove(self):
        totalMove = abs(self._move_end - self._move_start)
        if self.verbose: self.logger.info('getTotalMove()=%r' % totalMove)
        return totalMove

    def getGratingMoveDirectionPositive(self):
        return (self._grat_pitch_end - self._grat_pitch_start) > 0

    class DelayableCallable(Callable):
    
        def __init__(self, controller, demand_position):
            #self.start_event = threading.Event()
            self.start_event = controller._start_event
            self._controller, self._demand_position = controller, demand_position
            self.logger = LoggerFactory.getLogger("ContinuousPgmGratingEnergyMoveController:%s:DelayableCallable[%r]" % (controller.name, demand_position))
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
                    raise Exception("%rs timeout waiting for startMove() to be called on %s at position %r." % (timeout, self._controller.name, self._demand_position))
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
            sleeptime_s = (self._controller._pgm_runupdown_time
                + (complete * self._controller.getTotalTime()))
            
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
        if self._pgm_grat_pitch_speed_orig:
            if self.verbose: self.logger.info('Restoring original speed %r, was %r' % (self._pgm_grat_pitch_speed_orig, self._pgm_grat_pitch.speed))
            self._pgm_grat_pitch.speed = self._pgm_grat_pitch_speed_orig
            self._pgm_grat_pitch_speed_orig = None

    def atScanEnd(self):
        if self.verbose: self.logger.info('atScanEnd()...')
        self._restore_orig_speed()
#         self._pgm_grat_pitch.getController().setCollectingData(False)
        # Should we also move the pgm_energy to a known value too, such as the midpoint?

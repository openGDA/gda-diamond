"""
Continuous Energy Scannable and Controller for using Constant Velocity on I10
for use with GDA at Diamond Light Source
"""

from datetime import datetime, timedelta
from gda.device import DeviceBase
from gda.device.continuouscontroller import ConstantVelocityMoveController
from java.util.concurrent import Callable
from org.slf4j import LoggerFactory
import threading, time

class ContinuousPgmEnergyMoveController(ConstantVelocityMoveController, DeviceBase):

    def __init__(self, name, energy): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("ContinuousPgmEnergyMoveController:%s" % name)
        self.verbose = False
        
        self.name = name
        self._energy = energy
        self._start_event = threading.Event()
        self._energy_speed_orig = None
        self._movelog_time = datetime.now()
        self._pgm_runupdown_time = None

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

    def prepareForMove(self):
        if self.verbose: self.logger.info('prepareForMove()...')
        self._energy_speed_orig = self._energy.speed
        ### Calculate main cruise moves & speeds from start/end/step
        self._energy_speed = self.getTotalMove() / self.getTotalTime()
        ### Calculate ramp distance from required speed and ramp times
        # Set the speed before we read out ramp times in case it is dependent
        self._energy.speed = self._energy_speed 
        # Should really be / | | | | | \ not /| | | | |\
        self._pgm_runupdown_time = self._energy.timeToVelocity
        self._pgm_runupdown = self._energy_speed/2 * self._pgm_runupdown_time
        ### Move motor at full speed to start position
        self._energy.speed = self._energy_speed_orig
        if self.getMoveDirectionPositive():
            if self.verbose: self.logger.info('prepareForMove:asynchronousMoveTo(%r) @ %r (+ve)' % (
                                            self._move_start - self._pgm_runupdown, self._energy_speed_orig))
            self._energy.asynchronousMoveTo(self._move_start - self._pgm_runupdown)
        else:
            if self.verbose: self.logger.info('prepareForMove:asynchronousMoveTo(%r) @ %r (-ve)' % (
                                            self._move_start + self._pgm_runupdown, self._energy_speed_orig))
            self._energy.asynchronousMoveTo(self._move_start + self._pgm_runupdown)
        self.waitWhileMoving()
        ### Calculate trigger delays
        if self.verbose:
            self.logger.info('...End of prepareForMove')

    def startMove(self):
        if self.verbose: self.logger.info('startMove()...')
        
        # Notify all position callables to start waiting for their time
        self._start_time = datetime.now()
        self._start_event.set()
        # Start threads to start ID & PGM and at the correct times
        self._energy.speed = self._energy_speed
        if self.getMoveDirectionPositive():
            if self.verbose: self.logger.info('startMove:asynchronousMoveTo(%r) @ %r (+ve)' % (
                                            self._move_end + self._pgm_runupdown, self._energy_speed))
            self._energy.asynchronousMoveTo(self._move_end + self._pgm_runupdown)
        else:
            if self.verbose: self.logger.info('startMove:asynchronousMoveTo(%r) @ %r (-ve)' % (
                                            self._move_end - self._pgm_runupdown, self._energy_speed))
            self._energy.asynchronousMoveTo(self._move_end - self._pgm_runupdown)
        # How do we trigger the detectors, since they are 'HardwareTriggerable'?
        if self.verbose: self.logger.info('...End of startMove')

    def isMoving(self):
        if self.verbose and (datetime.now() - self._movelog_time) > timedelta(seconds=1):
            self.logger.info('isMoving()=%r @ %r' % (self._energy.isBusy(), self._energy()))
            self._movelog_time = datetime.now()
        return self._energy.isBusy()

    def waitWhileMoving(self):
        if self.verbose: self.logger.info('waitWhileMoving()...')
        while self.isMoving():
            time.sleep(1)
        if self.verbose: self.logger.info('...waitWhileMoving()')

    def stopAndReset(self):
        self._start_time = None
        self._start_event.clear()
        if self.verbose: self.logger.info('stopAndReset()')
        self._energy.stop()
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

    def getMoveDirectionPositive(self):
        return (self._move_end - self._move_start) > 0

    class DelayablePgmEnergyPositionCallable(Callable):
    
        def __init__(self, controller, demand_position):
            #self.start_event = threading.Event()
            self.start_event = controller._start_event
            self._controller, self._demand_position = controller, demand_position
            self.logger = LoggerFactory.getLogger("ContinuousPgmEnergyMoveController:%s:DelayablePgmEnergyPositionCallable[%r]" % (controller.name, demand_position))
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
            complete = abs( (self._demand_position - self._controller._move_start) /
                            (self._controller._move_end - self._controller._move_start) )
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
            position_rbv = self._controller._energy()
            if self._controller.verbose:
                self.logger.info('...DelayableCallable:call returning %r, %r' % (self._demand_position, position_rbv))
            return self._demand_position, position_rbv

    def getPositionCallableExtraNames(self):
        return ['readback']

    def getPositionCallableFormat(self):
        return ['%f', '%f']

    # public Callable<T> getPositionCallable() throws DeviceException;
    def getPositionCallableFor(self, position):
        if self.verbose: self.logger.info('getPositionCallableFor(%r)...' % position)
        # TODO: return actual positions back calculated from energy positions
        return self.DelayablePgmEnergyPositionCallable(self, position)

    def _restore_orig_speed(self):
        if self._energy_speed_orig:
            if self.verbose: self.logger.info('Restoring original speed %r, was %r' % (self._energy_speed_orig, self._energy.speed))
            self._energy.speed = self._energy_speed_orig
            self._energy_speed_orig = None

    def atScanEnd(self):
        if self.verbose: self.logger.info('atScanEnd()...')
        self._restore_orig_speed()

"""
Continuous Energy Scannable and Controller for using Constant Velocity on I10
for use with GDA at Diamond Light Source
"""

from datetime import datetime
from gda.device import DeviceBase
from gda.device.continuouscontroller import ConstantVelocityMoveController
from gda.device.scannable import ContinuouslyScannableViaController, \
    ScannableMotionBase, PositionCallableProvider
from java.util.concurrent import Callable
import threading, time


class ContinuousEnergyMoveController(ConstantVelocityMoveController, DeviceBase):

    def __init__(self, name, energy): # motors, maybe also detector to set the delay time
        self.name = name
        self._energy = energy
        self._start_event = threading.Event()

    # Implement: public interface ConstantVelocityMoveController extends ContinuousMoveController

    def setStart(self, start): # double
        self._move_start = start
        print str(datetime.now()), self.name, 'start=', start

    def setEnd(self, end): # double
        self._move_end = end
        print str(datetime.now()), self.name, 'end=', end

    def setStep(self, step): # double
        self._move_step = step
        print str(datetime.now()), self.name, 'step=', step

    # Implement: public interface ContinuousMoveController extends HardwareTriggerProvider

    def prepareForMove(self):
        print str(datetime.now()), self.name, 'prepareForMove...'
        self._energy_speed_orig = self._energy.speed
        ### Calculate main cruise moves & speeds from start/end/step
        self._energy_speed = self.getTotalMove() / self.getTotalTime()
        ### Calculate ramp distance from required speed and ramp times
        # Set the speed before we read out ramp times in case it is dependent
        self._energy.speed = self._energy_speed 
        # Should really be / | | | | | \ not /| | | | |\
        self._runupdown = self._energy_speed/2 * self._energy.timeToVelocity
        ### Move ID at full speed to start position
        ### Move pgm at full speed to start position
        self._energy.speed = self._energy_speed_orig
        if self.getMoveDirectionPositive():
            print str(datetime.now()), self.name, 'asynchronousMoveTo(%r)' % (
                                            self._move_start - self._runupdown)
            self._energy.asynchronousMoveTo(self._move_start - self._runupdown)
        else:
            print str(datetime.now()), self.name, 'asynchronousMoveTo(%r)' % (
                                            self._move_start + self._runupdown)
            self._energy.asynchronousMoveTo(self._move_start + self._runupdown)
        self.waitWhileMoving()
        ### Calculate trigger delays
        print str(datetime.now()), self.name, '...prepareForMove'

    def startMove(self):
        print str(datetime.now()), self.name, 'startMove...'
        
        # Notify all position callables to start waiting for their time
        self._start_time = datetime.now()
        self._start_event.set()
        # Start threads to start ID & PGM and at the correct times
        self._energy.speed = self._energy_speed
        if self.getMoveDirectionPositive():
            print str(datetime.now()), self.name, 'asynchronousMoveTo(%r)' % (
                                            self._move_end + self._runupdown)
            self._energy.asynchronousMoveTo(self._move_end + self._runupdown)
        else:
            print str(datetime.now()), self.name, 'asynchronousMoveTo(%r)' % (
                                            self._move_end - self._runupdown)
            self._energy.asynchronousMoveTo(self._move_end - self._runupdown)
        # How do we trigger the detectors, since they are 'HardwareTriggerable'?
        print str(datetime.now()), self.name, '...startMove'

    def isMoving(self):
        print str(datetime.now()), self.name, 'isMoving'
        return self._energy.isBusy()

    def waitWhileMoving(self):
        print str(datetime.now()), self.name, 'waitWhileMoving...'
        while self.isMoving():
            time.sleep(1)
        print str(datetime.now()), self.name, '...waitWhileMoving'

    def stopAndReset(self):
        self._start_time = None
        self._start_event.clear()
        print str(datetime.now()), self.name, 'stopAndReset'

    # Implement: public interface HardwareTriggerProvider extends Device

    def setTriggerPeriod(self, seconds): # double
        self._triggerPeriod = seconds
        print str(datetime.now()), self.name, 'setTriggerPeriod(%r)' % seconds

    def getNumberTriggers(self):
        triggers = self.getTotalMove() / self._move_step
        print str(datetime.now()), self.name, 'getNumberTriggers=', triggers, int(triggers)
        return int(triggers)

    def getTotalTime(self):
        return self.getNumberTriggers() * self._triggerPeriod

    # Override: public abstract class DeviceBase implements Device, ConditionallyConfigurable, Localizable

        # None needed

    # Other functions

    def getTotalMove(self):
        return abs(self._move_end - self._move_start)

    def getMoveDirectionPositive(self):
        return (self._move_end - self._move_start) > 0

    class DelayableEnergyPositionCallable(Callable):
    
        def __init__(self, controller, demand_position):
            self._controller, self._demand_position = controller, demand_position
            print str(datetime.now()), self._controller.name, self._demand_position, 'DelayableCallable:__init__(%r, %r)...' % (controller.name, demand_position)
    
        def call(self):
            print str(datetime.now()), self._controller.name, self._demand_position, 'DelayableCallable:call...'
            # Wait for controller to start all motors moving and set start time
            if self._controller._start_time:
                print str(datetime.now()), self._controller.name, self._demand_position, 'start_time=', self._controller._start_time
            else:
                print str(datetime.now()), self._controller.name, self._demand_position, 'wait()...'
                self._controller._start_event.wait(60)
                print str(datetime.now()), self._controller.name, self._demand_position, '...wait()' #, self._controller._start_event.is_set()
            # Wait for delay before actually move start and then a time given by
            # how far through the scan this point is
            complete = abs( (self._demand_position - self._controller._move_start) /
                            (self._controller._move_end - self._controller._move_start) )
            sleeptime_s = (self._controller._energy.timeToVelocity
                + (complete * self._controller.getTotalTime()))
            
            delta = datetime.now() - self._controller._start_time
            delta_s = delta.seconds + delta.microseconds/1000000.
            if delta_s > sleeptime_s:
                print str(datetime.now()), self._controller.name, self._demand_position, 'sleep time already past!!!'
            else:
                print str(datetime.now()), self._controller.name, self._demand_position, 'sleeping...', sleeptime_s, delta_s, sleeptime_s-delta_s
                time.sleep(sleeptime_s-delta_s)
            print str(datetime.now()), self._controller.name, self._demand_position, '...DelayableCallable:call'
            return self._controller._energy()

    # public Callable<T> getPositionCallable() throws DeviceException;
    def getPositionCallableFor(self, position):
        print str(datetime.now()), self.name, ':getPositionCallableFor(%r)...' % position
        # TODO: return actual positions back calculated from energy positions
        return self.DelayableEnergyPositionCallable(self, position)

    def atScanEnd(self):
        print str(datetime.now()), self.name, ':atScanEnd...'
        self._energy.speed = self._energy_speed_orig


class ContinuousEnergyScannable(ContinuouslyScannableViaController, ScannableMotionBase, PositionCallableProvider):

    def __init__(self, name, controller):
        self.name = name
        self._controller = controller
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%f']
        self._operating_continuously = False
        self._last_requested_position = None

    # Implement: public interface ContinuouslyScannableViaController extends Scannable

    def setOperatingContinuously(self, b):
        self._operating_continuously = b

    def isOperatingContinously(self):
        return self._operating_continuously

    def getContinuousMoveController(self):
        return self._controller

    # Implement: public interface PositionCallableProvider<T> {

    # public Callable<T> getPositionCallable() throws DeviceException;
    def getPositionCallable(self):
        print str(datetime.now()), self.name, ':getPositionCallable...'
        return self._controller.getPositionCallableFor(self._last_requested_position)

    # Override: public class ScannableMotionBase extends ScannableBase implements ScannableMotion, INeXusInfoWriteable

    def asynchronousMoveTo(self, position):
        print str(datetime.now()), self.name, ':asynchronousMoveTo(%r)...' % position
        position = float(position)
        if self._operating_continuously:
            self._last_requested_position = position
        else:
            raise Exception()

    def getPosition(self):
        print str(datetime.now()), self.name, ':getPosition...'
        if self._operating_continuously:
            raise Exception()
            # Should be using getPositionCallable
            #return self._last_requested_position
        else:
            raise Exception()

    def waitWhileBusy(self):
        print str(datetime.now()), self.name, ':waitWhileBusy...'
        if self._operating_continuously:
            return # self._controller.waitWhileMoving()
        else:
            raise Exception()

    def isBusy(self):
        if self._operating_continuously:
            return False #self._controller.isBusy()
        else:
            raise Exception()

    # public interface ScannableMotion extends Scannable

    # Override: public interface Scannable extends Device

    def atScanEnd(self):
        if self._operating_continuously:
            self._controller.atScanEnd()
        else:
            raise Exception()
        """ Why is this being called? See:

2013-06-18 18:14:04,094 INFO  gda.jython.logger.RedirectableFileLogger -  | 2013-06-18 18:14:04.094000  
2013-06-18 18:14:04,095 INFO  gda.jython.logger.RedirectableFileLogger -  |  mcs1  
2013-06-18 18:14:04,096 INFO  gda.jython.logger.RedirectableFileLogger -  |  atScanLineEnd  
2013-06-18 18:14:04,100 INFO  gda.jython.logger.RedirectableFileLogger -  | Traceback (most recent call last):  
2013-06-18 18:14:04,101 INFO  gda.jython.logger.RedirectableFileLogger -  |   File "<input>", line 1, in <module>  
2013-06-18 18:14:04,101 INFO  gda.jython.logger.RedirectableFileLogger -  |   File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/concurrentScanWrapper.py", line 151, in __call__  
2013-06-18 18:14:04,102 INFO  gda.jython.logger.RedirectableFileLogger -  |     scan.runScan()  
2013-06-18 18:14:04,103 INFO  gda.jython.logger.RedirectableFileLogger -  |   File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/concurrentScanWrapper.py", line 151, in __call__  
2013-06-18 18:14:04,103 INFO  gda.jython.logger.RedirectableFileLogger -  |     scan.runScan()  
2013-06-18 18:14:04,104 INFO  gda.jython.logger.RedirectableFileLogger -  |   File "/dls_sw/i10/software/gda/i10-config/scripts/scannable/continuous/energy.py", line 236, in atScanEnd  
2013-06-18 18:14:04,104 INFO  gda.jython.logger.RedirectableFileLogger -  |     raise Exception()  
2013-06-18 18:14:04,105 INFO  gda.jython.logger.RedirectableFileLogger -  | Exception  
2013-06-18 18:14:04,108 ERROR gda.jython.GDAInteractiveConsole - InteractiveConsole exception: Traceback (most recent call last):
  File "<input>", line 1, in <module>
  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/concurrentScanWrapper.py", line 151, in __call__
    scan.runScan()
  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/concurrentScanWrapper.py", line 151, in __call__
    scan.runScan()
  File "/dls_sw/i10/software/gda/i10-config/scripts/scannable/continuous/energy.py", line 236, in atScanEnd
    raise Exception()
Exception
 org.python.core.PyException
    at org.python.core.PyException.doRaise(PyException.java:219)
"""

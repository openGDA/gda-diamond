"""
Continuous Energy Scannable and Controller for using Constant Velocity on I10
for use with GDA at Diamond Light Source
"""

from gda.device import DeviceBase
from gda.device.continuouscontroller import ConstantVelocityMoveController
from gda.device.scannable import ContinuouslyScannableViaController, \
    ScannableMotionBase, PositionCallableProvider
from java.util.concurrent import Callable
import time


class ContinuousEnergyMoveController(ConstantVelocityMoveController, DeviceBase):

#    def __init__(self): # motors, maybe also detector to set the delay time
#        self.move_start = 0
#        self._end = None
#        self._step = None

    # Implement: public interface ConstantVelocityMoveController extends ContinuousMoveController

    def setStart(self, start): # double
        self.move_start = start
        print 'start=', start

    def setEnd(self, end): # double
        self._end = end
        print 'end=', end

    def setStep(self, step): # double
        self._step = step
        print 'step=', step

    # Implement: public interface ContinuousMoveController extends HardwareTriggerProvider

    def prepareForMove(self):
        print 'prepareForMove'

    def startMove(self):
        print 'startMove'

    def isMoving(self):
        print 'isMoving'
        return False

    def waitWhileMoving(self):
        print 'waitWhileMoving...'
        time.sleep(5)
        print '...waitWhileMoving'

    def stopAndReset(self):
        print 'stopAndReset'

    # Implement: public interface HardwareTriggerProvider extends Device

    def setTriggerPeriod(self, seconds): # double
        self._triggerPeriod = seconds
        print 'seconds=', seconds

    def getNumberTriggers(self):
        triggers = (self._end-self.move_start) / self._step
        print 'getNumberTriggers=', triggers, int(triggers)
        return int(triggers)

    def getTotalTime(self):
        return self.getNumberTriggers() * self._triggerPeriod

    # Override: public abstract class DeviceBase implements Device, ConditionallyConfigurable, Localizable


class NoddyCallable(Callable):

    def __init__(self, val):
        self.val = val

    def call(self):
        return self.val


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
        # TODO: return actual positions back calculated from energy positions
        return NoddyCallable(self._last_requested_position * 2)

    # Override: public class ScannableMotionBase extends ScannableBase implements ScannableMotion, INeXusInfoWriteable

    def asynchronousMoveTo(self, position):
        position = float(position)
        if self._operating_continuously:
            self._last_requested_position = position
        else:
            raise Exception()

    def getPosition(self):
        if self._operating_continuously:
            raise Exception()
            # Should be using getPositionCallable
            #return self._last_requested_position
        else:
            raise Exception()

    def waitWhileBusy(self):
        if self._operating_continuously:
            return # self._controller.waitWhileMoving()
        else:
            raise Exception()

    def isBusy(self):
        if self._operating_continuously:
            return False #self._controller.isBusy()
        else:
            raise Exception()

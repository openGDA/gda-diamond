"""
Continuous Energy Scannable and Controller for using Constant Velocity on I10
for use with GDA at Diamond Light Source
"""

from datetime import datetime
from gda.device.scannable import ContinuouslyScannableViaController, \
    ScannableMotionBase, PositionCallableProvider
from org.slf4j import LoggerFactory

class ContinuousPgmEnergyScannable(ContinuouslyScannableViaController, ScannableMotionBase, PositionCallableProvider):

    def __init__(self, name, controller):
        self.name = name
        self._controller = controller
        self.inputNames = [name]
        self.extraNames = controller.getPositionCallableExtraNames()
        self.outputFormat = controller.getPositionCallableFormat()
        self._operating_continuously = False
        self._last_requested_position = None
        self.logger = LoggerFactory.getLogger("ContinuousPgmEnergyScannable:%s" % name)
        self.verbose = False
    # Implement: public interface ContinuouslyScannableViaController extends Scannable

    def setOperatingContinuously(self, b):
        if self.verbose:
            self.logger.info('setOperatingContinuously(%r) was %r' % (b, self._operating_continuously))
        self._operating_continuously = b

    def isOperatingContinously(self):
        return self._operating_continuously

    def getContinuousMoveController(self):
        return self._controller

    # Implement: public interface PositionCallableProvider<T> {

    # public Callable<T> getPositionCallable() throws DeviceException;
    def getPositionCallable(self):
        if self.verbose:
            self.logger.info('getPositionCallable()... last_requested_position=%r' % (
                                                       self._last_requested_position))
        return self._controller.getPositionCallableFor(self._last_requested_position)

    # Override: public class ScannableMotionBase extends ScannableBase implements ScannableMotion, INeXusInfoWriteable

    def asynchronousMoveTo(self, position):
        if self.verbose:
            self.logger.info('asynchronousMoveTo(%r)...' % position)
        position = float(position)
        if self._operating_continuously:
            self._last_requested_position = position
        else:
            raise Exception()

    def getPosition(self):
        if self.verbose:
            self.logger.info('getPosition()...')
        if self._operating_continuously:
            raise Exception()
            # Should be using getPositionCallable
            #return self._last_requested_position
        else:
            raise Exception()

    def waitWhileBusy(self):
        if self.verbose:
            self.logger.info('waitWhileBusy()...')
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

    # Note that neither stop() nor atCommandFailure() are called when operatingContinuously, however stopAndReset()
    # is called on the controller, so the controller needs to handle failures there.
    
    # We do need an atScanEnd() though, since unlike stop() and atCommandFailure(), stopAndReset() isn't called
    # when the scan line completes.
    def atScanEnd(self):
        if self.verbose: self.logger.info('atScanEnd()... _operating_continuously=%r' % self._operating_continuously)
        if self._operating_continuously:
            self._controller.atScanEnd()
        else:
            #raise Exception()
            self._controller.atScanEnd()
        """ Note, self._operating_continuously is being set back to false before atScanEnd is being called. See:
2015-02-04 21:43:26,833 INFO  ContinuousPgmEnergyScannable:egy - setOperatingContinuously(1) was 0
...
2015-02-04 21:43:27,048 INFO  ContinuousPgmEnergyScannable:egy - asynchronousMoveTo(841)...  
2015-02-04 21:43:27,048 INFO  ContinuousPgmEnergyScannable:egy - waitWhileBusy()...  
2015-02-04 21:43:27,048 INFO  ContinuousPgmEnergyScannable:egy - waitWhileBusy()...  
2015-02-04 21:43:27,048 INFO  ContinuousPgmEnergyScannable:egy - getPositionCallable()... last_requested_position=841.0  
...
2015-02-04 21:30:53,128 INFO  ContinuousPgmEnergyScannable:egy - setOperatingContinuously(0) was 1
2015-02-04 21:30:53,128 INFO  ContinuousPgmEnergyScannable:egy - atScanEnd()... _operating_continuously=0
"""
"""
Continuous Thp Scannable and Controller for using Constant Velocity on I10
for use with GDA at Diamond Light Source
"""

from gda.device.scannable import ContinuouslyScannableViaController, \
    ScannableMotionBase, PositionCallableProvider
from java.util.concurrent import Callable
from org.slf4j import LoggerFactory
from pgm.pgm import angles2energy

""" This scannable uses the motor controller to just control the motor and calculates the
    actual position from the position callables provided by the specified pitch motors.
"""
class ContinuousMoveThpBinpointScannable(ContinuouslyScannableViaController, ScannableMotionBase, PositionCallableProvider):
    """ Since the binpoints are slaved from a multi channel scaler card, motion will fail if the
        no scaler channels are specified in the scan.
        
        Also, since this scannable takes over starting the binpoint mecahnism, it may not work if
        individual binpoint scannables are added to the scan. """

    def __init__(self, name, move_controller, binpointThp):
        self.logger = LoggerFactory.getLogger("ContinuousMovePgmEnergyBinpointScannable:%s" % name)
        self.verbose = False
        
        self.name = name
        #from gda.device.continuouscontroller import ConstantVelocityMoveController
        #self._move_controller = ConstantVelocityMoveController() # Enable completion of interface methods
        #self._binpointThp = PositionCallableProvider() # Enable completion of interface methods
        #self._binpointThp = ScannableMotionBase()      # Enable completion of class methods

        self._move_controller = move_controller
        self._binpointThp = binpointThp

        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%f']

        self._operating_continuously = False
        self._last_requested_position = None

    # Implement: public interface ContinuouslyScannableViaController extends Scannable

    def setOperatingContinuously(self, b):
        if self.verbose: self.logger.info('setOperatingContinuously(%r) was %r' % (b, self._operating_continuously))
        self._operating_continuously = b

    def isOperatingContinously(self):
        return self._operating_continuously

    def getContinuousMoveController(self):
        return self._move_controller

    # Implement: public interface PositionCallableProvider<T> {

    # public Callable<T> getPositionCallable() throws DeviceException;
    def getPositionCallable(self):
        if self.verbose: self.logger.info('getPositionCallable()... last_requested_position=%r' % (
                                               self._last_requested_position))
        return self._binpointThp.getPositionCallable()
        # Note that we use the binpoint mechanism to get the actual positions of the motor at each point.

    # Override: public class ScannableMotionBase extends ScannableBase implements ScannableMotion, INeXusInfoWriteable

    def asynchronousMoveTo(self, position):
        if self.verbose: self.logger.info('asynchronousMoveTo(%r)...' % position)
        position = float(position)
        if self._operating_continuously:
            self._last_requested_position = position
        else:
            raise Exception("asynchronousMoveTo only supports Continuous operation")

    def atScanLineStart(self):
        if self.verbose: self.logger.info('atScanLineStart()...')
        self._binpointThp.atScanLineStart()
        self._binpointThp.collectData()

    def atScanLineEnd(self):
        if self.verbose: self.logger.info('atScanLineEnd()...')
        self._binpointThp.atScanLineEnd()
        # TODO: This race condition should be fixed in gda-8.44
        # There is a race condition here, where if the motion completes before all position callables
        # have been returned, the detector will be told to shut down.

    def getPosition(self):
        if self.verbose: self.logger.info('getPosition()...')
        if self._operating_continuously:
            raise Exception("getPosition not supported during continuous operation")
        else:
            raise Exception("getPosition only supports continuous operation")

    def waitWhileBusy(self):
        if self.verbose: self.logger.info('waitWhileBusy()...')
        if self._operating_continuously:
            return # self._move_controller.waitWhileMoving()
        else:
            raise Exception("waitWhileBusy only supports continuous operation")

    def isBusy(self):
        if self._operating_continuously:
            return False #self._move_controller.isBusy()
        else:
            raise Exception("isBusy only supports continuous operation")

    # public interface ScannableMotion extends Scannable

    # Override: public interface Scannable extends Device

    # Note that neither stop() nor atCommandFailure() are called when operatingContinuously, however stopAndReset()
    # is called on the move_controller, so the move_controller needs to handle failures there.
    
    # We do need an atScanEnd() though, since unlike stop() and atCommandFailure(), stopAndReset() isn't called
    # when the scan line completes.
    def atScanEnd(self):
        if self.verbose: self.logger.info('atScanEnd()... _operating_continuously=%r' % self._operating_continuously)
        if self._operating_continuously:
            self._move_controller.atScanEnd()
        else:
            #raise Exception()
            self._move_controller.atScanEnd()

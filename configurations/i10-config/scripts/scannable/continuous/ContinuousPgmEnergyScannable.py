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
        self.extraNames = []
        self.outputFormat = ['%f']
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

    def atScanEnd(self):
        if self.verbose: self.logger.info('atScanEnd()... _operating_continuously=%r' % self._operating_continuously)
        if self._operating_continuously:
            self._controller.atScanEnd()
        else:
            #raise Exception()
            self._controller.atScanEnd()
        """ Why is this being called? 
        
            It looks like self._operating_continuously is being set back to false before atScanEnd is being called!
        
        See:

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

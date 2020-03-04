#from datetime import datetime, timedelta
from gda.device import DeviceException
from gda.device.scannable import ScannableMotionBase, ScannableMotor
from gdascripts.messages.handle_messages import simpleLog
from java.lang import InterruptedException
import threading
from org.slf4j import LoggerFactory

class RockerScannable(ScannableMotionBase):
    """ This scannable needs to be configured with a call to setupScan before
        being used:

            <scn>.setupScan(scannable, delta, expectedRockTime, numberOfRockCyclesPerExposure)

        For example:

            pos phi 58
            rocker.setupScan(phi, 5, 10)
            pos rocker 10

        will configure kphi_rockscan to make two rocks, first between 58-4 and
        58+4 at a speed such that the moves take 10 seconds.
    """
    def __init__(self, name):
        self.logger = LoggerFactory.getLogger("RockerScannable:%s" % name)
        self.scannable=ScannableMotor()
        self.setName(name)
        self.setScannableOutputFormat("%3.3f")
        self.setLevel(8) # Highest level before default detector level 9
        self.thread=None
        self.delta=0
        self.numberOfRockCyclesPerExposure=0
        self.rockTime=0
        self.centre=0
        self.accl=0
        self.vmax=0
        self.waitingToStart = False

    def setupScan(self, scannable, delta, expectedRockTime, numberOfRockCyclesPerExposure=1):
        self.logger.info("setupScan({}, {}, {})", scannable, delta, numberOfRockCyclesPerExposure)

        if len(scannable.getInputNames()) <> 1 or len(scannable.getExtraNames()) <> 0 or len(scannable.getOutputFormat()) <> 1:
            self.logger.error("setupScan() scannable {} must have 1 input name and 0 extra names", self.scannable.name)
            raise Exception("Scannable must have 1 input name and 0 extra names")

        if self.thread and self.thread.running:
            self.logger.warn("setupScan() Thread already running on {}, waiting for completion...", self.scannable.name)
            self.thread.join()
            self.logger.info("setupScan() Thread completed", self.scannable.name)

        # Fail early based on various sanity checks
        scannable.setSpeed(scannable.getSpeed())
        self.accl = scannable.getTimeToVelocity()
        self.logger.info("setupScan() verified that %s can have speed set and has a TimeToVelocity()" % (scannable.name))
        simpleLog("Calculated speed of %s for delta %f and rock time %f as %f" % (scannable.name, delta,
            expectedRockTime, self.calcSpeed(scannable, delta, expectedRockTime, numberOfRockCyclesPerExposure)))

        # Don't set the variables until all preconditions met.
        self.setScannableOutputFormat(scannable.getOutputFormat()[0])
        self.numberOfRockCyclesPerExposure = numberOfRockCyclesPerExposure
        self.delta=delta
        self.scannable=scannable

    def atScanStart(self):
        self.logger.info("atScanStart() {}", self.scannable.name)
        if not self.scannable.getMotor(): # Early fail for scan
            self.logger.error("No scannable set! Run {}.setupScan() before scanning {}", self.name, self.name)
            raise Exception("No scannable set! Run %s.setupScan() before scanning %s" % (self.name, self.name))

    def asynchronousMoveTo(self, rockTime):
        self.waitingToStart = True
        self.rockTime = rockTime
        self.logger.info("asynchronousMoveTo({}) {}", rockTime, self.scannable.name)

        if not self.scannable.getMotor(): # Early fail for pos
            self.logger.error("No scannable set! Run {}.setupScan() before using {}", self.name, self.name)
            raise Exception("No scannable set! Run %s.setupScan() before using %s" % (self.name, self.name))

        if self.thread and self.thread.running:
            self.logger.info("asynchronousMoveTo({}) Thread already running, waiting to complete!", rockTime)
            self.thread.join()
            # TODO: This makes it non async

        vbefore = self.scannable.getSpeed()
        speed = self.calcSpeed(self.scannable, self.delta, rockTime, self.numberOfRockCyclesPerExposure)
        self.centre = self.scannable.getPosition()

        self.thread=RockerThread(self.name, self.scannable, self.delta, self.numberOfRockCyclesPerExposure,
                                 self.centre, rockTime, speed, vbefore, self)
        self.thread.start()
        self.waitingToStart = False

    def calcSpeed(self, scannable, delta, rockTime, numberOfRockCyclesPerExposure):
        accl = scannable.getTimeToVelocity()
        scannableMotor = scannable.getMotor()
        vmax = scannableMotor.getMaxSpeed()

        if numberOfRockCyclesPerExposure > 1:
            self.logger.warn("calcSpeed() numberOfRockCyclesPerExposure > 1 not supported yet, setting to 1")

        # Normal profile       ______            Degenerate profile (not supported)
        #               _     /      \     _                       _  /\
        #                \___/        \___/                         \/  \/
        #                1   23      45   6                         1 23 4
        cruiseTime = rockTime - accl*2*(2+numberOfRockCyclesPerExposure)

        if cruiseTime > 0:
            averageCruiseTime = cruiseTime + accl*(2+numberOfRockCyclesPerExposure) # We effectively move at half speed during accl
            speed = delta*4*numberOfRockCyclesPerExposure / averageCruiseTime
        else:
            self.logger.error("calcSpeed() rockTime {} is {} less than minimum rock time for {}",
                              rockTime, cruiseTime, scannable.name)
            raise Exception("rockTime %r is %r less than minimum rock time for %r" % (
                              rockTime, cruiseTime, scannable.name))

        if speed > vmax:
            self.logger.error("calcSpeed() Time {} results in a speed {} greater than max speed of {} on {}",
                              rockTime, speed, vmax, scannable.name)
            raise Exception("Time %r results in a speed %r greater than max speed of %r on %r" % (
                              rockTime, speed, vmax, scannable.name))
        return speed

    def isBusy(self):
        return self.waitingToStart

    def setScannableOutputFormat(self, scannableOutputFormat):
        self.setInputNames(["rockTime"])
        self.setExtraNames(["centre", "delta", "rocks", "running"])
        self.setOutputFormat(["%3.3f", scannableOutputFormat, "%3.3f", "%d", "%d"])

    def getPosition(self):
        if self.thread and self.thread.running:
            return self.thread.getPosition()
        return [ self.rockTime, self.centre, self.delta, self.numberOfRockCyclesPerExposure, 0 ]

    def stop(self):
        if self.thread:
            self.thread.running=False
        if self.scannable:
            self.scannable.stop()
            self.logger.info("stop() {}", self.scannable.name)

    def atScanEnd(self):
        self.logger.info("atScanEnd() {}", self.scannable.name)

class RockerThread(threading.Thread):

    def __init__(self, name, scannable, delta, numberOfRockCyclesPerExposure, centre, rockTime, speed, vbefore, parent):
        super(RockerThread, self).__init__()
        self.name = name
        self.scannable = scannable
        self.delta = delta
        self.numberOfRockCyclesPerExposure = numberOfRockCyclesPerExposure
        self.centre = centre
        self.rockTime = float(rockTime)
        self.speed = speed
        self.vbefore = vbefore
        self.parent = parent

        self.rockCount=0
        self.running = False

    def run(self):
        self.running = True

        self.parent.logger.info("Setting speed of {} to {}", self.scannable.name, self.speed)
        self.scannable.setSpeed(self.speed)

        # Single cycle   ______            2 cycles   ______          ______
        #         _     /      \     _         _     /      \        /      \     _
        #  /4      \___/        \___/       /8  \___/        \______/        \___/
        #          1   23      45   6           1   23      45      67      89   A

        halfRockTime = self.rockTime/(2+self.numberOfRockCyclesPerExposure)
        interrupted = False

        self.moveTo(    self.centre - self.delta, halfRockTime/2, interrupted)
        for _ in range(self.numberOfRockCyclesPerExposure-1):
            self.moveTo(self.centre + self.delta, halfRockTime,   interrupted)
            self.moveTo(self.centre - self.delta, halfRockTime,   interrupted)
            if not interrupted:
                self.rockCount+=1

        self.moveTo(    self.centre + self.delta, halfRockTime,   interrupted)
        self.moveTo(    self.centre,              halfRockTime/2, interrupted)

        if not interrupted:
            self.rockCount+=1

        self.parent.logger.info("Setting speed of {} back to {}", self.scannable.name, self.vbefore)
        self.scannable.setSpeed(self.vbefore)
        self.running = False

    def moveTo(self, position, timeout, interrupted):
        if interrupted:
            self.parent.logger.info("Move to {} ignored as previous move interrupted", position)
            return
        self.parent.logger.info("Start    moving {} to {} with timeout {} seconds", self.scannable.name, position, timeout)
        self.scannable.asynchronousMoveTo(position)
        try:
            self.scannable.waitWhileBusy(timeout);
            self.parent.logger.info("Finished moving {} to {} within timeout {} seconds", self.scannable.name, position, timeout)
        except DeviceException:
            self.parent.logger.info("Move to {} not complete within {} seconds", position, timeout)
            self.scannable.stop()
            self.scannable.waitWhileBusy();
            currentPosition = self.scannable.getPosition()
            if abs(position - currentPosition) < 0.001:
                self.parent.logger.info("Move to {} not complete within {} seconds, but within 0.001", position, timeout)
            else:
                self.parent.logger.warn("Move to {} not complete within {} seconds, stopped at {} ({})",
                                        position, timeout, currentPosition, position - currentPosition, )
        except InterruptedException, e:
            self.parent.logger.info("Move to {} interrupted, stopping...", position)
            self.scannable.stop()
            self.scannable.waitWhileBusy();
            currentPosition = self.scannable.getPosition()
            self.parent.logger.error("Move to {} interrupted at {} ({}), not returning or origin",
                                     position, currentPosition, position - currentPosition, e)
            interrupted = True

    def getPosition(self):
        return [ self.rockTime, self.centre, self.delta, self.rockCount, 1 ]

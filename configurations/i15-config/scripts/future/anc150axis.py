from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from org.slf4j import LoggerFactory
from time import sleep

# Updated from commit f607d6b8fcd29420f02858b2d628c6909d306547
# gda-diamond.git/.../b16-config/scripts/scannable/epics/anc150axis.py
# Then added back i15 enhancements

class Anc150Axis(ScannableMotionBase):
    '''
    PD for Anc150Axis
    '''
    def __init__(self, name, root, delayAfterMove,
            forceEpicsRecordProcessingOnTweak=False, doZeroTweakSizeMoves=True):
        self.logger=LoggerFactory.getLogger("Anc150Axis:%s"%name)
        self.setName(name);
        self.delayAfterMove = delayAfterMove
        self.doZeroTweakSizeMoves = doZeroTweakSizeMoves
        self.pvRoot = root
        self.CAFrequency = CAClient(self.pvRoot + "F")
        self.CAVoltage = CAClient(self.pvRoot + "V")
        self.CATweakSize = CAClient(self.pvRoot + "TWSIZE")
        if forceEpicsRecordProcessingOnTweak:
            self.CATweakPositive = CAClient(self.pvRoot + "TWPOS.PROC")
            self.CATweakNegative = CAClient(self.pvRoot + "TWNEG.PROC")
        else:
            self.CATweakPositive = CAClient(self.pvRoot + "TWPOS")
            self.CATweakNegative = CAClient(self.pvRoot + "TWNEG")
        self.CAPosition = CAClient(self.pvRoot + "POS")
        self.configure()

    def isBusy(self):
        return 0

    def atScanStart(self):
        self.logger.debug("atScanStart()")

    def atScanEnd(self):
        self.logger.debug("atScanEnd()")

    def atCommandFailure(self):
        self.logger.debug("atCommandFailure()")
        self.atScanEnd()

    def getPosition(self):
        """
        Returns axis position
        """
        return float(self.CAPosition.caget())

    def asynchronousMoveTo(self, absPos):
        """
        Moves axis position to new position
        """
        currentPos=self.getPosition()
        diff = float(absPos) - float(currentPos)
        self.logger.debug("asynchronousMoveTo({}) pos={} diff={}", absPos, currentPos, diff)
        if self.doZeroTweakSizeMoves or int(abs(diff)) >= 1:
            self.CATweakSize.caput(int(abs(diff)))
            # do the move
            if (diff > 0):
                self.CATweakPositive.caput(1)
                self.logger.debug("asynchronousMoveTo({}) TWPOS={}", absPos, self.CATweakPositive.caget())
            else:
                self.logger.debug("asynchronousMoveTo({}) TWNEG={}", absPos, self.CATweakNegative.caget())
                self.CATweakNegative.caput(1)
            
            freq = float(self.CAFrequency.caget())
            sleepTime=(abs(diff)/freq)+self.delayAfterMove
            self.logger.debug("asynchronousMoveTo({}) sleepTime={}", absPos, sleepTime)
            sleep(sleepTime)
        else:
            self.logger.warn("Current {} motor position ({}) is less than 1 step away from requested position ({}), you"+
                " may need to scan with a larger step size", self.name, absPos, currentPos, diff)
            sleep(self.delayAfterMove)

    def configure(self):
        self.logger.debug("configure()")
        self.CAFrequency.configure()
        self.CAVoltage.configure()
        self.CATweakSize.configure()
        self.CATweakPositive.configure()
        self.CATweakNegative.configure()
        self.CAPosition.configure()

    def getFrequency(self):
        print "Frequency is " + str(self.CAFrequency.caget())
    
    def getVoltage(self):
        print "Voltage is: " + str(self.CAVoltage.caget())

    def setFrequency(self, newFrequency):
        print "Changing frequency from " + str(self.CAFrequency.caget()) + " to " + str(newFrequency) + "..."
        self.CAFrequency.caput(newFrequency)
        print "Done"
    
    def setVoltage(self, newVoltage):
        print "Changing voltage from " + str(self.CAVoltage.caget()) + " to " + str(newVoltage) + "..."
        self.CAVoltage.caput(newVoltage)
        print "Done"

    def resetAbsolute(self, newVal):
        print "Resetting position from " + self.getPosition() + " to " + str(newVal)
        self.CAPosition.caput(newVal)
        print "Done, position " + self.getPosition()

def createAnc150Axis(name, pvname, delayAfterMove, forceEpicsRecordProcessingOnTweak=False, doZeroTweakSizeMoves=True):
        
    try:
        result = Anc150Axis(name, pvname, delayAfterMove, forceEpicsRecordProcessingOnTweak, doZeroTweakSizeMoves)
    except Exception, e:
        print "*** Could not create Anc150Axis for pv '" + str(pvname) + "' because: " + str(e)
    return result
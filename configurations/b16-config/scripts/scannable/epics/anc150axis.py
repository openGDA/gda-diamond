from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from time import sleep

class Anc150Axis(ScannableMotionBase):
    '''
    PD for Anc150Axis
    '''
    def __init__(self, name, root, delayAfterMove):

        self.setName(name);
        self.delayAfterMove = delayAfterMove
        self.pvRoot = root
        self.CAFrequency = CAClient(self.pvRoot + "F")
        self.CAVoltage = CAClient(self.pvRoot + "V")
        self.CATweakSize = CAClient(self.pvRoot + "TWSIZE")
        self.CATweakPositive = CAClient(self.pvRoot + "TWPOS")
        self.CATweakNegative = CAClient(self.pvRoot + "TWNEG")
        self.CAPosition = CAClient(self.pvRoot + "POS")
        self.configure()
        
    def isBusy(self):
        return 0

    def getPosition(self):
        """
        Returns axis position
        """
        return self.CAPosition.caget()

    def asynchronousMoveTo(self, absPos):
        """
        Moves axis position to new position
        """
        diff = absPos - float(self.getPosition())
        self.CATweakSize.caput(abs(diff))
        
        # do the move
        if (diff > 0):
            self.CATweakPositive.caput(1)
        else:
            self.CATweakNegative.caput(1)
        
        freq = float(self.CAFrequency.caget())
        sleep((abs(diff)/freq)+self.delayAfterMove)

    def configure(self):
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

def createAnc150Axis(name, pvname, delayAfterMove):
    try:
        result = Anc150Axis(name, pvname, delayAfterMove)
    except Exception, e:
        print "*** Could not create Anc150Axis for pv '" + str(pvname) + "' because: " + str(e)
    return result
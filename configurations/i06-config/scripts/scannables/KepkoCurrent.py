from java import lang
from java.lang import System
from time import sleep
from gda.device.scannable import PseudoDevice
from gda.epics import CAClient

class kepko(PseudoDevice):
    def __init__(self,name,pvOut,pvIn):
        self.setName(name);
        self.setInputNames(['Ampere'])
        self.setOutputFormat(['%2.4f'])
        self.setLevel(6)
        self.currentPosition = 0.0
        self.iambusy = 0
        self.pvOut = pvOut
        self.pvIn = pvIn
        self.chIn=CAClient(self.pvIn)
        self.chIn.configure() 
        self.chOut=CAClient(self.pvOut)
        self.chOut.configure()

    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def getPosition(self):
        self.currentPosition = float(self.chIn.caget())*0.4 
        return self.currentPosition

    def asynchronousMoveTo(self, newpos):
        self.chOut.caput(newpos/0.4)
        sleep(0.5)
        return None

    def isBusy(self):
        return self.iambusy 
 
exec("kepko = None")
print"-> connect the Kepko to Analogue output 2 in patch panel U2 (branchline)"
kepko = kepko("kepko","BL06J-EA-USER-01:AO2","BL06J-EA-USER-01:AO2")

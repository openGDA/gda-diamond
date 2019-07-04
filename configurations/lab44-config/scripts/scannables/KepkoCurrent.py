from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from time import sleep

class KepkoCurrent(ScannableMotionBase):
    def __init__(self, name, pv):
        self.setName(name);
        self.setInputNames(['Ampere'])
        self.setOutputFormat(['%2.4f'])
        self.setLevel(6)
        self.ch=CAClient(pv)
        self.ch.configure() 

    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def getPosition(self):
        return float(self.ch.caget())*0.4

    def asynchronousMoveTo(self, newpos):
        self.ch.caput(newpos/0.4)
        sleep(0.5)
        return None

    def isBusy(self):
        return False 
 
#exec("kepko = None")
#print"-> connect the Kepko to Analogue output 2 in patch panel U2 (branchline)"
#kepko = KepkoCurrent("kepko", "BL06J-EA-USER-01:AO2")

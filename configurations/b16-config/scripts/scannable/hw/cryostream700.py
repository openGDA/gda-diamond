from scannable.moveToCore import DynamicPvManager
from gda.device.scannable import ScannableMotionBase
import time       

class Cryostream700(ScannableMotionBase):

    def __init__(self, name, pvPrefix):
        self.name = name
        self.inputNames = ['cryotarget']
        self.extraNames = ['cryoset','cryotemp']
        #self.outputFormat = ['%.2f', '%.2f']
        self.outputFormat = ['%.2f','%.2f', '%.2f']
        self.pvs = DynamicPvManager(pvPrefix)
        self.fancy = True
        
    def rawAsynchronousMoveTo(self, temp):
        self.ramp(temp)
    
    def rawGetPosition(self):
        return [float(self.pvs['RTEMP'].caget()),float(self.pvs['SETPOINT'].caget()), float(self.pvs['TEMP'].caget())]
        
    def isBusy(self):
        if self.fancy:
            return not(self.isAtTemp(float(self.pvs['RTEMP'].caget())))
        else:
            return False

    def isAtTemp(self, desiredTemp):
        return abs( float(self.pvs['TEMP'].caget()) - desiredTemp) <= .2

    def cool(self, temp):
        self.pvs['CTEMP'].caput(float(temp))
        time.sleep(.5)
        self.pvs['COOL.PROC'].caput(1)
        self.__waitForTargetSet(temp)
         
    def __waitForTargetSet(self, temp):
        starttime = time.time()
        while (time.time()-starttime) < 10:
            if self.__isTargetSet(temp):    return
            time.sleep(.2)
        raise Exception("Timed out setting %s's target cool temp to %sK after 10 seconds" % (self.getName(), `temp`))

    def __isTargetSet(self, temp):
        return float(self.pvs['SETPOINT'].caget()) == float(temp)
    
    def ramp(self, temp):
        self.pvs['RTEMP'].caput(float(temp))
        time.sleep(.5)
        self.pvs['RAMP.PROC'].caput(1)

    def setRampRate(self, rate):
        self.pvs['RRATE'].caput(float(rate))

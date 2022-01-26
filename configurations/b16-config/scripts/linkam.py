from gda.device.scannable import ScannableMotionBase
from scannable.moveToCore import DynamicPvManager
import time

class Linkam(ScannableMotionBase):

    def __init__(self, name, pvPrefix):
        self.name = name
        self.inputNames = ["target"]
        self.extraNames = ["rate", "temperature"]
        self.outputFormat = ["%5.5g"] * 3
        self.pvs = DynamicPvManager(pvPrefix)
        self.blocking = True

    def asynchronousMoveTo(self, temp):
        self.pvs["RAMP:LIMIT:SET"].caput(float(temp))
        time.sleep(1)
        self.pvs["RAMP:CTRL:SET"].caput(1)
        if self.blocking:
            time.sleep(2)

    def isBusy(self):
        if not self.blocking:
            return False
        status = float(self.pvs["STATUS"].caget())
        # 1 == Heating, 2 == Cooling
        return status == 1. or status == 2.

    def isAtTemp(self, target):
        return abs(float(self.pvs["TEMP"].caget()) == target) <= 0.1

    def getPosition(self):
        return [float(self.pvs["RAMP:LIMIT:SET"].caget()),
            float(self.pvs["RAMP:RATE:SET"].caget()),
            float(self.pvs["TEMP"].caget())]

    def setRampRate(self, rate):
        self.pvs["RAMP:RATE:SET"].caput(float(rate))

    def stop(self):
        self.pvs["RAMP:CTRL:SET"].caput(2)

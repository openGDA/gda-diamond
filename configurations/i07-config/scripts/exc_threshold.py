from gda.epics import PVWithSeparateReadback
from gda.epics import LazyPVFactory
from gda.device.scannable import ScannableBase
from java.lang import String
from java.util.function import Predicate

class JyPred(Predicate):
    def __init__(self, fn):
        self.test = fn


class ExcThreshold(ScannableBase):

    def __init__(self, name, basePv):
        self.setName(name)
        self.energyThreshold0 = PVWithSeparateReadback(LazyPVFactory.newDoublePV(basePv + "CAM:EnergyThreshold0"), LazyPVFactory.newReadOnlyDoublePV(basePv + "CAM:EnergyThreshold0_RBV"))
        self.energyThreshold1 = PVWithSeparateReadback(LazyPVFactory.newDoublePV(basePv + "CAM:EnergyThreshold1"), LazyPVFactory.newReadOnlyDoublePV(basePv + "CAM:EnergyThreshold1_RBV"))
        self.calibrating = LazyPVFactory.newEnumPV(basePv + "CAM:Calibrating_RBV", String)

    def isBusy(self):
        return self.calibrating.get() != "Idle"

    def getPosition(self):
        return self.energyThreshold0.get()

    def waitForCalibrating(self, value):
        return value == "Calibrating"

    def rawAsynchronousMoveTo(self, threshold):
        # Todo make actually async and use proper isBusy
        self.energyThreshold0.putWait(float(threshold));
        self.calibrating.waitForValue(JyPred(self.waitForCalibrating), 5.0)
        if abs(self.energyThreshold1.get() - 30.0) > 0.001:
            self.energyThreshold1.putWait(30.0);
            self.calibrating.waitForValue(JyPred(self.waitForCalibrating), 5.0)

try:
    excthresh = ExcThreshold("excthresh", "BL07I-EA-EXCBR-01:")
except Exception as e:
    print("Error setting up exc threshold", e)

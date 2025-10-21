from gda.epics import PVWithSeparateReadback
from gda.epics import LazyPVFactory
from gda.device.scannable import ScannableBase
from java.lang import String
from java.util.function import Predicate

class JyPred(Predicate):
    def __init__(self, fn):
        self.test = fn

class PilatusThreshold(ScannableBase):

    def __init__(self, name, basePv):
        self.setName(name)
        self.threshold_setter = PVWithSeparateReadback(LazyPVFactory.newDoublePV(basePv + "CAM:ThresholdEnergy"), LazyPVFactory.newReadOnlyDoublePV(basePv + "CAM:ThresholdEnergy_RBV"))
        self.amIbusy = False
        self.timeout = 10.0

    def isBusy(self):
        return self.amIbusy

    def getPosition(self):
        return self.threshold_setter.get()

    def rawAsynchronousMoveTo(self, threshold):
        self.amIbusy = True
        self.threshold_setter.putWait(float(threshold), self.timeout);
        if abs(self.threshold_setter.get() - threshold) > 0.001 :
            print("Detector did not reach desired threshold, please check the requested value is reasonable for this detector.")
        self.amIbusy = False

class ExcaliburThreshold(ScannableBase):

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
    exthresh = ExcaliburThreshold("excthresh", "BL07I-EA-EXCBR-01:")
    p2thresh = PilatusThreshold("p2thresh", "BL07I-EA-PILAT-02:")
    p2thresh.timeout = 30.0
    p3thresh = PilatusThreshold("p3thresh", "BL07I-EA-PILAT-03:")
except Exception as e:
    print("Error setting up exc threshold", e)
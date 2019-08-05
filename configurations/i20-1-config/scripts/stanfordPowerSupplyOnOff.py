from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider
from gda.epics import CAClient

class StanfordPowerOnOff(ScannableBase):

    def __init__(self, name):
        self.name = name
        self.inputNames = [name]
        self.setOutputFormat({});
        self.setInputNames({});
        self.ionchamberNames = ["scaler_for_zebra", "ionchambers", "ionchambers_diode"]
        self.pvName = "BL20J-EA-STANF-01:PWR:MODE"
        self.mains = 0
        self.battery = 1

    def getDetectorNames(self) :
        scanController = InterfaceProvider.getCurrentScanInformationHolder()
        return scanController.getCurrentScanInformation().getDetectorNames()

    def hasIonChambers(self):
        scannableNames = self.getDetectorNames()
        # print "scannable name ", scannableNames
        for name in scannableNames :
            for icn in self.ionchamberNames :
                if icn == name :
                    return True
        return False

    def stop(self):
        self.atScanEnd()

    def atCommandFailure(self):
        self.atScanEnd()

    def atScanStart(self) :
        if self.hasIonChambers() :
            CAClient.put(self.pvName, self.battery)

    def atScanEnd(self) :
        # if self.hasIonChambers() :
        CAClient.put(self.pvName, self.mains)

    def isBusy(self):
        return False

    def rawAsynchronousMoveTo(self,new_position):
        pass

    def rawGetPosition(self):
        return None
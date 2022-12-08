# Create a scannable to set/get the DTC energy (keV) on XSpress4
# Uses cspress4.setDtcEnergyKev, xspress4.getDtcEnergyKev to set/get the energy
# imh 28/2/2018

print "Setting up DTC_energy scannable to set/get Xspress4 DTC energy"

from gda.device.scannable import ScannableBase

class Xspress4DTCEnergy(ScannableBase):
    
    def __init__(self,name):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(['%.4f'])
        self.xspress4Detector = None

    def setXspress4(self, xspress4Detector):
        self.xspress4Detector = xspress4Detector

    def isBusy(self):
        return False
    
    def getPosition(self):
        return self.xspress4Detector.getDtcEnergyKev()
    
    def asynchronousMoveTo(self, energyKev):
        self.xspress4Detector.setDtcEnergyKev(energyKev)

DTC_energy = Xspress4DTCEnergy("DTC_energy")
DTC_energy.setXspress4(xspress4)
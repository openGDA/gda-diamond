from gda.device.scannable import ScannableBase
from gda.epics import CAClient
from gda.device import DeviceException

class StopOnFaultScannable( ScannableBase ):
    def __init__(self, name, pvs, shutter, close_val = 0):
        self.ca_pvs = []
        self.shutter = shutter
        self.close_val = close_val
        self.name = name
        self.extraNames = []
        self.inputNames = []
        self.outputFormat = []
        for pv in pvs:
            ca = CAClient(pv)
            ca.configure()
            self.ca_pvs.append(ca)

    def testForFault(self):
        for ca in self.ca_pvs:
            if int(ca.caget()) != 0:
                self.shutter.stop()
                self.shutter.moveTo(self.close_val)
                print "PV returned non-zero value - raising exception and closed shutter"
                raise DeviceException("PV returned non-zero value")

    def getPosition(self):
        self.testForFault()

    def atPointStart(self):
        self.testForFault()

    def atPointEnd(self):
        self.testForFault()

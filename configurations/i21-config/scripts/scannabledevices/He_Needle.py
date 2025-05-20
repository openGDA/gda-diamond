'''
A Scannable class to support the needle valve that controls Helium Transfer line.
Created on 28 Apr 2025

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient


class HeTransferVoltage(ScannableMotionBase):
    '''
    scannable to set voltage of He transfer line
    '''

    def __init__(self, name, pv_root="BL21I-EA-SMPL-01:HE:TRANSFER"):
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(['%f'])
        self.cli_set = CAClient(pv_root + ":VOLTAGE")
        self.cli_rbv = CAClient(pv_root + ":VOLTAGE_RBV")
        self._busy = False

    def configure(self):
        if self.isConfigured():
            return
        if not self.cli_set.isConfigured():
            self.cli_set.configure()
        if not self.cli_rbv.isConfigured():
            self.cli_rbv.configure()
        self.setConfigured(True)

    def getPosition(self):
        self.configure()
        return float(self.cli_rbv.caget())

    def asynchronousMoveTo(self, v):
        self._busy = True
        self.configure()
        self.cli_set.caput(float(v))
        self._busy = False

    def isBusy(self):
        return self._busy

    def open(self):
        self.asynchronousMoveTo(5.0)
        self.waitWhileBusy()

    def close(self):
        self.asynchronousMoveTo(10.0)
        self.waitWhileBusy()

    def optimalOpening(self):
        self.asynchronousMoveTo(8.0)
        self.waitWhileBusy()

needle = HeTransferVoltage("needle", pv_root="BL21I-EA-SMPL-01:HE:TRANSFER")

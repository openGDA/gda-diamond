from gda.device import DeviceException
from gda.device.scannable import ScannableBase
from gda.epics import CAClient
from time import sleep, time

class Ecc100Axis(ScannableBase):
    def __init__(self, name, pvroot):
        self.name = name
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ["%.6f"]
        self.pv_root = pvroot
        self.ca_freq = CAClient(self.pv_root + "CMD:FREQ")
        self.ca_freq_rbv = CAClient(self.pv_root + "CLC_FREQ")
        self.ca_amp = CAClient(self.pv_root + "CMD:AMPL")
        self.ca_amp_rbv = CAClient(self.pv_root + "CLC_AMPL")
        self.ca_dc = CAClient(self.pv_root + "CMD:DC")
        self.ca_dc_rbv = CAClient(self.pv_root + "CLC_DC")
        self.ca_position = CAClient(self.pv_root + "CMD:TARGET")
        self.ca_position_rbv = CAClient(self.pv_root + "POSITION")
        self.ca_inposition = CAClient(self.pv_root + "RD_INRANGE")
        self.ca_stop = CAClient(self.pv_root + "CMD:STOP")
        self.ca_hlimit = CAClient(self.pv_root + "ST_EOT_FWD")
        self.ca_llimit = CAClient(self.pv_root + "ST_EOT_BWD")
        self.min_delay = 1 #1 second
        self.time_at_move = 0
        self.configure()

    def isBusy(self):
        #"is busy" status is a little slow to update
        if time() < self.time_at_move + self.min_delay:
            return True
        if int(self.ca_hlimit.caget()) == 1:
            raise DeviceException("%s is on a high limit" % self.name)
        if int(self.ca_llimit.caget()) == 1:
            raise DeviceException("%s is on a low limit" % self.name)
        return int(self.ca_inposition.caget()) != 1

    def getPosition(self):
        return float(self.ca_position_rbv.caget())

    def asynchronousMoveTo(self, pos):
        self.ca_position.caput(pos)
        self.time_at_move = time()

    def configure(self):
        configurables = [self.ca_freq, self.ca_freq_rbv,
                self.ca_amp, self.ca_amp_rbv,
                self.ca_dc, self.ca_dc_rbv,
                self.ca_position, self.ca_position_rbv,
                self.ca_inposition, self.ca_stop,
                self.ca_hlimit, self.ca_llimit]
        for _c in configurables:
            _c.configure()

    def getFrequency(self):
        return self.ca_freq_rbv.caget()

    def getAmplitude(self):
        return self.ca_amp_rbv.caget()

    def getDC(self):
        return self.ca_dc_rbv.caget()

    def setFrequency(self, freq):
        return self.ca_freq(freq)

    def setAmplitude(self, amp):
        return self.ca_amp.caput(amp)

    def setDC(self, dc):
        return self.ca_dc.caput(dc)

    def stop(self):
        self.ca_stop.caput(0)
        self.time_at_move = 0

    def atCommandFailure(self):
        self.stop()

def createEcc100Axis(name, pv):
    return Ecc100Axis(name, pv)

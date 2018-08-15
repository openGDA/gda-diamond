from gdascripts.pd.time_pds import tictoc
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class PilatusThreshold(ScannableMotionBase):
    def __init__(self, name, pvbase):
        self.setName(name);
        self.waitstep = waitstep
        self.setInputNames([name])
        self.setExtraNames([])
        self.Units=['keV']
        self.setOutputFormat(['%4.2f'])
        self.setLevel(7)
        self.timer=tictoc()
        self.waitUntilTime = 0
        self.demand = 0.0
        self.gain = CAClient(pvbase+":GainMenu")
        self.thres = CAClient(pvbase+":ThresholdEnergy")
        self.gain.configure()
        self.thres.configure()
        #self.gainranges = { 0 : [6.5, 19.7], 1 : [4.4, 14.0], 2 : [3.8, 11.4] }
        self.gainranges = { } # P3 does autogain
        self.thresholdtolerance = 0.1
        #self.waittime = 30
        self.waittime = 8 # P3 faster

    def rawGetPosition(self):
        return [self.thres.caget() * 2.0]

    def rawAsynchronousMoveTo(self,newpos):
        gain = int(self.gain.caget())
        if newpos >= self.gainranges[gain][0] and newpos <= self.gainranges[gain][1]:
            # gain ok
            pass
        else:
            for i in self.gainranges.keys():
                if newpos >= self.gainranges[i][0] and newpos <= self.gainranges[i][1]:
                    self.gain.caput(i)	
                    self.timer.reset()
                    break
            # raise exception, value out of range
        thres = self.thres.caget()
        if abs((thres * 2.0) - newpos) < newpos * self.thresholdtolerance:
            # threshold ok
            pass
        else:
            self.thres.caput(newpos / 2.0)
            self.timer.reset()

    def rawIsBusy(self):
        return (self.timer()<self.waittime)

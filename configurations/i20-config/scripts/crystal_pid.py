#
# For commissionning ONLY!
#
# This operates the Epics-level PID loops which run the crystal pitch and roll
#
from gda.epics import CAClient
import time

class crystalPID(ScannableBase):
    
    def __init__(self,name,setPointPV,readbackPV,errorPV,threshold):
        self.setName(name)
        self.setPointPV = setPointPV
        self.readbackPV = readbackPV
        self.errorPV = errorPV
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(['%.4f'])
        self.ca = CAClient()
        self.threshold = threshold
        
    def isBusy(self):
        return abs(float(self.ca.caget(self.errorPV))) > self.threshold
    def getPosition(self):
        return float(self.ca.caget(self.readbackPV))
    def asynchronousMoveTo(self,targetPosition):
        self.ca.caput(self.setPointPV,targetPosition)
        # give a chance for things to start moving and the error to move above threshold
        time.sleep(1)
        
pid_xtal1p = crystalPID("pid_xtal1p","BL20I-OP-QCM-01:XTAL1:PITCH:FB.VAL","BL20I-OP-QCM-01:XTAL1:PITCH:FB.CVAL","BL20I-OP-QCM-01:XTAL1:PITCH:FB.ERR",0.002)
pid_xtal2r = crystalPID("pid_xtal2r","BL20I-OP-QCM-01:XTAL2:ROLL:FB.VAL","BL20I-OP-QCM-01:XTAL2:ROLL:FB.CVAL","BL20I-OP-QCM-01:XTAL2:ROLL:FB.ERR",0.002)
pid_xtal34r = crystalPID("pid_xtal34r","BL20I-OP-QCM-01:XTAL34:ROLL:FB.VAL","BL20I-OP-QCM-01:XTAL34:ROLL:FB.CVAL","BL20I-OP-QCM-01:XTAL34:ROLL:FB.ERR",0.002)
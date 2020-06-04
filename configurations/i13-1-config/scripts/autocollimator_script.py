import time
from epics_scripts import pv_scannable_utils
from gda.device.scannable.scannablegroup import ScannableGroup


#create a another scannable that starts the ac at each point and sets it running. Waits for it to end and returns
from gda.device.scannable import ScannableMotionBase
def _cpy_array(src): ## TODO: try tupel(acoll.getInputNames())
    cpy = []
    for r in src:
        cpy.append(r)
    return cpy
    
class AutoCollimator(ScannableMotionBase):
    def __init__(self, name, acoll):
#        ScannableMotionBase.__init__(self) #do not required as it will be called at end of this __init__ by default
        self.setName(name)
        self.setInputNames(["samplesize"])
        self.setExtraNames(_cpy_array(acoll.getInputNames())) # use list(acoll.getInputNames()) --RobW
        cpy=_cpy_array(acoll.getOutputFormat())
        cpy.append("%5.5g")
        self.setOutputFormat(cpy)
        self.acoll = acoll
        self.setLevel(8)
        
        
    def rawIsBusy(self):
        val = self.acoll.acoll_running()
        return val == 1

    def rawGetPosition(self):
        res = []
        res.append(self.acoll.acoll_average_size())
        vals = self.acoll.getPosition()
        for val in vals:
            if `val` == "nan":
                val = 99999.
            res.append(val)
        return res

    def rawAsynchronousMoveTo(self,new_position):
        self.acoll.acoll_average_size(new_position)
        self.acoll.acoll_go(0)
        time.sleep(0.1)
        self.acoll.acoll_go(1)
        time.sleep(0.1)
        
    def stop(self):
        self.acoll.acoll_stop(0)
        time.sleep(0.1)
        self.acoll.acoll_stop(1)



#===============================================================================
# Hi Paul, Ulrik wanted these scannables pulled out into the name space -- RobW
# I also changed the configuration to a more standar python idiom (from lala import *) while doing so

acoll_average_size= pv_scannable_utils.createPVScannable("acoll_average_size", "BL13J-OP-ACOLL-01:AVERAGESIZE", False)
acoll_x_value = pv_scannable_utils.createPVScannable("acoll_x_value", "BL13J-OP-ACOLL-01:XVALUE", False)
acoll_y_value = pv_scannable_utils.createPVScannable("acoll_y_value", "BL13J-OP-ACOLL-01:YVALUE", False)
acoll_x_invalid = pv_scannable_utils.createPVScannable("acoll_x_invalid", "BL13J-OP-ACOLL-01:XINVALID", False)
acoll_y_invalid = pv_scannable_utils.createPVScannable("acoll_y_invalid", "BL13J-OP-ACOLL-01:YINVALID", False)
acoll_x_samples = pv_scannable_utils.createPVScannable("acoll_x_samples", "BL13J-OP-ACOLL-01:XSAMPLES", False)
acoll_y_samples = pv_scannable_utils.createPVScannable("acoll_y_samples", "BL13J-OP-ACOLL-01:YSAMPLES", False)
acoll_x_std_dev = pv_scannable_utils.createPVScannable("acoll_x_std_dev", "BL13J-OP-ACOLL-01:XSTDDEV", False)
acoll_y_std_dev = pv_scannable_utils.createPVScannable("acoll_y_std_dev", "BL13J-OP-ACOLL-01:YSTDDEV", False)
acoll_sample_period = pv_scannable_utils.createPVScannable("acoll_sample_period", "BL13J-OP-ACOLL-01:SAMPLEPERIOD", False)
acoll_connected = pv_scannable_utils.createPVScannable("acoll_connected", "BL13J-OP-ACOLL-01:CONNECTED", False)
acoll_running = pv_scannable_utils.createPVScannable("acoll_running", "BL13J-OP-ACOLL-01:RUNNING", False)
acoll_go = pv_scannable_utils.createPVScannable("acoll_go", "BL13J-OP-ACOLL-01:GO", False)
acoll_stop = pv_scannable_utils.createPVScannable("acoll_stop", "BL13J-OP-ACOLL-01:STOP", False)
acoll = ScannableGroup()

acoll.setGroupMembers([acoll_average_size, acoll_x_value, acoll_y_value, acoll_x_samples, acoll_y_samples,
                        acoll_x_invalid, acoll_y_invalid, acoll_x_std_dev, acoll_y_std_dev,
                        acoll_sample_period, acoll_connected, acoll_running, acoll_go, acoll_stop])

acoll.setName("acoll")
acoll.configure()

autocollimator = AutoCollimator("autocollimator", acoll)

print "Autocollimator:"
print "To read last values >autocollimator"
print "to take reading >pos autocollimator 0.1 where 0.1 "
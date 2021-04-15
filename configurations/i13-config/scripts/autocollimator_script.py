import time
from epics_scripts.pv_scannable_utils import createPVScannable
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.jython import InterfaceProvider
def setup():
    acoll_average_size= createPVScannable("acoll_average_size", "BL13I-OP-ACOLL-01:AVERAGESIZE", False)
    acoll_x_value = createPVScannable("acoll_x_value", "BL13I-OP-ACOLL-01:XVALUE", False)
    acoll_y_value = createPVScannable("acoll_y_value", "BL13I-OP-ACOLL-01:YVALUE", False)
    acoll_x_invalid = createPVScannable("acoll_x_invalid", "BL13I-OP-ACOLL-01:XINVALID", False)
    acoll_y_invalid = createPVScannable("acoll_y_invalid", "BL13I-OP-ACOLL-01:YINVALID", False)
    acoll_x_samples = createPVScannable("acoll_x_samples", "BL13I-OP-ACOLL-01:XSAMPLES", False)
    acoll_y_samples = createPVScannable("acoll_y_samples", "BL13I-OP-ACOLL-01:YSAMPLES", False)
    acoll_x_std_dev = createPVScannable("acoll_x_std_dev", "BL13I-OP-ACOLL-01:XSTDDEV", False)
    acoll_y_std_dev = createPVScannable("acoll_y_std_dev", "BL13I-OP-ACOLL-01:YSTDDEV", False)
    acoll_sample_period = createPVScannable("acoll_sample_period", "BL13I-OP-ACOLL-01:SAMPLEPERIOD", False)
    acoll_connected = createPVScannable("acoll_connected", "BL13I-OP-ACOLL-01:CONNECTED", False)
    acoll_running = createPVScannable("acoll_running", "BL13I-OP-ACOLL-01:RUNNING", False)
    acoll_go = createPVScannable("acoll_go", "BL13I-OP-ACOLL-01:GO", False)
    acoll_stop = createPVScannable("acoll_stop", "BL13I-OP-ACOLL-01:STOP", False)
    acoll = ScannableGroup()
    acoll.addGroupMember(acoll_average_size)
    acoll.addGroupMember(acoll_x_value)
    acoll.addGroupMember(acoll_y_value)
    acoll.addGroupMember(acoll_x_samples)
    acoll.addGroupMember(acoll_y_samples)
    acoll.addGroupMember(acoll_x_invalid)
    acoll.addGroupMember(acoll_y_invalid)
    acoll.addGroupMember(acoll_x_std_dev)
    acoll.addGroupMember(acoll_y_std_dev)
    acoll.addGroupMember(acoll_sample_period)
    acoll.addGroupMember(acoll_connected)
    acoll.addGroupMember(acoll_running)
    acoll.addGroupMember(acoll_go)
    acoll.addGroupMember(acoll_stop)
    acoll.setName("acoll")
    acoll.configure()
    autocollimator = auto_collimator("autocollimator", acoll)

    commandServer = InterfaceProvider.getJythonNamespace()    
    commandServer.placeInJythonNamespace("autocollimator",autocollimator)
    commandServer.placeInJythonNamespace("acoll",acoll)
    
    print "Autocollimator:"
    print "To read last values >autocollimator"
    print "to take reading >pos autocollimator 0.1 where 0.1 "

#create a another scannable that starts the ac at each point and sets it running. Waits for it to end and returns
from gda.device.scannable import ScannableMotionBase
def cpy_array(src):
    cpy = []
    for r in src:
        cpy.append(r)
    return cpy
    
class auto_collimator(ScannableMotionBase):
    def __init__(self, name, acoll):
#        ScannableMotionBase.__init__(self) #do not required as it will be called at end of this __init__ by default
        self.setName(name)
        self.setInputNames(["samplesize"])
        self.setExtraNames(cpy_array(acoll.getInputNames()))
        cpy=cpy_array(acoll.getOutputFormat())
        cpy.append("%5.5g")
        self.setOutputFormat(cpy)
        self.acoll = acoll
        self.setLevel(8)
        
        
    def isBusy(self):
        val = self.acoll.acoll_running()
        return val == 1

    def rawGetPosition(self):
        res = []
        res.append(self.acoll.acoll_average_size())
        vals = self.acoll.getPosition()
        for val in vals:
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
        
    
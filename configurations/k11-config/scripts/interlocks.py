from gda.device.monitor import MonitorBase # @UnresolvedImport
from gda.epics import LazyPVFactory # @UnresolvedImport
from k11_utilities import is_live

class Interlock(MonitorBase):
    def __init__(self, name, pv, ok_value):
        self.setName(name)
        self.pv = LazyPVFactory.newIntegerPV(pv)
        self.pv.addObserver(lambda source, arg: self.notifyIObservers(self, self.getPosition()))
        self.ok_value = ok_value
        
    def rawGetPosition(self):
        word = self.pv.get()
        return word == self.ok_value

# for testing
dummy_pv_0 = "ws413-AD-SIM-01:CAM:NumExposures"
dummy_pv_1 = "ws413-AD-SIM-01:CAM:NumImages"

eh_pv = "BL11K-VA-VLVCC-03:ILK01:ILK" if is_live() else dummy_pv_0
eh_non_critical_jy = Interlock("eh_non_critical_jy", eh_pv, 65535) # all 1's

eh1_pv = "BL11K-PS-IOC-01:M11:LOP" if is_live() else dummy_pv_1
eh1_searched_locked_jy = Interlock("eh1_searched_locked_jy", eh1_pv, 0) # all 0's

guardlines_pv = "BL11K-VA-VLVCC-02:INT5:RAWILK" if is_live() else dummy_pv_0
guardlines_jy = Interlock("guardlines_jy", guardlines_pv, 65535)

# clean up namespace
del dummy_pv_0
del dummy_pv_1
del eh_pv
del eh1_pv
del guardlines_pv




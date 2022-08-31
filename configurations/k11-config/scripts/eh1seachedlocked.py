from gda.device.monitor import MonitorBase
from gda.epics import CAClient
from k11_utilities import is_live

class EH1SearchedAndLocked(MonitorBase):
    def __init__(self, name, pv):
        self.setName(name)
        self.ca = CAClient(pv)
        self.ca.configure()
        self.ca.camonitor(lambda event: self.notifyIObservers(self, self.getPosition()))
        
    def rawGetPosition(self):
        word = self.ca.cagetArrayInt()[0]
        return word == 0
    
pv = "BL11K-PS-IOC-01:M11:LOP" if is_live() else "ws413-MO-SIM-01:M5.RBV"
eh1_searched_locked_jy = EH1SearchedAndLocked("eh1_searched_locked_jy", pv)
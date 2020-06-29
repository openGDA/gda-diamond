#
# These classes change the configuration in daserver between its high and low
# energy modes (the threshold is 8keV).
#
# These two modes are independent of any settings the GDA uses or any corrections
# GDA should make to the raw data from Xspress.
#
# RJW Aug 2012
 
from java.util import ArrayList

from gda.factory import Finder

class _xspressconfigurer:
    """ base class for the two energy mode configurers"""
    def __init__(self):
        self.xspress = Finder.find("xspress2system")
        self.daserver = Finder.find("DAServer")

class SwitchToHighEnergy(_xspressconfigurer):
    
    def __call__(self):
        cmds = ArrayList()
        cmds.add("~config 9")
        self.daserver.setStartupCommands(cmds)
        self.daserver.reconnect()
        self.xspress.configure()
        
class SwitchToLowEnergy(_xspressconfigurer):
    
    def __call__(self):
        cmds = ArrayList()
        cmds.add("~config 7")
        self.daserver.setStartupCommands(cmds)
        self.daserver.reconnect()
        self.xspress.configure()
        
switchXspressToHighEnergyMode = SwitchToHighEnergy()
switchXspressToLowEnergyMode = SwitchToLowEnergy()
from gda.observable import IObserver
from gda.device.scannable import PseudoDevice

class FastShutterShutter(IObserver, PseudoDevice):
    def __init__(self, name, tfg):
        self.name = name
        self.inputNames = [name]
        self.tfg = tfg
        self.tfg.addIObserver(self)
	self.ourpos = "unknown"
	self.didsomething = False
	self.settings = { "Open": 0 , "Closed" : 255 }
        
    def update(self, observed, message):
	if not self.didsomething:
		self.ourpos = "unknown"
	self.didsomething = False
        
    def rawIsBusy(self):
	return self.didsomething

    def rawGetPosition(self):
        return self.ourpos

    def rawAsynchronousMoveTo(self,new_position):
	self.didsomething = True
	if not self.tfg.getStatus() == 0:
		raise DeviceException("timer not idle")
	if new_position in [True, 1, "Open"]:
		self.ourpos = "Open"
	elif new_position in [False, 0, "Close", "Closed"]:
		self.ourpos = "Closed"
	else:
		self.didsomething = False
		raise DeviceException("unknown new position")
	self.tfg.setAttribute("Inversion", self.settings[self.ourpos])
	self.tfg.clearFrameSets()
	self.tfg.addFrameSet(1,1000,1000, 0, 255, 0, 0)
	self.tfg.loadFrameSets()
	self.tfg.clearFrameSets()

fss=FastShutterShutter("fss", finder.find("Tfg"))

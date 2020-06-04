from gda.jython.scannable import ScannableMotionBase
from gda.epics import CAClient
from time import sleep

class SingleEpicsPositionerClass(ScannableMotionBase):
	'''Create PD for single EPICS positioner'''
	def __init__(self, name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring, delay):
		self.setName(name);
		self.setInputNames([name])
		#self.setExtraNames([name]);
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.incli=CAClient(pvinstring)
		self.outcli=CAClient(pvoutstring)
		self.statecli=CAClient(pvstatestring)
		self.stopcli=CAClient(pvstopstring)
		self.incli.configure()
		self.outcli.configure()
		self.statecli.configure()
		self.stopcli.configure()
		self.delay = delay

	def getPosition(self):
		return float(self.outcli.caget())
		
	def asynchronousMoveTo(self,new_position):
		self.incli.caput(new_position)
		sleep(self.delay)

	def isBusy(self):
		return not int(self.statecli.caget())
	
	def stop(self):
		self.stopcli.caput(1)


class SingleEpicsPositionerClassWithSet(ScannableMotionBase):
	'''Create PD for single EPICS positioner'''
	def __init__(self, name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring, delay):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames([name+"_set"]);
		self.setOutputFormat([formatstring]*2)
		self.setLevel(3)
		self.incli=CAClient(pvinstring)
		self.outcli=CAClient(pvoutstring)
		self.statecli=CAClient(pvstatestring)
		self.stopcli=CAClient(pvstopstring)
		self.incli.configure()
		self.outcli.configure()
		self.statecli.configure()
		self.stopcli.configure()
		self.delay = delay
		self.set=0

	def getPosition(self):
		return [float(self.outcli.caget()), float(self.set)]
		
	def asynchronousMoveTo(self,new_position):
		self.incli.caput(new_position)
		sleep(self.delay)
		self.set=new_position

	def isBusy(self):
		return not int(self.statecli.caget())
	
	def stop(self):
		self.stopcli.caput(1)

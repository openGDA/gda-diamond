from time import sleep
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 

class BipolarPS(ScannableMotionBase): 
	def __init__(self, name, pvBase):
		self.setName(name);
		self.setInputNames(['I_'+name])
		self.setOutputFormat(['%04.2f'])
		self.setLevel(6)
		self.pulsePowerMax = 20 #maximum value of (current X pulse duration)
		self.pulseDuration = 2
		
		self.chIn=CAClient(pvBase + ":I")
		self.chIn.configure()
		self.chOut=CAClient(pvBase + ':SETI')
		self.chOut.configure();
		self.chOnOff=CAClient(pvBase + ':ONOFFTOG.PROC')
		self.chOnOff.configure();
		self.chIsOnOff=CAClient(pvBase + ':ISONOFF')
		self.chIsOnOff.configure();
		self.currentPosition = 0
		self.verbose=False

	def pulse(self, current):
		if ((current * self.pulseDuration)<self.pulsePowerMax)&(self.pulseDuration<=10)&(self.pulseDuration>0):
			flag = True
			self.setCurrent(current)
			sleep(self.pulseDuration)
			self.setCurrent(0)
		else:
			flag = False
			print "error: pulse parameters out of range"
		return flag
	
	def getCurrent(self):
		current=self.chIn.caget()
		sleep(0.1)
		return current
	
	def setCurrent(self, I):
		self.chOut.caput(I)
		sleep(0.1)
		return
	
	def atScanStart(self):
		return
	
	def atScanEnd(self):
		return
	
	def getPosition(self): 
		return self.getCurrent()
	
	def asynchronousMoveTo(self, newCurrent):
		self.pulse(newCurrent)
		return
	
	def isBusy(self):
		return self.iambusy
	
	def isOnNotOff(self):
		if self.chIsOnOff.caget() == 0:
				return False
		return True
	
	def turnOn(self):
		if not self.isOnNotOff():
			if self.verbose:
				print self.name + " is Off, turning On..."
			self.chOnOff.caput(1)
		elif self.verbose:
			print self.name + " is already Off"

	def turnOff(self):
		if self.isOnNotOff():
			if self.verbose:
				print self.name + " is On, turning Off..."
			self.chOnOff.caput(1)
		elif self.verbose:
			print self.name + " is already On"

#exec('[magPulse]=[None]')
#magPulse=BipolarPS('magPulse', pvBase = 'BL06I-PC-CTRL-01')

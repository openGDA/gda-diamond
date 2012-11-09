from gda.epics import CAClient
from java import lang
from time import sleep

class SampleChanger(PseudoDevice):
	'''Create PD to operate row 3 of the Sample Changer'''
	def __init__(self, name, pvstring):
		self.setName(name);
		self.state=0
		self.nextmove=0
		self.setOutputFormat(["%s","%s","%s","%s","%s","%s"])
		self.setInputNames(["1","2","3","4","5","6"])
		self.banks=[]
		for i in [32,33,34,36,37,38]:
			foo=CAClient(pvstring+":TEMP"+i.__str__())
			foo.configure()
			self.banks.append(foo)
		self.heater=CAClient(pvstring+":HEATER3:SET")
		self.heater.configure()
		self.heaterprobe=CAClient(pvstring+":TEMP3:SEL:SET")
		self.heaterprobe.configure()
		self.temp=CAClient(pvstring+":TEMP35")
		self.temp.configure()
		self.tempdemand=CAClient(pvstring+":TEMP3:SET")
		self.tempdemand.configure()

	def heaterOff(self):
		self.heater.caput("Off")

	def heaterOn(self):
		self.heater.caput("On")
		self.heaterprobe.caput("Centre")

	def getPosition(self):
		temps=[]
		for b in self.banks:
			temps.append((b.caget()))
		return temps
	
	def asynchronousMoveTo(self,p):
		self.nextmove=float(p)
		t=float(self.temp.caget())
		self.tempdemand.caput(float(p))
		if (p==t):
			self.heaterOn()
			self.state=0
		if (p>t):
			self.heaterOn()
			self.state=1
		if (p<t):
			self.heaterOff()
			self.state=-1

	def isBusy(self):
		if (self.state==0):
			self.heaterOn()
			return 0
		if (self.state > 0):
			if (float(self.temp.caget()) >= self.nextmove):
				self.heaterOn()
				return 0
			else:
				return 1
		if (self.state < 0):
			if (float(self.temp.caget()) <= self.nextmove):
				self.heaterOn()
				return 0
			else:
				return 1
	
samch=SampleChanger("samch","BL22I-EA-SAMPC-01")

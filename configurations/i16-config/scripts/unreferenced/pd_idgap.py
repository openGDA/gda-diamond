from gda.device.scannable import PseudoDevice
from gda.epics import CAClient
from time import sleep

class IDGapFromPVClass(PseudoDevice):
	'''Create device to control ID gap etc'''
	def __init__(self, name, mingap, pvinstring, pvoutstring, pvexecutestring, pvstatestring, pvstopstring, unitstring, formatstring):
		self.setName(name);
		self.mingap=mingap
		self.setInputNames([name])
		#self.setExtraNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)
		self.incli=CAClient(pvinstring)
		self.incli.configure()
		self.outcli=CAClient(pvoutstring)
		self.outcli.configure()
		self.executecli=CAClient(pvexecutestring)
		self.executecli.configure()
		self.statecli=CAClient(pvstatestring)
		self.statecli.configure()
		self.stopcli=CAClient(pvstopstring)
		self.stopcli.configure()

	def getPosition(self):
		try:
			#print 'Returned position sring: '+self.outcli.caget()
			return float(self.outcli.caget())
		except:
			print "Error returning ID gap position"
			return 0

	def asynchronousMoveTo(self,new_position):
		if new_position>=self.mingap:
			try:
				self.incli.caput(new_position)
				self.executecli.caput(1)
				sleep(0.5)
				self.executecli.caput(0)
				sleep(0.5)
			except:
				print "error moving to position"
		else:
			print "=== Requested gap is less than the minimum gap of "+str(self.mingap)+" mm: Gap not changed"

	def isBusy(self):
		try:
			self.status=self.statecli.caget()
			#print "IsMovingString : "+self.status
			return int(float(self.status))
		except:	
			print "Device: "+self.getName()+"  Problem with isMoving string: "+self.status+": Returning busy status"
			return 1
	
	def stop(self):
		print "calling stop"
		self.stopcli.caput(1)

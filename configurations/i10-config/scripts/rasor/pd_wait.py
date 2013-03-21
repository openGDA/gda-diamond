from gda.device.scannable import PseudoDevice
from time import sleep

class WaitPD(PseudoDevice):
	'''
	PD to wait for beam during scan
	Returns 1 if beam OK
	If beam lost then wait for beam and return 0 to indicate a beam trip
	Fill cryocooler if necessary
	self.min is the attribute containing the min value
	'''
	def __init__(self, name,time_to_wait):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([]);
		self.Units=[]
		#self.setOutputFormat(['%.0f'])
		self.setLevel(6)
		self.waittime=time_to_wait
		

	def getPosition(self):
		print "waiting"
		sleep(self.waittime)
		
	def isBusy(self):
		return 0	

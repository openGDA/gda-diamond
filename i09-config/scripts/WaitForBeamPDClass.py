from gda.device.scannable import ScannableBase
from time import sleep
import time

class WaitForBeamPDClass(ScannableBase):
	'''
	PD to wait for beam during scan
	Returns 1 if beam OK
	If beam lost then wait for beam and return 0 to indicate a beam trip
	Fill cryocooler if necessary
	'''
	def __init__(self, name,pd_to_monitor, minval):
		self.setName(name);
		self.setInputNames([])
		self.pd=pd_to_monitor
		self.setExtraNames(['beamOK']);
		self.Units=[]
		self.setOutputFormat(['%.0f'])
		self.setLevel(6)
		self.min=minval
		self.lastcheck=1

	def getPosition(self):
		while 1:
			if self.pd.getPosition()>self.min:
				if self.lastcheck==1:
					return 1
				else:
					self.lastcheck=1
					print '===  Beam back at: '+time.ctime()
					return 0
			else:
				self.lastcheck=0
				print '===  Waiting for beam at: '+time.ctime()
				sleep(120)
	
	def isBusy(self):
		return 0	

	def atStart(self):
		print '===Beam checking is on: '+self.pd.getName()+' must exceed '+str(self.min)
		self.lastcheck=1
  

#checkbeamcurrent=WaitForBeamPDClass('BeamOK',rc,10)
checkbeam=WaitForBeamPDClass('BeamOK',Io,10) #@UndefinedVariable
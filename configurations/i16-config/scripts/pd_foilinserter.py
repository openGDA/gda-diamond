from gda.epics import CAClient
from gda.device.scannable import ScannableMotionBase
from mathd import exp

class Foilinserter(ScannableMotionBase):
	"""
	Class to communicate with the Foil inserters
	"""
	def __init__(self,name,pvstring,pvstatus,mat,thickness):
		self.name =name
		self.setExtraNames(["Transmission"])
		self.setOutputFormat(['%4.6f', '%4.6f'])
		self.pvstring=pvstring
		self.pvstatus=pvstatus
		self.mat = mat
		self.thickness = thickness #[microns]
		self.configure()
		self.target = None

	def configure(self):
		self.status=CAClient(self.pvstatus)
		self.status.configure()	
		self.client=CAClient(self.pvstring)
		self.client.configure()	

	def isBusy(self):
		return self.target is not None and int(self.status.caget()) != self.target
	
	def getPosition(self):
		self.getTransmission()
		status=self.status.caget()
		if status == '0':
			return [0, 1]
		elif status == '1':
			return [1, self.trans]
		else:
			return [None, None]

	def asynchronousMoveTo(self,n):
		if n=='in' or n=='IN' or n=='1' or n==1:
			self.target = 1
			self.client.caput('1')
		elif n=='out' or n=='OUT' or n=='0' or n==0:
			self.target = 0
			self.client.caput('0')

	def getTransmission(self,_energy=None):
		self.mat.getXproperties(_energy)
		self.trans = exp(-self.thickness/self.mat.AttenLength*1e4)
		return self.trans
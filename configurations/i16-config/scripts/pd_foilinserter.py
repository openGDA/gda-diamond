from inttobin import *
from gda.epics import CAClient
import string 
import beamline_info as BLi
from gda.device.scannable import ScannableMotionBase
import time
from time import sleep
from mathd import *

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

	def configure(self):
		self.status=CAClient(self.pvstatus)
		self.status.configure()	
		self.client=CAClient(self.pvstring)
		self.client.configure()	

	def isBusy(self):
		#sleep(1)
		return 0
	
	def getPosition(self):
		#start = time.clock()
		self.getTransmission()
		status=self.status.caget()
		#end = time.clock()
		#print "time taken = ", end-start
		if status == '0':
			return [0, 1]
		elif status == '1':
			return [1, self.trans]
		else:
			return [None, None]

	def asynchronousMoveTo(self,n):
		if n=='in' or n=='IN' or n=='1' or n==1:
			self.client.caput('1')
		elif n=='out' or n=='OUT' or n=='0' or n==0:
			self.client.caput('0')

	def movein(self):
		self.asynchronousMoveTo('in')
		if self.getPosition() == '1':
			return 'IN'
		elif self.getPosition() == '0':
			return 'OUT'

	def moveout(self):
		self.asynchronousMoveTo('out')
		if self.getPosition() == '1':
			return 'IN'
		elif self.getPosition() == '0':
			return 'OUT'

	def getTransmission(self,_energy=None):
		self.mat.getXproperties(_energy)
		self.trans = exp(-self.thickness/self.mat.AttenLength*1e4)
		return self.trans
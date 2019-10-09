# from JythonScannable import JythonPseudoDevice
from javashell import *

from gda.device.scannable import PseudoDevice

import beamline_objects as BLobjects
from Jama import Matrix

from jarray import array
from java.lang import String
from mathd import *
 
class thetatth(PseudoDevice):
	'''Theta 2 Theta Device'''
	def __init__(self,name,motor1,motor2,offset1,offset2,help=None):
		if help is not None: self.__doc__='\nHelp specific to '+name+':\n'+help
		self.setName(name)
		self.setInputNames(["theta","twotheta"])
		self.setExtraNames([])
		#self.setOutputFormat(["%4.4f","%4.4f","%4.4f","%4.4f"])
		self.setOutputFormat(["%4.4f","%4.4f"])
		self.key1=motor1
		self.key2=motor2

		self.offset1=offset1 
		self.offset2=offset2 
	


	def asynchronousMoveTo(self,new_position):
		angle1 =float(new_position[0])+self.offset1()
		angle2 =float(new_position[1])+self.offset2()
		#self.key1.asynchronousMoveTo(angle1)
		#self.key2.asynchronousMoveTo(angle2)
		self.key1.moveTo(angle1)
		self.key2.moveTo(angle2)

	def isBusy(self):
		if self.key1.isBusy()==1 or self.key2.isBusy()==1:
			xxx=1
		else:
			xxx=0 
		return xxx

	def getPosition(self):
		xxx1=self.key1()-self.offset1()
		xxx2=self.key2()-self.offset2()
		wl=BLi.getWavelength()
		Qperp=2*pi*( sind(xxx2-xxx1)+sind(xxx1))/wl
		Qpar=2*pi*( cosd(xxx2-xxx1)-cosd(xxx1))/wl
		#print Qperp,Qpar
#		print [Qperp*sind(chi()-90.),Qpar,Qperp*cosd(chi()-90.)]
#		return [xxx1, xxx2, Qperp, Qpar]
		return [xxx1, xxx2]




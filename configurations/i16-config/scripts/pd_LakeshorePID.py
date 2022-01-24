from gda.device.scannable import ScannableMotionBase
from misc_functions import  caput, caget
from time import sleep


class EpicsLakeshorePID(ScannableMotionBase):

	def __init__(self, name, readstring, writestring, unitstring, formatstring):
		self.setName(name);
		self.setInputNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)
		self.rstr=readstring
		self.wstr=writestring
		#self.Tset = 'unknown'

	def isBusy(self):
		sleep(0.5)
		return 0

	def getPosition(self):
		#caput('BL16I-EA-LS340-01:ASYN.AOUT',rstr)
		#Tset = caget('BL16I-EA-LS340-01:ASYN.AINP')
		#return Tset
		return [caget('BL16I-EA-LS340-01:P'),caget('BL16I-EA-LS340-01:I'),caget('BL16I-EA-LS340-01:D')]


	def asynchronousMoveTo(self,newPID):
		caput('BL16I-EA-LS340-01:P_S',newPID[0])
		sleep(2)
		caput('BL16I-EA-LS340-01:I_S',newPID[1])
		sleep(2)
		caput('BL16I-EA-LS340-01:D_S',newPID[2])
		sleep(2)

#	def asynchronousMoveTo(self,newPID):
#		self.pid = newPID
#		cmdstr = self.wstr
#		if len(newPID)>0:
#			cmdstr=cmdstr+', '+str(newPID[0])
#			if len(newPID)>1:
#				cmdstr=cmdstr+', '+str(newPID[1])
#				if len(newPID)>2:
#					cmdstr=cmdstr+', '+str(newPID[2])
#		caput('BL16I-EA-LS340-01:ASYN.AOUT',cmdstr)

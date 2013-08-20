from gda.device.scannable import PseudoDevice
from misc_functions import caput
class EpicsLSsetpoint(PseudoDevice):

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
		return 0

	def getPosition(self):
		#caput('BL16I-EA-LS340-01:ASYN.AOUT',self.rstr)
		#Tset = caget('BL16I-EA-LS340-01:ASYN.AINP')
		#return float(Tset)
		return self.Tset

	def asynchronousMoveTo(self,newT):
		self.Tset = newT
		cmdstr = self.wstr+', '+str(newT)
		caput('BL16I-EA-LS340-01:ASYN.AOUT',cmdstr)

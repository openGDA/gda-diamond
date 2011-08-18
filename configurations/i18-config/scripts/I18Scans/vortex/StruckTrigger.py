from gda.epics import CAClient 
from java import lang
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from time import sleep

#
#
#   Struck used when using an external pulse to trigger counting, i.e. using a hardware trigger to read 
#    the vortex detector and ion chambers
#   This class does does not set collection times etc.... it simply reads the 
#   counts of a given set of scalar channels
#
class StruckTrigger(ScannableBase):
	def __init__(self, name,pv1,channels,formatstring):
		# Basic names
		newname=name+str(channels[0])
		self.setName(name)
		self.setInputNames([newname])
		self.setLevel(9)
		self.pvstring =pv1
		self.setOutputFormat([formatstring]*len(channels))
		extraNames=[]
		for i in range(len(channels)-1):
			extraNames.append(name+str(channels[i]+1))
		self.setExtraNames(extraNames)
		# EPICS interface
		self.str1 = self.pvstring+".CNT" 
		self.configstr=self.pvstring+'.RATE' 
		self.counts=[]
		for i in range(len(channels)):
			str1 = self.pvstring +".S"+str(channels[i])    # counts in the channel
			self.counts.append(CAClient(str1))
		# Set the update rate to 60Hz
		self.rate=CAClient(self.configstr)
		self.rate.configure()
		self.rate.caput(60)
		self.rate.clearup()

	#
	# Return counts....Warning....this can read while still collecting....
	#
	def getPosition(self):
		value=[]	
		try:
			for i in range(len(self.counts)):
				self.counts[i].configure()
				val=float(self.counts[i].caget())
				value.append(val)
				self.counts[i].clearup()
			return value
		except:
			print "Error returning position"
			return 0

	#
	# Returns state of the struck
	#
	def isBusy(self):
			self.clock.configure()
			if self.clock.caget()=='0':
				return 0
			if self.clock.caget()=='1':
				return 1 
			self.clock.clearup()
			
	#
	# start collection
	#
	def start(self):
		self.clock.configure()
		self.clock.caput("1")
		self.clock.clearup()

	#
	# Stop collection
	# 
	def stop(self):
		try:
			self.clock.configure()
			self.clock.caput("0")
			self.clock.clearup()
		except:
			print "Struck::stop failure"


vortex_trigger=StruckTrigger('struck_channel','BL18I-EA-DET-03:SCALER',[7,8,9],"%4.4f")

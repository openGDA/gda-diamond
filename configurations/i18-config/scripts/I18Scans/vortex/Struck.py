from gda.epics import CAClient 
from java import lang
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from time import sleep

class Struck(ScannableBase):
	'''Create PD for single EPICS positioner'''
	def __init__(self, name,pv1,channel,formatstring):
		self.setName(name)
		self.setInputNames([name])
		self.setLevel(9)
		self.pvstring =pv1
		self.setOutputFormat([formatstring])
		self.str1 = self.pvstring+".CNT" 
		self.configstr=self.pvstring+'.RATE' 
		self.str2 = self.pvstring+".TP" # preset the counting time
		self.str3 =	self.pvstring+".G1" #Gate Control Preset clock
		self.str4 =	self.pvstring +".G"+str(channel) #gate Control Preset channel
		self.str5 = self.pvstring +".S"+str(channel)    # counts in the channel
		self.str6 = self.pvstring +".PR"+str(channel) # Logic, gate on the channel
		self.str7 = self.pvstring +".S1" # preset channel
		self.str8 = self.pvstring +".PR1" # Logic, gate on the channel
		self.clock=CAClient(self.str1)
		self.tp =CAClient(self.str2)
		self.gatepreset = CAClient(self.str3)
		self.chpreset = CAClient(self.str4)
		self.counts = CAClient(self.str5)
		self.chgate = CAClient(self.str6)
		self.ch1 =CAClient(self.str7)
		self.chgate1 = CAClient(self.str8)
		self.rate=CAClient(self.configstr)
		self.rate.configure()
		self.rate.caput(60)
		self.rate.clearup()

	#
	# Return counts....Warning....this can read while still collecting....
	#
	def getPosition(self):
		try:
			self.counts.configure()
			self.ch1.configure()
			self.chgate1.configure()
			#changed to float due to change in Jython type conversion SPC 22/2/07
			if  float(self.ch1.caget()) < float(self.chgate1.caget()):
				print 'Warning :Not finished counting '
			value= float(self.counts.caget())
			self.counts.clearup()
			self.ch1.clearup()
			self.chgate1.clearup()
			return value
			
		except:
			print "Error returning position"
			return 0

	#
	# Returns state of the struck
	#
	def isBusy(self):
			self.clock.configure()
			# Change string from 'Done' and 'Count'to '0' and '1' as something changed! SPC 22/2/07
			if self.clock.caget()=='0':
				return 0
			if self.clock.caget()=='1':
				return 1 
			self.clock.clearup()
			
	#
	# Collect for a given time. Starts timer
	#  
	def asynchronousMoveTo(self,new_position):
		try:
			self.clock.configure()
			self.tp.configure()
			self.tp.caput(new_position)
			self.clock.caput("1")
			self.tp.clearup()
			self.clock.clearup()
		except:
			print "Struck::asynchronousMoveTo error"

	#
	# Set collection Time
	#
	def setCollectionTime(self,collectionTime):
		self.tp.configure()
		self.tp.caput(collectionTime)
		self.tp.clearup()

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


vortex1=Struck('vortex1','BL18I-EA-DET-03:SCALER',7,"%.0f")

from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase

class Struck(ScannableMotionBase):
	'''Create PD for single EPICS positioner'''
	def __init__(self, name,pv1,channel,formatstring):
		self.setName(name)
		self.setInputNames([name])
		self.setLevel(9)
		self.pvstring =pv1
#		self.setInputNames(["name"])
#		self.setExtraNames([name+'_time'])
		self.setOutputFormat([formatstring])
#		self.setOutputFormat([formatstring,formatstring])
		self.str1 = self.pvstring+".CNT" 
# returns Count and Done, input 1 to start count, stop to stop
		self.configstr=self.pvstring+'.RATE' 
		self.str2 = self.pvstring+".TP" # preset the counting time
		self.str3 =	self.pvstring+".G1" #Gate Control Preset clock
		self.str4 =	self.pvstring +".G"+str(channel) #gate Control Preset channel
		self.str5 = self.pvstring +".S"+str(channel)    # counts in the channel
		self.str6 = self.pvstring +".PR"+str(channel) # Logic, gate on the channel
		self.str7 = self.pvstring +".S1" # preset channel
		self.str8 = self.pvstring +".PR1" # Logic, gate on the channel
		self.clock=   CAClient(self.str1)
		self.tp =   CAClient(self.str2)
		self.gatepreset = CAClient(self.str3)
		self.chpreset = CAClient(self.str4)
		self.counts = CAClient(self.str5)
		self.chgate = CAClient(self.str6)
		self.ch1 =CAClient(self.str7)
		self.chgate1 = CAClient(self.str8)
		self.rate =CAClient(self.configstr)
#to verify
		self.rate.configure()
		#self.rate.caput(60)
		self.rate.clearup()
		self.count_time=0
	
	def getPosition(self):
		try:
			self.counts.configure()
			self.ch1.configure()
			self.chgate1.configure()
#			changed to float due to change in Jython type conversion SPC 22/2/07
#			if  int(self.ch1.caget()) < int(self.chgate1.caget()):
			if  float(self.ch1.caget()) < float(self.chgate1.caget()):						 		
				pass
				#print "Warning:: preset time not reached"
				

			return float(self.counts.caget())
#			return [float(self.chgate1.caget())/5.0E7, float(self.counts.caget())]
			self.counts.clearup()
			self.ch1.clearup()
			self.chgate1.clearup()
		except:
			print "Error returning position"
			return 0

	def isBusy(self):
			self.clock.configure()
#			Change string from 'Done' and 'Count'to '0' and '1' as something changed! SPC 22/2/07
#			if self.clock.caget()=='Done':
			if self.clock.caget()=='0':
#				print 0
				return 0
#			if self.clock.caget()=='Count':
			if self.clock.caget()=='1':
#				print 1
				return 1 
			self.clock.clearup()
			
	def asynchronousMoveTo(self,new_position):
		try:
			self.count_time=new_position	#spc - set time as attribute
			self.clock.configure()
			self.tp.configure()
			self.tp.caput(new_position)
			self.clock.caput("1")
			self.tp.clearup()
			self.clock.clearup()
		except:
			print "Struck::asynchronousMoveTo error"

	def stop(self):
		try:
			self.clock.configure()
			self.clock.caput("0")
			self.clock.clearup()
		except:
			print "Struck::stop failure"

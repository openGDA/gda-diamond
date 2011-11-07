from gda.epics import CAClient 
from java import lang
from time import *

#
#
#  A class that determines if the beam is on or off
#  To be used by all scripts to pause and resume scans in the event of a beam dump
#  If the beam is found to be off - turn off the feedback system
#  If it is on - check the feedback system - if it is off turn it back on.
#  
# Example use is before each data point to check the beam is on and if not, keep checking every 2mins until it comes back...
# while(BeamMonitor.beamOn()==0):
#	print 'Beam lost : Pausing until resumed'
#	sleep(120)
#
#
#

#class BeamMonitorClass:
class BeamMonitorClass(PseudoDevice):
	def __init__(self,ringCurrentPV,ringModePV,feAbsorberPV,opticsHutchShutterPV,pitchFeedBackPV,rollFeedBackPV,topupCountDownPV):
		self.ringCurrent= CAClient(ringCurrentPV)
		self.ringCurrent.configure()
		self.ringMode = CAClient(ringModePV)
		self.ringMode.configure()
		self.feAbsorber= CAClient(feAbsorberPV)
		self.feAbsorber.configure()
		self.opticsHutchShutter= CAClient(opticsHutchShutterPV)
		self.opticsHutchShutter.configure()
		self.pitchFB= CAClient(pitchFeedBackPV)
		self.pitchFB.configure()
		self.rollFB= CAClient(rollFeedBackPV)
		self.rollFB.configure()
		self.topupPV= CAClient(topupCountDownPV)
		self.topupPV.configure()
		self.topupTest=0
		self.override=0
		self.fillingOverride=0
		self.delayAfterTopup=2.0
		self.timetocollect=1.0
		name='BeamMonitor'
		self.setName(name)
		self.setInputNames([])
		self.setExtraNames(['BeamMonitor'])
		self.setOutputFormat(["%d"])
		self.simulateTP = 0
		self.simTopCount = 0
		# highest priority ....should be checked first in list of a scan
		self.setLevel(1)

		print 'BeamMonitor with detector fill check on'
	#===========================================
	#
	# Check if beam is on
	# return 1 if true, 0 if not
	#
	#===========================================
	def beamOn(self):
		if(self.override==0):	
			returnvalue=1
			if(self.feAbsorber.caget()=='1' and float(self.ringCurrent.caget()) > 1.0 ):
			#if(self.feAbsorber.caget()=='1'  and self.ringMode.caget() =='4' and float(self.ringCurrent.caget()) > 1.0 ):
				self.selectBeamOnMode()
				returnvalue=1
			else:
				self.selectBeamOffMode()
				returnvalue=0
			return returnvalue
		else:
			return 1
	#===========================================
	# Override: When in shutdown, no beam and want 
 	# to return a "beamon" for scripts to run 
	# override=1 return false beamOn
	# override=0 check if beam is on  
	#============================================
	def setOverride(self,value):
		if(value==1):
			self.override=1
		else:
			self.override=0

	def getOverride(self):
		return	self.override

	#===========================================
	# Override: When in shutdown, no beam and want 
 	# to return a "beamon" for scripts to run 
	# override=1 return false beamOn
	# override=0 check if beam is on  
	#============================================
	def setFillingOverride(self,value):
		if(value==1):
			self.fillingOverride=1
		else:
			self.fillingOverride=0

	def getFillingOverride(self):
		return	self.fillingOverride
		
	def simulateTopUp(self, value):
		self.simulateTP = value
		self.simTopCount = 0

	#===========================================
	# Select BeamOn Mode
	# Turns off feedback if on
	#============================================
	def selectBeamOffMode(self):
		return
		#if(int(self.rollFB.caget())==1):
			#self.rollFB.caput(0)
		#if(int(self.pitchFB.caget())==1):
			#self.pitchFB.caput(0)

	#===========================================
	# Select BeamOn Mode
	# Turns on feedback if off
	#============================================
	def selectBeamOnMode(self):
		return
		#if(int(self.rollFB.caget())==0):
			#self.rollFB.caput(1)
		#if(int(self.pitchFB.caget())==0):
			#self.pitchFB.caput(1)

	# ===========================================
	# Check time to see if LN2 fill. 9-9:35
	# 1 if filling, 0 if not
	# ===========================================
	def isFilling(self):
		if(self.fillingOverride==0):
			mytime=localtime()
			if(mytime[3]==9):
				if(mytime[4]>=0 and mytime[4]<=30):
					return 1
		
		return 0

	#
	# 1 if topup is too close to collect data
	# 0 if it is ok to collect
	#
	def collectBeforeTopupTime(self,collection=1.0,offset=1.0):		
		# In the event of a fault ignore the topup message
#		if not self.topupPV.isConfigured():
#			self.topupPV.configure()
		self.simTopCount = self.simTopCount + 1
		#print "simCount " + str(self.simTopCount)
		#topup simulation
		if(self.simulateTP ):
			if(7 <= self.simTopCount <= 8):
				print "topup returned true"
				self.topupTest = 1
				self.simTopCount = -1
				return 1
			else:
				# After the topup variable has reset, want to wait for a delaytime before starting collection again
				if(self.topupTest==1):
					print "delay after topup"
					sleep(self.delayAfterTopup)
					self.topupTest=0
				return 0
		
		if(float(self.topupPV.caget())<0):
			return 0
		if(float(self.topupPV.caget())<(collection+offset)):
			self.topupTest=1
			return 1
		else:
			# After the topup variable has reset, want to wait for a delaytime before starting collection again
			if(self.topupTest==1):
				sleep(self.delayAfterTopup)
				self.topupTest=0
			return 0


	#
	# Return time before topup occurs
	#
	def timeBeforeTopup(self):
		return float(self.topupPV.caget())


	def getPosition(self):
		#while(self.isBusy()==1):
		#	sleep(1)
		return 1


	def asynchronousMoveTo(self,newPosition):
		self.timetocollect=newPosition

	def isBusy(self):
		if(self.beamOn()==0 or self.collectBeforeTopupTime(self.timetocollect)==0):
			return 1
		else:
			return 0	
			
					 
BeamMonitor = BeamMonitorClass('SR21C-DI-DCCT-01:SIGNAL','CS-CS-MSTAT-01:MODE','FE18I-RS-ABSB-02:STA','FE18I-PS-SHTR-02:STA','BL18I-OP-DCM-01:FPMTR:FFB.FBON','BL18I-OP-DCM-01:FRMTR:FFB.FBON','SR-CS-FILL-01:COUNTDOWN')

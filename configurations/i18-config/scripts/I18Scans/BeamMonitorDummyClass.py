from gda.epics import CAClient 
from java import lang
#from time import *

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

class BeamMonitorClass:
	def __init__(self):
		self.topupTest=0
		self.override=0
		self.fillingOverride=0
		self.delayAfterTopup=2.0
		print 'BeamMonitor Dummy'

	#===========================================
	#
	# Check if beam is on
	# return 1 if true, 0 if not
	#
	#===========================================
	def beamOn(self):
		returnvalue=1
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


	# ===========================================
	# Check time to see if LN2 fill. 9-9:30 
	# 1 if filling, 0 if not
	# ===========================================
	def isFilling(self):
		return 0
	#
	# 1 if topup is too close to collect data
	# 0 if it is ok to collect
	#
	def collectBeforeTopupTime(self,collection=1.0):
		return 0


	#
	# Return time before topup occurs
	#
	def timeBeforeTopup(self):
		return 10000000.0

			
					 
BeamMonitor = BeamMonitorClass()


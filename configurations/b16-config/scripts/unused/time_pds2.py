#
# A collection of pds which can be used in scans to help time the scan steps.
# To create the pds simply type: run time_pds
#

from time import sleep
from java import lang
from gda.jython.scannable import ScannableMotionBase
from gda.jython.scannable import Scannable
import time

class tictoc:
	"""Class tictoc. Creates new timer object.
	__call__ returns numerical value of elapsed time in seconds since initialization
	__repr__ returns a mesage containing the elapsed time
	reset resets timer
	e.g. t1=tictoc()  -  create a new timer
	t1 -  display elapsed time"""

	def __init__(self):
		print 'Creating new timer'
		self.starttime=time.clock();
	def reset(self):
		self.starttime=time.clock();
		return 'Resetting timer'	
	def __call__(self):
		return time.clock()-self.starttime;
	def __repr__(self):
		return 'Elapsed time: %.4g seconds' % (time.clock()-self.starttime)


class showtimeClass(ScannableMotionBase):
	"""showtimeClass - show time since initialization or atStart. Useful for timing scan points"""
	def __init__(self, name):
		self.setName(name);
		self.setInputNames(['Elapsed'])
		self.Units=['sec']
		self.setOutputFormat(['%6.2f'])
		self.setLevel(7)
		self.timer=tictoc()
		self.waitUntilTime = 0

	def atStart(self):
		#print "Reseting timer"
		self.timer.reset()

	def getPosition(self):
		#print "Returning time"
		return self.timer()

	def asynchronousMoveTo(self,waitUntilTime):
		#print "Changing waitUntilTimer to: ", waitUntilTime
		self.waitUntilTime=waitUntilTime

	#def stop(self):
	#	self.waitUntilTime = 0

	def isBusy(self):
		#print "Checking isBusy"
		if self.timer()<self.waitUntilTime:
			#print "Is busy"
			return 1
		else:
			#print "Is not busy"
			return 0
	

class showincrementaltimeClass(ScannableMotionBase):
	'''showtimeClass - show time since initialization or atStart. Useful for timing scan points'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames(['Elapsed']);
		self.Units=['sec']
		self.setOutputFormat(['%6.2f'])
		self.setLevel(7)
		self.timer=tictoc()

	def getPosition(self):
		t=self.timer()
		self.timer.reset()
		return t

	def isBusy(self):
		return 0
	
	def atStart(self):
		self.timer.reset()



class waittimeClass(ScannableMotionBase):
	'''waittimeClass - waits for elapsed time. Use as dummy counter in scans etc'''
	
	def __init__(self, name):
		self.setName(name);
		self.setInputNames(['Time'])
		self.Units=['sec'];
		self.setOutputFormat(['%6.2f'])
		self.setLevel(7)
		self.timer=tictoc()
		self.waitfortime=0
		self.currenttime=0

	def asynchronousMoveTo(self,waittime):
		self.currenttime=self.timer()
		self.waitfortime=self.currenttime+waittime

	def getPosition(self):
		return self.timer()-self.currenttime

	def isBusy(self):
		if self.timer()<self.waitfortime:
			return 1
		else:
			return 0


if __name__ == "__main__":
	showtime=showtimeClass('Showtime')
	inctime=showincrementaltimeClass('inctime')
	waittime=waittimeClass('Waittime')
	w=waittime	#abreviated name
	print "finished time_utilities"

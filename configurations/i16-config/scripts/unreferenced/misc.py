from time import sleep
from java import lang
from gda.device.scannable import PseudoDevice

import time

class tictoc(java.lang.Object):
	'''Class tictoc. Creates new timer object.
	__call__ returns numerical value of elapsed time in seconds since initialization
	__repr__ returns a mesage containing the elapsed time
	reset resets timer
	e.g. t1=tictoc()  -  create a new timer
	t1 -  display elapsed time'''

	def __init__(self):
		print 'Creating new timer'
		self.starttime=time.clock();
	def reset(self):
		print 'Resetting timer'
		self.starttime=time.clock();	
	def __call__(self):
		return time.clock()-self.starttime;
	def __repr__(self):
		return 'Elapsed time: %.4g seconds' % (time.clock()-self.starttime)


class showtimeClass(PseudoDevice):
	'''showtimeClass - show time since initialization or atStart. Useful for timing scan points'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames(['Elapsed']);
		self.Units=['sec'];
		self.setOutputFormat(['%6.2f'])
		self.setLevel(7)
		self.timer=tictoc()

	def getPosition(self):
		return self.timer()

	def isBusy(self):
		return 0
	
	def atScanStart(self):
		self.timer.reset()

class waittimeClass(PseudoDevice):
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
	

class dummyClass(PseudoDevice):
	'''Dummy PD Class'''
	def __init__(self, name):
		self.setName(name)
		self.setInputNames(['value'])
		self.Units=['Units']
		self.setOutputFormat(['%6.3f'])
		self.setLevel(3)
		self.currentposition=0

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,new_position):
		self.currentposition = new_position

	def getPosition(self):
		return self.currentposition


dummy = dummyClass('Dummy')
x = dummyClass('x')
showtime=showtimeClass('Showtime')
waittime=waittimeClass('Waittime')


from gda.device.scannable import ScannableMotionBase

import time


class tictoc:
	'''Class tictoc. Creates new timer object.
	__call__ returns numerical value of elapsed time in seconds since initialization
	__repr__ returns a mesage containing the elapsed time
	reset resets timer
	e.g. t1=tictoc()  -  create a new timer
	t1 -  display elapsed time'''

	def __init__(self):
	#	print 'Creating new timer'
		self.starttime=time.clock();
	def reset(self):
		self.starttime=time.clock();
		return 'Resetting timer'	
	def __call__(self):
		return time.clock()-self.starttime;
	def __repr__(self):
		return 'Elapsed time: %.4g seconds' % (time.clock()-self.starttime)


class showtimeClass(ScannableMotionBase):
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
		return self.timer()

	def isBusy(self):
		return 0
	
	def atScanStart(self):
		self.timer.reset()

class mrwolfClass(ScannableMotionBase):
	'''mrwolfClass - show clock time'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames(['Year','Month','Day','Hours','Minutes','Seconds']);
#		self.Units=['sec']
		self.setOutputFormat(['%4.0f','%2.0f','%2.0f','%2.0f','%2.0f','%2.0f'])
		self.setLevel(7)

	def getPosition(self):
		tt=time.localtime()
		return [tt[0], tt[1], tt[2], tt[3], tt[4],tt[5]]

	def isBusy(self):
		return 0
	
class absoluteTimeClass(ScannableMotionBase):
	'''absoluteTimeClass - show absolute time in seconds'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames(['TimeSec']);
#		self.Units=['sec']
		self.setOutputFormat(['%.3f'])
		self.setLevel(7)

	def getPosition(self):
		return time.clock()

	def isBusy(self):
		return 0

class absoluteTimeClassTwo(ScannableMotionBase):
	'''absoluteTimeClass - show absolute time in seconds'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames(['TimeFromEpoch']);
#		self.Units=['sec']
		self.setOutputFormat(['%.3f'])
		self.setLevel(7)

	def getPosition(self):
		return time.time()

	def isBusy(self):
		return 0

class showincrementaltimeClass(ScannableMotionBase):
	'''showtimeClass - show time since initialization or atStart. Useful for timing scan points'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames(['time_increment']);
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
	
	def atScanStart(self):
		self.timer.reset()

VERBOSE = False

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
		
	def waitWhileBusy(self):
		if VERBOSE:
			print "* %s - started waiting" % self.name
		while self.isBusy():
			time.sleep(.1)
		if VERBOSE:
			print "* %s - stopped waiting" % self.name
		
		
	def stop(self):
		print "Stopping clock"
		self.waitfortime=0
	
	
class TimeScannable(ScannableMotionBase):
	'''TimeScannable: to scan time with regular steps'''

	def __init__(self, name):
		self.setName(name);
		self.setInputNames(['Time'])
		self.Units=['sec'];
		self.setOutputFormat(['%6.2f'])
		self.setLevel(7)
		self.timer=tictoc()
		self.waitfortime=0

	def asynchronousMoveTo(self,newtime):
		self.waitfortime=newtime

	def getPosition(self):
		return self.timer()

	def isBusy(self):
		if self.timer()<self.waitfortime:
			return 1
		else:
			return 0

	def atScanStart(self):
		self.timer.reset()

	def stop(self):
		print "Stopping clock"
		self.waitfortime=0


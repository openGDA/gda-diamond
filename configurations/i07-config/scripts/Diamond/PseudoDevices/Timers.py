#
# A collection of timing utility which can be used to help time the scan steps.

from gda.device.scannable import ScannableBase;
from gda.device.detector import DetectorBase

from Diamond.Objects.Shutter import ShutterDeviceClass

import sys, time;
import random;

class TicToc:
	'''Class TicToc. Creates new timer object.
	__call__ returns numerical value of elapsed time in seconds since initialization
	__repr__ returns a mesage containing the elapsed time
	reset resets timer
	e.g. t1=TicToc()  -  create a new timer
	t1 -  display elapsed time'''

	def __init__(self):
		self.reset();
	def reset(self):
		self.starttime = time.clock();
		return 'Resetting timer'
	def __call__(self):
		return time.clock()-self.starttime;
	def __repr__(self):
		return 'Elapsed time: %.4g seconds' % (time.clock()-self.starttime)


class ShowTimeClass(ScannableBase):
	'''ShowtimeClass - show time since initialization or atStart. Useful for timing scan points'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([name])
#		self.setExtraNames(['Stopwatch']);
		self.Units = ['sec']
		self.setOutputFormat(['%6.2f'])
		self.setLevel(7)
		self.timer = TicToc()
		self.autoReset=True;

	def reset(self):
		return self.timer.reset();
	
	def asynchronousMoveTo(self, whatever):
		self.timer.reset();

	def getPosition(self):
		return self.timer()

	def isBusy(self):
		return 0

	def atScanStart(self):
		if self.autoReset:
			self.timer.reset();

class ShowClockClass(ScannableBase):
	'''ShowClockClass - show clock time'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames(['Year', 'Month', 'Day', 'Hours', 'Minutes', 'Seconds']);
#		self.Units=['sec']
		self.setOutputFormat(['%4.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f', '%2.0f'])
		self.setLevel(7);
		
		self.currentTime = time.localtime();

	def getPosition(self):
		self.currentTime = time.localtime();
		return [self.currentTime[0], self.currentTime[1], self.currentTime[2], self.currentTime[3], self.currentTime[4], self.currentTime[5]];

	def isBusy(self):
		return 0
	
	def toString(self):
 		self.getPosition();
		return str(self.currentTime[0]) + '.' + str(self.currentTime[1]) + '.' + str(self.currentTime[2]) +', ' + str(self.currentTime[3]) + ':'+ str(self.currentTime[4])+ ':'+ str(self.currentTime[5]);

class LineTimeClass(ScannableBase):
	'''LineTimeClass - show time since initialization or atStart. Useful for timing lines of scan points'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames(['LineInterval']);
		self.Units = ['sec']
		self.setOutputFormat(['%6.2f'])
		self.setLevel(7)
		self.timer = TicToc()

	def getPosition(self):
		return self.timer();

	def isBusy(self):
		return 0

	def atScanLineStart(self):
		self.timer.reset()


class PointTimeClass(ScannableBase):
	'''showtimeClass - show time since initialization or atStart. Useful for timing scan points'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames(['PointInterval']);
		self.Units = ['sec']
		self.setOutputFormat(['%6.2f'])
		self.setLevel(7)
		self.timer = TicToc()

	def getPosition(self):
		return self.timer();

	def isBusy(self):
		return 0

	def atPointStart(self):
		self.timer.reset()


class WaitTimerClass(ScannableBase):
	'''WaitTimeClass - waits for elapsed time. Use as dummy counter in scans etc'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames(['Time'])
		self.Units = ['sec'];
		self.setOutputFormat(['%6.2f'])
		self.setLevel(7)
		self.timer = TicToc();
		self.waittime = 1;
		self.currenttime = self.timer();
		self.waitfortime = self.currenttime + self.waittime;

	def asynchronousMoveTo(self, waittime):
		self.waittime = waittime;
		self.currenttime = self.timer();
		self.waitfortime = self.currenttime + waittime

	def getPosition(self):
		return self.timer()-self.currenttime

	def isBusy(self):
		if self.timer()<self.waitfortime:
			return 1
		else:
			return 0
		
	def stop(self):
		print "Stopping clock"
		self.waitfortime = 0


class ScanTimerClass(ScannableBase):
	'''ScanTimeClass: to scan time with regular steps'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames(['Timer'])
		self.Units = ['sec'];
		self.setOutputFormat(['%8.2f'])
#		self.setLevel(7)
		self.timer = TicToc()
		self.waitfortime = 0;

	def asynchronousMoveTo(self, newtime):
		self.waitfortime = newtime

	def getPosition(self):
		return self.timer()

	def isBusy(self):
		if self.timer() < self.waitfortime:
			return 1
		else:
			return 0

	def atScanStart(self):
		self.timer.reset()

	def stop(self):
		print "Stopping clock"
		self.waitfortime = 0;

class SoftCounterClass(DetectorBase, ShutterDeviceClass):
	'''SoftCounterClass - A dummy counter that can returns random counts'''
	DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);
	
	def __init__(self, name):
		self.setName(name);
#		self.setInputNames(['ExposureTime'])
		self.Units = ['sec'];
		self.setOutputFormat(['%6.2f'])
		self.setLevel(7);
		self.timer = TicToc();
		self.exposureTime = 1;
		self.currenttime = self.timer();
		self.waitfortime = self.currenttime + self.exposureTime;
		self.output=0;
		
		self.debug=False;
		ShutterDeviceClass.__init__(self);

# Detector implementations
	def getCollectionTime(self):
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos;

	def collectData(self):
		self.currenttime = self.timer();
		self.waitfortime = self.currenttime + self.exposureTime
		self.output = int(random.uniform(0, 1000));
		self.openShutter()

		if self.debug:
			print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		
		return;

	def prepareForCollection(self):
		if self.debug:
			print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		
		self.openShutter();
		
	def endCollection(self):
		if self.debug:
			print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.closeShutter();


	def readout(self):
		if self.debug:
			print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		return self.output;

	def getStatus(self):
		if self.timer()<self.waitfortime:
			return SoftCounterClass.DETECTOR_STATUS_BUSY
		else:
			return SoftCounterClass.DETECTOR_STATUS_IDLE;
	
	def createsOwnFiles(self):
		return False;

#Scannable implementations:	
#	def asynchronousMoveTo(self,newExpos):
#		self.setCollectionTime(newExpos)
#		self.collectData();

	def stop(self):
		print "Stopping clock"
		self.waitfortime = 0
		self.closeShutter();
		if self.debug:
			print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		
	def atCommandFailure(self):
		self.closeShutter();
		if self.debug:
			print "Debug: "+  sys._getframe().f_code.co_name +" is called";
			
	def atPointEnd(self):
		self.closeShutter();
		if self.debug:
			print "Debug: "+  sys._getframe().f_code.co_name +" is called";

	def atScanLineEnd(self):
		self.closeShutter();
		if self.debug:
			print "Debug: "+  sys._getframe().f_code.co_name +" is called";

	def atScanEnd(self):
		self.closeShutter();
		if self.debug:
			print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		
	def toString(self):
		#return str(self.readout());
		return 'Exposure Time: ' + str(self.exposureTime) + ' sec';

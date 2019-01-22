'''
module provides a class definition for creating a PseudoDevice from DummyEpicsMonitorDouble and a monitoring thread.
The thread is used to control the scan process that this object involved in. When this object reaches a specified maximum scan pauses; 
the scan would resume again only if this object reaches a specified minimum value.
 usage:
		temp = EpicsPVWithMonitorListener('temp', 'ME02P-MO-RET-01:ROT:TEMP', 'degree', '%.4.1f')
 
 more examples in pvmonitor.polarimeterTemperatureMonitor.py
		
Created on 15 Dec 2009

@author: fy65
'''

MAXTEMP=100.0
MINTEMP=50.0

from java.lang import Thread, Runnable
from time import sleep

from gda.device.scannable import ScannableMotionBase
from gda.jython import JythonServerFacade, JythonStatus


class DummyEpicsPVWithDummyEpicsMonitorDouble(ScannableMotionBase, Runnable):
	'''create a scannable that gets value from a DummyEpicsMonitorDouble instance and use it
	in a running thread to control the scan processing this object participates in.
	'''
	def __init__(self, name, dummyepicsmonitordouble, unitstring, formatstring):
		self.setName(name)
		self.setInputNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)
		self.dummyepicsmonitordouble=dummyepicsmonitordouble
		self.currenttemp=dummyepicsmonitordouble.getPosition()
		self.monitor=None
		self.thread=None
		self.runThread=False

	def atScanStart(self):
		'''prepare to start scan: creating channel, monitor, and start control thread'''
		if self.dummyepicsmonitordouble is not None:
			self.thread=Thread(self,"Thread: "+self.getName())
			self.runThread=True
			self.thread.start()
			
	def atScanEnd(self):
		'''clean up after scan finished successfully: remove monitor, destroy channel, and stop control thread'''
		if self.dummyepicsmonitordouble is not None:
			self.runThread=False
			self.thread=None
			
	def rawGetPosition(self):
		''' return current position.'''
		output=0.0
		if self.dummyepicsmonitordouble is not None:
			output=self.dummyepicsmonitordouble.getPosition()
		return output

	def rawAsynchronousMoveTo(self,position):  # @UnusedVariable
		'''Not implemented, this is only a monitoring object'''
		print "object " + self.getName()+" cannot be moved."
		return

	def rawIsBusy(self):
		'''monitoring object never busy'''
		return 0

	def run(self):
	#	print "Thread: " + self.getName() + " started"
		while (self.runThread):
			self.currenttemp = self.dummyepicsmonitordouble.getPosition()
			if (JythonServerFacade.getInstance().getScanStatus() == JythonStatus.RUNNING and self.currenttemp >= float(MAXTEMP)):
				JythonServerFacade.getInstance().pauseCurrentScan()	
				print "Scan paused as temperature " + self.getName() +" returns: "+str(self.currenttemp)
			elif (JythonServerFacade.getInstance().getScanStatus() == JythonStatus.PAUSED and self.currenttemp <= float(MINTEMP)):
				print "Scan resumed as temperature " + self.getName() +" returns: "+str(self.currenttemp)
				JythonServerFacade.getInstance().resumeCurrentScan()
			sleep(10)

	def stop(self):
		'''clean up after scan finished successfully: stop control thread on emergence stop or 
		unexpected crash. If required, can be used to manually clean up the object.'''
		if not self.thread == None:
			self.runThread=False
			self.thread=None

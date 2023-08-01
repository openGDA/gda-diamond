from contextlib import contextmanager
from datetime import datetime
from gda.device.scannable import ScannableMotionBase, ScannableStatus
from gda.observable import IObserver
from org.slf4j import LoggerFactory
import scisoftpy as dnp
from scisoftpy import plot as dpl
from threading import Timer
import time
from org.ejml import data

# Inspired by /dls_sw/i11-1/scripts/config_tests/slug_trigger.py and
# Live_plot_scannables from /dls_sw/i15-1/scripts/Xpdf/xpdfUtils.py

"""
TODO:	Add trimpoints support
		Find out why mark happens with 
		Document
		Get rid of the "Warning: replaced collection-1 in ROI list with current ROI"
		Make dev optional in start/stop & make it list
		Support multiple striptools
		
		Hook into reset_namespace
"""

class StriptoolManager():
	"""
	A class to manage StriptoolListener instances.

	Usage:
		>>> striptool=StripTool()
		>>> striptool.run(prop)
		>>> scan dummy1 1 5 1 w 0.2*i plot.getStriptoolTimeScannable() prop
		>>> striptool.stop(prop)
	"""
	

	def __init__(self, name = "Diode Trace", interval = 1):
		self.logger = LoggerFactory.getLogger("StriptoolManager:"+name)
		self.name = name
		self.interval = interval
		self.monitors = {}
		self.clear()
		self.start = time.time()
		self.timer = Timer(self.interval, self._update)

	def run(self, dev):
		if not self.monitors.has_key(dev.name):
			self.logger.info("Starting {} monitor", dev.name)
			self.monitors[dev.name]=dev
			self._update_axes()
			self._timer_start()
		else:
			self.logger.warn("Monitoring of {} already started", dev.name)

	def stop(self, dev=None):
		if dev == None:
			self.logger.info("Stopping all monitors on {}", self.name)
			monitors_to_remove = [monitor for monitor in self.monitors]
		else:
			if self.monitors.has_key(dev.name):
				monitors_to_remove = [dev.name]
			else:
				monitors_to_remove = []
				self.logger.warn("Monitoring of {} already stopped", dev.name)

		for monitor in monitors_to_remove:
			self.logger.info("Stopping {} monitor", monitor)
			del(self.monitors[monitor])

		if monitors_to_remove:
			self._update_axes()

		if len(self.monitors) == 0:
			self.logger.info("Last monitor stopped", monitor)
			self._timer_stop()
		else:
			self.logger.warn("Monitoring of {} already stopped", dev.name)

	def clear(self):
		self.data = dnp.array([])
		self.marks = dpl.roi_list()
		dnp.plot.clear(name=self.name)

	def mark_x_axis(self):
		t=self._now()
		try:
			y_min = min(self.data[-1][1:])
			y_len = max(self.data[-1][1:]) - y_min
			self.marks.append(dpl.roi.line(point=[t, y_min], length=y_len, angledegrees=90, name=datetime.now().strftime("%H:%M.%S %d/%m/%Y")))
		except:
			pass # Ignore marks before first data

	def getStriptoolTimeScannable(self, dev):
		if self.monitors.has_key(dev.name):
			t = self.monitors[dev.name].getStriptoolTimeScannable()
			self.logger.debug("Returning {} scannable", t.name)
			return t
		self.logger.error("The {} scannable is not being monitored", dev.name)

	def _update_axes(self):
		self.plot_title = "Striptool of " + ",".join([monitor for monitor in self.monitors])
		#self.y_labels = ["Lbl "+monitor for monitor in self.monitors]
		#self.y_axis_positions = ["left" for monitor in self.monitors]
		self.x_axis = "time/s"
		self.y_axes = [(monitor,"left" if i%2 == 0 else "right") for i,monitor in enumerate(self.monitors)]
		self.clear() # TODO: Fix work around of clearing dataset whenever monitors added/removed. 

	def _update(self):
		t = dnp.array([self._now()])
		d = dnp.array([self.monitors[monitor].getPosition() for monitor in self.monitors])
		self.logger.info("t={}, d={}", t, d)

		if len(self.data) == 0:
			self.data = dnp.concatenate([t,d])
		else:
			# TODO: Fix work around of clearing dataset whenever monitors added/removed.
			self.data = dnp.vstack([self.data,dnp.concatenate([t,d])])
			# When adding or removing an element this fails with "Datasets are not compatible"

			x = {self.x_axis:self.data.T[0]}
			y = [{self.y_axes[i]:(self.data.T[i+1],monitor)} for i,monitor in enumerate(self.monitors)]
	
			self.logger.info("x={}, y={}", x, y)
	
			dpl.clear()
			dpl.line(x, y, title=self.plot_title, name=self.name)
			bean = dpl.getbean(name=self.name)
			dpl.setrois(bean,self.marks)
			dpl.setbean(bean,name=self.name,warn=False)

		self.timer.run()

	def _timer_start(self):
		if self.timer.is_alive(): return
		self.timer.start()

	def _timer_stop(self):
		self.timer.cancel()
		self.timer = Timer(self.interval, self._update)

	def _now(self):
		return time.time() - self.start


@contextmanager
def striptool_of(dev):
	"""
	A ContextManager that creates a StriptoolListener for the duration of a context

	@param: device - The device to plot. Should be observable and callable (eg a scannable)

	Usage:
		>>> with striptool_of(diode) as plot:
		...  scan dummy1 1 5 1 w 0.2 plot.getStriptoolTimeScannable() diode
		...  plot.mark_x_axis() # add a line marking the current time
		>>> # plotting stops here
	"""
	logger = LoggerFactory.getLogger("striptool_of:%s" % dev.name)
	logger.info("Starting {} monitor", dev.name)
	listener = StriptoolListener(dev)
	listener.addIObserver()
	try:
		yield listener
		listener.plot()
	finally:
		logger.info("Stopping {} monitor", dev.name)
		listener.deleteIObserver()

class StriptoolListener(IObserver):
	"""Listener for scannable values that plots trace of history"""
	def __init__(self, dev, interval = 1):
		self.logger = LoggerFactory.getLogger("StriptoolListener:%s" % dev.name)
		self.name = "Striptool of " + dev.name
		self.plot_title ="Plot_title of " + dev.name
		self.start = time.time()
		self.data = dnp.array([])
		self.marks = dpl.roi_list()

		self.interval = interval
		self.next_plot = self.interval

		self.dev = dev
		self.min = 0
		self.max = 0

		self.current = dev()
		dnp.plot.clear(name=self.name)

	def update(self, source, event):
		self.logger.info("Update from {} scannable: {} ({})", source, event, type(event))
		if isinstance(event, ScannableStatus):
			self.logger.debug("Ignoring event of type ScannableStatus")
			return

		now = self.offset()
		if event > self.max: self.max = event
		if event < self.min: self.min = event

		t = dnp.array([now])
		d = dnp.array([event])
		self.logger.info("t={}, d={}", t, d)

		if len(self.data) == 0:
			self.data = dnp.concatenate([t,d])
		else:
			self.data = dnp.vstack([self.data,dnp.concatenate([t,d])])

		if now > self.next_plot:
			self.next_plot = now + self.interval
			self.plot()

	def plot(self):
		x = {"time/s":self.data.T[0]}
		y = [{(self.dev.name,"left"):(self.data.T[1],self.dev.name)}]
		self.logger.info("x={}, y={}", x, y)

		dpl.clear()
		dpl.line(x, y, title=self.plot_title, name=self.name)
		bean = dpl.getbean(name=self.name)
		dpl.setrois(bean,self.marks)
		dpl.setbean(bean,name=self.name,warn=False)

	def offset(self):
		return time.time() - self.start

	def mark_x_axis(self):
		t=self.offset()
		try:
			y_min = min(self.data[-1][1:])
			y_len = max(self.data[-1][1:]) - y_min
			self.marks.append(dpl.roi.line(point=[t, y_min], length=y_len, angledegrees=90, name=datetime.now().strftime("%H:%M.%S %d/%m/%Y")))
		except:
			pass # Ignore marks before first data

	def addIObserver(self):
		self.dev.addIObserver(self)

	def deleteIObserver(self):
		self.dev.deleteIObserver(self)

	def getStriptoolTimeScannable(self):
		return StriptoolTimeScannable(self.dev.name+"_striptool_time", self.start)


class StriptoolTimeScannable(ScannableMotionBase):
	"""Scannable whose value is the timedelta since a given start time"""
	def __init__(self, name, start):
		"""
		Create new offset scannable
		@param: name - The name of this scannable
		@param: start - The time the offset is measured against. Should be an
						instance of datetime.datetime
		"""
		self.name = name
		self.setInputNames([name])
		self.start = start
		self.setLevel(5)

	def getPosition(self):
		return time.time() - self.start

	def isBusy(self):
		return False

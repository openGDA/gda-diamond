from jarray import zeros
from org.python.core.util import StringUtil
from gda.device.scannable import ScannableBase
import threading

class TemperatureSocketDevice(ScannableBase):
	def __init__(self, name, address, port):
		self.address = address
		self.port = port
		self.socket = None
		self.stopped = True
		self.inputNames = []
		self.extraNames = ["Temperature"]
		self.outputFormat = ["%5.5g"]
		self.monitorThread = None
		self.current_position = -1
		self.name = name

	def start_read(self):
		if self.socket is not None:
			self.socket.close()
		self.socket = java.net.Socket(self.address, self.port)
		self.monitorThread = threading.Thread(None, self.monitor_output, "htc_temp_monitor", None)
		self.monitorThread.start()
		self.stopped = False

	def monitor_output(self):
		buffer = zeros(1024, 'b')
		stream = self.socket.getInputStream()
		try:
			while not (java.lang.Thread.currentThread().isInterrupted() or self.stopped):
				nread = stream.read(buffer)
				if nread < 128:
					out = StringUtil.fromBytes(buffer)
					self.current_position = float(out.split('\n')[0])

		finally:
			print "Temperature monitor stopped"

	def stop_read(self):
		self.stopped = True
		if self.socket is not None:
			self.socket.close()
		if self.monitorThread is not None:
			self.monitorThread.join()

	def asynchronousMoveTo(self, position):
		pass

	def isBusy(self):
		return False

	def getPosition(self):
		return self.current_position

""" #########################################################################################################
Pseudo device which allows communication from epics for both jython with gda, and python in linux 
provides: caget, caput, cagetWaveform, cagetString
for python only callbacks can be added

David Burn - 13/7/16

######################################################################################################### """


def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		pass
 
	try:
		import unicodedata
		unicodedata.numeric(s)
		return True
	except (TypeError, ValueError):
		pass

	return False

""" ##################################################################################################### """

class PythonEpicsDevice:
	import epics
	def __init__(self, rootPV=None):
		
		if rootPV == None:
			self.device = None
		else:
			self.device = self.epics.Device(rootPV, delim=":")

	def caget(self, pv):
		if self.device:
			return self.device.get(pv)
		else:
			return self.epics.caget(pv)

	def caput(self, pv, value):
		if self.device:
			self.device.put(pv, value)
		else:
			self.epics.caput(pv, value)
		return True



	def cagetWaveform(self, pv):
		if self.device:
			return (self.device.get(pv))
		else:
			return self.epics.caget(pv)

		

	def cagetString(self, pv):
		out = ""
		for i in self.device.get(pv):
			out = out + chr(i)
		return out

	def caputString(self, pv, value):
		out = [0]*256
		# camera fileames have length 256 characters
		i = 0
		for c in value:
			out[i] = ord(c)
			i = i + 1
		self.device.put(pv, out)
		return True
	
	def addCallback(self, attr, callback):
		self.device.add_callback(attr, callback)

#	def caputWaveform(self, pv, value):
#		return self.device.put(pv, str(value))
#


""" ##################################################################################################### """

import threading
import time

class JythonEpicsDevice:
	def __init__(self, rootPV):
		from gda.epics import CAClient

		self.rootPV = rootPV + ":"
		self.channel = CAClient();
		
		self.callbackSet = False
		self.t = None

			
	def caget(self, pv):
		#print "caget " + self.rootPV+pv
		return self.channel.caget(self.rootPV+pv)
	
	def caput(self, pv, value):
		self.channel.caput(self.rootPV + pv, value)
#		if is_number(value):
#			self.channel.caput(self.rootPV + pv, float(value))
#		else:
#			self.channel.putStringAsWaveform(self.rootPV + pv, value)		#not sure this should be here
		return True

	def cagetWaveform(self, pv):
		unicode = self.channel.cagetArray(self.rootPV+pv)
		output = []
		for entry in unicode: 
			output = output + [float(entry)]
		return output
	
	
	def cagetString(self, pv):
		out = ""
		for i in self.channel.cagetArray(self.rootPV+pv):
			out = out + chr(int(i))
		return str(out)
	
	
	def caputString(self, pv, value):
		self.channel.putStringAsWaveform(self.rootPV + pv, value)
		return True

	""" in the future add callback functionality with epics monitor """
	
	
#	def addCallback(self, attr, callback):
#		#self.dummyCallbackThread = jythonDummyCallback(self, attr, callback)
#		#t = Thread(self.dummyCallbackThread)
#		#self.callbackSet = True
##		self.t = jythonDummyCallback(self, attr, callback)
#		self.t.setDaemon(True)#
#		self.t.start()

#	def removeCallback(self):
#		#self.callbackSet = False
#		self.t.running = False


#	def caput2(self, pv, value):
#		self.channel.caput(self.rootPV + pv, value)
#		return True

#	def cagetArray(self, pv):
#		output = self.channel.cagetArray(self.rootPV+pv)
#		return output




#class jythonDummyCallback(threading.Thread):
#	
#	def __init__(self, parentDevice, attr, callback):
#		threading.Thread.__init__(self)
#		self.name = "dummyCallbackThread"
#		self.parentDevice = parentDevice
#		self.attr = attr
#		self.callback = callback
#		self.oldvalue = None
#		self.running = False
#		
#	def run(self):
#		print "running jython dummy callback thread"
#		self.running = True
#		self.oldValue = self.parentDevice.caget(self.attr)
#		
#		while (self.running == True):
#			print "alive = true 6"
#			newValue = self.parentDevice.caget(self.attr)
#			if (self.oldValue != newValue):
#				self.oldValue = newValue
#				self.callback(value = newValue)
#			time.sleep(1)




import os
if (os.name == "java"): 
	device = JythonEpicsDevice
else:
	device = PythonEpicsDevice







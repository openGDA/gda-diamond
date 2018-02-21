""" #########################################################################################################
Pseudo device which allows communication from epics for both jython with gda, and python in linux 
provides: caget, caput, cagetWaveform, cagetString
for python only callbacks can be added

David Burn - 17/8/16

######################################################################################################### """
import os

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

class EpicsDevice:
	def __init__(self, rootPV=None):
		if (os.name == "java"): 
			from gda.epics import CAClient
			self.CAClient = CAClient();
		else:
			import epics as CAClient
			self.CAClient = CAClient

		self.rootPV = ""
		self.device = None
		if rootPV:
			self.rootPV = rootPV + ":"

	def caget(self, pv):
		return self.CAClient.caget(self.rootPV+pv)

	def caput(self, pv, value):
		return self.CAClient.caput(self.rootPV+pv, value)

	def cagetWaveform(self, pv):
		if (os.name == "java"): 
			unicode = self.CAClient.cagetArray(self.rootPV+pv)
			output = [float(i) for i in unicode]
			return output
		else:
			return self.CAClient.caget(self.rootPV+pv)


	def cagetString(self, pv):
		if (os.name == "java"):
			out = ""
			for i in self.CAClient.cagetArray(self.rootPV+pv):
				out = out + chr(int(i))
			return str(out)
		else:
			out = ""
			for i in self.caget(pv):
				out = out + chr(i)
			return out


	def caputString(self, pv, value):
		out = [0]*256			# camera fileames have length 256 characters
		i = 0
		for c in value:
			out[i] = ord(c)
			i = i + 1
		return self.caput(pv, out)
		

	def addCallback(self, attr, callback):
		if (os.name == "java"):
			raise NameError('Callbacks not yet implemented in gda')
		else:
			self.CAClient.add_callback(attr, callback)








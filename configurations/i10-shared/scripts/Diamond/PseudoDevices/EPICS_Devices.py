#
# A collection of pseudo devices representing some Epics objects
#

from time import sleep
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient


#
# a pseudo device representing a PV.  It will not change the value of the
# PV, so is used simply for monitoring.
#
# Example usage:
# img2=DisplayEpicsPVClass('IMG02', 'BL16I-VA-IMG-02:P', 'mbar', '%.1e')
#
class DisplayEpicsPVClass(ScannableMotionBase):
	'''Create PD to display single EPICS PV'''

	def __init__(self, name, pvstring, unitstring, formatstring):
		self.setName(name);
		self.setInputNames([name])
		self.Units = [unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(8)
		self.outcli = CAClient(pvstring)

	def getPosition(self):
		self.outcli.configure()
		output = float(self.outcli.caget())
		output = self.getOutputFormat()[0] % output
		self.outcli.clearup()
		return float(output)

	def asynchronousMoveTo(self, position):
		return

	def isBusy(self):
		return 0


#
# a pseudo device representing an Epics positioner
#
# Example usage:
# diag1pos=SingleEpicsPositionerClass('diag1','BL16I-OP-ATTN-02:P:SETVALUE2.VAL','BL16I-OP-ATTN-02:P:UPD.D','BL16I-OP-#ATTN-02:POSN.DMOV','BL16I-OP-ATTN-02:MP:STOP.PROC','mm','%.2f')
#
class SingleEpicsPositionerClass(ScannableMotionBase):
	'''Create PD for single EPICS positioner'''

	def __init__(self, name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring):
		self.setName(name);
		self.setInputNames([name])
		self.Units = [unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.incli = CAClient(pvinstring)
		self.outcli = CAClient(pvoutstring)
		self.statecli = CAClient(pvstatestring)
		self.stopcli = CAClient(pvstopstring)

	def getPosition(self):
		try:
			self.outcli.configure()
			output = float(self.outcli.caget())
			self.outcli.clearup()
			return output
		except:
			print "Error returning position"
			return 0

	def asynchronousMoveTo(self, new_position):
		try:
			self.incli.configure()
			self.incli.caput(new_position)
			self.incli.clearup()
		except:
			print "error moving to position"

	def isBusy(self):
		try:
			self.statecli.configure()
			self.status = self.statecli.caget()
			self.statecli.clearup()
			return not int(self.status)
		except:
			print "problem with isMoving string: " + self.status + ": Returning busy status"
			return 1

	def stop(self):
		print "calling stop"
		self.stopcli.configure()
		self.stopcli.caput(1)
		self.stopcli.clearup()


#
# a pseudo device representing an Epics positioner but will not return the status of the PV.  This should
# be used where enquiring about the status during a scan causes network problems
#
# Example usage:
# finepitch=SingleEpicsPositionerNoStatusClass('finepitch','BL16I-MO-DCM-01:FPMTR:PINP','BL16I-MO-DCM-01:FPMTR:PREAD','dummystring','BL16I-MO-#DCM-01:FPMTR:PMOVE.PROC','urad','%.3f')
#
class SingleEpicsPositionerNoStatusClass(SingleEpicsPositionerClass):
	"Class for PD devices without status "

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self, new_position):
		try:
			self.new_position = new_position  # need this attribute for some other classes
			self.incli.configure()
			self.statecli.configure()
			self.incli.caput(new_position)
			self.statecli.caput('0')
			self.incli.clearup()
			self.statecli.clearup()
			sleep(0.5)
		except:
			print "error moving to position"


#
# a pseudo device representing an Epics positioner but bases the status on if
# the new value is close to the commanded position.
#
# Example usage:
# id_gap=SingleEpicsPositionerNoStatusClass2('ID_gap','SR16I-MO-SERVC-01:BLGSET','SR16I-MO-SERVC-01:CURRGAPD','SR16I-MO-#SERVC-01:ALLMOVE','SR16I-MO-SERVC-01:ESTOP','mm','%.3f',0.005)
#
class SingleEpicsPositionerNoStatusClassDeadband(SingleEpicsPositionerNoStatusClass):
	'EPICS device that obtains a status from a deadband'

	def __init__(self, name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring, deadband):
		self.deadband = deadband
		SingleEpicsPositionerNoStatusClass.__init__(self, name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring)

	def isBusy(self):
		try:
			if abs(self.new_position - self()) < self.deadband:
				return 0
			else:
				return 1
		except:
			print 'Warning - can''t get isBusy status. Perhaps new_position or deadband attrubutes not set?'
			return 0


class SingleChannelBimorphClass(ScannableMotionBase):
	'''Create PD for single EPICS Bimorph channel'''

	def __init__(self, name, pvinstring, pvoutstring, pvstatestring, unitstring, formatstring):
		self.setName(name);
		self.setInputNames([name])
		# self.setExtraNames([name]);
		self.Units = [unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.incli = CAClient(pvinstring)
		self.outcli = CAClient(pvoutstring)
		self.statecli = CAClient(pvstatestring)

	def atStart(self):
		if not self.incli.isConfigured():
			self.incli.configured()
			if not self.outcli.isConfigured():
				self.outcli.configured()
			if not self.statecli.isConfigured():
				self.statecli.configured()

	def getPosition(self):
		try:
			if self.outcli.isConfigured():
				output = float(self.outcli.caget())
			else:
				self.outcli.configure()
				output = float(self.outcli.caget())
				self.outcli.clearup()
			return output
		except:
			print("Error returning position")
			return 0

	def asynchronousMoveTo(self, new_position):
		try:
			if self.incli.isConfigured():
				self.incli.caput(new_position)
			else:
				self.incli.configure()
				self.incli.caput(new_position)
				self.incli.clearup()
		except:
			print("error moving to position")

	def isBusy(self):
		try:
			if self.statecli.isConfigured():
				self.status = self.statecli.caget()
			else:
				self.statecli.configure()
				self.status = self.statecli.caget()
				self.statecli.clearup()
			return int(self.status)
		except:
			print("problem with isMoving string: " + self.status + ": Returning busy status")
			return 1


from gda.epics import CAClient 
from java import lang
from gda.device.scannable import ScannableMotionBase

from time import sleep

class DisplayEpicsPVClass(ScannableMotionBase):
	'''Create PD to display single EPICS PV'''
	def __init__(self, name, pvstring, unitstring, formatstring):
		self.setName(name)
		self.setInputNames([])
		self.setExtraNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.cli=CAClient(pvstring)

	def atScanStart(self):
		if not self.cli.isConfigured():
			self.cli.configure()

	def getPosition(self):
		if self.cli.isConfigured():
			return float(self.cli.caget())
		else:
			self.cli.configure()
			return float(self.cli.caget())
			self.cli.clearup()

	def isBusy(self):
		return 0
	
	def atScanEnd(self):
		if self.cli.isConfigured():
			self.cli.clearup()

class DisplayEpicsPVArrayClass(ScannableMotionBase):
	'''Create PD to display single EPICS PV which return multiple
element values as an array of string in jython.  Users need to type
conversion e.g. to float element by element. '''
	def __init__(self, name, pvstring, unitstring, formatstring):
		self.setName(name)
		self.setInputNames([])
		self.setExtraNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.cli=CAClient(pvstring)

	def atScanStart(self):
		if not self.cli.isConfigured():
			self.cli.configure()

	def getPosition(self):
		if self.cli.isConfigured():
			return self.cli.cagetArray()
		else:
			self.cli.configure()
			return self.cli.cagetArray()
			self.cli.clearup()

	def isBusy(self):
		return 0
	# the atScanEnd() method is now optional, but good practice for scan.  
	def atScanEnd(self):
		if self.cli.isConfigured():
			self.cli.clearup()


#class DisplayEpicsPVClass(ScannableMotionBase):
#	'''Create PD to display single EPICS PV'''
#	def __init__(self, name, pvstring, unitstring, formatstring):
#		self.setName(name)
#		self.setInputNames([])
#		self.setExtraNames([name])
#		self.Units=[unitstring]
#		self.setOutputFormat([formatstring])
#		self.setLevel(3)
#		self.cli=CAClient(pvstring)

#	def getPosition(self):
#		self.cli.configure()
#		return float(self.cli.caget())
#		self.cli.clearup()
#
#	def isBusy(self):
#		return 0
	


#monoE=DisplayEpicsPVClass('monoE', 'BL16I-MO-DCM-01:EURB', 'keV', '%.3f')
#img2=DisplayEpicsPVClass('IMG02', 'BL16I-VA-IMG-02:P', 'mbar', '%.1e')
#pitch=DisplayEpicsPVClass('Pitch', 'BL16I-MO-DCM-01:PTMTR:MOT.RBV', 'V', '%.6f')
#roll=DisplayEpicsPVClass('Roll', 'BL16I-MO-DCM-01:RLMTR2:MOT.RBV', 'V', '%.6f')
diode1=DisplayEpicsPVClass('Roll', 'BL16I-DI-PHDGN-01:DIODE:I', 'V', '%.6f')

class SingleEpicsPositionerClass(ScannableMotionBase):
	'''Create PD for single EPICS positioner'''
	def __init__(self, name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring):
		self.setName(name)
		self.setInputNames([name])
		self.setExtraNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.incli=CAClient(pvinstring)
		self.outcli=CAClient(pvoutstring)
		self.statecli=CAClient(pvstatestring)
		self.stopcli=CAClient(pvstopstring)

	def atScanStart(self):
		if not self.incli.isConfigured():
			self.incli.configure()
		if not self.outcli.isConfigured():
			self.outcli.configure()
		if not self.statecli.isConfigured():
			self.statecli.configure()
		if not self.stopcli.isConfigured():
			self.stopcli.configure()

	def getPosition(self):
	#	try:
		if self.outcli.isConfigured():
#			if not isinstance(self.outcli.caget(),type(None)):
#			print self.outcli.caget()
			return float(self.outcli.caget())
		else:
			self.outcli.configure()
			output = float(self.outcli.caget())
			self.outcli.clearup()
			return output
	#	except Exception,e :
	#		print "error in getPosition", e.getMessage()

	def asynchronousMoveTo(self,new_position):
		if self.incli.isConfigured():
			self.incli.caput(new_position)
		else:
			self.incli.configure()
			self.incli.caput(new_position)
			self.incli.clearup()	
	

	def isBusy(self):
		#print "calling isBusy"
		if self.statecli.isConfigured():
			self.status=self.statecli.caget()
		else:
			self.statecli.configure()
			self.status=self.statecli.caget()
			self.statecli.clearup()	
#		print "status: "+self.status	
		if self.status=='1':
			return 0
		elif self.status=='0':
			return 1
		elif type(self.status)==type(None):
			return 1
			print "return type is >>> none"
		else:
			print 'Error: Unexpected state: '+self.status
#			raise
	def stop(self):
		if self.outcli.isConfigured():
			self.stopcli.caput(1)
 		else:
			self.stopcli.configure()
			self.stopcli.caput(1)
			self.stopcli.clearup()
		

#diag1=SingleEpicsPositionerClass('diag1','BL16I-OP-ATTN-02:P:SETVALUE2.VAL','BL16I-OP-ATTN-02:P:UPD.D','BL16I-OP-ATTN-02:P:DMOV','BL16I-OP-ATTN-02:MP:STOP.PROC','mm','%.2f')

#s1ctrset = SingleEpicsPositionerClass('s1ctr','BL16I-AL-SLITS-01:X:CENTER.VAL','BL16I-AL-SLITS-01:X:CENTER.RBV','BL16I-AL-SLITS-01:X:CENTER.DMOV','BL16I-AL-SLITS-01:X:CENTER.STOP','mm','%.2f')

#s1ctrpos = SingleEpicsPositionerClass('s1ctr','BL16I-AL-SLITS-01:X:CENTER.VAL','BL16I-AL-SLITS-01:X:CENTER.RBV','BL16I-AL-SLITS-01:X:CENTER.DMOV','BL16I-AL-SLITS-01:X:CENTER.STOP','mm','%.2f')

s1lpos = SingleEpicsPositionerClass('s1lpos','BL16I-AL-SLITS-01:XA.VAL','BL16I-AL-SLITS-01:XA.RBV','BL16I-AL-SLITS-01:XA.DMOV','BL16I-AL-SLITS-01:XA.STOP','mm','%.4f')

s1lset = SingleEpicsPositionerClass('s1lset','BL16I-AL-SLITS-01:XA.VAL','BL16I-AL-SLITS-01:XA.RBV','BL16I-AL-SLITS-01:XA.DMOV','BL16I-AL-SLITS-01:XA.STOP','mm','%.4f')

#State=1 if ready, 0 if moving
#need to stop motors on error; get propper State 

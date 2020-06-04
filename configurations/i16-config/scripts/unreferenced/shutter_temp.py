class Epics_Shutter(ScannableMotionBase):
	'''Create PD for single EPICS shutter'''
	def __init__(self, name, pvstring):
		self.setName(name);
		self.setInputNames([name])
		self.setOutputFormat(['%.0f'])
		self.setLevel(3)
		self.pvstring=pvstring

	def getPosition(self):
		self.cli=CAClient(self.pvstring)
		self.cli.configure()
		self.state=self.cli.caget()
		self.cli.clearup()
		if self.state=='0':
			print "Shutter open"
			return 1
		elif self.state=='1':
			print "Shutter closed"
			return 0
		elif self.state=='2':
			print "Shutter closed waiting for Reset"
			return 0
		else:
			print "Unknown state:",self.state
			raise

	def asynchronousMoveTo(self,new_position):
		if new_position>0.5:
			caput('BL16I-PS-SHTR-01:CON','Reset')
			sleep(.5)
			caput('BL16I-PS-SHTR-01:CON','Open')
		else:
			caput('BL16I-PS-SHTR-01:CON','Close')

	def isBusy(self):
		return 0

shutter= Epics_Shutter('shutter','BL16I-PS-SHTR-01:CON')

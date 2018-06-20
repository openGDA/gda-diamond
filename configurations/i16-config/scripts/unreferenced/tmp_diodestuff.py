class DisplayEpicsPVClassWithOffset(DisplayEpicsPVClass):
	'''Create PD to display single EPICS PV with persistent offset'''
	def getPosition(self):
		self.cli.configure()
		return float(self.cli.caget())-self.offsetval
		self.cli.clearup()

	def Darkcurrent(self):
		print "=== Measuring dark current (offset) value"
#		print "=== Old offset: "+str(self.offsetval)
		self.offsetval=0
		self.offsetval=self.getPosition()
		print "=== New offset: "+str(self.offsetval)
 
adctest1=DisplayEpicsPVClassWithOffset('adc1','BL16I-EA-USER-01:AI1AV','V','%6f'); 
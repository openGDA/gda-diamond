	def setResistance(self):
		print 'Resistance mode'
		keithpv=CAClient('BL16I-EA-SPARE-03:asyn.AOUT');keithpv.configure(); keithpv.caput(":FUNC 'RES'"); keithpv.clearup();
		self.setExtraNames(['Res_ohm'])
		
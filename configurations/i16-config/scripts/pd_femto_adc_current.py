from gda.device.scannable import PseudoDevice

class pd_femto_adc_current(PseudoDevice):
	'''Device to read current using femto amplifier and adc
	Femto switched to REMOTE, AC, 10Hz for remote operation
	Gains:\n10^3 low noise (0)\n10^4 low noise (1)\n10^5 low noise (2)\n10^6 low noise (3)\n10^7 low noise (4)\n10^8 low noise (5)\n10^9 low noise (6)\n10^5 high speed (8)\n10^6 high speed (9)\n10^7 high speed (10)\n10^8 high speed(11)\n10^9 high speed (12)\n10^10 high speed (13)\n10^11 high speed (14)\n
	pd=pd_femto_adc_current(name, adcpv, femtogainpv , factor, unitstring, formatstring)
	factor=scale factor for current (e.g. +/- 1e6 for microamps)
	use device.setGain(value) to set gain
	use device.getGain() to get gain
	'''
	def __init__(self, name, adcpv, femtogainpv , factor, unitstring, formatstring,help=None):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.setOutputFormat([formatstring])
		self.factor=factor
		self.unitstring=unitstring
		self.setLevel(9)
		self.adccli=CAClient(adcpv)
		self.adccli.configure()
		self.femtogaincli=CAClient(femtogainpv)
		self.femtogaincli.configure()
		self.gain_settings=[1e3,1e4,1e5,1e6,1e7,1e8,1e9,1e5,1e6,1e7,1e8,1e9,1e10,1e11]
		self.__doc__+='Units for current: '+self.unitstring
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.getGain()

	def getPosition(self):
		self.adcvolts=float(self.adccli.caget())
		if abs(self.adcvolts)>9.9:
			print "=== Warning: "+self.name+" out of range. Use setGain(value) to change. Type help "+self.name
		return self.adcvolts*self.gainval

	def getGain(self):
		gain_setting=int(self.femtogaincli.caget())
		self.gainval=self.factor/self.gain_settings[gain_setting]
		return gain_setting

	def setGain(self, newgainsetting):
		self.femtogaincli.caput(newgainsetting)
		print 'New gain: '+str(self.getGain())


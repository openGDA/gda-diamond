from gda.device.scannable import ScannableMotionBase

class pd_epics_femto_gain(ScannableMotionBase):
	'''Device to set femto amplifier gain
	input/output is an integer
	self.gain() is the numerical gain value
	'''
	def __init__(self,name,gains_list,femtogainpv,help=None):
		self.setName(name);
		self.setInputNames([name])
		self.setOutputFormat(['%.0f'])
		self.setLevel(9)
		self.gain_settings=gains_list
		self.femtogaincli=CAClient(femtogainpv)
		self.femtogaincli.configure()

	def getPosition(self):
		gain_setting=int(self.femtogaincli.caget())
		self.gain=self.gain_settings[gain_setting]
		return gain_setting

	def asynchronousMoveTo(self, newgainsetting):
		self.femtogaincli.caput(newgainsetting)

	def isBusy(self):
		return 0

	def gain(self):
		self()
		return self.gain

class pd_epics_femto_current(ScannableMotionBase):
	'''Device to read current using femto amplifier and adc
	Femto switched to REMOTE, AC, 10Hz for remote operation
	Gains:\n10^3 low noise (0)\n10^4 low noise (1)\n10^5 low noise (2)\n10^6 low noise (3)\n10^7 low noise (4)\n10^8 low noise (5)\n10^9 low noise (6)\n10^5 high speed (8)\n10^6 high speed (9)\n10^7 high speed (10)\n10^8 high speed(11)\n10^9 high speed (12)\n10^10 high speed (13)\n10^11 high speed (14)\n
	pd=pd_femto_adc_current(name, adcpv, femtogainpv , factor, unitstring, formatstring)
	use pos device.gain to get/set gain
	'''
	def __init__(self, name, adcpv, femtogainpd , unitstring, formatstring, help=None):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.setOutputFormat([formatstring])
		self.unitstring=unitstring
		self.setLevel(9)
		self.adccli=CAClient(adcpv)
		self.adccli.configure()
		self.__doc__+='Units for current: '+self.unitstring
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.gain=femtogainpd
		self.gain()

	def getPosition(self):
		self.adcvolts=float(self.adccli.caget())
		if abs(self.adcvolts)>9.9:
			print "=== Warning: "+self.name+" out of range - reduce gain. Type help "+self.name
		return self.adcvolts/self.gain.gain

	def isBusy(self):
		return 0

class pd_epics_femto_current_from_monitor(ScannableMotionBase):
	'''Device to read current using femto amplifier and adc
	Femto switched to REMOTE, AC, 10Hz for remote operation
	Gains:\n10^3 low noise (0)\n10^4 low noise (1)\n10^5 low noise (2)\n10^6 low noise (3)\n10^7 low noise (4)\n10^8 low noise (5)\n10^9 low noise (6)\n10^5 high speed (8)\n10^6 high speed (9)\n10^7 high speed (10)\n10^8 high speed(11)\n10^9 high speed (12)\n10^10 high speed (13)\n10^11 high speed (14)\n
	pd=pd_femto_adc_current(name, adcpv, femtogainpv , factor, unitstring, formatstring)
	use pos device.gain to get/set gain
	'''
	def __init__(self, name, monitor, femtogainpd , unitstring, formatstring, help=None):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.setOutputFormat([formatstring])
		self.unitstring=unitstring
		self.setLevel(9)
		self.mon = monitor
		self.__doc__+='Units for current: '+self.unitstring
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.gain=femtogainpd
		self.gain()

	def getPosition(self):
		self.adcvolts=self.mon()
		if abs(self.adcvolts)>9.9:
			print "=== Warning: "+self.name+" out of range - reduce gain. Type help "+self.name
		return self.adcvolts/self.gain.gain

	def isBusy(self):
		return 0


#[1e3*1e-6,1e4*1e-6,1e5*1e-6,1e6*1e-6,1e7*1e-6,1e8*1e-6,1e9*1e-6,1e5*1e-6,1e6*1e-6,1e7*1e-6,1e8*1e-6,1e9*1e-6,1e10*1e-6,1e11*1e-6]
#[1e3*1e-9,1e4*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e10*1e-9,1e11*1e-9]

diode=pd_epics_femto_current('diode','BL16I-EA-USER-01:AI1AV',pd_epics_femto_gain('diode_gain',[1e3*1e-6,1e4*1e-6,1e5*1e-6,1e6*1e-6,1e7*1e-6,1e8*1e-6,1e9*1e-6,1e5*1e-6,1e6*1e-6,1e7*1e-6,1e8*1e-6,1e9*1e-6,1e10*1e-6,1e11*1e-6],'BL16I-DI-FEMTO-03:GAIN'),'microamps','%.6f',help='diode: usually use gain 0 for direct beam')

bsdiode=pd_epics_femto_current('bsdiode','BL16I-EA-USER-01:AI1AV',pd_epics_femto_gain('diode_gain',[-1e3*1e-6,-1e4*1e-6,-1e5*1e-6,-1e6*1e-6,-1e7*1e-6,-1e8*1e-6,-1e9*1e-6,-1e5*1e-6,-1e6*1e-6,-1e7*1e-6,-1e8*1e-6,-1e9*1e-6,-1e10*1e-6,-1e11*1e-6],'BL16I-DI-FEMTO-03:GAIN'),'microamps','%.6f',help='beamstop diode (plug into Femto on detector arm): usually use gain 0 for direct beam')
#ic1=pd_epics_femto_current('ic1','BL16I-EA-USER-01:AI4AV',pd_epics_femto_gain('ic1_gain',[-1e3*1e-9,-1e4*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e10*1e-9,-1e11*1e-9],'BL16I-DI-FEMTO-01:GAIN',help='some help on ic1 gain'),'nanoamps','%.6f',help='ic1: He-filled ion chamber before attenuators. Gain typically around 5')

ic1=pd_epics_femto_current_from_monitor('ic1', ic1poll_ ,pd_epics_femto_gain('ic1_gain',[-1e3*1e-9,-1e4*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e10*1e-9,-1e11*1e-9],'BL16I-DI-FEMTO-01:GAIN',help='some help on ic1 gain'),'nanoamps','%.6f',help='ic1: He-filled ion chamber before attenuators. Gain typically around 5')
ic1monitor=pd_epics_femto_current_from_monitor('ic1monitor', ic1monitor_ ,pd_epics_femto_gain('ic1_gain',[-1e3*1e-9,-1e4*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e10*1e-9,-1e11*1e-9],'BL16I-DI-FEMTO-01:GAIN',help='some help on ic1 gain'),'nanoamps','%.6f',help='ic1: He-filled ion chamber before attenuators. Gain typically around 5')

ic2=pd_epics_femto_current('ic2','BL16I-EA-USER-01:AI6AV',pd_epics_femto_gain('ic2_gain',[-1e3*1e-9,-1e4*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e10*1e-9,-1e11*1e-9],'BL16I-DI-FEMTO-02:GAIN',help='some help on ic2 gain'),'nanoamps','%.6f',help='ic2: He-filled ion chamber after attenuators. Gain typically around 5')


#diode=pd_epics_femto_current('diode','BL16I-EA-USER-01:AI1AV',pd_epics_femto_gain('diode_gain',[-1e3*1e-6,-1e4*1e-6,-1e5*1e-6,-1e6*1e-6,-1e7*1e-6,-1e8*1e-6,-1e9*1e-6,-1e5*1e-6,-1e6*1e-6,-1e7*1e-6,-1e8*1e-6,-1e9*1e-6,-1e10*1e-6,-1e11*1e-6],'BL16I-DI-FEMTO-03:GAIN'),'microamps','%.6f',help='diode: usually use gain 0 for direct beam')

#bsdiode=pd_epics_femto_current('bsdiode','BL16I-EA-USER-01:AI1AV',pd_epics_femto_gain('diode_gain',[1e3*1e-6,1e4*1e-6,1e5*1e-6,1e6*1e-6,1e7*1e-6,1e8*1e-6,1e9*1e-6,1e5*1e-6,1e6*1e-6,1e7*1e-6,1e8*1e-6,1e9*1e-6,1e10*1e-6,1e11*1e-6],'BL16I-DI-FEMTO-03:GAIN'),'microamps','%.6f',help='beamstop diode (plug into Femto on detector arm): usually use gain 0 for direct beam')

#ic1=pd_epics_femto_current('ic1','BL16I-EA-USER-01:AI4AV',pd_epics_femto_gain('ic1_gain',[1e3*1e-9,1e4*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e10*1e-9,1e11*1e-9],'BL16I-DI-FEMTO-01:GAIN',help='some help on ic1 gain'),'nanoamps','%.6f',help='ic1: He-filled ion chamber before attenuators. Gain typically around 9')

#ic2=pd_epics_femto_current('ic2','BL16I-EA-USER-01:AI6AV',pd_epics_femto_gain('ic2_gain',[1e3*1e-9,1e4*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e10*1e-9,1e11*1e-9],'BL16I-DI-FEMTO-02:GAIN',help='some help on ic2 gain'),'nanoamps','%.6f',help='ic2: He-filled ion chamber after attenuators. Gain typically around 9')




#diode=adc1=DisplayEpicsPVClass('adc1','BL16I-EA-USER-01:AI1AV','V','%6f');diode.setLevel(9) #AV=average over pre-set number of readings (100 samples @ 1 kHz)
#adc2=DisplayEpicsPVClass('adc2','BL16I-EA-USER-01:AI2AV','V','%6f')
#ic1=adc4=DisplayEpicsPVClass('IC1','BL16I-EA-USER-01:AI4AV','V','%6f'); ic1.setLevel(9)
#ic2=adc6=DisplayEpicsPVClass('IC2','BL16I-EA-USER-01:AI6AV','V','%6f'); ic2.setLevel(9)

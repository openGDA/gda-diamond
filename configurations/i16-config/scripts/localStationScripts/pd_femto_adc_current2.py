from gda.device.scannable import ScannableMotionBase
import logging
import installation

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
		if femtogainpv:
			self.femtogaincli=CAClient(femtogainpv)
			self.femtogaincli.configure()
		else:
			self.femtogaincli=None

	def getPosition(self):
		if self.femtogaincli:
			gain_setting=int(self.femtogaincli.caget())
		else:
			gain_setting=5
			msg="No femto gain PV for %s, returning %d and setting gain to %f" % (
				self.name, gain_setting, self.gain_settings[gain_setting])
			print msg
			logging.getLogger("pd_epics_femto_gain:"+self.name).warning(msg)
		self.gain=self.gain_settings[gain_setting]
		return gain_setting

	def asynchronousMoveTo(self, newgainsetting):
		self.femtogaincli.caput(newgainsetting)

	def isBusy(self):
		return 0

	def gain(self):
		logging.getLogger("pd_epics_femto_gain:"+self.name).debug("gain()...")
		self()
		logging.getLogger("pd_epics_femto_gain:"+self.name).debug("gain() called self(), returning gain %d" % self.gain)
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

"""$caget -d31 BL16I-DI-FEMTO-03:GAIN
BL16I-DI-FEMTO-03:GAIN
    Native data type: DBF_ENUM
    Request type:     DBR_CTRL_ENUM
    Element count:    1
    Value:            10^3 low noise
    Status:           NO_ALARM
    Severity:         NO_ALARM
    Enums:            (14)
                      [ 0] 10^3 low noise
                      [ 1] 10^4 low noise
                      [ 2] 10^5 low noise
                      [ 3] 10^6 low noise
                      [ 4] 10^7 low noise
                      [ 5] 10^8 low noise
                      [ 6] 10^9 low noise
                      [ 7] 10^5 high speed
                      [ 8] 10^6 high speed
                      [ 9] 10^7 high speed
                      [10] 10^8 high speed
                      [11] 10^9 high speed
                      [12] 10^10 high spd
                      [13] 10^11 high spd
"""
#diode_gain_array=[1e3*1e-9,1e4*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e10*1e-9,1e11*1e-9]
diode_gain_array=[1e3*1e-6,1e4*1e-6,1e5*1e-6,1e6*1e-6,1e7*1e-6,1e8*1e-6,1e9*1e-6,1e5*1e-6,1e6*1e-6,1e7*1e-6,1e8*1e-6,1e9*1e-6,1e10*1e-6,1e11*1e-6]
#diode_gain_array=[-1e3*1e-6,-1e4*1e-6,-1e5*1e-6,-1e6*1e-6,-1e7*1e-6,-1e8*1e-6,-1e9*1e-6,-1e5*1e-6,-1e6*1e-6,-1e7*1e-6,-1e8*1e-6,-1e9*1e-6,-1e10*1e-6,-1e11*1e-6]

bsdiode_gains_list=[-1e3*1e-6,-1e4*1e-6,-1e5*1e-6,-1e6*1e-6,-1e7*1e-6,-1e8*1e-6,-1e9*1e-6,-1e5*1e-6,-1e6*1e-6,-1e7*1e-6,-1e8*1e-6,-1e9*1e-6,-1e10*1e-6,-1e11*1e-6]
#bsdiode_gains_list=[1e3*1e-6,1e4*1e-6,1e5*1e-6,1e6*1e-6,1e7*1e-6,1e8*1e-6,1e9*1e-6,1e5*1e-6,1e6*1e-6,1e7*1e-6,1e8*1e-6,1e9*1e-6,1e10*1e-6,1e11*1e-6]

if installation.isLive():
	diode=pd_epics_femto_current('diode','BL16I-EA-USER-01:AI1AV',
		pd_epics_femto_gain('diode_gain',diode_gain_array,'BL16I-DI-FEMTO-03:GAIN' if installation.isLive() else None),
		'microamps','%.6f',help='diode: usually use gain 0 for direct beam')
	
	bsdiode=pd_epics_femto_current('bsdiode','BL16I-EA-USER-01:AI1AV',
		pd_epics_femto_gain('diode_gain',bsdiode_gains_list,'BL16I-DI-FEMTO-03:GAIN' if installation.isLive() else None),
		'microamps','%.6f',help='beamstop diode (plug into Femto on detector arm): usually use gain 0 for direct beam')
else:
	diode=pd_epics_femto_current_from_monitor('diode',diode_,
		pd_epics_femto_gain('diode_gain',diode_gain_array,'BL16I-DI-FEMTO-03:GAIN' if installation.isLive() else None),
		'microamps','%.6f',help='diode: usually use gain 0 for direct beam')
	
	bsdiode=pd_epics_femto_current_from_monitor('bsdiode',diode_,
		pd_epics_femto_gain('diode_gain',bsdiode_gains_list,'BL16I-DI-FEMTO-03:GAIN' if installation.isLive() else None),
		'microamps','%.6f',help='beamstop diode (plug into Femto on detector arm): usually use gain 0 for direct beam')

"""$caget -d31 BL16I-DI-FEMTO-01:GAIN
BL16I-DI-FEMTO-01:GAIN
    Native data type: DBF_ENUM
    Request type:     DBR_CTRL_ENUM
    Element count:    1
    Value:            10^6 low noise
    Status:           NO_ALARM
    Severity:         NO_ALARM
    Enums:            (14)
                      [ 0] 10^3 low noise
                      [ 1] 10^4 low noise
                      [ 2] 10^5 low noise
                      [ 3] 10^6 low noise
                      [ 4] 10^7 low noise
                      [ 5] 10^8 low noise
                      [ 6] 10^9 low noise
                      [ 7] 10^5 high speed
                      [ 8] 10^6 high speed
                      [ 9] 10^7 high speed
                      [10] 10^8 high speed
                      [11] 10^9 high speed
                      [12] 10^10 high spd
                      [13] 10^11 high spd
"""

ic1_gains_list=[-1e3*1e-9,-1e4*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e10*1e-9,-1e11*1e-9]
#ic1_gains_list=[1e3*1e-9,1e4*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e10*1e-9,1e11*1e-9]

ic1=pd_epics_femto_current_from_monitor('ic1', ic1poll_ ,
	pd_epics_femto_gain('ic1_gain',ic1_gains_list,'BL16I-DI-FEMTO-01:GAIN' if installation.isLive() else None,help='some help on ic1 gain'),
	'nanoamps','%.6f',help='ic1: He-filled ion chamber before attenuators. Gain typically around 5')

ic1monitor=pd_epics_femto_current_from_monitor('ic1monitor', ic1monitor_ ,
	pd_epics_femto_gain('ic1_gain',ic1_gains_list,'BL16I-DI-FEMTO-01:GAIN' if installation.isLive() else None,help='some help on ic1 gain'),
	'nanoamps','%.6f',help='ic1: He-filled ion chamber before attenuators. Gain typically around 5')

"""$caget -d31 BL16I-DI-FEMTO-02:GAIN
BL16I-DI-FEMTO-02:GAIN
    Native data type: DBF_ENUM
    Request type:     DBR_CTRL_ENUM
    Element count:    1
    Value:            10^7 low noise
    Status:           NO_ALARM
    Severity:         NO_ALARM
    Enums:            (14)
                      [ 0] 10^3 low noise
                      [ 1] 10^4 low noise
                      [ 2] 10^5 low noise
                      [ 3] 10^6 low noise
                      [ 4] 10^7 low noise
                      [ 5] 10^8 low noise
                      [ 6] 10^9 low noise
                      [ 7] 10^5 high speed
                      [ 8] 10^6 high speed
                      [ 9] 10^7 high speed
                      [10] 10^8 high speed
                      [11] 10^9 high speed
                      [12] 10^10 high spd
                      [13] 10^11 high spd
"""

ic2_gains_list=[-1e3*1e-9,-1e4*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e5*1e-9,-1e6*1e-9,-1e7*1e-9,-1e8*1e-9,-1e9*1e-9,-1e10*1e-9,-1e11*1e-9]
#ic2_gains_list=[1e3*1e-9,1e4*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e5*1e-9,1e6*1e-9,1e7*1e-9,1e8*1e-9,1e9*1e-9,1e10*1e-9,1e11*1e-9]

ic2=pd_epics_femto_current('ic2','BL16I-EA-USER-01:AI6AV',
	pd_epics_femto_gain('ic2_gain',ic2_gains_list,'BL16I-DI-FEMTO-02:GAIN' if installation.isLive() else None,help='some help on ic2 gain'),
	'nanoamps','%.6f',help='ic2: He-filled ion chamber after attenuators. Gain typically around 5')

#diode=adc1=DisplayEpicsPVClass('adc1','BL16I-EA-USER-01:AI1AV','V','%6f');diode.setLevel(9) #AV=average over pre-set number of readings (100 samples @ 1 kHz)
#adc2=DisplayEpicsPVClass('adc2','BL16I-EA-USER-01:AI2AV','V','%6f')
#ic1=adc4=DisplayEpicsPVClass('IC1','BL16I-EA-USER-01:AI4AV','V','%6f'); ic1.setLevel(9)
#ic2=adc6=DisplayEpicsPVClass('IC2','BL16I-EA-USER-01:AI6AV','V','%6f'); ic2.setLevel(9)

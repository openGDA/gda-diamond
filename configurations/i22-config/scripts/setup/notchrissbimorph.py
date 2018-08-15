# Script to allow access to KB bimorph mirrors
from gdascripts.pd.epics_pds import SingleChannelBimorphClass
from gda.device.scannable import PseudoDevice
import time

format = '%3.1f'

# VFM Bimorph voltage channels

status = 'BL22I-OP-KBM-01:VFM:GET-STATUS'

ch0_pv_in =  'BL22I-OP-KBM-01:VFM:SET-VOUT00'
ch1_pv_in =  'BL22I-OP-KBM-01:VFM:SET-VOUT01'
ch2_pv_in =  'BL22I-OP-KBM-01:VFM:SET-VOUT02'
ch3_pv_in =  'BL22I-OP-KBM-01:VFM:SET-VOUT03'
ch4_pv_in =  'BL22I-OP-KBM-01:VFM:SET-VOUT04'
ch5_pv_in =  'BL22I-OP-KBM-01:VFM:SET-VOUT05'
ch6_pv_in =  'BL22I-OP-KBM-01:VFM:SET-VOUT06'
ch7_pv_in =  'BL22I-OP-KBM-01:VFM:SET-VOUT07'
ch8_pv_in =  'BL22I-OP-KBM-01:VFM:SET-VOUT08'
ch9_pv_in =  'BL22I-OP-KBM-01:VFM:SET-VOUT09'
ch10_pv_in = 'BL22I-OP-KBM-01:VFM:SET-VOUT10'
ch11_pv_in = 'BL22I-OP-KBM-01:VFM:SET-VOUT11'
ch12_pv_in = 'BL22I-OP-KBM-01:VFM:SET-VOUT12'
ch13_pv_in = 'BL22I-OP-KBM-01:VFM:SET-VOUT13'
ch14_pv_in = 'BL22I-OP-KBM-01:VFM:SET-VOUT14'
ch15_pv_in = 'BL22I-OP-KBM-01:VFM:SET-VOUT15'

ch0_pv_out = 'BL22I-OP-KBM-01:VFM:GET-VOUT00'
ch1_pv_out =  'BL22I-OP-KBM-01:VFM:GET-VOUT01'
ch2_pv_out =  'BL22I-OP-KBM-01:VFM:GET-VOUT02'
ch3_pv_out =  'BL22I-OP-KBM-01:VFM:GET-VOUT03'
ch4_pv_out =  'BL22I-OP-KBM-01:VFM:GET-VOUT04'
ch5_pv_out =  'BL22I-OP-KBM-01:VFM:GET-VOUT05'
ch6_pv_out =  'BL22I-OP-KBM-01:VFM:GET-VOUT06'
ch7_pv_out =  'BL22I-OP-KBM-01:VFM:GET-VOUT07'
ch8_pv_out =  'BL22I-OP-KBM-01:VFM:GET-VOUT08'
ch9_pv_out =  'BL22I-OP-KBM-01:VFM:GET-VOUT09'
ch10_pv_out = 'BL22I-OP-KBM-01:VFM:GET-VOUT10'
ch11_pv_out = 'BL22I-OP-KBM-01:VFM:GET-VOUT11'
ch12_pv_out = 'BL22I-OP-KBM-01:VFM:GET-VOUT12'
ch13_pv_out = 'BL22I-OP-KBM-01:VFM:GET-VOUT13'
ch14_pv_out = 'BL22I-OP-KBM-01:VFM:GET-VOUT14'
ch15_pv_out = 'BL22I-OP-KBM-01:VFM:GET-VOUT15'

vfm_ch0 = SingleChannelBimorphClass('vfm_ch0',ch0_pv_in,ch0_pv_out,status,'V', format)
vfm_ch1 = SingleChannelBimorphClass('vfm_ch1',ch1_pv_in,ch1_pv_out,status,'V', format)
vfm_ch2 = SingleChannelBimorphClass('vfm_ch2',ch2_pv_in,ch2_pv_out,status,'V', format)
vfm_ch3 = SingleChannelBimorphClass('vfm_ch3',ch3_pv_in,ch3_pv_out,status,'V', format)
vfm_ch4 = SingleChannelBimorphClass('vfm_ch4',ch4_pv_in,ch4_pv_out,status,'V', format)
vfm_ch5 = SingleChannelBimorphClass('vfm_ch5',ch5_pv_in,ch5_pv_out,status,'V', format)
vfm_ch6 = SingleChannelBimorphClass('vfm_ch6',ch6_pv_in,ch6_pv_out,status,'V', format)
vfm_ch7 = SingleChannelBimorphClass('vfm_ch7',ch7_pv_in,ch7_pv_out,status,'V', format)
vfm_ch8 = SingleChannelBimorphClass('vfm_ch8',ch8_pv_in,ch8_pv_out,status,'V', format)
vfm_ch9 = SingleChannelBimorphClass('vfm_ch9',ch9_pv_in,ch9_pv_out,status,'V', format)
vfm_ch10 = SingleChannelBimorphClass('vfm_ch10',ch10_pv_in,ch10_pv_out,status,'V', format)
vfm_ch11 = SingleChannelBimorphClass('vfm_ch11',ch11_pv_in,ch11_pv_out,status,'V', format)
vfm_ch12 = SingleChannelBimorphClass('vfm_ch12',ch12_pv_in,ch12_pv_out,status,'V', format)
vfm_ch13 = SingleChannelBimorphClass('vfm_ch13',ch13_pv_in,ch13_pv_out,status,'V', format)
vfm_ch14 = SingleChannelBimorphClass('vfm_ch14',ch14_pv_in,ch14_pv_out,status,'V', format)
vfm_ch15 = SingleChannelBimorphClass('vfm_ch15',ch15_pv_in,ch15_pv_out,status,'V', format)

for device in [vfm_ch0, vfm_ch1, vfm_ch2, vfm_ch3, vfm_ch4, vfm_ch5, vfm_ch6, vfm_ch7, vfm_ch8, vfm_ch9, vfm_ch10, vfm_ch11, vfm_ch12, vfm_ch13, vfm_ch14, vfm_ch15 ]:
	device.setProtectionLevel(3)
del device
	
# HFM Bimorph voltage channels

h_status = 'BL22I-OP-KBM-01:HFM:GET-STATUS'

h_ch0_pv_in =  'BL22I-OP-KBM-01:HFM:SET-VOUT00'
h_ch1_pv_in =  'BL22I-OP-KBM-01:HFM:SET-VOUT01'
h_ch2_pv_in =  'BL22I-OP-KBM-01:HFM:SET-VOUT02'
h_ch3_pv_in =  'BL22I-OP-KBM-01:HFM:SET-VOUT03'
h_ch4_pv_in =  'BL22I-OP-KBM-01:HFM:SET-VOUT04'
h_ch5_pv_in =  'BL22I-OP-KBM-01:HFM:SET-VOUT05'
h_ch6_pv_in =  'BL22I-OP-KBM-01:HFM:SET-VOUT06'
h_ch7_pv_in =  'BL22I-OP-KBM-01:HFM:SET-VOUT07'

h_ch0_pv_out = 'BL22I-OP-KBM-01:HFM:GET-VOUT00'
h_ch1_pv_out =  'BL22I-OP-KBM-01:HFM:GET-VOUT01'
h_ch2_pv_out =  'BL22I-OP-KBM-01:HFM:GET-VOUT02'
h_ch3_pv_out =  'BL22I-OP-KBM-01:HFM:GET-VOUT03'
h_ch4_pv_out =  'BL22I-OP-KBM-01:HFM:GET-VOUT04'
h_ch5_pv_out =  'BL22I-OP-KBM-01:HFM:GET-VOUT05'
h_ch6_pv_out =  'BL22I-OP-KBM-01:HFM:GET-VOUT06'
h_ch7_pv_out =  'BL22I-OP-KBM-01:HFM:GET-VOUT07'

hfm_ch0 = SingleChannelBimorphClass('hfm_ch0',h_ch0_pv_in,h_ch0_pv_out,h_status,'V', format)
hfm_ch1 = SingleChannelBimorphClass('hfm_ch1',h_ch1_pv_in,h_ch1_pv_out,h_status,'V', format)
hfm_ch2 = SingleChannelBimorphClass('hfm_ch2',h_ch2_pv_in,h_ch2_pv_out,h_status,'V', format)
hfm_ch3 = SingleChannelBimorphClass('hfm_ch3',h_ch3_pv_in,h_ch3_pv_out,h_status,'V', format)
hfm_ch4 = SingleChannelBimorphClass('hfm_ch4',h_ch4_pv_in,h_ch4_pv_out,h_status,'V', format)
hfm_ch5 = SingleChannelBimorphClass('hfm_ch5',h_ch5_pv_in,h_ch5_pv_out,h_status,'V', format)
hfm_ch6 = SingleChannelBimorphClass('hfm_ch6',h_ch6_pv_in,h_ch6_pv_out,h_status,'V', format)
hfm_ch7 = SingleChannelBimorphClass('hfm_ch7',h_ch7_pv_in,h_ch7_pv_out,h_status,'V', format)

for device in [hfm_ch0, hfm_ch1, hfm_ch2, hfm_ch3, hfm_ch4, hfm_ch5, hfm_ch6, hfm_ch7]:
	device.setProtectionLevel(3)
del device

from gda.epics import CAClient
from java import lang
from time import sleep

class SYS900SBimorph(PseudoDevice):
	'''Create PD to operate Linkam'''

	def __init__(self, name, pvstring, noElements):
		self.numOfChans = noElements
		self.bimorphPVbase=pvstring
		self.noElements=noElements
		self.setName(name)
		self.voltagePVs=[]
		for i in range(noElements):
			pv=CAClient(self.bimorphPVbase+":SET-VTRGT%02d" % i)
			pv.configure()
			self.voltagePVs.append(pv)
		self.voltagePVsRBV=[]
		for i in range(noElements):
			pv=CAClient(self.bimorphPVbase+":GET-VOUT%02d" % i)
			pv.configure()
			self.voltagePVsRBV.append(pv)
		self.statusPV=CAClient(self.bimorphPVbase+":GET-STATUS")
		self.statusPV.configure()
		self.setterPV=CAClient(self.bimorphPVbase+":SET-ALLTRGT")
		self.setterPV.configure()
		inputNames=[]
		outputFormat=[]
		for i in range(noElements):
			inputNames.append("chn%02d" % i)
			outputFormat.append("%3.1f")
		self.setInputNames(inputNames)
		self.setOutputFormat(outputFormat)
		self.state = "IDLE"
		self.nextAction = time.time()
		self.idleCounter=0
		self.setProtectionLevel(3)
	
	def asynchronousMoveTo(self,voltages):
		if len(voltages) != self.noElements:
			raise DeviceException("wrong number of parameters")
		if self.state != "IDLE":
			raise DeviceException("not idle")
			
		self.state = "RUNNING"
		for i in range(len(voltages)):
			self.voltagePVs[i].caput(float(voltages[i]))
			sleep(1)
		self.setterPV.caput(1)
		self.idleCounter=0
		self.nextAction=time.time()+40

	def isBusy(self):
		moving = int(self.statusPV.caget())
		if moving == 1:
			self.state="RUNNING"
			self.idleCounter=0
			return True
		if time.time() < self.nextAction:
			return True
		if self.state == "IDLE":
			return False
		self.idleCounter+=1
		if self.idleCounter > 4:
			self.state = "IDLE"
			return False
		self.nextAction=time.time()+4
		return True

	def getPosition(self):
                rep=[]
                for i in range(self.noElements):
                        v=self.voltagePVsRBV[i].caget()
                        rep.append(float(v))
                return rep

	def isAt(self, demand):
		if self.isBusy():
			return False
		if len(demand) != self.noElements:
			raise DeviceException("wrong number of parameters")

		rbv=self.getPosition()
		for i in range(len(demand)):
			if abs(float(demand[i])-float(rbv[i])) > 1:
				return False
		return True

vfm_v=SYS900SBimorph("vfm_v","BL22I-OP-KBM-01:VFM", 16)
hfm_v=SYS900SBimorph("hfm_v","BL22I-OP-KBM-01:HFM", 8)

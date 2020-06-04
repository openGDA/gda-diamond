from gda.epics import CAClient 
from java import lang
from gda.device.scannable import ScannableMotionBase

from time import sleep

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
#
#	def atScanStart(self):
#		if not self.cli.isConfigured():
#			self.cli.configure()
#
#	def getPosition(self):
#		if self.cli.isConfigured():
#			return float(self.cli.caget())
#		else:
#			self.cli.configure()
#			return float(self.cli.caget())
#			self.cli.clearup()
#
#	def isBusy(self):
#		return 0
#	
#	def atScanEnd(self):
#		if self.cli.isConfigured():
#			self.cli.clearup()
#


class DisplayEpicsPVClass(ScannableMotionBase):
	'''Create PD to display single EPICS PV'''
	def __init__(self, name, pvstring, unitstring, formatstring):
		self.setName(name)
		self.setInputNames([])
		self.setExtraNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(8)
		self.cli=CAClient(pvstring)

	def getPosition(self):
		self.cli.configure()
		return float(self.cli.caget())
		self.cli.clearup()

	def isBusy(self):
		return 0



#monoE=DisplayEpicsPVClass('monoE', 'BL16I-MO-DCM-01:EURB', 'keV', '%.3f')
img2=DisplayEpicsPVClass('IMG02', 'BL16I-VA-IMG-02:P', 'mbar', '%.1e')
T1dcm = DisplayEpicsPVClass('T1dcmSi111','BL16I-MP-DCM-01:TMP3','K','%.2f')
T2dcm = DisplayEpicsPVClass('T2dcmSi111','BL16I-MP-DCM-01:TMP4','K','%.2f')
showpitch=DisplayEpicsPVClass('Pitch', 'BL16I-MO-DCM-01:PTMTR:MOT.RBV', 'mrad', '%.4f')
pitchready=DisplayEpicsPVClass('Pitchready', 'BL16I-MO-DCM-01:PTMTR:MOT.DMOV', ' ', '%.0f')
pitchcommand=DisplayEpicsPVClass('Pitchcommand', 'BL16I-MO-DCM-01:PTMTR:MOT.VAL', 'mrad', '%.4f')
showroll1=DisplayEpicsPVClass('Roll1', 'BL16I-MO-DCM-01:RLMTR1:MOT.RBV', 'mrad', '%.4f')
showroll2=DisplayEpicsPVClass('Roll2', 'BL16I-MO-DCM-01:RLMTR2:MOT.RBV', 'mrad', '%.4f')

cc1=DisplayEpicsPVClass('cc1', 'BL16I-DI-IAMP-01:PHD1:I', 'uA', '%.9e'); cc1.setLevel(9)
cc2=DisplayEpicsPVClass('cc2', 'BL16I-DI-IAMP-01:PHD2:I', 'uA', '%.9e'); cc2.setLevel(9)
cc3=DisplayEpicsPVClass('cc3', 'BL16I-DI-IAMP-01:PHD3:I', 'uA', '%.9e'); cc3.setLevel(9)
cc4=DisplayEpicsPVClass('cc4', 'BL16I-DI-IAMP-01:PHD4:I', 'uA', '%.9e'); cc4.setLevel(9)

cc5=DisplayEpicsPVClass('cc5', 'BL16I-DI-IAMP-07:PHD1:I', 'uA', '%.9e'); cc5.setLevel(9)
cc6=DisplayEpicsPVClass('cc6', 'BL16I-DI-IAMP-07:PHD2:I', 'uA', '%.9e'); cc6.setLevel(9)
cc7=DisplayEpicsPVClass('cc7', 'BL16I-DI-IAMP-07:PHD3:I', 'uA', '%.9e'); cc7.setLevel(9)
cc8=DisplayEpicsPVClass('cc8', 'BL16I-DI-IAMP-07:PHD4:I', 'uA', '%.9e'); cc8.setLevel(9)

APD = DisplayEpicsPVClass('APD','BL16I-EA-DET-01:SCALER.S3','K','%4f')
Scintillator = DisplayEpicsPVClass('APD','BL16I-EA-DET-01:SCALER.S2','K','%4f')

adc1=DisplayEpicsPVClass('adc1','BL16I-EA-USER-01:AI1AV','V','%6f'); #AV=average over pre-set number of readings (100 samples @ 1 kHz)
adc2=DisplayEpicsPVClass('adc2','BL16I-EA-USER-01:AI2AV','V','%6f')
adc4=DisplayEpicsPVClass('adc4','BL16I-EA-USER-01:AI4AV','V','%6f')
adc6=DisplayEpicsPVClass('adc6','BL16I-EA-USER-01:AI6AV','V','%6f')

diag1=DisplayEpicsPVClass('diag1','SR15C-DI-EBPM-07:SA:Y','mm','%6f')
diag2=DisplayEpicsPVClass('diag2','SR16C-DI-EBPM-07:SA:Y','mm','%6f')
diag3=DisplayEpicsPVClass('diag3','SR17C-DI-EBPM-07:SA:Y','mm','%6f')

#hrcxw=DisplayEpicsPVClass('hirescam_xwidth','BL16I-DI-DCAM-01:XW', 'pixels', '%.4f') 
hrcyw=DisplayEpicsPVClass('hirescam_ywidth','BL16I-DI-DCAM-01:YW', 'pixels', '%.4f') 
hrcyp=DisplayEpicsPVClass('hirescam_ypos','BL16I-DI-DCAM-01:YP', 'pixels', '%.4f') 
hrcxp=DisplayEpicsPVClass('hirescam_xpos','BL16I-DI-DCAM-01:XP', 'pixels', '%.4f') 

k2xp=DisplayEpicsPVClass('k2_xpos','BL16I-DI-DCAM-02:XP', 'pixels', '%.4f') 

heater=DisplayEpicsPVClass('heater','BL16I-EA-LS340-01:HTR', '%', '%.2f')


class SingleEpicsPositionerClass(ScannableMotionBase):
	'''Create PD for single EPICS positioner'''
	def __init__(self, name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring,command=None):
		self.setName(name);
		self.setInputNames([name])
		#self.setExtraNames([name]);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)
		self.incli=CAClient(pvinstring)
		self.incli.configure()
		self.outcli=CAClient(pvoutstring)
		self.outcli.configure()
		self.statecli=CAClient(pvstatestring)
		self.statecli.configure()
		self.stopcli=CAClient(pvstopstring)
		self.stopcli.configure()
		self.optflag=None
		self.command=command
		if command != None:
			self.optflag =0

	def getPosition(self):
		try:
			#print 'Returned position sring: '+self.outcli.caget()
			return float(self.outcli.caget())
		except:
			print "Error returning position"
			return 0

	def asynchronousMoveTo(self,new_position):
		if self.optflag != None:
			if self.optflag == 0:
				self.shellcommand(self.command[0])
				sleep(1)
				self.optflag = 1
		try:
			self.incli.caput(new_position)
			sleep(0.5)
		except:
			print "error moving to position"

	def isBusy(self):
		try:
			self.status_string=self.statecli.caget()
			self.status=not int(float(self.status_string))
			#print self.getName()+": DMOVstring : "+self.status_string
			#print self.getName()+": isBusy: ", self.status
			return self.status
		except:	
			print "Device: "+self.getName()+"  Problem with DMOV string: "+self.status_string+": Returning busy status"
			return 1
	
	def stop(self):
		print "calling stop"
		self.stopcli.caput(1)


	def shellcommand(self,command):
		shellexecute(command)

	def atScanStart(self):
		if self.optflag != None:
			if self.optflag == 0:
				self.shellcommand(self.command[0])
				self.optflag =1

	def atScanEnd(self):
		if self.optflag != None:
			if self.optflag == 1:
				self.shellcommand(self.command[0])
				self.optflag =0


		
class SingleEpicsPositionerNoStatusClass(SingleEpicsPositionerClass):
	"Class for PD devices without status "

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,new_position):
		try:
			self.new_position=new_position	# need this attribute for some other classes
			self.incli.configure()
			self.statecli.configure()
			self.incli.caput(new_position)
			self.statecli.caput('0')
			self.incli.clearup()
			self.statecli.clearup()
			sleep(0.5)
		except:
			print "error moving to position"


m2bender=SingleEpicsPositionerClass('m2bender','BL16I-OP-HFM-01:BEND.VAL','BL16I-OP-HFM-01:BEND.RBV','BL16I-OP-HFM-01:BEND.DMOV','BL16I-OP-HFM-01:BEND.STOP','mm','%.2f')

diag1pos=SingleEpicsPositionerClass('diag1','BL16I-OP-ATTN-02:P:SETVALUE2.VAL','BL16I-OP-ATTN-02:P:UPD.D','BL16I-OP-ATTN-02:POSN.DMOV','BL16I-OP-ATTN-02:MP:STOP.PROC','mm','%.2f')

#pitch=SingleEpicsPositionerClass('pitch','BL16I-MO-DCM-01:PTMTR:MOT.VAL','BL16I-MO-DCM-01:PTMTR:MOT.RBV','BL16I-MO-DCM-01:PTMTR:MOT.DMOV','BL16I-MO-DCM-01:PTMTR:MOT.STOP','mrad','%.3f')

pitch=SingleEpicsPositionerClass('pitch','BL16I-MO-DCM-01:PTMTR:MOT.VAL','BL16I-MO-DCM-01:PTMTR:MOT.RBV','BL16I-MO-DCM-01:PTMTR:MOT.DMOV','BL16I-MO-DCM-01:STOP.PROC','mrad','%.3f')

#don't use roll1 except for one-off alignment
#roll1=SingleEpicsPositionerClass('roll1','BL16I-MO-DCM-01:RLMTR1:MOT.VAL','BL16I-MO-DCM-01:RLMTR1:MOT.RBV','BL16I-MO-DCM-01:RLMTR1:MOT.DMOV','BL16I-MO-DCM-01:STOP.PROC','mrad','%.3f')

roll2=SingleEpicsPositionerClass('roll2','BL16I-MO-DCM-01:RLMTR2:MOT.VAL','BL16I-MO-DCM-01:RLMTR2:MOT.RBV','BL16I-MO-DCM-01:RLMTR2:MOT.DMOV','BL16I-MO-DCM-01:STOP.PROC','mrad','%.3f')

d3diag=SingleEpicsPositionerClass('d3diag','BL16I-DI-PHDGN-03:P2:SETVALUE2.VAL','BL16I-DI-PHDGN-03:P2:UPD.D','BL16I-DI-PHDGN-03:MP2:DMOV','BL16I-DI-PHDGN-03:MP2:STOP.PROC','mm','%.4f')

bragg=SingleEpicsPositionerClass('Bragg','BL16I-MO-DCM-01:BRMTR:MOT.VAL','BL16I-MO-DCM-01:BRMTR:MOT.RBV','BL16I-MO-DCM-01:BRMTR:MOT.DMOV','BL16I-MO-DCM-01:BRMTR:STOP.PROC','deg','%.4f')

#stop doesn't stop piezos but stops all other DCM motors
#fineroll=SingleEpicsPositionerNoStatusClass('fineroll','BL16I-MO-DCM-01:FRMTR:PINP','BL16I-MO-DCM-01:FRMTR:PREAD','BL16I-MO-DCM-01:FRMTR:PMOVE.PROC','BL16I-MO-DCM-01:STOP.PROC','urad','%.3f')

finepitch=SingleEpicsPositionerNoStatusClass('finepitch','BL16I-MO-DCM-01:FPMTR:PINP','BL16I-MO-DCM-01:FPMTR:PREAD','BL16I-MO-DCM-01:FPMTR:PMOVE.PROC','BL16I-MO-DCM-01:STOP.PROC','urad','%.3f')

perp=SingleEpicsPositionerClass('Perp','BL16I-MO-DCM-01:PDMTR1:MOT.VAL','BL16I-MO-DCM-01:PDMTR1:MOT.RBV','BL16I-MO-DCM-01:PDMTR1:MOT.DMOV','BL16I-MO-DCM-01:STOP.PROC','mm','%.3f')

dcmlat=SingleEpicsPositionerClass('DCMlat','BL16I-MO-DCM-01:PDMTR2:MOT.VAL','BL16I-MO-DCM-01:PDMTR2:MOT.RBV','BL16I-MO-DCM-01:PDMTR2:MOT.DMOV','BL16I-MO-DCM-01:PDMTR2:MOT.STOP','mm','%.3f')


#psAh=SingleEpicsPositionerClass('psAp','BL16I-AL-SLITS-01:XA.VAL','BL16I-AL-SLITS-01:XA.RBV','BL16I-AL-SLITS-01:XA.DMOV','BL16I-AL-SLITS-01:XA.STOP','mm','%.4f')


#psBh=SingleEpicsPositionerClass('psBh','BL16I-AL-SLITS-01:XB.VAL','BL16I-AL-SLITS-01:XB.RBV','BL16I-AL-SLITS-01:XB.DMOV','BL16I-AL-SLITS-01:XB.STOP','mm','%.4f')

#psBv=SingleEpicsPositionerClass('psBh','BL16I-AL-SLITS-01:YB.VAL','BL16I-AL-SLITS-01:YB.RBV','BL16I-AL-SLITS-01:YB.DMOV','BL16I-AL-SLITS-01:YB.STOP','mm','%.4f')


#psAv=SingleEpicsPositionerClass('psAp','BL16I-AL-SLITS-01:YA.VAL','BL16I-AL-SLITS-01:YA.RBV','BL16I-AL-SLITS-01:YA.DMOV','BL16I-AL-SLITS-01:YA.STOP','mm','%.4f')





## SLITS ####

S2xgap=SingleEpicsPositionerClass('S2xgap','BL16I-AL-SLITS-02:X:SIZE.VAL','BL16I-AL-SLITS-02:X:SIZE.RBV','BL16I-AL-SLITS-02:X:SIZE.DMOV','BL16I-AL-SLITS-02:X:SIZE.STOP','mm','%.4f')
S2xgap.setLevel(6)

S2xcentre=SingleEpicsPositionerClass('S2xcentre','BL16I-AL-SLITS-02:X:CENTER.VAL','BL16I-AL-SLITS-02:X:CENTER.RBV','BL16I-AL-SLITS-02:X:CENTER.DMOV','BL16I-AL-SLITS-02:X:CENTER.STOP','mm','%.4f')

S2ygap=SingleEpicsPositionerClass('S2ygap','BL16I-AL-SLITS-02:Y:SIZE.VAL','BL16I-AL-SLITS-02:Y:SIZE.RBV','BL16I-AL-SLITS-02:Y:SIZE.DMOV','BL16I-AL-SLITS-02:Y:SIZE.STOP','mm','%.4f')
S2ygap.setLevel(6)

S2ycentre=SingleEpicsPositionerClass('S2ycentre','BL16I-AL-SLITS-02:Y:CENTER.VAL','BL16I-AL-SLITS-02:Y:CENTER.RBV','BL16I-AL-SLITS-02:Y:CENTER.DMOV','BL16I-AL-SLITS-02:Y:CENTER.STOP','mm','%.4f')


S3xgap=SingleEpicsPositionerClass('S3xgap','BL16I-AL-SLITS-03:X:SIZE.VAL','BL16I-AL-SLITS-03:X:SIZE.RBV','BL16I-AL-SLITS-03:X:SIZE.DMOV','BL16I-AL-SLITS-03:X:SIZE.STOP','mm','%.4f')
S3xgap.setLevel(6)

S3xcentre=SingleEpicsPositionerClass('S3xcentre','BL16I-AL-SLITS-03:X:CENTER.VAL','BL16I-AL-SLITS-03:X:CENTER.RBV','BL16I-AL-SLITS-03:X:CENTER.DMOV','BL16I-AL-SLITS-03:X:CENTER.STOP','mm','%.4f')

S3ygap=SingleEpicsPositionerClass('S3ygap','BL16I-AL-SLITS-03:Y:SIZE.VAL','BL16I-AL-SLITS-03:Y:SIZE.RBV','BL16I-AL-SLITS-03:Y:SIZE.DMOV','BL16I-AL-SLITS-03:Y:SIZE.STOP','mm','%.4f')
S3ygap.setLevel(6)

S3ycentre=SingleEpicsPositionerClass('S3ycentre','BL16I-AL-SLITS-03:Y:CENTER.VAL','BL16I-AL-SLITS-03:Y:CENTER.RBV','BL16I-AL-SLITS-03:Y:CENTER.DMOV','BL16I-AL-SLITS-03:Y:CENTER.STOP','mm','%.4f')


S4xgap=SingleEpicsPositionerClass('S4xgap','BL16I-AL-SLITS-04:X:SIZE.VAL','BL16I-AL-SLITS-04:X:SIZE.RBV','BL16I-AL-SLITS-04:X:SIZE.DMOV','BL16I-AL-SLITS-04:X:SIZE.STOP','mm','%.4f')
S2xgap.setLevel(6)

S4xcentre=SingleEpicsPositionerClass('S4xcentre','BL16I-AL-SLITS-04:X:CENTER.VAL','BL16I-AL-SLITS-04:X:CENTER.RBV','BL16I-AL-SLITS-04:X:CENTER.DMOV','BL16I-AL-SLITS-04:X:CENTER.STOP','mm','%.4f')

S4ygap=SingleEpicsPositionerClass('S4ygap','BL16I-AL-SLITS-04:Y:SIZE.VAL','BL16I-AL-SLITS-04:Y:SIZE.RBV','BL16I-AL-SLITS-04:Y:SIZE.DMOV','BL16I-AL-SLITS-04:Y:SIZE.STOP','mm','%.4f')
S4ygap.setLevel(6)

S4ycentre=SingleEpicsPositionerClass('S4ycentre','BL16I-AL-SLITS-04:Y:CENTER.VAL','BL16I-AL-SLITS-04:Y:CENTER.RBV','BL16I-AL-SLITS-04:Y:CENTER.DMOV','BL16I-AL-SLITS-04:Y:CENTER.STOP','mm','%.4f')

#PA stages 
comm1=['/home/i16user/bin/power_up_xtal_translation','/home/i16user/bin/power_down_xtal_translation']
zp=SingleEpicsPositionerClass('zp','BL16I-EA-POLAN-01:X.VAL','BL16I-EA-POLAN-01:X.RBV','BL16I-EA-POLAN-01:X.DMOV','BL16I-EA-POLAN-01:X.STOP','mm','%.3f',comm1)


comm2=['/home/i16user/bin/power_up_xtal_rotation','/home/i16user/bin/power_down_xtal_rotation']
thp=SingleEpicsPositionerClass('thp','BL16I-EA-POLAN-01:THETAp.VAL','BL16I-EA-POLAN-01:THETAp.RBV','BL16I-EA-POLAN-01:THETAp.DMOV','BL16I-EA-POLAN-01:THETAp.STOP','deg','%.4f')

tthp=SingleEpicsPositionerClass('tthp','BL16I-EA-POLAN-01:DET1:2THETAp.VAL','BL16I-EA-POLAN-01:DET1:2THETAp.RBV','BL16I-EA-POLAN-01:DET1:2THETAp.DMOV','BL16I-EA-POLAN-01:DET1:2THETAp.STOP','deg','%.3f')

stoke=SingleEpicsPositionerClass('stoke','BL16I-EA-POLAN-01:ETA.VAL','BL16I-EA-POLAN-01:ETA.RBV','BL16I-EA-POLAN-01:ETA.DMOV','BL16I-EA-POLAN-01:ETA.STOP','deg','%.3f')


##############################################################

s6vgap=SingleEpicsPositionerClass('s6vgap','BL16I-AL-SLITS-06:Y:GAP.VAL','BL16I-AL-SLITS-06:Y:GAP.RBV','BL16I-AL-SLITS-06:Y:GAP.DMOV','BL16I-AL-SLITS-06:Y:GAP.STOP','mm','%.3f')

s6vtrans=SingleEpicsPositionerClass('s6vtrans','BL16I-AL-SLITS-06:Y:TRANSLATION.VAL','BL16I-AL-SLITS-06:Y:TRANSLATION.RBV','BL16I-AL-SLITS-06:Y:TRANSLATION.DMOV','BL16I-AL-SLITS-06:Y:TRANSLATION.STOP','mm','%.3f')

s6hgap=SingleEpicsPositionerClass('s6hgap','BL16I-AL-SLITS-06:X:GAP.VAL','BL16I-AL-SLITS-06:X:GAP.RBV','BL16I-AL-SLITS-06:X:GAP.DMOV','BL16I-AL-SLITS-06:X:GAP.STOP','mm','%.3f')

s6htrans=SingleEpicsPositionerClass('s6htrans','BL16I-AL-SLITS-06:X:TRANSLATION.VAL','BL16I-AL-SLITS-06:X:TRANSLATION.RBV','BL16I-AL-SLITS-06:X:TRANSLATION.DMOV','BL16I-AL-SLITS-06:X:TRANSLATION.STOP','mm','%.3f')

s5hgap=SingleEpicsPositionerClass('s5hgap','BL16I-AL-SLITS-05:X:GAP.VAL','BL16I-AL-SLITS-05:X:GAP.RBV','BL16I-AL-SLITS-05:X:GAP.DMOV','BL16I-AL-SLITS-05:X:GAP.STOP','mm','%.3f')

s5htrans=SingleEpicsPositionerClass('s5htrans','BL16I-AL-SLITS-05:X:TRANSLATION.VAL','BL16I-AL-SLITS-05:X:TRANSLATION.RBV','BL16I-AL-SLITS-05:X:TRANSLATION.DMOV','BL16I-AL-SLITS-05:X:TRANSLATION.STOP','mm','%.3f')

s5vgap=SingleEpicsPositionerClass('s5vgap','BL16I-AL-SLITS-05:Y:GAP.VAL','BL16I-AL-SLITS-05:Y:GAP.RBV','BL16I-AL-SLITS-05:Y:GAP.DMOV','BL16I-AL-SLITS-05:Y:GAP.STOP','mm','%.3f')

s5vtrans=SingleEpicsPositionerClass('s5vtrans','BL16I-AL-SLITS-05:Y:TRANSLATION.VAL','BL16I-AL-SLITS-05:Y:TRANSLATION.RBV','BL16I-AL-SLITS-05:Y:TRANSLATION.DMOV','BL16I-AL-SLITS-05:Y:TRANSLATION.STOP','mm','%.3f')

sx=SingleEpicsPositionerClass('sample_x','BL16I-MO-DIFF-01:SAMPLE:X.VAL','BL16I-MO-DIFF-01:SAMPLE:X.RBV','BL16I-MO-DIFF-01:SAMPLE:X.DMOV','BL16I-MO-DIFF-01:SAMPLE:X.STOP','mm','%.3f')
sy=SingleEpicsPositionerClass('sample_y','BL16I-MO-DIFF-01:SAMPLE:Y.VAL','BL16I-MO-DIFF-01:SAMPLE:Y.RBV','BL16I-MO-DIFF-01:SAMPLE:Y.DMOV','BL16I-MO-DIFF-01:SAMPLE:Y.STOP','mm','%.3f')
sz=SingleEpicsPositionerClass('sample_z','BL16I-MO-DIFF-01:SAMPLE:Z.VAL','BL16I-MO-DIFF-01:SAMPLE:Z.RBV','BL16I-MO-DIFF-01:SAMPLE:Z.DMOV','BL16I-MO-DIFF-01:SAMPLE:Z.STOP','mm','%.3f')

#####################
# Optical Table
#################

ztable=SingleEpicsPositionerClass('table_vert','BL16I-MO-TABLE-01:Y.VAL','BL16I-MO-TABLE-01:Y.RBV','BL16I-MO-TABLE-01:Y.DMOV','BL16I-MO-TABLE-01:Y.STOP','mm','%.3f')

ytable=SingleEpicsPositionerClass('table_horiz','BL16I-MO-TABLE-01:X.VAL','BL16I-MO-TABLE-01:X.RBV','BL16I-MO-TABLE-01:X.DMOV','BL16I-MO-TABLE-01:X.STOP','mm','%.3f')

#####################
# Phase plate
#####################


ppth=SingleEpicsPositionerClass('ppth','BL16I-OP-PPR-01:THETA.VAL','BL16I-OP-PPR-01:THETA.RBV','BL16I-OP-PPR-01:THETA.DMOV','BL16I-OP-PPR-01:THETA.STOP','deg','%.5f')
ppy=SingleEpicsPositionerClass('ppy','BL16I-OP-PPR-01:Y.VAL','BL16I-OP-PPR-01:Y.RBV','BL16I-OP-PPR-01:Y.DMOV','BL16I-OP-PPR-01:Y.STOP','mm','%.3f')
ppx=SingleEpicsPositionerClass('ppx','BL16I-OP-PPR-01:X.VAL','BL16I-OP-PPR-01:X.RBV','BL16I-OP-PPR-01:X.DMOV','BL16I-OP-PPR-01:X.STOP','mm','%.3f')
ppchi=SingleEpicsPositionerClass('ppchi','BL16I-OP-PPR-01:CHI.VAL','BL16I-OP-PPR-01:CHI.RBV','BL16I-OP-PPR-01:CHI.DMOV','BL16I-OP-PPR-01:CHI.STOP','deg','%.3f')


class SingleEpicsPositionerSetAndGetOnlyClass(ScannableMotionBase):
	'''Create PD for single EPICS positioner which respond only to set and get'''
	def __init__(self, name, pvinstring, pvoutstring, unitstring, formatstring,help=None):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)
		self.incli=CAClient(pvinstring)
		self.incli.configure()
		self.outcli=CAClient(pvoutstring)
		self.outcli.configure()
		
	def getPosition(self):
		try:
			#print 'Returned position sring: '+self.outcli.caget()
			return float(self.outcli.caget())
		except:
			print "Error returning position"
			return 0

	def asynchronousMoveTo(self,new_position):
		try:
			self.incli.caput(new_position)
			sleep(0.5)
		except:
			print "error moving to position"

	def isBusy(self):
		return 0


################
# Cryocooler
################

cryolevel=DisplayEpicsPVClass('N2level','BL16I-CG-CRYO-01:MNLEV','%','%.2f')
cryopressure=DisplayEpicsPVClass('N2buffpressure','BL16I-CG-CRYO-01:NBUFF','%','%.3f')
n2fill=DisplayEpicsPVClass('N2solenoide','BL16I-CG-CRYO-01:ST12','%','%.0f')
#cryolevel.setInputNames(['cryolevel'])

cryo_pump_speed=SingleEpicsPositionerSetAndGetOnlyClass('pump_speed','BL16I-CG-CRYO-01:PSET','BL16I-CG-CRYO-01:PSET','Hz','%.0f',help='Crypump speed - do not change unless you are sure!!')

buffer_pressure=SingleEpicsPositionerSetAndGetOnlyClass('buffer_pressure','BL16I-CG-CRYO-01:TPBUF','BL16I-CG-CRYO-01:TPBUF','PSI','%.1f',help='LN high pressure circuit pressure - do not change unless you are sure!!')

vessel_startfill=SingleEpicsPositionerSetAndGetOnlyClass('vessel_startfill','BL16I-CG-CRYO-01:LP1L','BL16I-CG-CRYO-01:LP1L','%','%.1f',help='Cryocooler vessel start fill level - do not change unless you are sure!!')

vessel_stopfill=SingleEpicsPositionerSetAndGetOnlyClass('vessel_stopfill','BL16I-CG-CRYO-01:LP1H','BL16I-CG-CRYO-01:LP1H','%','%.1f',help='Cryocooler vessel stop fill level - do not change unless you are sure!!')

def checkcryolevel():
	if cryolevel < 64 or cryolevel > 54.5:
		return 1
	else:
		return 0

def waitcryoready():
	while n2fill()==0:
		sleep(60)
	return	

def dofill():
	current_startfill=vessel_startfill()
	vessel_startfill(vessel_stopfill())
	sleep(1)
	vessel_startfill(current_startfill)
alias dofill

#State=1 if ready, 0 if moving
#need to stop motors on error; get propper State 

class EnergyFromBraggPD(ScannableMotionBase):
	'Energy PD - calls Bragg angle PD'
	def __init__(self, name,link):
		self.setName(name);
		self.setInputNames([name])
		#self.setExtraNames([name])
		self.Units=['keV']
		self.setOutputFormat(['%.4f'])
		self.setLevel(3)
		self.braggpd=bragg
		self.dspace=3.1356
		self.scalefac=-1
#		self.offset=bragg_offset()
		self.c=6.19921
		self.setLink(link)


	def setLink(self,link):
		"""Establish the link with the diffractometer objects """
		self.link=link

	def getPosition(self):
		ang=self.braggpd()*self.scalefac+bragg_offset()
		self.link.setEnergy(self.c/self.dspace/sin(ang*pi/180))
		return self.c/self.dspace/sin(ang*pi/180)


	def asynchronousMoveTo(self,energy):
		ang=(180/pi*asin(self.c/self.dspace/energy)-bragg_offset())/self.scalefac
		self.braggpd.asynchronousMoveTo(ang)

	def isBusy(self):
		return self.braggpd.isBusy()
	
	def stop(self):
		self.braggpd.stop()

	def calibrate(self, newenergy):
		"""Recalibrate the energy of the monochromator """
		cal_ang=180/pi*asin(self.c/self.dspace/newenergy)
		dcm_ang=self.braggpd()
		bragg_offset(cal_ang-dcm_ang*self.scalefac)
		print 'Calculated offset='+str(bragg_offset())+' deg'


class EnergyFromBraggwithHarmonicPD(ScannableMotionBase):
	'Energy PD - calls Bragg angle PD'
	def __init__(self, name,link,harmonicPD):
		self.setName(name);
		self.setInputNames([name])
		#self.setExtraNames([name])
		self.Units=['keV']
		self.setOutputFormat(['%.4f'])
		self.setLevel(3)
		self.harmonic = harmonicPD
		self.braggpd=bragg
		self.dspace=3.1356
		self.scalefac=-1
#		self.offset=bragg_offset()
		self.c=6.19921
		self.setLink(link)


	def setLink(self,link):
		"""Establish the link with the diffractometer objects """
		self.link=link

	def getPosition(self):
		ang=self.braggpd()*self.scalefac+bragg_offset()
		self.link.setEnergy(self.harmonic()*self.c/self.dspace/sin(ang*pi/180))
		return self.harmonic()*self.c/self.dspace/sin(ang*pi/180)


	def asynchronousMoveTo(self,energy):
		ang=(180/pi*asin(self.harmonic()*self.c/self.dspace/energy)-bragg_offset())/self.scalefac
		self.braggpd.asynchronousMoveTo(ang)

	def isBusy(self):
		return self.braggpd.isBusy()
	
	def stop(self):
		self.braggpd.stop()

	def calibrate(self, newenergy):
		"""Recalibrate the energy of the monochromator """
		cal_ang=180/pi*asin(self.harmonic()*self.c/self.dspace/newenergy)
		dcm_ang=self.braggpd()
		bragg_offset(cal_ang-dcm_ang*self.scalefac)
		print 'Calculated offset='+str(bragg_offset())+' deg'


class EnergyFromBraggFixedoffsetPD(ScannableMotionBase):
	'Energy PD with optional fixed offset - calls Bragg angle PD'
	def __init__(self, name,link):
		self.setName(name);
		self.setInputNames([name])
		#self.setExtraNames([name]);
		self.Units=['keV']
		self.setOutputFormat(['%.4f'])
		self.setLevel(3)
		self.braggpd=bragg
		self.perp=perp
		self.dspace=3.1356
		self.scalefac=-1
#			-0.13924 old value
		self.c=6.19921
		self.beamoffset=12
		self.fixedoffsetmode=1
		#self.gap_at_perp_zero=5
		self.gap_at_perp_zero=3.6; #measured by survey may07
		print self.name+'.fixedoffsetmode: '+str(self.fixedoffsetmode)
		print 'gap_at_perp_zero='+str(self.gap_at_perp_zero)
		print self.name+'.beamoffset='+str(self.beamoffset)
		self.setLink(link)


	def setLink(self,link):
		"""Establish the link with the diffractometer objects """
		self.link=link



	def getPosition(self):
		ang=self.braggpd()*self.scalefac+bragg_offset()
		self.link.setEnergy(self.c/self.dspace/sin(ang*pi/180))
		return self.c/self.dspace/sin(ang*pi/180)

	def asynchronousMoveTo(self,energy):
		ang=(180/pi*asin(self.c/self.dspace/energy)-bragg_offset())/self.scalefac
		self.braggpd.asynchronousMoveTo(ang)
		if self.fixedoffsetmode==1:
			#print "moving perp to",(self.beamoffset/2/cos(ang*pi/180)-self.gap_at_perp_zero)
			self.perp.asynchronousMoveTo(self.beamoffset/2/cos(ang*pi/180)-self.gap_at_perp_zero)

	def isBusy(self):
		return (self.braggpd.isBusy() or self.perp.isBusy())
	
	def stop(self):
		self.braggpd.stop()

	def calibrate(self, newenergy):
		cal_ang=180/pi*asin(self.c/self.dspace/newenergy)
		dcm_ang=self.braggpd()
		bragg_offset(cal_ang-dcm_ang*self.scalefac)
		print 'Calculated offset='+str(bragg_offset())+' deg'

class EnergyFromBraggFixedoffsetwithHarmonicPD(ScannableMotionBase):
	'''
	Energy PD with optional fixed offset with Harmonic PD - calls Bragg angle PD
	'''
	def __init__(self,name,link,harmonicPD):
		self.setName(name);
		self.setInputNames([name])
		#self.setExtraNames([name]);
		self.Units=['keV']
		self.setOutputFormat(['%.4f'])
		self.setLevel(3)
		self.harmonic = harmonicPD
		self.braggpd=bragg
		self.perp=perp
		self.dspace=3.1356
		self.scalefac=-1
#			-0.13924 old value
		self.c=6.19921
		self.beamoffset=12
		self.fixedoffsetmode=1
		#self.gap_at_perp_zero=5
		self.gap_at_perp_zero=3.6; #measured by survey may07
		print self.name+'.fixedoffsetmode: '+str(self.fixedoffsetmode)
		print 'gap_at_perp_zero='+str(self.gap_at_perp_zero)
		print self.name+'.beamoffset='+str(self.beamoffset)
		self.setLink(link)
		self.warnings =1


	def atScanStart(self):
		print self.harmonic
		self.warnings=0

	def atScanEnd(self):
		self.warnings=1


	def setLink(self,link):
		"""Establish the link with the diffractometer objects """
		self.link=link


	def getPosition(self):
		if int(self.harmonic())!=1 and self.warnings == 1:
			print self.harmonic
		ang=self.braggpd()*self.scalefac+bragg_offset()
		self.link.setEnergy(self.harmonic()*self.c/self.dspace/sin(ang*pi/180))
		return self.harmonic()*self.c/self.dspace/sin(ang*pi/180)

	def asynchronousMoveTo(self,energy):
		ang=(180/pi*asin(self.harmonic()*self.c/self.dspace/energy)-bragg_offset())/self.scalefac
		self.braggpd.asynchronousMoveTo(ang)
		if self.fixedoffsetmode==1:
			#print "moving perp to",(self.beamoffset/2/cos(ang*pi/180)-self.gap_at_perp_zero)
			self.perp.asynchronousMoveTo(self.beamoffset/2/cos(ang*pi/180)-self.gap_at_perp_zero)

	def isBusy(self):
		return (self.braggpd.isBusy() or self.perp.isBusy())
	
	def stop(self):
		self.braggpd.stop()

	def calibrate(self, newenergy):
		cal_ang=180/pi*asin(self.harmonic()*self.c/self.dspace/newenergy)
		dcm_ang=self.braggpd()
		bragg_offset(cal_ang-dcm_ang*self.scalefac)
		print 'Calculated offset='+str(bragg_offset())+' deg'


#en=EnergyFromBraggPD('Energy',BLi)
#enf=EnergyFromBraggFixedoffsetPD('energy',BLi)
en=EnergyFromBraggwithHarmonicPD('Energy',BLi,dcmharmonic)
enf = EnergyFromBraggFixedoffsetwithHarmonicPD('energy',BLi,dcmharmonic)


class SingleEpicsPositionerNoStatusClass2(SingleEpicsPositionerNoStatusClass):
	'EPICS device that obtains a status from the actual position vs command position'
	def isBusy(self):
		try:
			if abs(self.new_position-self())<self.deadband:
				return 0
			else:
				return 1
		except:
			print 'Warning - can''t get isBusy status. Perhaps new_position or deadband attrubutes not set?'
			return 0

id_gap=SingleEpicsPositionerNoStatusClass2('ID_gap','SR16I-MO-SERVC-01:BLGSET','SR16I-MO-SERVC-01:CURRGAPD','SR16I-MO-SERVC-01:ALLMOVE','SR16I-MO-SERVC-01:ESTOP','mm','%.3f'); 
id_gap.deadband=0.005

class IDGapFromPVClass(ScannableMotionBase):
	'''Create device to control ID gap etc'''
	def __init__(self, name, pvinstring, pvoutstring, pvexecutestring, pvstatestring, pvstopstring, unitstring, formatstring):
		self.setName(name);
		self.setInputNames([name])
		#self.setExtraNames([name]);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)
		self.incli=CAClient(pvinstring)
		self.incli.configure()
		self.outcli=CAClient(pvoutstring)
		self.outcli.configure()
		self.executecli=CAClient(pvexecutestring)
		self.executecli.configure()
		self.statecli=CAClient(pvstatestring)
		self.statecli.configure()
		self.stopcli=CAClient(pvstopstring)
		self.stopcli.configure()

	def getPosition(self):
		try:
			#print 'Returned position sring: '+self.outcli.caget()
			return float(self.outcli.caget())
		except:
			print "Error returning position"
			return 0

	def asynchronousMoveTo(self,new_position):
		try:
			self.incli.caput(new_position)
			self.executecli.caput(1)
			sleep(0.5)
			self.executecli.caput(0)
			sleep(0.5)
		except:
			print "error moving to position"

	def isBusy(self):
		try:
			self.status=self.statecli.caget()
			#print "IsMovingString : "+self.status
			return int(float(self.status))
		except:	
			print "Device: "+self.getName()+"  Problem with isMoving string: "+self.status+": Returning busy status"
			return 1
	
	def stop(self):
		print "calling stop"
		self.stopcli.caput(1)

				
idgap=IDGapFromPVClass('IDgap','SR16I-MO-SERVC-01:BLGSET','SR16I-MO-SERVC-01:CURRGAPD','SR16I-MO-SERVC-01:BLGSETP','SR16I-MO-SERVC-01:ALLMOVE','SR16I-MO-SERVC-01:ESTOP','mm','%.3f')

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

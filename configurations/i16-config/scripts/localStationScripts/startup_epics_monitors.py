from pd_epics import DisplayEpicsPVClass
from pd_metadata_group import ReadPDGroupClass
from gdascripts.pd.dummy_pds import DummyPD

#monoE=DisplayEpicsPVClass('monoE', 'BL16I-MO-DCM-01:EURB', 'keV', '%.3f')
img2=DisplayEpicsPVClass('IMG02', 'BL16I-VA-IMG-02:P', 'mbar', '%.1e')
absorber1=DisplayEpicsPVClass('absorber1', 'FE16I-RS-ABSB-01:STA', '.', '%.0f')
absorber2=DisplayEpicsPVClass('absorber2', 'FE16I-RS-ABSB-02:STA', '.', '%.0f')
d2=DisplayEpicsPVClass('d2', 'BL16I-DI-PHDGN-02:STA', '.', '%.0f')
T1dcm = DisplayEpicsPVClass('T1dcmSi111','BL16I-OP-DCM-01:TMP3','K','%.2f')
T2dcm = DisplayEpicsPVClass('T2dcmSi111','BL16I-OP-DCM-01:TMP4','K','%.2f')
showpitch=DisplayEpicsPVClass('Pitch', 'BL16I-MO-DCM-01:PTMTR:MOT.RBV', 'mrad', '%.4f')
pitchready=DisplayEpicsPVClass('Pitchready', 'BL16I-MO-DCM-01:PTMTR:MOT.DMOV', ' ', '%.0f')
pitchcommand=DisplayEpicsPVClass('Pitchcommand', 'BL16I-MO-DCM-01:PTMTR:MOT.VAL', 'mrad', '%.4f')
showroll1=DisplayEpicsPVClass('Roll1', 'BL16I-MO-DCM-01:RLMTR1:MOT.RBV', 'mrad', '%.4f')
showroll2=DisplayEpicsPVClass('Roll2', 'BL16I-MO-DCM-01:RLMTR2:MOT.RBV', 'mrad', '%.4f')

cc1=DisplayEpicsPVClass('cc1', 'BL16I-DI-IAMP-01:PHD1:I', 'uA', '%.9e'); cc1.setLevel(9)  # <---hangs
cc2=DisplayEpicsPVClass('cc2', 'BL16I-DI-IAMP-01:PHD2:I', 'uA', '%.9e'); cc2.setLevel(9)
cc3=DisplayEpicsPVClass('cc3', 'BL16I-DI-IAMP-01:PHD3:I', 'uA', '%.9e'); cc3.setLevel(9)
cc4=DisplayEpicsPVClass('cc4', 'BL16I-DI-IAMP-01:PHD4:I', 'uA', '%.9e'); cc4.setLevel(9)

cc5=DisplayEpicsPVClass('cc5', 'BL16I-DI-IAMP-07:PHD1:I', 'uA', '%.9e'); cc5.setLevel(9)
cc6=DisplayEpicsPVClass('cc6', 'BL16I-DI-IAMP-07:PHD2:I', 'uA', '%.9e'); cc6.setLevel(9)
cc7=DisplayEpicsPVClass('cc7', 'BL16I-DI-IAMP-07:PHD3:I', 'uA', '%.9e'); cc7.setLevel(9)
cc8=DisplayEpicsPVClass('cc8', 'BL16I-DI-IAMP-07:PHD4:I', 'uA', '%.9e'); cc8.setLevel(9)
xps2Uptime=DisplayEpicsPVClass('xps2Uptime','BL16I-MO-XPS-02:UPTIME', 's', '%.9e'); xps2Uptime.setLevel(9)
xps2CPUTemp=DisplayEpicsPVClass('xps2CPUTemp','BL16I-MO-XPS-02:CPUTEMP', 'deg', '%.9e'); xps2CPUTemp.setLevel(9)
xps1Uptime=DisplayEpicsPVClass('xps1Uptime','BL16I-MO-XPS-01:UPTIME', 's', '%.9e'); xps1Uptime.setLevel(9)
xps1CPUTemp=DisplayEpicsPVClass('xps1CPUTemp','BL16I-MO-XPS-01:CPUTEMP', 'deg', '%.9e'); xps1CPUTemp.setLevel(9)


APD = DisplayEpicsPVClass('APD','BL16I-EA-DET-01:SCALER.S3','K','%4f')
Scintillator = DisplayEpicsPVClass('APD','BL16I-EA-DET-01:SCALER.S2','K','%4f')

#diode=adc1=DisplayEpicsPVClass('adc1','BL16I-EA-USER-01:AI1AV','V','%6f');diode.setLevel(9) #AV=average over pre-set number of readings (100 samples @ 1 kHz)
#adc2=DisplayEpicsPVClass('adc2','BL16I-EA-USER-01:AI2AV','V','%6f')
#ic1=adc4=DisplayEpicsPVClass('IC1','BL16I-EA-USER-01:AI4AV','V','%6f'); ic1.setLevel(9)
#ic2=adc6=DisplayEpicsPVClass('IC2','BL16I-EA-USER-01:AI6AV','V','%6f'); ic2.setLevel(9)

diag1=DisplayEpicsPVClass('diag1','SR15C-DI-EBPM-07:SA:Y','mm','%6f')
diag2=DisplayEpicsPVClass('diag2','SR16C-DI-EBPM-07:SA:Y','mm','%6f')
diag3=DisplayEpicsPVClass('diag3','SR17C-DI-EBPM-07:SA:Y','mm','%6f')

hrcxp=DisplayEpicsPVClass('hirescam_xpos','BL16I-DI-DCAM-01:CAM:XP', 'pixels', '%.4f') 
hrcyp=DisplayEpicsPVClass('hirescam_ypos','BL16I-DI-DCAM-01:CAM:YP', 'pixels', '%.4f') 
hrcxw=DisplayEpicsPVClass('hirescam_xwidth','BL16I-DI-DCAM-01:CAM:XW', 'pixels', '%.4f') 
hrcyw=DisplayEpicsPVClass('hirescam_ywidth','BL16I-DI-DCAM-01:CAM:YW', 'pixels', '%.4f') 

d3cyp=DisplayEpicsPVClass('d3_ypos','BL16I-DI-PHDGN-03:CAM:YP', 'pixels', '%.4f')
d3cxp=DisplayEpicsPVClass('d3_xpos','BL16I-DI-PHDGN-03:CAM:XP', 'pixels', '%.4f')
#d4cxp=DisplayEpicsPVClass('d4_xpos','BL16I-DI-PHDGN-04:CAM:XP', 'pixels', '%.4f')
#d4cyp=DisplayEpicsPVClass('d4_ypos','BL16I-DI-PHDGN-04:CAM:YP', 'pixels', '%.4f')
d5cxp=DisplayEpicsPVClass('d5_xpos','BL16I-DI-PHDGN-05:CAM:XP', 'pixels', '%.4f')
d5cyp=DisplayEpicsPVClass('d5_ypos','BL16I-DI-PHDGN-05:CAM:YP', 'pixels', '%.4f')
d5cxw=DisplayEpicsPVClass('d5_xwidth','BL16I-DI-PHDGN-05:CAM:XW', 'pixels', '%.4f')
d5cyw=DisplayEpicsPVClass('d5_ywidth','BL16I-DI-PHDGN-05:CAM:YW', 'pixels', '%.4f')

# 01/09/08 comment out temporarily as pv not working
#k2xp=DisplayEpicsPVClass('k2_xpos','BL16I-DI-DCAM-02:XP', 'pixels', '%.4f') 

#heater=DisplayEpicsPVClass('heater','BL16I-EA-LS340-01:HTR', '%', '%.2f')


################
# Analogue inputs
################
x25_anin=DisplayEpicsPVClass('x25_anin','BL16I-EA-USER-01:AI7', 'V', '%.4f')
x26_anin=DisplayEpicsPVClass('x26_anin','BL16I-EA-USER-01:AI8', 'V', '%.4f')

BPM1XR=DisplayEpicsPVClass('BPM1XR','FE16I-DI-PBPM-01:BEAMX', 'mm', '%.4f')	#PBPM1 x-relative
BPM1YR=DisplayEpicsPVClass('BPM1YR','FE16I-DI-PBPM-01:BEAMY', 'mm', '%.4f')	#PBPM1 y-relative
BPM2XR=DisplayEpicsPVClass('BPM2XR','FE16I-DI-PBPM-02:BEAMX', 'mm', '%.4f')	#PBPM2 x-relative
BPM2YR=DisplayEpicsPVClass('BPM2YR','FE16I-DI-PBPM-02:BEAMY', 'mm', '%.4f')	#PBPM2 y-relative

m1piezo_readback=DisplayEpicsPVClass('m1piezo_readback','BL16I-OP-VFM-01:PIEZO:FBACK','V','%.3f')

showkphi=DisplayEpicsPVClass('showkphi','BL16I-MO-DIFF-01:SAMPLE:KPHI.RBV', 'deg', '%.5f')
showkap=DisplayEpicsPVClass('showkap','BL16I-MO-DIFF-01:SAMPLE:KAPPA.RBV', 'deg', '%.5f')
showkth=DisplayEpicsPVClass('showkth','BL16I-MO-DIFF-01:SAMPLE:KTHETA.RBV', 'deg', '%.5f')
showmu=DisplayEpicsPVClass('showmu','BL16I-MO-DIFF-01:SAMPLE:MU.RBV', 'deg', '%.5f')
showdelta=DisplayEpicsPVClass('showdelta','BL16I-MO-DIFF-01:ARM:DELTA.RBV', 'deg', '%.5f')
showgam=DisplayEpicsPVClass('showgam','BL16I-MO-DIFF-01:ARM:GAMMA.RBV', 'deg', '%.5f')
showkap6=ReadPDGroupClass('showkap6',[showkphi,showkap,showkth, showmu, showdelta, showgam])


blower_temp_c=DisplayEpicsPVClass('cyberstar_gas_blower_temp','BL16I-EA-BLOW-01:LOOP1:PV:RBV', 'C', '%.1f')

if installation.isLive():
	ppchitemp=DisplayEpicsPVClass('ppchitemp', 'BL16I-OP-PPR-01:CHI:TEMP',      'deg', '%.9e'); ppchitemp.setLevel(9)
	ppth1temp=DisplayEpicsPVClass('ppth1temp', 'BL16I-OP-PPR-01:S1:THETA:TEMP', 'deg', '%.9e'); ppth1temp.setLevel(9)
	ppz1temp =DisplayEpicsPVClass('ppz1temp',  'BL16I-OP-PPR-01:S1:Z:TEMP',     'deg', '%.9e'); ppz1temp.setLevel(9)
	ppth2temp=DisplayEpicsPVClass('ppth2temp', 'BL16I-OP-PPR-01:S2:THETA:TEMP', 'deg', '%.9e'); ppth2temp.setLevel(9)
	ppz2temp =DisplayEpicsPVClass('ppz2temp',  'BL16I-OP-PPR-01:S2:Z:TEMP',     'deg', '%.9e'); ppz2temp.setLevel(9)
else:
	ppchitemp=DummyPD('ppchitemp') ; ppchitemp.Units=['deg'], ppchitemp.setOutputFormat(['%.9e']); ppchitemp.setLevel(9)
	ppth1temp=DummyPD('ppth1temp') ; ppth1temp.Units=['deg']; ppth1temp.setOutputFormat(['%.9e']); ppth1temp.setLevel(9)
	ppz1temp =DummyPD('ppz1temp')  ;  ppz1temp.Units=['deg'];  ppz1temp.setOutputFormat(['%.9e']);  ppz1temp.setLevel(9)
	ppth2temp=DummyPD('ppth2temp') ; ppth2temp.Units=['deg']; ppth2temp.setOutputFormat(['%.9e']); ppth2temp.setLevel(9)
	ppz2temp =DummyPD('ppz2temp')  ;  ppz2temp.Units=['deg'];  ppz2temp.setOutputFormat(['%.9e']);  ppz2temp.setLevel(9)


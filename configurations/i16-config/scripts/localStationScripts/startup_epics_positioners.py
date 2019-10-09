from pd_epics import *

#===mirrors==========
#(robw) m2bender=SingleEpicsPositionerClass('m2bender','BL16I-OP-HFM-01:BEND.VAL','BL16I-OP-HFM-01:BEND.RBV','BL16I-OP-HFM-01:BEND.DMOV','BL16I-OP-HFM-01:BEND.STOP','mm','%.2f')

#M1y=SingleEpicsPositionerClass('m1y','BL16I-OP-VFM-01:Y.VAL','BL16I-OP-VFM-01:Y.RBV','BL16I-OP-VFM-01:Y.DMOV','BL16I-OP-VFM-01:Y.STOP','mm','%.3f')#not used#

#M2y=SingleEpicsPositionerClass('m2y','BL16I-OP-HFM-01:Y.VAL','BL16I-OP-HFM-01:Y.RBV','BL16I-OP-HFM-01:Y.DMOV','BL16I-OP-HFM-01:Y.STOP','mm','%.3f')#mot used delete

m3x=SingleEpicsPositionerClass('m3x','BL16I-OP-MFM-01:M3:X.VAL','BL16I-OP-MFM-01:M3:X.RBV','BL16I-OP-MFM-01:M3:X.DMOV','BL16I-OP-MFM-01:M3:X.STOP','mm','%.3f')
m4x=SingleEpicsPositionerClass('m4x','BL16I-OP-MFM-01:M4:X.VAL','BL16I-OP-MFM-01:M4:X.RBV','BL16I-OP-MFM-01:M4:X.DMOV','BL16I-OP-MFM-01:M4:X.STOP','mm','%.3f')
m3pitch=SingleEpicsPositionerClass('m3pitch','BL16I-OP-MFM-01:M3:YAW.VAL','BL16I-OP-MFM-01:M3:YAW.RBV','BL16I-OP-MFM-01:M3:YAW.DMOV','BL16I-OP-MFM-01:M3:YAW.STOP','mm','%.3f')
m4pitch=SingleEpicsPositionerClass('m4pitch','BL16I-OP-MFM-01:M4:YAW.VAL','BL16I-OP-MFM-01:M4:YAW.RBV','BL16I-OP-MFM-01:M4:YAW.DMOV','BL16I-OP-MFM-01:M4:YAW.STOP','mm','%.3f')


#==================

# removed 29th september 
#diag1pos=SingleEpicsPositionerClass('diag1','BL16I-OP-ATTN-02:P:SETVALUE2.VAL','BL16I-OP-ATTN-02:P:UPD.D','BL16I-OP-ATTN-02:POSN.DMOV','BL16I-OP-ATTN-02:MP:STOP.PROC','mm','%.2f')

#pitch=SingleEpicsPositionerClass('pitch','BL16I-MO-DCM-01:PTMTR:MOT.VAL','BL16I-MO-DCM-01:PTMTR:MOT.RBV','BL16I-MO-DCM-01:PTMTR:MOT.DMOV','BL16I-MO-DCM-01:PTMTR:MOT.STOP','mrad','%.3f')

####pitch=SingleEpicsPositionerClass('pitch','BL16I-MO-DCM-01:PTMTR:MOT.VAL','BL16I-MO-DCM-01:PTMTR:MOT.RBV','BL16I-MO-DCM-01:PTMTR:MOT.DMOV','BL16I-MO-DCM-01:STOP.PROC','mrad','%.3f')

#don't use roll1 except for one-off alignment
###roll1=SingleEpicsPositionerClass('roll1','BL16I-MO-DCM-01:RLMTR1:MOT.VAL','BL16I-MO-DCM-01:RLMTR1:MOT.RBV','BL16I-MO-DCM-01:RLMTR1:MOT.DMOV','BL16I-MO-DCM-01:STOP.PROC','mrad','%.3f')

####roll2=SingleEpicsPositionerClass('roll2','BL16I-MO-DCM-01:RLMTR2:MOT.VAL','BL16I-MO-DCM-01:RLMTR2:MOT.RBV','BL16I-MO-DCM-01:RLMTR2:MOT.DMOV','BL16I-MO-DCM-01:STOP.PROC','mrad','%.3f')
# removed 29th september
# d3diag=SingleEpicsPositionerClass('d3diag','BL16I-DI-PHDGN-03:P2:SETVALUE2.VAL','BL16I-DI-PHDGN-03:P2:UPD.D','BL16I-DI-PHDGN-03:MP2:DMOV','BL16I-DI-PHDGN-03:MP2:STOP.PROC','mm','%.4f')


#### bragg=SingleEpicsPositionerClass('Bragg','BL16I-MO-DCM-01:BRMTR:MOT.VAL','BL16I-MO-DCM-01:BRMTR:MOT.RBV','BL16I-MO-DCM-01:BRMTR:MOT.DMOV','BL16I-MO-DCM-01:BRMTR:STOP.PROC','deg','%.4f')



#stop doesn't stop piezos but stops all other DCM motors
#fineroll=SingleEpicsPositionerNoStatusClass('fineroll','BL16I-MO-DCM-01:FRMTR:PINP','BL16I-MO-DCM-01:FRMTR:PREAD','BL16I-MO-DCM-01:FRMTR:PMOVE.PROC','BL16I-MO-DCM-01:STOP.PROC','urad','%.3f')

####finepitch=SingleEpicsPositionerNoStatusClass('finepitch','BL16I-MO-DCM-01:FPMTR:PINP','BL16I-MO-DCM-01:FPMTR:PREAD','BL16I-MO-DCM-01:FPMTR:PMOVE.PROC','BL16I-MO-DCM-01:STOP.PROC','urad','%.3f')

####perp=SingleEpicsPositionerClass('Perp','BL16I-MO-DCM-01:PDMTR1:MOT.VAL','BL16I-MO-DCM-01:PDMTR1:MOT.RBV','BL16I-MO-DCM-01:PDMTR1:MOT.DMOV','BL16I-MO-DCM-01:STOP.PROC','mm','%.3f')

####dcmlat=SingleEpicsPositionerClass('DCMlat','BL16I-MO-DCM-01:PDMTR2:MOT.VAL','BL16I-MO-DCM-01:PDMTR2:MOT.RBV','BL16I-MO-DCM-01:PDMTR2:MOT.DMOV','BL16I-MO-DCM-01:PDMTR2:STOP.PROC','mm','%.3f')

	
# Not here





#psAh=SingleEpicsPositionerClass('psAp','BL16I-AL-SLITS-01:XA.VAL','BL16I-AL-SLITS-01:XA.RBV','BL16I-AL-SLITS-01:XA.DMOV','BL16I-AL-SLITS-01:XA.STOP','mm','%.4f')


#psBh=SingleEpicsPositionerClass('psBh','BL16I-AL-SLITS-01:XB.VAL','BL16I-AL-SLITS-01:XB.RBV','BL16I-AL-SLITS-01:XB.DMOV','BL16I-AL-SLITS-01:XB.STOP','mm','%.4f')

#psBv=SingleEpicsPositionerClass('psBh','BL16I-AL-SLITS-01:YB.VAL','BL16I-AL-SLITS-01:YB.RBV','BL16I-AL-SLITS-01:YB.DMOV','BL16I-AL-SLITS-01:YB.STOP','mm','%.4f')


#psAv=SingleEpicsPositionerClass('psAp','BL16I-AL-SLITS-01:YA.VAL','BL16I-AL-SLITS-01:YA.RBV','BL16I-AL-SLITS-01:YA.DMOV','BL16I-AL-SLITS-01:YA.STOP','mm','%.4f')

frontendx=SingleEpicsPositionerClass('frontendx','FE16I-AL-APTR-02:X.VAL','FE16I-AL-APTR-02:X.RBV','FE16I-AL-APTR-02:X.DMOV','FE16I-AL-APTR-02:X.STOP','mm','%.3f')

frontendy=SingleEpicsPositionerClass('frontendy','FE16I-AL-APTR-02:Y.VAL','FE16I-AL-APTR-02:Y.RBV','FE16I-AL-APTR-02:Y.DMOV','FE16I-AL-APTR-02:Y.STOP','mm','%.3f')

## SLITS ####
"""REMOVE
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
"""
#PA stages 
comm1=['/home/i16user/bin/power_up_xtal_translation','/home/i16user/bin/power_down_xtal_translation']
zp=SingleEpicsPositionerClass('zp','BL16I-EA-POLAN-01:X.VAL','BL16I-EA-POLAN-01:X.RBV','BL16I-EA-POLAN-01:X.DMOV','BL16I-EA-POLAN-01:X.STOP','mm','%.3f',comm1)


comm2=['/home/i16user/bin/power_up_xtal_rotation','/home/i16user/bin/power_down_xtal_rotation']

class DeprecatedSingleEpicsPositionerClass(SingleEpicsPositionerClass):
	def __init__(self, name, replacement, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring, help=None, command=None):
		SingleEpicsPositionerClass.__init__(self, name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring, help, command)
		self.replacement=replacement
		print "Warning, scannable '%s' is deprecated and should not be used, please use '%s' instead." % (self.getName(), self.replacement)

	def getPosition(self):
		print "Warning, scannable '%s' is deprecated and should not be used, please use '%s' instead." % (self.getName(), self.replacement)
		return SingleEpicsPositionerClass.getPosition(self)

	def asynchronousMoveTo(self,new_position):
		print "Warning, scannable '%s' is deprecated and should not be used, please use '%s' instead." % (self.getName(), self.replacement)
		SingleEpicsPositionerClass.asynchronousMoveTo(self, new_position)

stoke=DeprecatedSingleEpicsPositionerClass( 'stoke','stokes','BL16I-EA-POLAN-01:ETA.VAL','BL16I-EA-POLAN-01:ETA.RBV','BL16I-EA-POLAN-01:ETA.DMOV','BL16I-EA-POLAN-01:ETA.STOP','deg','%.3f')
""" stokes now defined in Spring
stokes=         SingleEpicsPositionerClass('stokes',         'BL16I-EA-POLAN-01:ETA.VAL','BL16I-EA-POLAN-01:ETA.RBV','BL16I-EA-POLAN-01:ETA.DMOV','BL16I-EA-POLAN-01:ETA.STOP','deg','%.3f')
"""

##############################################################

s6vgap=SingleEpicsPositionerClass('s6vgap','BL16I-AL-SLITS-06:Y:GAP.VAL','BL16I-AL-SLITS-06:Y:GAP.RBV','BL16I-AL-SLITS-06:Y:GAP.DMOV','BL16I-AL-SLITS-06:Y:GAP.STOP','mm','%.3f')

s6vtrans=SingleEpicsPositionerClass('s6vtrans','BL16I-AL-SLITS-06:Y:TRANSLATION.VAL','BL16I-AL-SLITS-06:Y:TRANSLATION.RBV','BL16I-AL-SLITS-06:Y:TRANSLATION.DMOV','BL16I-AL-SLITS-06:Y:TRANSLATION.STOP','mm','%.3f')

s6hgap=SingleEpicsPositionerClass('s6hgap','BL16I-AL-SLITS-06:X:GAP.VAL','BL16I-AL-SLITS-06:X:GAP.RBV','BL16I-AL-SLITS-06:X:GAP.DMOV','BL16I-AL-SLITS-06:X:GAP.STOP','mm','%.3f')

s6htrans=SingleEpicsPositionerClass('s6htrans','BL16I-AL-SLITS-06:X:TRANSLATION.VAL','BL16I-AL-SLITS-06:X:TRANSLATION.RBV','BL16I-AL-SLITS-06:X:TRANSLATION.DMOV','BL16I-AL-SLITS-06:X:TRANSLATION.STOP','mm','%.3f')

s5hgap=SingleEpicsPositionerClass('s5hgap','BL16I-AL-SLITS-05:X:GAP.VAL','BL16I-AL-SLITS-05:X:GAP.RBV','BL16I-AL-SLITS-05:X:GAP.DMOV','BL16I-AL-SLITS-05:X:GAP.STOP','mm','%.3f')

s5htrans=SingleEpicsPositionerClass('s5htrans','BL16I-AL-SLITS-05:X:TRANSLATION.VAL','BL16I-AL-SLITS-05:X:TRANSLATION.RBV','BL16I-AL-SLITS-05:X:TRANSLATION.DMOV','BL16I-AL-SLITS-05:X:TRANSLATION.STOP','mm','%.3f')

s5vgap=SingleEpicsPositionerClass('s5vgap','BL16I-AL-SLITS-05:Y:GAP.VAL','BL16I-AL-SLITS-05:Y:GAP.RBV','BL16I-AL-SLITS-05:Y:GAP.DMOV','BL16I-AL-SLITS-05:Y:GAP.STOP','mm','%.3f')

s5vtrans=SingleEpicsPositionerClass('s5vtrans','BL16I-AL-SLITS-05:Y:TRANSLATION.VAL','BL16I-AL-SLITS-05:Y:TRANSLATION.RBV','BL16I-AL-SLITS-05:Y:TRANSLATION.DMOV','BL16I-AL-SLITS-05:Y:TRANSLATION.STOP','mm','%.3f')


###########
# XPS motors #
###########

#(robw)sx=SingleEpicsPositionerClass('sample_x','BL16I-MO-DIFF-01:SAMPLE:X.VAL','BL16I-MO-DIFF-01:SAMPLE:X.RBV','BL16I-MO-DIFF-01:SAMPLE:X.DMOV','BL16I-MO-DIFF-01:SAMPLE:X.STOP','mm','%.4f')
#(robw)sy=SingleEpicsPositionerClass('sample_y','BL16I-MO-DIFF-01:SAMPLE:Y.VAL','BL16I-MO-DIFF-01:SAMPLE:Y.RBV','BL16I-MO-DIFF-01:SAMPLE:Y.DMOV','BL16I-MO-DIFF-01:SAMPLE:Y.STOP','mm','%.4f')
#(robw)sz=SingleEpicsPositionerClass('sample_z','BL16I-MO-DIFF-01:SAMPLE:Z.VAL','BL16I-MO-DIFF-01:SAMPLE:Z.RBV','BL16I-MO-DIFF-01:SAMPLE:Z.DMOV','BL16I-MO-DIFF-01:SAMPLE:Z.STOP','mm','%.4f')
from gda.factory import FactoryException
try:
	pin1x=xps3m1=SingleEpicsPositionerClass('xps3motor1','BL16I-MO-XPS3-01:P1.VAL','BL16I-MO-XPS3-01:P1.RBV','BL16I-MO-XPS3-01:P1.DMOV','BL16I-MO-XPS3-01:P1.STOP','mm','%.3f')
	pin1y=xps3m2=SingleEpicsPositionerClass('xps3motor2','BL16I-MO-XPS3-01:P2.VAL','BL16I-MO-XPS3-01:P2.RBV','BL16I-MO-XPS3-01:P2.DMOV','BL16I-MO-XPS3-01:P2.STOP','mm','%.3f')
	pin2x=xps3m3=SingleEpicsPositionerClass('xps3motor3','BL16I-MO-XPS3-01:P3.VAL','BL16I-MO-XPS3-01:P3.RBV','BL16I-MO-XPS3-01:P3.DMOV','BL16I-MO-XPS3-01:P3.STOP','mm','%.3f')
	pin2y=xps3m4=SingleEpicsPositionerClass('xps3motor4','BL16I-MO-XPS3-01:P4.VAL','BL16I-MO-XPS3-01:P4.RBV','BL16I-MO-XPS3-01:P4.DMOV','BL16I-MO-XPS3-01:P4.STOP','mm','%.3f')
	pin3x=xps3m5=SingleEpicsPositionerClass('xps3motor5','BL16I-MO-XPS3-01:P5.VAL','BL16I-MO-XPS3-01:P5.RBV','BL16I-MO-XPS3-01:P5.DMOV','BL16I-MO-XPS3-01:P5.STOP','mm','%.3f')
	pin3y=xps3m6=SingleEpicsPositionerClass('xps3motor6','BL16I-MO-XPS3-01:P6.VAL','BL16I-MO-XPS3-01:P6.RBV','BL16I-MO-XPS3-01:P6.DMOV','BL16I-MO-XPS3-01:P6.STOP','mm','%.3f')

except FactoryException, e:
	print "ERROR: Problem configuring XPS3 motor: ", str(e)
#####################
# Misc - XPS3
#####################

#xps axis 7 motor
#xps7=SingleEpicsPositionerClass('xps7','BL16I-MO-ROTAR-01:P.VAL','BL16I-MO-ROTAR-01:P.RBV','BL16I-MO-ROTAR-01:P.DMOV','BL16I-MO-ROTAR-01:P.STOP','deg','%.2f')

#####################
# Optical Table
#################

ztable=SingleEpicsPositionerClass('table_vert','BL16I-MO-TABLE-01:Y.VAL','BL16I-MO-TABLE-01:Y.RBV','BL16I-MO-TABLE-01:Y.DMOV','BL16I-MO-TABLE-01:Y.STOP','mm','%.3f')

ytable=SingleEpicsPositionerClass('table_horiz','BL16I-MO-TABLE-01:X.VAL','BL16I-MO-TABLE-01:X.RBV','BL16I-MO-TABLE-01:X.DMOV','BL16I-MO-TABLE-01:X.STOP','mm','%.3f')

################
# XIA inserters
################
#change to F3
xia1=qbpm6inserter=SingleEpicsPositionerSetAndGetOnlyClass('XIA1','BL16I-OP-ATTN-05:F3TRIGGER','BL16I-OP-ATTN-05:F3TRIGGER','%','%.0f',help='XIA inserter1')
xia2=SingleEpicsPositionerSetAndGetOnlyClass('XIA2','BL16I-OP-ATTN-05:F4TRIGGER','BL16I-OP-ATTN-05:F4TRIGGER','%','%.0f',help='XIA inserter2')

################
# Femto gains
################
#ic1gain=SingleEpicsPositionerSetAndGetOnlyClass('IC1gain','BL16I-DI-FEMTO-01:GAIN','BL16I-DI-FEMTO-01:GAIN','%','%.0f',help='Femto1/IC0 gain\nFemto switched to REMOTE, AC, 10Hz for remote operation\nGains:\n0:    10^3\n1:    10^4\n2:    10^5\n3:    10^6\n4:    10^7\n5:    10^8\n6:    10^5\n7:    10^6\n8:    10^7\n9:    10^8\n10:    10^9\n11:    10^10\n')
#ic2gain=SingleEpicsPositionerSetAndGetOnlyClass('IC2gain','BL16I-DI-FEMTO-02:GAIN','BL16I-DI-FEMTO-02:GAIN','%','%.0f',help='Femto2/IC0 gain\nFemto switched to REMOTE, AC, 10Hz for remote operation\nGains:\n0:    10^3\n1:    10^4\n2:    10^5\n3:    10^6\n4:    10^7\n5:    10^8\n6:    10^5\n7:    10^6\n8:    10^7\n9:    10^8\n10:    10^9\n11:    10^10\n')
#diodegain=SingleEpicsPositionerSetAndGetOnlyClass('diodegain','BL16I-DI-FEMTO-03:GAIN','BL16I-DI-FEMTO-03:GAIN','%','%.0f',help='Femto3/IC0 gain\nFemto switched to REMOTE, AC, 10Hz for remote operation\nGains:\n10^3 low noise (0)\n10^4 low noise (1)\n10^5 low noise (2)\n10^6 low noise (3)\n10^7 low noise (4)\n10^8 low noise (5)\n10^9 low noise (6)\n10^5 high speed (8)\n10^6 high speed (9)\n10^7 high speed (10)\n10^8 high speed(11)\n10^9 high speed (12)\n10^10 high speed (13)\n10^11 high speed (14)\n')

################
# TTL and analogue outputs
################
x1=x1_ttl=SingleEpicsPositionerSetAndGetOnlyClass('x1_ttl','BL16I-EA-USER-01:BO1','BL16I-EA-USER-01:BO1','logical','%.0f',help='TTL out socket x1 (used for fast shutter)')
x2=x2_ttl=SingleEpicsPositionerSetAndGetOnlyClass('x2_ttl','BL16I-EA-USER-01:BO2','BL16I-EA-USER-01:BO2','logical','%.0f',help='TTL out socket x2')
x3=x3_ttl=SingleEpicsPositionerSetAndGetOnlyClass('x3_ttl','BL16I-EA-USER-01:BO3','BL16I-EA-USER-01:BO3','logical','%.0f',help='TTL out socket x3')
x4=x4_ttl=SingleEpicsPositionerSetAndGetOnlyClass('x4_ttl','BL16I-EA-USER-01:BO4','BL16I-EA-USER-01:BO4','logical','%.0f',help='TTL out socket x4')
x17=x17_ttl=SingleEpicsPositionerSetAndGetOnlyClass('x17_ttl','BL16I-EA-USER-01:BO6','BL16I-EA-USER-01:BO6','logical','%.0f',help='TTL out socket x17')
x21=x21_ttl=SingleEpicsPositionerSetAndGetOnlyClass('x21_ttl','BL16I-EA-USER-01:BO7','BL16I-EA-USER-01:BO7','logical','%.0f',help='TTL out socket x21')

x18_anout=SingleEpicsPositionerSetAndGetOnlyClass('x18_anout','BL16I-EA-USER-01:AO2','BL16I-EA-USER-01:AO2','V','%.3f',sleeptime=0,help='+/- 10V analogue out socket x18')
x19_anout=SingleEpicsPositionerSetAndGetOnlyClass('x19_anout','BL16I-EA-USER-01:AO3','BL16I-EA-USER-01:AO3','V','%.3f',sleeptime=0,help='+/- 10V analogue out socket x19')
x20_anout=SingleEpicsPositionerSetAndGetOnlyClass('x20_anout','BL16I-EA-USER-01:AO4','BL16I-EA-USER-01:AO4','V','%.3f',sleeptime=0,help='+/- 10V analogue out socket x20')
x22_anout=SingleEpicsPositionerSetAndGetOnlyClass('x22_anout','BL16I-EA-USER-01:AO6','BL16I-EA-USER-01:AO6','V','%.3f',sleeptime=0,help='+/- 10V analogue out socket x22')
x23_anout=SingleEpicsPositionerSetAndGetOnlyClass('x23_anout','BL16I-EA-USER-01:AO7','BL16I-EA-USER-01:AO7','V','%.3f',sleeptime=0,help='+/- 10V analogue out socket x23')
x24_anout=SingleEpicsPositionerSetAndGetOnlyClass('x24_anout','BL16I-EA-USER-01:AO8','BL16I-EA-USER-01:AO8','V','%.3f',sleeptime=0,help='+/- 10V analogue out socket x24')


p2mj1=SingleEpicsPositionerClass('p2mj1','BL16I-MO-P2TAB-01:Y1.VAL','BL16I-MO-P2TAB-01:Y1.RBV','BL16I-MO-P2TAB-01:Y1.DMOV','BL16I-MO-P2TAB-01:Y1.STOP','mm','%.3f')
p2mj2=SingleEpicsPositionerClass('p2mj2','BL16I-MO-P2TAB-01:Y2.VAL','BL16I-MO-P2TAB-01:Y2.RBV','BL16I-MO-P2TAB-01:Y2.DMOV','BL16I-MO-P2TAB-01:Y2.STOP','mm','%.3f')
p2mj3=SingleEpicsPositionerClass('p2mj3','BL16I-MO-P2TAB-01:Y3.VAL','BL16I-MO-P2TAB-01:Y3.RBV','BL16I-MO-P2TAB-01:Y3.DMOV','BL16I-MO-P2TAB-01:Y3.STOP','mm','%.3f')
p2mx1=SingleEpicsPositionerClass('p2mx1','BL16I-MO-P2TAB-01:X1.VAL','BL16I-MO-P2TAB-01:X1.RBV','BL16I-MO-P2TAB-01:X1.DMOV','BL16I-MO-P2TAB-01:X1.STOP','mm','%.3f')
p2mx2=SingleEpicsPositionerClass('p2mx2','BL16I-MO-P2TAB-01:X2.VAL','BL16I-MO-P2TAB-01:X2.RBV','BL16I-MO-P2TAB-01:X2.DMOV','BL16I-MO-P2TAB-01:X2.STOP','mm','%.3f')
p2mz1=SingleEpicsPositionerClass('p2mz1','BL16I-MO-P2TAB-01:Z1.VAL','BL16I-MO-P2TAB-01:Z1.RBV','BL16I-MO-P2TAB-01:Z1.DMOV','BL16I-MO-P2TAB-01:Z1.STOP','mm','%.3f')

m1piezo=SingleEpicsPositionerSetAndGetOnlyClass('m1piezo','BL16I-OP-VFM-01:PIEZO:OUT','BL16I-OP-VFM-01:PIEZO:OUT','%.3f','%.3f',help='Mirror 1 piezo device for fine horizontal control of beam position')

magv=SingleEpicsPositionerSetAndGetOnlyClass('magv','BL16I-EA-MAG-01:VPROG','BL16I-EA-MAG-01:VMON','%.2f','%.2f',help='1T magnet volts. See also magi')
magi=SingleEpicsPositionerSetAndGetOnlyClass('magi','BL16I-EA-MAG-01:IPROG','BL16I-EA-MAG-01:IMON','%.2f','%.2f',help='1T magnet current (A). See also magv')

bpmin=SingleEpicsPositionerSetAndGetOnlyClass('bpmin','BL16I-DI-BPM-01:DIAG.VAL','BL16I-DI-BPM-01:DIAG.RBV','%.2f','%.2f',help='bpm screen motor')

shtr3x=shx=SingleEpicsPositionerClass('shtr3x','BL16I-EA-SHTR-03:X.VAL','BL16I-EA-SHTR-03:X.RBV','BL16I-EA-SHTR-03:X.DMOV','BL16I-EA-SHTR-03:X.STOP','mm','%.2f')
shtr3y=shy=SingleEpicsPositionerClass('shtr3y','BL16I-EA-SHTR-03:Y.VAL','BL16I-EA-SHTR-03:Y.RBV','BL16I-EA-SHTR-03:Y.DMOV','BL16I-EA-SHTR-03:Y.STOP','mm','%.2f')

hx=huberx=SingleEpicsPositionerClass('huberx','BL16I-MO-HUB-01:X.VAL','BL16I-MO-HUB-01:X.RBV','BL16I-MO-HUB-01:X.DMOV','BL16I-MO-HUB-01:X.STOP','mm','%.3f',help='Huber xy stage x motor')
hy=hubery=SingleEpicsPositionerClass('hubery','BL16I-MO-HUB-01:Y.VAL','BL16I-MO-HUB-01:Y.RBV','BL16I-MO-HUB-01:Y.DMOV','BL16I-MO-HUB-01:Y.STOP','mm','%.3f',help='Huber xy stage y motor')
fsgap=frontslitgap=SingleEpicsPositionerClass('frontslity','BL16I-MO-TMP-07:Y:GAP.VAL','BL16I-MO-TMP-07:Y:GAP.RBV','BL16I-MO-TMP-07:Y:GAP.DMOV','BL16I-MO-TMP-07:Y:GAP.STOP','mm','%.3f',help='Front slits y gap (mm)')
fsy=fontslity=SingleEpicsPositionerClass('frontslity','BL16I-MO-TMP-07:Y:TRANSLATION.VAL','BL16I-MO-TMP-07:Y:TRANSLATION.RBV','BL16I-MO-TMP-07:Y:TRANSLATION.DMOV','BL16I-MO-TMP-07:Y:TRANSLATION.STOP','mm','%.3f',help='Front slits y offset (mm)')


zp1x=SingleEpicsPositionerClass('zp1x','BL16I-MO-ZPT-02:X1.VAL','BL16I-MO-ZPT-02:X1.RBV','BL16I-MO-ZPT-02:X1.DMOV','BL16I-MO-ZPT-02:X1.VAL.STOP','mm','%.4f')
zp1y=SingleEpicsPositionerClass('zp1y','BL16I-MO-ZPT-03:Y1.VAL','BL16I-MO-ZPT-03:Y1.RBV','BL16I-MO-ZPT-03:Y1.DMOV','BL16I-MO-ZPT-03:Y1.VAL.STOP','mm','%.4f')
zp1z=SingleEpicsPositionerClass('zp1z','BL16I-MO-ZPT-04:Z1.VAL','BL16I-MO-ZPT-04:Z1.RBV','BL16I-MO-ZPT-04:Z1.DMOV','BL16I-MO-ZPT-04:Z1.VAL.STOP','mm','%.4f')
zp2x=SingleEpicsPositionerClass('zp2x','BL16I-MO-ZPT-05:X2.VAL','BL16I-MO-ZPT-05:X2.RBV','BL16I-MO-ZPT-05:X2.DMOV','BL16I-MO-ZPT-05:X2.VAL.STOP','mm','%.4f')
zp2y=SingleEpicsPositionerClass('zp2y','BL16I-MO-ZPT-06:Y2.VAL','BL16I-MO-ZPT-06:Y2.RBV','BL16I-MO-ZPT-06:Y2.DMOV','BL16I-MO-ZPT-06:Y2.VAL.STOP','mm','%.4f')
zp2z=SingleEpicsPositionerClass('zp2z','BL16I-MO-ZPT-07:Z2.VAL','BL16I-MO-ZPT-07:Z2.RBV','BL16I-MO-ZPT-07:Z2.DMOV','BL16I-MO-ZPT-07:Z2.VAL.STOP','mm','%.4f')

#micosx=SingleEpicsPositionerClass('micosx','BL16I-MO-PIEZO-03:MMC:01:DEMAND','BL16I-MO-PIEZO-03:MMC:01:POS:ENC','BL16I-MO-PIEZO-03:MMC:01:ACT:BUSY','BL16I-MO-PIEZO-03:MMC:01:STOP','mm','%.4f')
#micosy=SingleEpicsPositionerClass('micosy','BL16I-MO-PIEZO-03:MMC:02:DEMAND','BL16I-MO-PIEZO-03:MMC:02:POS:ENC','BL16I-MO-PIEZO-03:MMC:02:ACT:BUSY','BL16I-MO-PIEZO-03:MMC:02:STOP','mm','%.4f')

#micosx=SingleEpicsPositionerNotDmovClassDirtyPiezo('micosx','BL16I-MO-PIEZO-03:MMC:01:DEMAND','BL16I-MO-PIEZO-03:MMC:01:POS:ENC','BL16I-MO-PIEZO-03:MMC:01:ACT:BUSY','BL16I-MO-PIEZO-03:MMC:01:STOP','mm','%.4f')
#micosx.setOutputFormat(['%.5f'])
#micosy=SingleEpicsPositionerNotDmovClassDirtyPiezo('micosy','BL16I-MO-PIEZO-03:MMC:02:DEMAND','BL16I-MO-PIEZO-03:MMC:02:POS:ENC','BL16I-MO-PIEZO-03:MMC:02:ACT:BUSY','BL16I-MO-PIEZO-03:MMC:02:STOP','mm','%.4f')
#micosy.setOutputFormat(['%.5f'])

######## PV's seem to have changed for micos.
micosx=SingleEpicsPositionerSetAndGetOnlyClass('micosx','BL16I-EA-PIEZO-01:C1:X:MOV:WR','BL16I-EA-PIEZO-01:C1:X:MOV:WR','microns','%.2f',help='micos motor')
micosy=SingleEpicsPositionerSetAndGetOnlyClass('micosy','BL16I-EA-PIEZO-01:C1:Y:MOV:WR','BL16I-EA-PIEZO-01:C1:Y:MOV:WR','microns','%.2f',help='micos motor')
micosz=SingleEpicsPositionerSetAndGetOnlyClass('micosz','BL16I-EA-PIEZO-01:C1:Z:MOV:WR','BL16I-EA-PIEZO-01:C1:Z:MOV:WR','microns','%.2f',help='micos motor')

#BL16I-MO-PIEZO-03:MMC:02:POS:ENC
#BL16I-MO-ZPT-02:X1.VAL

kbt1=SingleEpicsPositionerClass('kbt1','BL16I-MO-KBM-01:T1.VAL','BL16I-MO-KBM-01:T1.RBV','BL16I-MO-KBM-01:T1.DMOV','BL16I-MO-KBM-01:T1.VAL.STOP','mm','%.4f')
kbt2=SingleEpicsPositionerClass('kbt2','BL16I-MO-KBM-01:T2.VAL','BL16I-MO-KBM-01:T2.RBV','BL16I-MO-KBM-01:T2.DMOV','BL16I-MO-KBM-01:T2.VAL.STOP','mm','%.4f')
kbt3=SingleEpicsPositionerClass('kbt3','BL16I-MO-KBM-01:T3.VAL','BL16I-MO-KBM-01:T3.RBV','BL16I-MO-KBM-01:T3.DMOV','BL16I-MO-KBM-01:T3.VAL.STOP','mm','%.4f')
kbt4=SingleEpicsPositionerClass('kbt4','BL16I-MO-KBM-01:T4.VAL','BL16I-MO-KBM-01:T4.RBV','BL16I-MO-KBM-01:T4.DMOV','BL16I-MO-KBM-01:T4.VAL.STOP','mm','%.4f')
kbt5=SingleEpicsPositionerClass('kbt5','BL16I-MO-KBM-01:T5.VAL','BL16I-MO-KBM-01:T5.RBV','BL16I-MO-KBM-01:T5.DMOV','BL16I-MO-KBM-01:T5.VAL.STOP','mm','%.4f')
kbt6=SingleEpicsPositionerClass('kbt6','BL16I-MO-KBM-01:T6.VAL','BL16I-MO-KBM-01:T6.RBV','BL16I-MO-KBM-01:T6.DMOV','BL16I-MO-KBM-01:T6.VAL.STOP','mm','%.4f')
kbroll1=SingleEpicsPositionerClass('kbroll1','BL16I-MO-KBM-01:ROLL1.VAL','BL16I-MO-KBM-01:ROLL1.RBV','BL16I-MO-KBM-01:ROLL1.DMOV','BL16I-MO-KBM-01:ROLL1.VAL.STOP','mm','%.4f')
kbroll2=SingleEpicsPositionerClass('kbroll2','BL16I-MO-KBM-01:ROLL2.VAL','BL16I-MO-KBM-01:ROLL2.RBV','BL16I-MO-KBM-01:ROLL2.DMOV','BL16I-MO-KBM-01:ROLL2.VAL.STOP','mm','%.4f')
kbr1=kbroll1
kbr2=kbroll2
kbho=kbt3
kbvo=kbt4
kbbhd=kbt1
kbbhu=kbt2
kbbvu=kbt5
kbbvd=kbt6
a1=SingleEpicsPositionerClass('a1','BL16I-OP-ATTN-02:POSN.VAL','BL16I-OP-ATTN-02:POSN.RBV','BL16I-OP-ATTN-02:POSN.DMOV','BL16I-OP-ATTN-02:POSN.STOP','mm','%.2f') #added 08/02/2016
a1x=SingleEpicsPositionerSetAndGetOnlyClass('a1x','BL16I-EA-ANC-01:M3:POS','BL16I-EA-ANC-01:M3:POS','V','%5.2f',help='Attocube 1 x')

x2posneg=epics_binary_pos_neg('x2_ttl_posneg','BL16I-EA-USER-01:BO2','BL16I-EA-USER-01:BO2','logical','%.0f',help='TTL out socket x2 in posneg mode')


pilatus2m_thresh=SingleEpicsPositionerSetAndGetOnlyClass('pilatus2m_tresh','BL16I-EA-PILAT-02:CAM:ThresholdEnergy','BL16I-EA-PILAT-02:CAM:ThresholdEnergy','keV','%.2f',help='Pilatus 2M threshold via Epics Jython class')

blower_setpoint=SingleEpicsPositionerSetAndGetOnlyClass('cyberstar_gas_blower','BL16I-EA-BLOW-01:LOOP1:SP','BL16I-EA-BLOW-01:LOOP1:SP:RBV','deg C','%.1f',help='cyberstar gas blower setpoint deg C')

#pil3_thresh=SingleEpicsPositionerSetAndGetOnlyClass('pil3_tresh','BL16I-EA-PILAT-03:CAM:ThresholdEnergy','BL16I-EA-PILAT-03:CAM:ThresholdEnergy','keV','%.2f',help='Pilatus3 100K  threshold via Epics Jython class')


'''
Created on 30 Nov 2023

@author: eir17846
'''
from gdascripts.pd.epics_pds import SingleEpicsPositionerNoStatusClassDeadband
from gdascripts import installation as installation

if installation.isLive():
	sx1 = SingleEpicsPositionerNoStatusClassDeadband("sx1","BL09K-MO-SM-01:PI:X1:MOV:WR","BL09K-MO-SM-01:PI:X1:POS:RD","BL09K-MO-SM-01:PI:X1:SRG:RD","BL09K-MO-SM-01:PI:X1:HLT:WR.PROC","mm","%f",0.01)
	sx2 = SingleEpicsPositionerNoStatusClassDeadband("sx2","BL09K-MO-SM-01:PI:X2:MOV:WR","BL09K-MO-SM-01:PI:X2:POS:RD","BL09K-MO-SM-01:PI:X2:SRG:RD","BL09K-MO-SM-01:PI:X2:HLT:WR.PROC","mm","%f",0.01)
	sx3 = SingleEpicsPositionerNoStatusClassDeadband("sx3","BL09K-MO-SM-01:PI:X3:MOV:WR","BL09K-MO-SM-01:PI:X3:POS:RD","BL09K-MO-SM-01:PI:X3:SRG:RD","BL09K-MO-SM-01:PI:X3:HLT:WR.PROC","mm","%f",0.01)
	sy = SingleEpicsPositionerNoStatusClassDeadband("sy","BL09K-MO-SM-01:PI:Y:MOV:WR","BL09K-MO-SM-01:PI:Y:POS:RD","BL09K-MO-SM-01:PI:Y:SRG:RD","BL09K-MO-SM-01:PI:Y:HLT:WR.PROC","mm","%f",0.01)
	sz1 = SingleEpicsPositionerNoStatusClassDeadband("sz1","BL09K-MO-SM-01:PI:Z1:MOV:WR","BL09K-MO-SM-01:PI:Z1:POS:RD","BL09K-MO-SM-01:PI:Z1:SRG:RD","BL09K-MO-SM-01:PI:Z1:HLT:WR.PROC","mm","%f",0.01)
	sz2 = SingleEpicsPositionerNoStatusClassDeadband("sz2","BL09K-MO-SM-01:PI:Z2:MOV:WR","BL09K-MO-SM-01:PI:Z2:POS:RD","BL09K-MO-SM-01:PI:Z2:SRG:RD","BL09K-MO-SM-01:PI:Z2:HLT:WR.PROC","mm","%f",0.01)
	"""if defined as ScannableMotor then every pos there is error "target request is missed"!"""
	sxc = SingleEpicsPositionerNoStatusClassDeadband("sxc","BL09K-MO-SM-01:PI:X","BL09K-MO-SM-01:PI:X.RBV","BL09K-MO-SM-01:PI:X.MOVN","BL09K-MO-SM-01:PI:X.STOP","mm","%f",0.01)
	szc = SingleEpicsPositionerNoStatusClassDeadband("szc","BL09K-MO-SM-01:PI:Z","BL09K-MO-SM-01:PI:Z.RBV","BL09K-MO-SM-01:PI:Z.MOVN","BL09K-MO-SM-01:PI:Z.STOP","mm","%f",0.01)
else:
	from gda.device.scannable import DummyScannable #@UnresolvedImport
	sx1 = DummyScannable("sx1")
	sx2 = DummyScannable("sx2")
	sx3 = DummyScannable("sx3")
	sy  = DummyScannable("sy")
	sz1 = DummyScannable("sz1")
	sz2 = DummyScannable("sz2")
	sxc = DummyScannable("sxc")
	szc = DummyScannable("szc")
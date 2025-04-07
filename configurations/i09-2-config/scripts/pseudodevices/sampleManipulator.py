'''
Created on 30 Nov 2023

@author: eir17846
'''
from gdascripts.pd.epics_pds import SingleEpicsPositionerNoStatusClassDeadbandSyncInput
from gdascripts import installation as installation

if installation.isLive():
	base_pv = "BL09K-MO-SM-01:PI:"
	"""if defined as ScannableMotor then every pos there is error "target request is missed"!"""
	# sxc = SingleEpicsPositionerNoStatusClassDeadbandCheckInput("sxc","BL09K-MO-SM-01:PI:X","BL09K-MO-SM-01:PI:X.RBV","BL09K-MO-SM-01:PI:X.MOVN","BL09K-MO-SM-01:PI:X.STOP","mm","%f",0.01)
	# szc = SingleEpicsPositionerNoStatusClassDeadbandCheckInput("szc","BL09K-MO-SM-01:PI:Z","BL09K-MO-SM-01:PI:Z.RBV","BL09K-MO-SM-01:PI:Z.MOVN","BL09K-MO-SM-01:PI:Z.STOP","mm","%f",0.01)

	sx1 = SingleEpicsPositionerNoStatusClassDeadbandSyncInput("sx1",base_pv+"X1:MOV:WR","BL09K-MO-SM-01:PI:X1:POS:RD","BL09K-MO-SM-01:PI:X1:ONT:RD","BL09K-MO-SM-01:PI:X1:HLT:WR.PROC","mm","%f",0.01)
	sx2 = SingleEpicsPositionerNoStatusClassDeadbandSyncInput("sx2","BL09K-MO-SM-01:PI:X2:MOV:WR","BL09K-MO-SM-01:PI:X2:POS:RD","BL09K-MO-SM-01:PI:X2:ONT:RD","BL09K-MO-SM-01:PI:X2:HLT:WR.PROC","mm","%f",0.01)
	sx3 = SingleEpicsPositionerNoStatusClassDeadbandSyncInput("sx3","BL09K-MO-SM-01:PI:X3:MOV:WR","BL09K-MO-SM-01:PI:X3:POS:RD","BL09K-MO-SM-01:PI:X3:ONT:RD","BL09K-MO-SM-01:PI:X3:HLT:WR.PROC","mm","%f",0.01)
	sz1 = SingleEpicsPositionerNoStatusClassDeadbandSyncInput("sz1","BL09K-MO-SM-01:PI:Z1:MOV:WR","BL09K-MO-SM-01:PI:Z1:POS:RD","BL09K-MO-SM-01:PI:Z1:ONT:RD","BL09K-MO-SM-01:PI:Z1:HLT:WR.PROC","mm","%f",0.01)
	sz2 = SingleEpicsPositionerNoStatusClassDeadbandSyncInput("sz2","BL09K-MO-SM-01:PI:Z2:MOV:WR","BL09K-MO-SM-01:PI:Z2:POS:RD","BL09K-MO-SM-01:PI:Z2:ONT:RD","BL09K-MO-SM-01:PI:Z2:HLT:WR.PROC","mm","%f",0.01)
	sy  = SingleEpicsPositionerNoStatusClassDeadbandSyncInput("sy","BL09K-MO-SM-01:PI:Y:MOV:WR","BL09K-MO-SM-01:PI:Y:POS:RD","BL09K-MO-SM-01:PI:Y:ONT:RD","BL09K-MO-SM-01:PI:Y:HLT:WR.PROC","mm","%f",0.01)

else:
	from gda.device.scannable import DummyScannable #@UnresolvedImport
	import java #@UnresolvedImport
	base_pv = java.net.InetAddress.getLocalHost().getHostName().split(".")[0] + "-MO-SIM-01:"
	sx1 = SingleEpicsPositionerNoStatusClassDeadbandSyncInput("sx1",base_pv+"M1",base_pv+"M1.RBV",base_pv+"M1.DMOV",base_pv+"M1.STOP","mm","%f",0.01)
	sx2 = SingleEpicsPositionerNoStatusClassDeadbandSyncInput("sx2",base_pv+"M2",base_pv+"M2.RBV",base_pv+"M2.DMOV",base_pv+"M2.STOP","mm","%f",0.01)
	sx3 = SingleEpicsPositionerNoStatusClassDeadbandSyncInput("sx3",base_pv+"M3",base_pv+"M3.RBV",base_pv+"M3.DMOV",base_pv+"M3.STOP","mm","%f",0.01)
	sy 	= SingleEpicsPositionerNoStatusClassDeadbandSyncInput("sy", base_pv+"M4",base_pv+"M4.RBV",base_pv+"M4.DMOV",base_pv+"M4.STOP","mm","%f",0.01)
	sz1 = SingleEpicsPositionerNoStatusClassDeadbandSyncInput("sz1",base_pv+"M5",base_pv+"M5.RBV",base_pv+"M5.DMOV",base_pv+"M5.STOP","mm","%f",0.01)
	sz2 = DummyScannable("sz2")
'''
Created on 30 Nov 2023

@author: eir17846
'''
from gdascripts.pd.epics_pds import SingleEpicsPositionerNoStatusClassDeadband
sx1 = SingleEpicsPositionerNoStatusClassDeadband("sx1","BL09K-MO-SM-01:PI:X1:MOV:WR","BL09K-MO-SM-01:PI:X1:POS:RD","BL09K-MO-SM-01:PI:X1:SRG:RD","BL09K-MO-SM-01:PI:X1:HLT:WR.PROC","mm","%f",0.01)
sx2 = SingleEpicsPositionerNoStatusClassDeadband("sx2","BL09K-MO-SM-01:PI:X2:MOV:WR","BL09K-MO-SM-01:PI:X2:POS:RD","BL09K-MO-SM-01:PI:X2:SRG:RD","BL09K-MO-SM-01:PI:X2:HLT:WR.PROC","mm","%f",0.01)
sx3 = SingleEpicsPositionerNoStatusClassDeadband("sx3","BL09K-MO-SM-01:PI:X3:MOV:WR","BL09K-MO-SM-01:PI:X3:POS:RD","BL09K-MO-SM-01:PI:X3:SRG:RD","BL09K-MO-SM-01:PI:X3:HLT:WR.PROC","mm","%f",0.01)
sy = SingleEpicsPositionerNoStatusClassDeadband("sy","BL09K-MO-SM-01:PI:Y:MOV:WR","BL09K-MO-SM-01:PI:Y:POS:RD","BL09K-MO-SM-01:PI:Y:SRG:RD","BL09K-MO-SM-01:PI:Y:HLT:WR.PROC","mm","%f",0.01)
sz1 = SingleEpicsPositionerNoStatusClassDeadband("sz1","BL09K-MO-SM-01:PI:Z1:MOV:WR","BL09K-MO-SM-01:PI:Z1:POS:RD","BL09K-MO-SM-01:PI:Z1:SRG:RD","BL09K-MO-SM-01:PI:Z1:HLT:WR.PROC","mm","%f",0.01)
sz2 = SingleEpicsPositionerNoStatusClassDeadband("sz2","BL09K-MO-SM-01:PI:Z2:MOV:WR","BL09K-MO-SM-01:PI:Z2:POS:RD","BL09K-MO-SM-01:PI:Z2:SRG:RD","BL09K-MO-SM-01:PI:Z2:HLT:WR.PROC","mm","%f",0.01)

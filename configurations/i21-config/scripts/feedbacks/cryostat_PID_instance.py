'''
create an object 'cryostat_PID' that provides PID control of cryostat temperature ramping rate to prevent vacuum pressure reach too high

USAGE:
    To start this PID control:
        >>>cryostat_PID.start()
    To stop this PID control:
        >>>cryostat_PID.stop()
        
Created on 14 Feb 2018

@author: fy65
'''
from gdascripts.pd.epics_pds import DisplayEpicsPVClass
from feedbacks.cryostatPID import cryostatPID
from gdaserver import lakeshore
gauge21=DisplayEpicsPVClass("gauge21","BL21I-VA-GAUGE-21:P","mbar","%.2e")
cryostat_PID=cryostatPID(lakeshore,gauge21,maxRampRate=10.0, minRampRate=0.05,maxPressure=5e-8)

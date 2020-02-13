'''
create an object 'temperature' that provides control of cryostat temperature ramping rate to prevent vacuum pressure exceed <maxPressure>

USAGE:
    pos temperature <new_temperature_value>
        
Created on 06 Feb 2019

@author: fy65
'''
print "-"*100
print "create an object 'temperature' that provides control of cryostat temperature ramping rate to prevent vacuum pressure exceed <maxPressure>"

from gdascripts.pd.epics_pds import DisplayEpicsPVClass
from gdaserver import lakeshore
from feedbacks.cryostatWarmUp import CryostatWarmUp
gauge21=DisplayEpicsPVClass("gauge21","BL21I-VA-GAUGE-21:P","mbar","%.2e")
tsample=CryostatWarmUp("tsample",lakeshore,gauge21,maxRampRate = 10.0, minRampRate=0.1, maxPressure = 5e-8, pressureFactor=3.0, sleepTime=10.0, tolerance=0.001, lowThreshold=130.0, highThreshold=160.0, maxRampRate130_160=1.0)
tsample.tolerance_demand=0.001
tsample.tolerance_sample=5.0
tsample.MAX_RAMP_RATE=10.0
tsample.MAX_RAMP_RATE_130_160=1.0
tsample.CRYO_SAMPLE_DIFFERENCE=8.0
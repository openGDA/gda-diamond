'''
This module creates I11 specific gas rig objects: 
    mfc1 - mass flow controller 1
    mfc2 - mass flow controller 2
    mfc3 - mass flow controller 3
    bpr - BPR pressure controller
    dvpc - DVPC pressure controller
    gasrig - injection control

each object provides methods for accessing EPICS PV field with method name match what it is on the EDM GUI in EPICS.
To access methods of these objects use 'dot' operator like:

>>>mfc1.setTarget(10.0) 

You can find what methods available for each object from its defining class, or at GDA Jython Terminal use 'objectName.+<CTRL-Space>'.
Created on 6 Dec 2013

@author: fy65
'''
from gasrig.alicatMassFlowController import AlicatMassFlowController 
from gasrig.gasRig import GasRigClass
from gasrig.alicatPressureController import AlicatPressureController
from gasrig.samplePressure import SamplePressure


#sampleP=SamplePressure("sampleP", bpr)
gasrig=GasRigClass("gasrig", "BL11J-EA-GIR-01:")

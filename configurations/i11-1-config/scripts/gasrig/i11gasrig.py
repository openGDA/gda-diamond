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

mfc1=AlicatMassFlowController("mfc1","I11GasRig:MFC1:","%.3f")
mfc2=AlicatMassFlowController("mfc2","I11GasRig:MFC2:","%.3f")
mfc3=AlicatMassFlowController("mfc3","I11GasRig:MFC3:","%.3f")
bpr=AlicatPressureController("bpr","I11GasRig:BPR:","%.3f")
dvpc=AlicatPressureController("dvpc","I11GasRig:DVPC:","%.3f")
gasrig=GasRigClass("gasrig", "I11GasRig:")
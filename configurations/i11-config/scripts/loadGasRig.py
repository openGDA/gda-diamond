'''
Created on 10 Sep 2015

@author: fy65
'''
from types import NoneType
from gasrig.gdaScriptDose import DoseControl
from gasrig.gadSriptVac import VacControl
#dose=DoseControl("dose","BL11I-EA-GIR-01:BPR:P:RD")
#vac=VacControl("vac")

print "-----------------------------------------------------------------------------------------------------------------"
print "Create 'gasrig' object to control Gas Panel"
#from gasrig.gasRig import *  # @UnusedWildImport
from gasrig.alicatMassFlowController import AlicatMassFlowController  # @UnusedImport
from gasrig.gasRig import GasRigClass
from gasrig.alicatPressureController import AlicatPressureController  # @UnusedImport
from gasrig.samplePressure import SamplePressure  # @UnusedImport
gasrig=GasRigClass("gasrig", "BL11I-EA-GIR-01:")
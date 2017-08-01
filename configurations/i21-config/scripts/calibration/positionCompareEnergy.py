'''
Created on 1 Dec 2016

@author: fy65
'''
from calibration.positionCompareMotorClass import PositionCompareMotorClass

pgmenergy=PositionCompareMotorClass("pgmenergy","BL21I-OP-PGM-01:ENERGY.VAL", "BL21I-OP-PGM-01:ENERGY.RBV", "BL21I-OP-PGM-01:ENERGY.STOP", 0.01, "eV", "%5.2f", delay=0.0)
print "Create an 'new_energy' scannable which can be used for energy scan in GDA. It moves both ID gap and PGM energy"
new_energy=BeamEnergy("new_energy",idscannable, idgap, pgmenergy)  # @UndefinedVariable

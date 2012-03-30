'''
example usage of the PositionCompareMotorClass - I12 Large Sample table PMAC motors

Created on 27 Oct 2010

@author: fy65
'''
from epics.motor.positionCompareMotorClass import PositionCompareMotorClass

# Input data must be replaced by PV names of your beamline hexapod device

# the root PV name for the device, must be set to beamline value"
deviceName="BL12I-MO-TAB-06"

x_inputPV=deviceName+":X:DEMAND"
x_readbackPV=deviceName+":X:POSRB"
x_stopPV=deviceName+":X:STOP"
x_tolerance=0.001
y_inputPV=deviceName+":Y:DEMAND"
y_readbackPV=deviceName+":Y:POSRB"
y_stopPV=deviceName+":Y:STOP"
y_tolerance=0.001
z_inputPV=deviceName+":Z:DEMAND"
z_readbackPV=deviceName+":Z:POSRB"
z_stopPV=deviceName+":Z:STOP"
z_tolerance=0.001
p_inputPV=deviceName+":PITCH:DEMAND"
p_readbackPV=deviceName+":PITCH:POSRB"
p_stopPV=deviceName+":PITCH:STOP"
p_tolerance=0.001
t_inputPV=deviceName+":THETA:DEMAND"
t_readbackPV=deviceName+":THETA:POSRB"
t_stopPV=deviceName+":THETA:STOP"
t_tolerance=0.001

ss2x=PositionCompareMotorClass('ss2x', x_inputPV, x_readbackPV, x_stopPV, x_tolerance, 'mm', '%4.3f')
ss2y=PositionCompareMotorClass('ss2y', y_inputPV, y_readbackPV, y_stopPV, y_tolerance, 'mm', '%4.3f')
ss2z=PositionCompareMotorClass('ss2z', z_inputPV, z_readbackPV, z_stopPV, z_tolerance, 'mm', '%4.3f')
ss2pitch=PositionCompareMotorClass('ss2pitch', p_inputPV, p_readbackPV, p_stopPV, p_tolerance, 'mm', '%4.3f')
ss2theta=PositionCompareMotorClass('ss2theta', t_inputPV, t_readbackPV, t_stopPV, t_tolerance, 'mm', '%4.3f')

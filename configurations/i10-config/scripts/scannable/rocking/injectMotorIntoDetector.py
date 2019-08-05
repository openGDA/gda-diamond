'''
modify a specified NXDetector instance so a specified motor is moving during the detector exposure period.

Run this script will permanently change the detector's behaviour until reset_namespace.

To recover the original detector use reset_namespace!

Created on 2 Aug 2019

@author: fy65
'''
from gdaserver import pimte, th
import types
import math

ROCKING_RANGE_CENTRE=0.0
#edit the following line for your selected detector
detector=pimte
#edit the following line for your selected motor
motor=th

ADJUST_MOTOR_SPEED=False

def calculateStartStopPosition(changeSpeed):
    if not changeSpeed:
        motor_range = motor.getSpeed()*detector.getCollectionTime()
        
        if motor_range > (motor.getUpperMotorLimit()-motor.getLowerMotorLimit()):
            raise Exception("motor rocking range is greater than hardware limits permitted")
        
        start_motor_angle=ROCKING_RANGE_CENTRE-motor_range/2.0
        end_motor_angle=ROCKING_RANGE_CENTRE+motor_range/2.0
        
        if (start_motor_angle/2.0) < motor.getLowerMotorLimit():
            raise Exception("start rocking angle is outside hardware low limit")
        if (end_motor_angle/2.0) > motor.getUpperMotorLimit():
            raise Exception("end rocking angle is outside hardware high limit")
    else:
        motorspeed=(motor.getUpperMotorLimit() - motor.getLowerMotorLimit())/detector.getCollectionTime()
        #Need to check if motor speed is valid or not
        motor.setSpeed(motorspeed)
        start_motor_angle = motor.getLowerMotorLimit()
        end_motor_angle = motor.getUpperMotorLimit()
    return start_motor_angle, end_motor_angle
    
def _atScanStart(self):
    self.atScanStart()
    self.start_motor_angle,self.end_motor_angle = calculateStartStopPosition(ADJUST_MOTOR_SPEED)
    motor.moveTo(self.start_motor_angle)
    
def _collectData(self):
    curpos = float(motor.getPosition())
    if math.fabs(curpos - self.start_motor_angle) < math.fabs(curpos - self.end_motor_angle): 
        motor.asynchronousMoveTo(self.end_motor_angle)
    else:
        motor.asynchronousMoveTo(self.start_motor_angle)
    self.collectData()
    
def _readout(self):
    motor.stop()
    return self.readout()

detector.atScanStart = types.MethodType(_atScanStart, detector)
detector.collectData = types.MethodType(_collectData, detector)
detector.readout = types.MethodType(_readout, detector)

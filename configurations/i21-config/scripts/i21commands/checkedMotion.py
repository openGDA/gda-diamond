'''
i21commands.checkedMotion -- define 'move' commands that check if requested target is achievable or not. 

i21commands.checkedMotion is a module defining new command for moving motor if and only if the specified conditions are meet.

if conditions are not meet, the move is blocked and exception throws giving the reason.

@author:     Fajin Yuan
@updated:    20 June 2022
@copyright:  2019 Diamond Light Source Ltd. All rights reserved.
@license:    license
@contact:    fajin.yuan@diamond.ac.uk
'''
from lookup.twoKeysLookupTable2 import loadLookupTable
import math
from time import sleep
from gdascripts.utils import caput
from scannabledevices.M5GroupScannable import alltth
import installation
from gda.configuration.properties import LocalProperties


__all__ = []
__version__ = 0.1
__date__ = '2019-04-25'
__updated__ = '2022-06-20'

MOTOR_POSITION_TOLERANCE = 0.005

lookuptable = loadLookupTable(LocalProperties.get("gda.config") + "/lookupTables/ArmMotionProtectionLimits2.txt")

    
def move_within_limits(current, demand):
    in_range = False
    for key in lookuptable.keys():
        in_range = (current >= key[0] and current <= key[1]) and (demand >= key[0] and demand <= key[1]) or in_range
    return in_range


def find_range(current, demand):
    for key in lookuptable.keys():
        if (current >= key[0] and current <= key[1]) and (demand >= key[0] and demand <= key[1]):
            return key
    return None


def is_sgmr1_in_range(current, key):
    if (current >= lookuptable[key][0] and current <= lookuptable[key][1]):
        return True
    return False


class IllegalMoveException(Exception):
    ''' Raised when an operation attempts to move a motor to positions that's not allowed.
    '''
    pass

from gdaserver import sgmr1, specl, armtth, spech, armtthoffset# @UnresolvedImport
    
def enable_arm_motion():
    '''this function just clear following errors for specl and spech
    '''
    if installation.isDummy():
        print("set BL21I-MO-ARM-01:CLRF to clrf")
    else:
        caput("BL21I-MO-ARM-01:CLRF", 'msclrf4 msclrf5 clrf')
        sleep(1)
        spech.stop()
        specl.stop()


def check_armtth_and_move_sgmr1_if_required(motor, new_position):
    if not move_within_limits(float(motor.getPosition()), float(new_position)):
        raise IllegalMoveException("Cannot move across region limits %s from %f to %f" % (sorted(lookuptable.keys()), float(motor.getPosition()), new_position))
    else:
        found_range = find_range(float(motor.getPosition()), float(new_position))
        if found_range is None:
            raise IllegalMoveException("Your requested move is outside the legal range limits %s" % (sorted(lookuptable.keys())))
        # check if sgmr1 is at safe position
        sgmr1_current = float(sgmr1.getPosition())
        if not is_sgmr1_in_range(sgmr1_current, found_range):
            if (math.fabs(sgmr1_current - lookuptable[found_range][0]) < math.fabs(sgmr1_current - lookuptable[found_range][1])):
                sgmr1.moveTo(lookuptable[found_range][0] + 1.0)
                print('sleep 1 second after sgmr1 move')
                sleep(1)
            else:
                sgmr1.moveTo(lookuptable[found_range][1] - 1.0)
                print('sleep 1 second after sgmr1 move')
                sleep(1)

def check_if_move_legal(motor, new_position):
    '''check motor limits using lookup table data. this is to work around the issues related to motion stuck problems
    '''
    if motor is alltth:
        motor = motor.armtth # Only need to check armtth motor in the group alltth motor
        
    if math.fabs(float(motor.getPosition()) - float(new_position)) <= MOTOR_POSITION_TOLERANCE:
        print("Motor '%s' is already in position." % (motor.getName()))
        return True
    
    if motor is armtth:
        check_armtth_and_move_sgmr1_if_required(motor, new_position)    
        if math.fabs(float(motor.getPosition()) - float(new_position)) > MOTOR_POSITION_TOLERANCE:
            return False
        else:
            print("Motor '%s' is already in position." % (motor.getName()))
            return True
    elif motor is sgmr1:
        if math.fabs(float(motor.getPosition()) - float(new_position)) > MOTOR_POSITION_TOLERANCE:
            return False
        else:
            print("Motor '%s' is already in position." % (motor.getName()))
            return True
    elif motor is spech or motor is specl:
        enable_arm_motion()
        return False


def switch_on_air_supply(motor):
    if (motor is armtth or motor is alltth) and not armtth.isOn():
        armtth.on()
        if not sgmr1.isOn():
            sgmr1.on()
        print("switch arm air on, wait for 14 seconds.")
        sleep(14.0)
        print("sleep 1 second after call armtth stop to clear following error")
        sleep(1.0)
    if motor is sgmr1 and not sgmr1.isOn():
        sgmr1.on()
        print("switch sgm air on, wait for 10 seconds.")
        sleep(10.0)


def switch_off_air_supply(motor):
    if motor is armtth or motor is sgmr1 or motor is alltth:
        armtth.off()
        sgmr1.off()
        print("air supply is off for both sgmr1 and armtth!")

def move(motor, new_position, sgmr1_val=None):
    if not check_if_move_legal(motor, new_position):
        #switch on air supply if they are not on yet
        switch_on_air_supply(motor)
        
        #the following 2 ifs should not be here - this is an awful hack to ensure remove of following error in motor
        #motor engineer should solve the following error issue in the motor driver
        if motor is armtth or motor is alltth:
            armtth.stop() #called to clear following error of the motor
            sgmr1.stop()
        if motor is sgmr1:
            sgmr1.stop()
   
        print("moving '%s' to %f ...."  % (motor.getName(), new_position))
        motor.moveTo(new_position)
        print("sleep 5 seconds after %s move." % motor.getName())
        sleep (5)
        
        #reset motor values
        if motor is armtth or motor is alltth:
            armtthoffset.moveTo(-0.1)
            sgmr1.moveTo(sgmr1_val)
            print("%s moves completed at %f" % (motor.getName(), motor.getPosition()))
            
        #switch off air supply
        switch_off_air_supply(motor)

try:
    from gda.jython.commands.GeneralCommands import alias
    alias("move")
    alias("enable_arm_motion")
except Exception, e:
    pass


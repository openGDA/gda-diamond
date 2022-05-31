'''
i21commands.checkedMotion -- define 'move' and 'asynmove' commands that check if it is safe to proceed with the move demand. 

i21commands.checkedMotion is a module defining new command for moving motor if and only if the specified conditions are meet.

It defines methods 'move' and 'asynmove' which checks if the safe conditions are satisfied or not before any move. 
if conditions are not meet, the move is blocked and exception throw giving the reason.

@author:     Fajin Yuan

@copyright:  2019 Diamond Light Source Ltd. All rights reserved.

@license:    license

@contact:    fajin.yuan@diamond.ac.uk
@deffield    updated: Updated
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
__updated__ = '2019-04-25'

SGMR1_TOLERANCE = 10.0
SPECL_TOLERANCE = 20.0
MOTOR_POSITION_TOLERANCE = 0.005
MOTION_INCREMENT = 10.0

lookuptable = loadLookupTable(LocalProperties.get("gda.config") + "/lookupTables/ArmMotionProtectionLimits2.txt")
# for key, value in lookuptable.iteritems():
#     print key, value
# print "region limits %s" % sorted(lookuptable.keys())

    
def moveWithinLimits(current, demand):
    inRange = False
    for key in lookuptable.keys():
        inRange = (current >= key[0] and current <= key[1]) and (demand >= key[0] and demand <= key[1]) or inRange
#         print key, inRange
    return inRange


def findRange(current, demand):
    for key in lookuptable.keys():
        if (current >= key[0] and current <= key[1]) and (demand >= key[0] and demand <= key[1]):
            return key
    return None


def isSgmr1InRange(current, key):
    if (current >= lookuptable[key][0] and current <= lookuptable[key][1]):
        return True
    return False


def isSpeclInRange(current, key):
    if (current >= lookuptable[key][2] and current <= lookuptable[key][3]):
        return True
    return False
    

class UnsafeOperationException(Exception):
    ''' Raised when an operation attempts to move a motor to positions that's not allowed.
    '''
    pass


class IllegalMoveException(Exception):
    ''' Raised when an operation attempts to move a motor to positions that's not allowed.
    '''
    pass

from gdaserver import sgmr1, specl, armtth, spech, armtthoffset# @UnresolvedImport
    
def enable_arm_motion():
    '''this function just clear errors
    '''
    if installation.isDummy():
        print("set BL21I-MO-ARM-01:CLRF to clrf")
    else:
        caput("BL21I-MO-ARM-01:CLRF", 'clrf')
    sleep(1)

def checkIfMoveLegal(motor, new_position):
    '''
    '''
    if motor is alltth:  # @UndefinedVariable
        motor = motor.armtth # Only need to check armtth motor in the group
        
    if math.fabs(float(motor.getPosition()) - float(new_position)) <= MOTOR_POSITION_TOLERANCE:
        print("Motor '%s' is already in position." % (motor.getName()))
        return True
    
    if motor is armtth:  # @UndefinedVariable
        if not moveWithinLimits(float(motor.getPosition()), float(new_position)):
            raise IllegalMoveException("Cannot move across region limits %s from %f to %f" % (sorted(lookuptable.keys()), float(motor.getPosition()), new_position))
        else:
            find_range = findRange(float(motor.getPosition()), float(new_position))
            if find_range is None:
                raise IllegalMoveException("Your requested move is outside the legal range limits %s" % (sorted(lookuptable.keys())))
            # check if sgmr1 is at safe position
            sgmr1_current=float(sgmr1.getPosition())
            if not isSgmr1InRange(sgmr1_current, find_range):
                if armtth.isOn():
                    armtth.off()
                    print("switch arm air off, wait for 10 seconds.")
                    sleep(10.0)
                if not sgmr1.isOn():
                    sgmr1.on()
                    print("switch sgm air on, wait for 8 seconds.")
                    sleep(8.0)                    
                if (math.fabs(sgmr1_current-lookuptable[find_range][0]) < math.fabs(sgmr1_current-lookuptable[find_range][1])):
                    sgmr1.moveTo(lookuptable[find_range][0]+1.0)
                    print('sleep 1 second after sgmr1 move')
                    sleep(1)
                else:
                    sgmr1.moveTo(lookuptable[find_range][1]-1.0)
                    print('sleep 1 second after sgmr1 move')
                    sleep(1)
#             if math.fabs(float(sgmr1.getPosition()) - lookuptable[find_range][0]) > SGMR1_TOLERANCE:
#                 raise UnsafeOperationException("Cannot proceed as 'sgmr1' is not at the required safe position of %f" % (lookuptable[find_range][0]))
#            
            # check if specl is at safe position
            specl_current=float(specl.getPosition())
            if not isSpeclInRange(specl_current, find_range):
                enable_arm_motion()
                if (math.fabs(specl_current-lookuptable[find_range][2]) < math.fabs(specl_current-lookuptable[find_range][3])):
                    specl.moveTo(lookuptable[find_range][2]+1.0)
                else:
                    specl.moveTo(lookuptable[find_range][3]-1.0)  
                             
#             if math.fabs(float(specl.getPosition()) - lookuptable[find_range][1]) > SPECL_TOLERANCE:
#                 raise UnsafeOperationException("Cannot proceed as 'specl' is not at the required safe position of %f" % (lookuptable[find_range][1]))
#         
        if math.fabs(float(motor.getPosition()) - float(new_position)) > MOTOR_POSITION_TOLERANCE:
            if sgmr1.isOn():
                sgmr1.off()  # switch off air
                print("switch sgm air off, wait for 8 seconds.")
                sleep(8.0)
            if not armtth.isOn():
                armtth.on()  # switch on air
                print("switch arm air on, wait for 14 seconds.")
                sleep(14.0)
                armtth.stop() #called to clear following error of the motor
                print("sleep 1 second after call armtth stop to clear following error")
                sleep(1.0)
            return False
        else:
            print("Motor '%s' is already in position." % (motor.getName()))
            return True
    elif motor is sgmr1:
        if math.fabs(float(motor.getPosition()) - float(new_position)) > MOTOR_POSITION_TOLERANCE:
            if armtth.isOn():
                armtth.off()
                sleep(10.0)
            if not sgmr1.isOn():
                sgmr1.on()
                sleep(8.0)
            return False
        else:
            print("Motor '%s' is already in position." % (motor.getName()))
            return True
    elif motor is spech or motor is specl:
        enable_arm_motion()
        return False
            

def move(motor, new_position, sgmr1_val=None, specl_val=None):
    if not checkIfMoveLegal(motor, new_position):
        print("moving '%s' to %f ...."  % (motor.getName(), new_position))
        motor.moveTo(new_position)
        print("sleep 5 seconds after %s move." % motor.getName())
        sleep (5)
        if motor is armtth or motor is alltth:
            armtthoffset.moveTo(-0.14)
            if sgmr1_val:
                if armtth.isOn():
                    armtth.off()
                    print("switch arm air off, wait for 15 seconds.")
                    sleep(15.0)
#                 if not sgmr1.isOn():
                sgmr1.on()
                print("switch sgm air on, wait for 10 seconds.")
                sleep(10.0)
                sgmr1.moveTo(sgmr1_val)
            if specl_val:
                enable_arm_motion()
                specl.moveTo(specl_val)
            print("%s moves completed at %f" % (motor.getName(), motor.getPosition()))

            if motor is armtth or motor is sgmr1 or motor is alltth:
                armtth.off()
                sgmr1.off()
                print("air supply is off for both sgmr1 and armtth!")


def asynmove(motor, new_position):
    if not checkIfMoveLegal(motor, new_position):
        motor.asynchronousMoveTo(new_position)
        print("%s starts to move to %f " % (motor.getName(), new_position))


try:
    from gda.jython.commands.GeneralCommands import alias
    alias("move")
    alias("asynmove")
    alias("enable_arm_motion")
except Exception, e:
    pass


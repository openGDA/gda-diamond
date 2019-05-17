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

__all__ = []
__version__ = 0.1
__date__ = '2019-04-25'
__updated__ = '2019-04-25'

SGMR1_TOLERANCE=10.0
SPECL_TOLERANCE=20.0
MOTOR_POSITION_TOLERANCE=0.01

lookuptable=loadLookupTable("/dls_sw/i21/software/gda/config/lookupTables/ArmMotionProtectionLimits.txt")
# for key, value in lookuptable.iteritems():
#     print key, value
# print "region limits %s" % sorted(lookuptable.keys())
    
def moveWithinLimits(current, demand):
    inRange=False
    for key in lookuptable.keys():
        inRange = (current >= key[0] and current <= key[1]) and (demand >= key[0] and demand <= key[1]) or inRange
#         print key, inRange
    return inRange

def findRange(current, demand):
    for key in lookuptable.keys():
        if (current >= key[0] and current <= key[1]) and (demand >= key[0] and demand <= key[1]):
            return key
    return None

class UnsafeOperationException(Exception):
    ''' Raised when an operation attempts to move a motor to positions that's not allowed.
    '''
    pass

class IllegalMoveException(Exception):
    ''' Raised when an operation attempts to move a motor to positions that's not allowed.
    '''
    pass

def checkIfMoveLegal(motor, new_position):
    '''
    '''
    from gdaserver import sgmr1, specl, epics_armtth
    if motor is armtth:  # @UndefinedVariable
        if not moveWithinLimits(float(motor.getPosition()), float(new_position)):
            raise IllegalMoveException("Cannot move across region limits %s from %f to %f" % (sorted(lookuptable.keys()), float(motor.getPosition()), new_position))
        else:
            find_range = findRange(float(motor.getPosition()), float(new_position))
            if find_range is None:
                raise IllegalMoveException("Your requested move is outside the legal range limits %s" % (sorted(lookuptable.keys())))
            #check if sgmr1 is at safe position
            if math.fabs(float(sgmr1.getPosition()) - lookuptable[find_range][0]) > SGMR1_TOLERANCE:
                raise UnsafeOperationException("Cannot proceed as 'sgmr1' is not at the required safe position of %f" % (lookuptable[find_range][0]))
            #check if specl is at safe position
            if math.fabs(float(specl.getPosition()) - lookuptable[find_range][1]) > SPECL_TOLERANCE:
                raise UnsafeOperationException("Cannot proceed as 'specl' is not at the required safe position of %f" % (lookuptable[find_range][1]))
        if math.fabs(float(motor.getPosition())-float(new_position))>MOTOR_POSITION_TOLERANCE:
            if sgmr1.isOn():
                sgmr1.off() #switch off air
                sleep(8.0)
            if not epics_armtth.isOn():
                epics_armtth.on() # switch on air
                sleep(8.0)
            return False
        else:
            print "Motor '%s' is already in position." % (motor.getName())
            return True
    elif motor is sgmr1:
        if math.fabs(float(motor.getPosition())-float(new_position))>MOTOR_POSITION_TOLERANCE:
            if epics_armtth.isOn():
                epics_armtth.off()
                sleep(10.0)
            if not sgmr1.isOn():
                sgmr1.on()
                sleep(8.0)
            return False
        else:
            print "Motor '%s' is already in position." % (motor.getName())
            return True

            

def move(motor, new_position):
    if not checkIfMoveLegal(motor, new_position):
        motor.moveTo(new_position)
        print "%s moves completed at %f" % (motor.getName(), motor.getPosition())

def asynmove(motor, new_position):
    if not checkIfMoveLegal(motor, new_position):
        motor.asynchronousMoveTo(new_position)
        print "%s starts to move to %f " % (motor.getName(), new_position)

try:
    from gda.jython.commands.GeneralCommands import alias
    alias("move")
    alias("asynmove")
except:
    pass


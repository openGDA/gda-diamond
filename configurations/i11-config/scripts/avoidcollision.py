'''
Created on 17 Oct 2011

@author: fy65
'''
from gda.factory import Finder
from gda.hrpd.pmac import UnsafeOperationException
macsafeposition=Finder.find("macsafeposition")
psdsafeposition=Finder.find("psdsafeposition")
MAC_SAFE_POSITION=macsafeposition.getPosition()
MAC_SAFE_POSITION_TOLERANCE=macsafeposition.getTolerance()
PSD_SAFE_POSITION=psdsafeposition.getPosition()
PSD_SAFE_POSITION_TOLERANCE=psdsafeposition.getTolerance()


def move(motor, new_position):
    if motor is tth: #@UndefinedVariable
        if not psdsafeposition.test(float(delta.getPosition())):
            delta.moveTo(PSD_SAFE_POSITION)
        if not psdsafeposition.test(float(delta.getPosition())): #@UndefinedVariable
            raise UnsafeOperationException(float(delta.getPosition()), PSD_SAFE_POSITION, "Cannot proceed as PSD detector is not at safe position.") #@UndefinedVariable
        else:
            motor.moveTo(new_position)
            print "%s move completed at %f" % (motor.getName(), motor.getPosition())
    elif motor is delta: #@UndefinedVariable
        if not macsafeposition.test(float(tth.getPosition())):
            tth.moveTo(MAC_SAFE_POSITION)
        if not macsafeposition.test(float(tth.getPosition())): #@UndefinedVariable
            raise UnsafeOperationException(float(tth.getPosition()),MAC_SAFE_POSITION, "Cannot proceed as MAC detector is not at safe position.") #@UndefinedVariable
        else:
            motor.moveTo(new_position)
            print "%s move completed at %f" % (motor.getName(), motor.getPosition())

def asynmove(motor, new_position):
    if motor is tth: #@UndefinedVariable
        if not psdsafeposition.test(float(delta.getPosition())): #@UndefinedVariable
            raise UnsafeOperationException(float(delta.getPosition()), PSD_SAFE_POSITION, "Cannot proceed as PSD detector is not at safe position.") #@UndefinedVariable
        else:
            motor.asynchronousMoveTo(new_position)
            print "%s starts to move" % (motor.getName())
    elif motor is delta: #@UndefinedVariable
        if not macsafeposition.test(float(tth.getPosition())): #@UndefinedVariable
            raise UnsafeOperationException(float(tth.getPosition()),MAC_SAFE_POSITION, "Cannot proceed as MAC detector is not at safe position.") #@UndefinedVariable
        else:
            motor.asynchronousMoveTo(new_position)
            print "%s starts to move" % (motor.getName())

from gda.jython.commands.GeneralCommands import alias
alias("move")
alias("asynmove")
#
class UnsafeOperation(Exception):
    ''' Raised when an operation attempts to move a motor to positions that's not allowed.

    Attributes:
        prev -- position at the beginning of motion
        next -- attempted new position
        msg  -- explanation of why the specific transition is not allowed
    '''
    def __init__(self, prev, next, msg):
        self.prev = prev
        self.next = next
        self.msg = msg


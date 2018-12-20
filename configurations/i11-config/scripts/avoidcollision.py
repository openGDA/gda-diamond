'''
Created on 17 Oct 2011

@author: fy65
'''
from gda.factory import Finder
from gda.hrpd.pmac import UnsafeOperationException
finder=Finder.getInstance()
macsafeposition=finder.find("macsafeposition")
psdsafeposition=finder.find("psdsafeposition")
MAC_SAFE_POSITION=macsafeposition.getPosition()
MAC_SAFE_POSITION_TOLERANCE=macsafeposition.getTolerance()
PSD_SAFE_POSITION=psdsafeposition.getPosition()
PSD_SAFE_POSITION_TOLERANCE=psdsafeposition.getTolerance()


def move(motor, new_position):
    if motor is tth: #@UndefinedVariable
        if abs(float(delta.getPosition()) - PSD_SAFE_POSITION) > PSD_SAFE_POSITION_TOLERANCE: #@UndefinedVariable
            raise UnsafeOperationException(float(delta.getPosition()), PSD_SAFE_POSITION, "Cannot proceed as PSD detector is not at safe position.") #@UndefinedVariable
        else:
            motor.moveTo(new_position)
            print "%s move completed at %f" % (motor.getName(), motor.getPosition())
    elif motor is delta: #@UndefinedVariable
        if abs(float(tth.getPosition()) - MAC_SAFE_POSITION) > MAC_SAFE_POSITION_TOLERANCE: #@UndefinedVariable
            raise UnsafeOperationException(float(tth.getPosition()),MAC_SAFE_POSITION, "Cannot proceed as MAC detector is not at safe position.") #@UndefinedVariable
        else:
            motor.moveTo(new_position)
            print "%s move completed at %f" % (motor.getName(), motor.getPosition())

def asynmove(motor, new_position):
    if motor is tth: #@UndefinedVariable
        if abs(float(delta.getPosition()) - PSD_SAFE_POSITION) > PSD_SAFE_POSITION_TOLERANCE: #@UndefinedVariable
            raise UnsafeOperationException(float(delta.getPosition()), PSD_SAFE_POSITION, "Cannot proceed as PSD detector is not at safe position.") #@UndefinedVariable
        else:
            motor.asynchronousMoveTo(new_position)
            print "%s starts to move" % (motor.getName())
    elif motor is delta: #@UndefinedVariable
        if abs(float(tth.getPosition()) - MAC_SAFE_POSITION) > MAC_SAFE_POSITION_TOLERANCE: #@UndefinedVariable
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
        

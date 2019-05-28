'''
i09 command.checkedMotion -- define 'move' command that check if feedbacks need to be disabled or not for the move demand. 

i09 command.checkedMotion is a module defining new command for moving motor - ienergy and jenergy in which feedback will be disable and enabled when required..

@author:     Fajin Yuan

@copyright:  2019 Diamond Light Source Ltd. All rights reserved.

@license:    license

@contact:    fajin.yuan@diamond.ac.uk
@deffield    updated: Updated
'''
import math
from gdaserver import dcmfrollfeedback, dcmfpitchfeedback, sm1fpitchfeedback

__all__ = []
__version__ = 0.1
__date__ = '2019-05-03'
__updated__ = '2019-05-03'

IENERGY_MOVE_LIMIT=0.050 # 50eV hard X-ray
JENERGY_MOVE_LIMIT=0.010 # 50eV hard X-ray
  
def moveWithinLimits(current, demand, change_range):
    if math.fabs(current-demand) < change_range:
        return True
    else:
        return False

def move(motor, new_position):
    '''enable or disable EPICS feedbacks depending on the energy changes requested
    '''
    if motor is ienergy:  # @UndefinedVariable
        if not moveWithinLimits(float(motor.getPosition()), float(new_position), IENERGY_MOVE_LIMIT):
            dcmfrollfeedback.moveTo("Disabled")
            dcmfpitchfeedback.moveTo("Disabled")
            motor.moveTo(new_position)
            dcmfrollfeedback.moveTo("Enabled")
            dcmfpitchfeedback.moveTo("Enabled")
        else:
            motor.moveTo(new_position)
    elif motor is jenergy:  # @UndefinedVariable
        if not moveWithinLimits(float(motor.getPosition()), float(new_position), JENERGY_MOVE_LIMIT):
            sm1fpitchfeedback.moveTo("Disabled")
            motor.moveTo(new_position)
            sm1fpitchfeedback.moveTo("Enabled")
        else:
            motor.moveTo(new_position)
    else:
        motor.moveTo(new_position)
    print "%s moves completed at %f" % (motor.getName(), motor.getPosition())
    
try:
    from gda.jython.commands.GeneralCommands import alias
    alias("move")
except:
    pass


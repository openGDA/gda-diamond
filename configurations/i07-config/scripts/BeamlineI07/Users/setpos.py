from gda.device.scannable import ScannableMotor
from gda.jython.commands.GeneralCommands import alias

def setpos(motor, newpos):
	if (motor.getClass() != ScannableMotor):
		raise typeError('Not a scannable')
	if (type(newpos) != int and type(newpos) != float):
		raise typeError('Position must be given a value')

	motor.setPosition(newpos)

alias("setpos")

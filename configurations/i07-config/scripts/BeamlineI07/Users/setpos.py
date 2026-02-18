from gda.device.scannable import ScannableMotor
from gda.jython.commands.GeneralCommands import alias
from gda.device.scannable.scannablegroup import CoordinatedChildScannableMotionUnits
from BeamlineI07.useMotors import thv

def setpos(motor, newpos):
	if (type(newpos) != int and type(newpos) != float):
		raise TypeError('Position must be given a value')
	if(isinstance(motor, thv.__class__)) :
		motor.setOffset(motor.real_motor.getPosition() - (newpos/motor.getScaleFactor()))
		print "Offset changed"
	elif (isinstance(motor, ScannableMotor)):
		motor.setPosition(float(newpos))
		print "Offset changed"
	elif (isinstance(motor, CoordinatedChildScannableMotionUnits)):
		print "Warning: changing this offset may make continuous scan readbacks incorrect"
		offsetscannable = False
		if(motor.getName() == 'diff1chi'):
			offsetscannable = diff1chioffset
		elif(motor.getName() == 'diff1delta'):
			offsetscannable = diff1vdeltaoffset
		elif(motor.getName() == 'diff1gamma'):
			offsetscannable = diff1vgammaoffset
		elif(motor.getName() == 'diff1theta'):
			offsetscannable = diff1homegaoffset
		elif(motor.getName() == 'diff1omega'):
			offsetscannable = diff1vomegaoffset
		else:
			raise TypeError('Not a scannable')
		if offsetscannable:
			oldpos = motor.getPosition()
			inc(offsetscannable, float(newpos)-oldpos)
	else:
		raise TypeError('Not a scannable')

alias("setpos")

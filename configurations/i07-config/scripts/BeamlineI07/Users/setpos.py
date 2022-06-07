from gda.device.scannable import ScannableMotor
from gda.jython.commands.GeneralCommands import alias
from gda.device.scannable.scannablegroup import CoordinatedChildScannableMotionUnits

def setpos(motor, newpos):
	if (type(newpos) != int and type(newpos) != float):
		raise TypeError('Position must be given a value')
	if (motor.getClass() == ScannableMotor):
		motor.setPosition(float(newpos))
		print "Offset changed"
	elif (motor.getClass() == CoordinatedChildScannableMotionUnits):
		offsetscannable = False
		if(motor.getName() == 'diff1chi'):
			offsetscannable = diff1halphaoffset
		elif(motor.getName() == 'diff1delta'):
			offsetscannable = diff1vdeltaoffset
		elif(motor.getName() == 'diff1gamma'):
			offsetscannable = diff1vgammaoffset
		elif(motor.getName() == 'diff1theta'):
			offsetscannable = diff1homegaoffset
		elif(motor.getName() == 'diff1alpha'):
			offsetscannable = diff1valphaoffset
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

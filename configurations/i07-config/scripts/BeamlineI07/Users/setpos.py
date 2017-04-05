def setpos(motor, newpos):
	if (motor.getClass() != gda.device.scannable.ScannableMotor):
		raise typeError('Not a scannable')
	if (type(newpos) != int and type(newpos) != float):
		raise typeError('Position must be given a value')

	# getPosition seems to get the position, but setPosition sets the offset!
	# so the only way to increment the offset is to set it to zero first,
	# otherwise we don't know the original value of the offset
	motor.getMotor().setPosition(0)	
	oldpos = motor.getMotor().getPosition()
	deltaoffset = newpos - oldpos
	motor.getMotor().setPosition(deltaoffset)

alias("setpos")

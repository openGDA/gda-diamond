from gda.jython.commands import InputCommands
from localStationScripts.shutterCommands import sh, openEHShutter, closeEHShutter
#import marAuxiliary
from gdascripts.messages.handle_messages import simpleLog
import java
from localStationConfiguration import d3x_in, d3y_in, d3x_out, d3y_out, d4x_in, d4y_in, d4x_out, d4y_out
from localStationScripts.scan_commands import scan
from gda.jython.commands.ScannableCommands import cscan

global configured, isccd, beamline, dkappa, dktheta, cryobsx
configured = False

CON_IN=1
CON_OUT=0

def configure(jythonNameMap, beamlineParameters):
	global configured, isccd, beamline, dkappa, dktheta, cryobsx, d3x, d3y, d4x, d4y
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	beamline = jythonNameMap.beamline
	dkappa = jythonNameMap.dkappa
	dktheta = jythonNameMap.dktheta
	cryobsx = jythonNameMap.cryobsx
	d3x = jythonNameMap.d3x
	d3y = jythonNameMap.d3y
	d4x = jythonNameMap.d4x
	d4y = jythonNameMap.d4y
	configured = True
	
def checkConfigured():
	if not configured:
		raise Exception, "operationalControl not configured"	

def shopen():
	"""
	sh('o')  - Reset and Open EH & Fast shutter.
	"""
	sh('o')

def oehs():
	"""
	short for openEHShutter which:
		1. Opens the experimental hutch shutter.
		2. Waits for it to open.
		3. Checks the shutter status.
	syntax: openEHShutter()
	"""
	openEHShutter()

def shclose():
	"""
	sh('c')  - Close EH & Fast Shutter
	"""
	sh('c')

def cehs():
	"""
	Short for closeEHShutter
		closeExperimentalHutchShutter
		1. Closes the experimental hutch shutter.
		2. Waits for it to close.
		3. Checks the shutter status.
	"""
	closeEHShutter()

def shopenall():
	"""
	sh('oa') - Reset and Open FE, OH, EH & Fast Shutters
	"""
	sh('oa')

def shcloseall():
	"""
	sh('ca') - Close FE, OH, EH & Fast Shutters"
	"""
	sh('ca')

def cfs():
	"""
	Close Fast shutter
	
	Note: The Fast Shutter should be switched to Ext. trigger rather than Atlas
	
	See: http://wiki.diamond.ac.uk/Wiki/Wiki.jsp?page=Atlas%20detector%20does%20not%20acquire%20images
	"""
	checkConfigured()
	sh('r')

def ofs():
	"""
	Open Fast shutter
	
	Note: The Fast Shutter should be switched to Ext. trigger rather than Atlas
	
	See: http://wiki.diamond.ac.uk/Wiki/Wiki.jsp?page=Atlas%20detector%20does%20not%20acquire%20images
	"""
	checkConfigured()
	sh('f')

def d1in():
	"""
	move diode 1 in
	"""
	setState("D1", "-DI-PHDGN-01:CON", CON_IN)

def d2in():
	"""
	move diode 2 in
	"""
	setState("D2", "-DI-PHDGN-02:CON", CON_IN)

def moveMotorsTogether(motor1, position1, motor2, position2):
	motor1.asynchronousMoveTo(position1)
	motor2.asynchronousMoveTo(position2)
	motor1.waitWhileBusy()
	motor2.waitWhileBusy()

def d3in():
	"""
	move diode 3 in
	"""
	moveMotorsTogether(d3x, d3x_in, d3y, d3y_in)

def d4in():
	"""
	move diode 4 in
	"""
	d4x.moveTo(d4x_in)
	d4y.moveTo(d4y_in)

def d1out():
	"""
	move diode 1 out
	"""
	setState("D1", "-DI-PHDGN-01:CON", CON_OUT)

def d2out():
	"""
	move diode 2 out
	"""
	setState("D2", "-DI-PHDGN-02:CON", CON_OUT)

def d3out():
	"""
	move diode 3 out and reset the brightness of the questar to zero
	"""
	#TODO: read these from the motor limits?
	#      moveMotorsTogether(d3x, math.floor(d3x.upperMotorLimit), d3y, math.floor(d3y.upperMotorLimit)) ?
	moveMotorsTogether(d3x, d3x_out, d3y, d3y_out)

def d4out():
	"""
	move diode 4 out
	"""
	d4x.moveTo(d4x_out)
	d4y.moveTo(d4y_out)

def d4cryoIn():
	print "Moving d4cryo in."
	setState("D4cryo", "-RS-ABSB-04:CON", CON_IN)

def d4cryoOut():
	print "Moving d4cryo out."
	setState("D4cryo", "-RS-ABSB-04:CON", CON_OUT)

def setState(name, pv, newState):
	text = "IN"
	if (newState == 0):
		text = "OUT"
	
	currentState = beamline.getValue(None,"Top",pv)
	if (newState == currentState):
		print name + " position already: "  + text
	else:
		beamline.setValue("Top",pv, newState)
		print name + " position changed to: "  + text

def align():           # open EH and fast shutter
	"""
	close mar, move d2 and d3 in and reset and open EH & Fast shutter.
	"""
	#marAuxiliary.closeMarShield()
	d2in()
	d3in()
	sh('o')

def ready():
	"""
	close EH & Fast shutter, move d2 and d3 out and open the mar
	"""
	sh('c')
	d1out()
	d2out()
	d3out()
	#marAuxiliary.openMarShield()		# N.b. if mar disconnected, will just do nothing

def cscanChecks(motor, start, step, param1, param2=-1, param3=-1):
	"""
	Do align(), then a cscan 
	e.g. 
		cscanChecks( testLinearDOF1, 0.1, 0.02 ,dummyDiode)
		cscanChecks( testLinearDOF1, 0.1, 0.02, w, 0.2 ,dummyDiode)
	"""
	genericScanChecks(True, True, motor, start, -1, step, param1, param2, param3)

def scanChecks(motor, start, stop, step, param1, param2=-1, param3=-1):
	"""
	Do align(), then a scan
	e.g. 
		scanChecks( testLinearDOF1, 1, 10, 0.3 ,dummyDiode)
		scanChecks( testLinearDOF1, 1, 10, 0.3 ,w, 0.2, dummyDiode)
	"""
	genericScanChecks(True, False, motor, start, stop, step, param1, param2, param3)

def genericScanChecks(alignFlag, cscanFlag, motor, start, stop, step, param1, param2, param3):
	"""
	Do align(), then a scan, returning motor to initial position if there's 
	an interrupt
	"""	
	if (alignFlag):
		align()
	
	initialPosition = motor.getPosition()
	
	args = []	
	try:
		if (cscanFlag):
			if (param2 == -1 and param3 == -1):
				args = [motor, start, step, param1]
			else:
				args = [motor, start, step, param1, param2, param3]
			cscan(args)
		else:
			if (param2 == -1 and param3 == -1):
				args = [motor, start, stop, step, param1]
			else:
				args = [motor, start, stop, step, param1, param2, param3]
			scan(args)
	
	except java.lang.InterruptedException:
		response = InputCommands.requestInput("Return " + str(motor.name) + " to initial position: " + str(initialPosition) + " ? (y/n)")
		if (response == 'y'):
			moveMotor(motor, initialPosition)
		else:
			simpleLog("motor not moved")
			return

def homeToMinus():
	""" 
	if dkappa and dktheta are at the home positions of 0 then move them to -134.76 and  -34.197 respectively
	"""
	if (not checkMotorsInPosition(0, 0)):
		return

	moveMotor(dkappa, -134.76)
	moveMotor(dktheta, -34.197)
	simpleLog("Done")

def minusToHome():
	""" 
	if dkappa and dktheta are at -134.76 and -34.197 respectively then move them to the home position of 0
	"""
	if (not checkMotorsInPosition(-134.76, -34.197)):
		return

	moveMotor(dktheta, 0)
	moveMotor(dkappa, 0)
	simpleLog("Done")

def homeToMinus57():
	""" 
	if dkappa and dktheta are at the home positions of 0 then move them to 134.65 and  31.785 respectively
	"""
	if (not checkMotorsInPosition(0, 0)):
		return

	moveMotor(dkappa, 134.65)
	moveMotor(dktheta, 31.785)
	simpleLog("Done")

def minus57ToMinus122():
	""" 
	if dkappa and dktheta are at -134.76 and -34.197 respectively then move them to 134.65 and  31.785 respectively
	"""
	if (not checkMotorsInPosition(134.65, 31.785)):
		return
	
	ret = InputCommands.requestInput("Ensure mu stage, etc. is clear..!!! Continue (y/n) ?")
	if (ret != 'y'):
		simpleLog("Motors not moved")
		return
	
	ret = InputCommands.requestInput("ARE YOU REALLY SURE? (y/n) ?")
	if (ret != 'y'):
		simpleLog("Motors not moved")
		return
	
	moveMotor(dkappa, 0)
	moveMotor(dktheta, 0)
	moveMotor(dkappa, -134.76)
	moveMotor(dktheta, -34.197)
	simpleLog("Done")

def checkMotorsInPosition(pos1, pos2):
	tolerance = 0.1           # = motor.tolerance
	if (abs(dkappa.getPosition() - pos1) > tolerance):
		simpleLog("Cannot home as dkappa not at " + str(pos1) +" (at " + str(dkappa.getPosition()) + ")")
		return False
	if (abs(dktheta.getPosition() - pos2) > tolerance):
		simpleLog("Cannot home as dktheta not at " + str(pos2) +" (at " + str(dktheta.getPosition()) + ")")
		return False
	
	return True

def moveMotor(motor, newPos):
	"""
	Moves motor to new position and checks that it has indeed moved to that position
	(within a certain tolerance)
	"""
	simpleLog( "Moving " + motor.name + " to " + str(newPos))
	motor(newPos)
	
	tolerance = 0.1           # = motor.tolerance?
	if (abs(motor.getPosition() - newPos) > tolerance):
		raise Exception, "Error: motor has not moved to target position (currently at: " +  str(motor.getPosition()) + ") - SCRIPT TERMINATED"
	
	simpleLog( "Now at: " + str(motor.getPosition()) )


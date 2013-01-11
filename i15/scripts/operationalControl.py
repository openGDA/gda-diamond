import glob
from gda.jython.commands import InputCommands
from util_scripts import updateFileOverwriteFlag
from util_scripts import doesFileExist
import shutterCommands
import marAuxiliary
from gdascripts.messages.handle_messages import simpleLog
import java
from scan_commands import *
from gda.jython.commands.ScannableCommands import cscan

global configured, isccd, beamline, dkappa, dktheta
configured = False

def configure(jythonNameMap, beamlineParameters):
	global configured, isccd, beamline, dkappa, dktheta
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	isccd = jythonNameMap.atlas
	beamline = jythonNameMap.beamline
	dkappa = jythonNameMap.dkappa
	dktheta = jythonNameMap.dktheta
	configured = True
	
def checkConfigured():
	if not configured:
		raise "operationalControl not configured"	

def shopen():
	"""
	sh('o')  - Reset and Open EH & Atlas shutter.
	"""
	shutterCommands.sh('o')

def oehs():
	"""
	short for openEHShutter which:
		1. Opens the experimental hutch shutter.
		2. Waits for it to open.
		3. Checks the shutter status.
	syntax: openEHShutter()
	"""
	shutterCommands.openEHShutter()

def shclose():
	"""
	sh('c')  - Close EH & Atlas Shutter
	"""
	shutterCommands.sh('c')


def cehs():
	"""
	Short for closeEHShutter
		closeExperimentalHutchShutter
		1. Closes the experimental hutch shutter.
		2. Waits for it to close.
		3. Checks the shutter status.
	"""
	shutterCommands.closeEHShutter()

def shopenall():
	"""
	sh('oa') - Reset and Open FE, OH, EH & Atlas Shutters
	"""
	shutterCommands.sh('oa')

def shcloseall():
	"""
	sh('ca') - Close FE, OH, EH & Atlas Shutters"
	"""
	shutterCommands.sh('ca')

def cfs():
	"""
	Close Atlas fast shutter
	
	Note: If the Atlas is switched to Ext. trigger rather than Atlas, then
		the Atlas shutter will follow the Epics synoptic FS control and
		Newport XPS position compare.
	
	See: http://wiki.diamond.ac.uk/Wiki/Wiki.jsp?page=Atlas%20detector%20does%20not%20acquire%20images
	"""
	checkConfigured()
	isccd.closeS()

def ofs():
	"""
	Open Atlas fast shutter
	
	Note: If the Atlas is switched to Ext. trigger rather than Atlas, then
		the Atlas shutter will follow the Epics synoptic FS control and
		Newport XPS position compare.
	
	See: http://wiki.diamond.ac.uk/Wiki/Wiki.jsp?page=Atlas%20detector%20does%20not%20acquire%20images
	"""
	checkConfigured()
	isccd.openS()

def d1in():
	"""
	move diode 1 in
	"""
	setState("D1", "-DI-PHDGN-01:CON", 1)

def d2in():
	"""
	move diode 2 in
	"""
	setState("D2", "-DI-PHDGN-02:CON", 1)

def d3in():
	"""
	move diode 3 in
	"""
	setState("D3", "-DI-PHDGN-04:CON", 1)

def d1out():
	"""
	move diode 1 out
	"""
	setState("D1", "-DI-PHDGN-01:CON", 0)
		
def d2out():
	"""
	move diode 2 out
	"""
	setState("D2", "-DI-PHDGN-02:CON", 0)
		
def d3out():
	"""
	move diode 3 out and reset the brightness of the questar to zero
	"""
	setState("D3", "-DI-PHDGN-04:CON", 0)
		
def d4out():
	"""
	move diode 4 out
	"""
	setState("D4", "-DI-PHDGN-04:CON", 0)
		
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
	close mar, move d2 and d3 in and reset and open EH & Atlas shutter.
	"""
	marAuxiliary.closeMarShield()		# N.b. if mar disconnected, will just do nothing 
	d2in()
	d3in()
	shutterCommands.sh('o')
	
def ready():
	"""
	close EH & Atlas shutter, move d2 and d3 out and open the mar
	"""
	shutterCommands.sh('c')
	d1out()
	d2out()
	d3out()
	marAuxiliary.openMarShield()		# N.b. if mar disconnected, will just do nothing
	

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
	
	except java.lang.InterruptedException, e:
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
		raise "Error: motor has not moved to target position (currently at: " +  str(motor.getPosition()) + ") - SCRIPT TERMINATED"
	
	simpleLog( "Now at: " + str(motor.getPosition()) )


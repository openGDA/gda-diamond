from gdascripts.parameters import beamline_parameters
from gda.scan import ConcurrentScan, ConstantVelocityScanLine
from gdascripts.pd.dummy_pds import DummyPD
from localStationScripts.detector_scan_commands import DiodeController, _configureDetector, _configureConstantVelocityMove
from org.slf4j import LoggerFactory

# Help definitions

_exposeHelp = """
	exposeTime is the time of each exposure in seconds, fileName is the suffix added to file names in order to help identify them.
	"""

_exposeNHelp = """
	exposeNumber is the number of exposures to take at each point.
	"""

_lineHelp = """
	lineMotor is the motor to scan (dx or dy or dz). stepNumber is the number of steps, so the number of points is this plus one.
	"""
	
_rockHelp = """
	rockMotor is assumed (default) to be dkphi, rockCentre is assumed (default) to be 58.0.
	"""

_rockNHelp = """
	rockNumber is the number of rocks per exposure. Note that if this is > 1 then the image acquisition will not be synchronised with motion.
	"""


_gridHelp = """
	horizontal is dx (inner loop) and vertical is dz (outer loop). horizStepNumber, vertStepNumber are the number of steps, so the number of positions are these numbers plus one.
	"""


# Static exposure

'''
def expose(exposeTime, fileName):
	"""
	Static exposure
	"""
	return exposeN(exposeTime, 1, fileName)

expose.__doc__ += _exposeHelp
'''

def exposeN(exposeTime, exposeNumber, fileName):
	"""
	Multiple static exposures
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName)
	if len(verification)>0:
		return verification
	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName)

exposeN.__doc__ += _exposeHelp + _exposeNHelp


# Line scans

def exposeLineAbs(exposeTime, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName):
	"""
	Line scan using absolute motor positions and stepNumber (which then defines a stepSize)
	"""
	return exposeNLineAbs(exposeTime, 1, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName)

exposeLineAbs.__doc__ += _exposeHelp + _lineHelp


def exposeLineStep(exposeTime, lineMotor, stepSize, stepNumber, fileName):
	"""
	Line scan using stepSize and stepNumber relative to the current motor position
	"""
	return exposeNLineStep(exposeTime, 1, lineMotor, stepSize, stepNumber, fileName)

exposeLineStep.__doc__ += _exposeHelp + _lineHelp


def exposeNLineAbs(exposeTime, exposeNumber, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName):
	"""
	Line scan with multiple exposures at each position using absolute motor positions and stepNumber
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, lineMotor=lineMotor, AbsoluteStartPos=AbsoluteStartPos, AbsoluteEndPos=AbsoluteEndPos, stepNumber=stepNumber, fileName=fileName)
	if len(verification)>0:
		return verification
	
	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, horizMotor=lineMotor, AbsoluteHorizStart=AbsoluteStartPos, AbsoluteHorizEnd=AbsoluteEndPos, horizStepNumber=stepNumber)

exposeNLineAbs.__doc__ += _exposeHelp + _exposeNHelp + _lineHelp


def exposeNLineStep(exposeTime, exposeNumber, lineMotor, stepSize, stepNumber, fileName):
	"""
	Line scan with multiple exposures at each position using stepSize and stepNumber relative to the current motor position
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber,
		lineMotor=lineMotor, stepSize=stepSize, stepNumber=stepNumber, fileName=fileName)
	if len(verification)>0:
		return verification
	
	AbsoluteStartPos, AbsoluteEndPos=_calcAbsPositions(motor=lineMotor, stepSize=stepSize, numSteps=stepNumber)
	
	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, horizMotor=lineMotor, AbsoluteHorizStart=AbsoluteStartPos, AbsoluteHorizEnd=AbsoluteEndPos, horizStep=stepSize, horizStepNumber=stepNumber)

exposeNLineStep.__doc__ += _exposeHelp + _exposeNHelp + _lineHelp


# Grid scans

def exposeGridAbs(exposeTime, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName):
	"""
	Grid scan (in effect 2 dimensional line scans), absolute
	"""
	return exposeNGridAbs(exposeTime, 1, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName)

exposeGridAbs.__doc__ += _exposeHelp + _gridHelp


def exposeGridStep(exposeTime, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName):
	"""
	Grid scan (in effect 2 dimensional line scans), relative
	"""
	return exposeNGridStep(exposeTime, 1, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName)

exposeGridStep.__doc__ += _exposeHelp + _gridHelp


def exposeNGridAbs(exposeTime, exposeNumber, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName):
	"""
	Grid scan (in effect 2 dimensional line scans), absolute, with multiple exposures at each position
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStepNumber=horizStepNumber, AbsoluteVertStart=AbsoluteVertStart, AbsoluteVertEnd=AbsoluteVertEnd, vertStepNumber=vertStepNumber, fileName=fileName)
	if len(verification)>0:
		return verification
	
	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, horizMotor=_horizMotor(), AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStepNumber=horizStepNumber, vertMotor=_vertMotor(),   AbsoluteVertStart=AbsoluteVertStart,   AbsoluteVertEnd=AbsoluteVertEnd,   vertStepNumber=vertStepNumber)

exposeNGridAbs.__doc__ += _exposeHelp + _exposeNHelp + _gridHelp


def exposeNGridStep(exposeTime, exposeNumber, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName):
	"""
	Grid scan (in effect 2 dimensional line scans), relative, with multiple exposures at each position
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, horizStep=horizStep, horizStepNumber=horizStepNumber, vertStep=vertStep, vertStepNumber=vertStepNumber, fileName=fileName)
	if len(verification)>0:
		return verification
	
	AbsoluteHorizStart, AbsoluteHorizEnd = _calcAbsPositions(motor=_horizMotor(), stepSize=horizStep, numSteps=horizStepNumber)
	AbsoluteVertStart,  AbsoluteVertEnd  = _calcAbsPositions(motor=_vertMotor(),  stepSize=vertStep,  numSteps=vertStepNumber)
	
	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, horizMotor=_horizMotor(), AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStep=horizStep, horizStepNumber=horizStepNumber, vertMotor=_vertMotor(),   AbsoluteVertStart=AbsoluteVertStart,   AbsoluteVertEnd=AbsoluteVertEnd,   vertStep=vertStep,   vertStepNumber=vertStepNumber)

exposeNGridStep.__doc__ += _exposeHelp + _exposeNHelp + _gridHelp


# Rocking during exposure:

def exposeRock(exposeTime, rockAngle, fileName):
	"""
	Single exposure while rocking
	"""
	return exposeRockN(exposeTime, rockAngle, 1, fileName)

exposeRock.__doc__ += _exposeHelp + _rockHelp


def exposeRockN(exposeTime, rockAngle, rockNumber, fileName):
	"""
	Multiple rocks while exposing
	"""
	return exposeNRockN(exposeTime, 1, rockAngle, rockNumber, fileName)

exposeRockN.__doc__ += _exposeHelp + _rockHelp + _rockNHelp


def exposeNRockN(exposeTime, exposeNumber, rockAngle, rockNumber, fileName):
	"""
	Multiple exposures while rocking several times per exposure
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, rockAngle=rockAngle, rockNumber=rockNumber, fileName=fileName)
	if len(verification)>0:
		return verification
	
	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, rockMotor=_rockMotor(), rockAngle=rockAngle, rockNumber=rockNumber)

exposeNRockN.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _rockNHelp


# Combining exposure, line or grid scans, and rocking

def exposeRockLineAbs(exposeTime, rockAngle, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName):
	"""
	Rocking at every position during line scan, absolute
	"""
	return exposeNRockLineAbs(exposeTime, 1, rockAngle, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName)

exposeRockLineAbs.__doc__ += _exposeHelp + _rockHelp + _lineHelp


def exposeRockLineStep(exposeTime, rockAngle, lineMotor, stepSize, stepNumber, fileName):
	"""
	Rocking at every position during line scan, relative
	"""
	return exposeNRockLineStep(exposeTime, 1, rockAngle, lineMotor, stepSize, stepNumber, fileName)

exposeRockLineStep.__doc__ += _exposeHelp + _rockHelp + _lineHelp


def exposeRockGridAbs(exposeTime, rockAngle, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName):
	"""
	Rocking at every position during grid scan, absolute
	"""
	return exposeNRockGridAbs(exposeTime, 1, rockAngle, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName)

exposeRockGridAbs.__doc__ += _exposeHelp + _rockHelp + _gridHelp


def exposeRockGridStep(exposeTime, rockAngle, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName):
	"""
	Rocking at every position during grid scan, relative
	"""
	return exposeNRockGridStep(exposeTime, 1, rockAngle, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName)

exposeRockGridStep.__doc__ += _exposeHelp + _rockHelp + _gridHelp


def exposeNRockLineAbs(exposeTime, exposeNumber, rockAngle, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName):
	"""
	Multiple exposures at each position while rocking at every position during line scan, absolute
	"""
	return exposeNRockNLineAbs(exposeTime, exposeNumber, rockAngle, 1, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName)

exposeNRockLineAbs.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _lineHelp


def exposeNRockLineStep(exposeTime, exposeNumber, rockAngle, lineMotor, stepSize, stepNumber, fileName):
	"""
	Multiple exposures at each position while rocking at every position during line scan, relative
	"""
	return exposeNRockNLineStep(exposeTime, exposeNumber, rockAngle, 1, lineMotor, stepSize, stepNumber, fileName)

exposeNRockLineStep.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _lineHelp


def exposeNRockGridAbs(exposeTime, exposeNumber, rockAngle, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName):
	"""
	Multiple exposures at each position while rocking at every position during grid scan, absolute
	"""
	return exposeNRockNGridAbs(exposeTime, exposeNumber, rockAngle, 1, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName)

exposeNRockGridAbs.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _gridHelp


def exposeNRockGridStep(exposeTime, exposeNumber, rockAngle, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName):
	"""
	Multiple exposures at each position while rocking at every position during grid scan, relative
	"""
	return exposeNRockNGridStep(exposeTime, exposeNumber, rockAngle, 1, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName)

exposeNRockGridStep.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _gridHelp


def exposeNRockNLineAbs(exposeTime, exposeNumber, rockAngle, rockNumber, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName):
	"""
	Multiple exposures while rocking several times per exposure at each position during line scan, absolute
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, rockAngle=rockAngle, rockNumber=rockNumber, lineMotor=lineMotor, AbsoluteStartPos=AbsoluteStartPos, AbsoluteEndPos=AbsoluteEndPos, stepNumber=stepNumber, fileName=fileName)
	if len(verification)>0:
		return verification
	
	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, rockMotor=_rockMotor(), rockAngle=rockAngle, rockNumber=rockNumber, horizMotor=lineMotor, AbsoluteHorizStart=AbsoluteStartPos, AbsoluteHorizEnd=AbsoluteEndPos, horizStepNumber=stepNumber)

exposeNRockNLineAbs.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _rockNHelp + _lineHelp


def exposeNRockNLineStep(exposeTime, exposeNumber, rockAngle, rockNumber, lineMotor, stepSize, stepNumber, fileName):
	"""
	Multiple exposures while rocking several times per exposure at each position during line scan, relative
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, rockAngle=rockAngle, rockNumber=rockNumber, lineMotor=lineMotor, stepSize=stepSize, stepNumber=stepNumber, fileName=fileName)
	if len(verification)>0:
		return verification
	
	AbsoluteStartPos, AbsoluteEndPos=_calcAbsPositions(motor=lineMotor, stepSize=stepSize, numSteps=stepNumber)
	
	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName,
			rockMotor=_rockMotor(), rockAngle=rockAngle, rockNumber=rockNumber,
			horizMotor=lineMotor, AbsoluteHorizStart=AbsoluteStartPos, AbsoluteHorizEnd=AbsoluteEndPos, horizStep=stepSize, horizStepNumber=stepNumber)

exposeNRockNLineStep.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _rockNHelp + _lineHelp


def exposeNRockNGridAbs(exposeTime, exposeNumber, rockAngle, rockNumber, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName):
	"""
	Multiple exposures while rocking several times per exposure at each position during grid scan
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, rockAngle=rockAngle, rockNumber=rockNumber, AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStepNumber=horizStepNumber, AbsoluteVertStart=AbsoluteVertStart, AbsoluteVertEnd=AbsoluteVertEnd, vertStepNumber=vertStepNumber, fileName=fileName)
	if len(verification)>0:
		return verification
	
	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, rockMotor=_rockMotor(), rockAngle=rockAngle, rockNumber=rockNumber, horizMotor=_horizMotor(), AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStepNumber=horizStepNumber, vertMotor=_vertMotor(),   AbsoluteVertStart=AbsoluteVertStart,   AbsoluteVertEnd=AbsoluteVertEnd,   vertStepNumber=vertStepNumber,)

exposeNRockNGridAbs.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _rockNHelp + _gridHelp


def exposeNRockNGridStep(exposeTime, exposeNumber, rockAngle, rockNumber, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName):
	""" Multiple exposures while rocking several times per exposure at each position during grid scan
	horizontal is dx and vertical is dz
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, rockAngle=rockAngle, rockNumber=rockNumber, horizStep=horizStep, horizStepNumber=horizStepNumber, vertStep=vertStep, vertStepNumber=vertStepNumber, fileName=fileName)
	if len(verification)>0:
		return verification
	
	AbsoluteHorizStart, AbsoluteHorizEnd = _calcAbsPositions(motor=_horizMotor(), stepSize=horizStep, numSteps=horizStepNumber)
	AbsoluteVertStart,  AbsoluteVertEnd  = _calcAbsPositions(motor=_vertMotor(), stepSize=vertStep,  numSteps=vertStepNumber)
	
	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, rockMotor=_rockMotor(), rockAngle=rockAngle, rockNumber=rockNumber, horizMotor=_horizMotor(), AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStep=horizStep, horizStepNumber=horizStepNumber, vertMotor=_vertMotor(),   AbsoluteVertStart=AbsoluteVertStart,   AbsoluteVertEnd=AbsoluteVertEnd,   vertStep=vertStep,   vertStepNumber=vertStepNumber)

exposeNRockNGridStep.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _rockNHelp + _gridHelp


# User input verification functions

def isfloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

def isint(value):
	try:
		int(value)
		return True
	except ValueError:
		return False

def verifyParameters(exposeTime=None, exposeNumber=None, fileName=None,
					 rockAngle=None, rockNumber=None, lineMotor=None, 
					 horizStep=None, horizStepNumber=None, vertStep=None, vertStepNumber=None, stepSize=None, stepNumber=None,
					 AbsoluteHorizStart=None, AbsoluteHorizEnd=None, AbsoluteVertStart=None, AbsoluteVertEnd=None,
					 AbsoluteStartPos=None, AbsoluteEndPos=None
					):
	failures=[]
	# if check required		and 	(incorrect type			or incorrect value)			then report failure			Note: "not (a and b)" = "not a or not b" but shorter
	if exposeTime			and not (isfloat(exposeTime) 	and exposeTime > 0):		failures.append("exposeTime should be a positive number: %r" % exposeTime)
	if exposeNumber			and not (isint(exposeNumber) 	and exposeNumber > 0):		failures.append("exposeNumber should be a positive integer: %r" % exposeNumber)
	if fileName				and not (type(fileName) is str):							failures.append("fileName should be a string: %r" % fileName)

	if rockAngle			and not (isfloat(rockAngle)):								failures.append("rockAngle should be a number: %r" % rockAngle)
	if rockNumber			and not (isint(rockNumber) 		and rockNumber > 0):		failures.append("rockNumber should be a positive integer: %r" % rockNumber)

	if lineMotor			and not (hasattr(lineMotor, 'name') and 
									lineMotor.name in ('dx', 'dy', 'dz')):				failures.append("lineMotor invalid, use dx, dy or dz: %r" % lineMotor)

	if horizStep			and not (isfloat(horizStep)):								failures.append("horizStep should be a number: %r" % horizStep)
	if horizStepNumber		and not (isint(horizStepNumber)	and horizStepNumber > 0):	failures.append("horizStepNumber should be a positive integer: %r" % horizStepNumber)
	if vertStep				and not (isfloat(vertStep)):								failures.append("vertStep should be a number: %r" % vertStep)
	if vertStepNumber		and not (isint(vertStepNumber)	and vertStepNumber > 0):	failures.append("vertStepNumber should be a positive integer: %r" % vertStepNumber)
	if stepSize				and not (isfloat(stepSize)):								failures.append("stepSize should be a number: %r" % stepSize)
	if stepNumber			and not (isint(stepNumber)		and stepNumber > 0):		failures.append("stepNumber should be a positive integer: %r" % stepNumber)

	if AbsoluteHorizStart	and not (isfloat(AbsoluteHorizStart)):						failures.append("AbsoluteHorizStart should be a number: %r" % AbsoluteHorizStart)
	if AbsoluteHorizEnd		and not (isfloat(AbsoluteHorizEnd)):						failures.append("AbsoluteHorizEnd should be a number: %r" % AbsoluteHorizEnd)
	if AbsoluteVertStart	and not (isfloat(AbsoluteVertStart)):						failures.append("AbsoluteVertStart should be a number: %r" % AbsoluteVertStart)
	if AbsoluteVertEnd		and not (isfloat(AbsoluteVertEnd)):							failures.append("AbsoluteVertEnd should be a number: %r" % AbsoluteVertEnd)
	if AbsoluteStartPos		and not (isfloat(AbsoluteStartPos)):						failures.append("AbsoluteStartPos should be a number: %r" % AbsoluteStartPos)
	if AbsoluteEndPos		and not (isfloat(AbsoluteEndPos)):							failures.append("AbsoluteEndPos should be a number: %r" % AbsoluteEndPos)

	if failures:
		LoggerFactory.getLogger("verifyParameters").info("Scan verification failed:\n  %s" % "\n  ".join(failures))

	return failures

# Utility functions

def _calcStepSize(start, stop, numPoints):
	stepSize =  0 if numPoints <= 1 else (float(start)-float(stop))/float(numPoints)
	LoggerFactory.getLogger("_calcStepSize").info("start=%r, step=%r, numPoints=%r, stepSize=%r" % (start, stop, numPoints, stepSize))
	return stepSize

def _calcAbsPositions(motor, stepSize, numSteps):
	if type(motor) is str:
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		motor = jythonNameMap[motor]

	currentPosition =  motor.getPosition()
	AbsoluteStartPos = currentPosition
	AbsoluteEndPos =   currentPosition + stepSize * numSteps
	return AbsoluteStartPos, AbsoluteEndPos

def _horizMotor():
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	return jythonNameMap.dx

def _vertMotor():
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	return jythonNameMap.dz

def _rockMotor():
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	return jythonNameMap.dkphi

def _rockCentre():
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	logger = LoggerFactory.getLogger("_rockCentre")
	rockCentre = jythonNameMap.rockCentre
	if rockCentre == None:
		rockCentre = 58.
		msg = "rockCentre not defined, assuming %r. Add 'rockCentre=xx' to localStationUser.py for another centre position." % rockCentre
		logger.info(msg)
		print msg
	return rockCentre

def _exposeDetector():
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	logger = LoggerFactory.getLogger("_exposeDetector")
	detector = jythonNameMap.exposeDetector
	if detector == None:
		msg = "exposeDetector not defined, please add 'exposeDetector=xx' to localStationUser.py, where 'xx' is 'pe' or 'mar'"
		logger.error(msg)
		print msg
		raise Exception(msg)

	if type(detector) is str:
		detector = jythonNameMap[detector]
	
	return detector

def _staticExposeScanParams(detector, exposeTime, totalExposures, fileName, dark):
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	zebraFastShutter = jythonNameMap.zebraFastShutter
	
	_configureDetector(detector, exposeTime, totalExposures, fileName, dark=False)
	return [detector, exposeTime, zebraFastShutter, exposeTime]

def _rockScanParams(detector, exposeTime, exposeNumber, fileName, rockMotor, rockCentre, rockAngle, rockNumber):
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	logger = LoggerFactory.getLogger("_rockScanParams")
	
	if type(rockMotor) is str:
		rockMotor = jythonNameMap[rockMotor]
	
	if not rockMotor.name == 'dkphi':
		raise Exception('Only dkphi currently supported, not %r' % (rockMotor.name))
	
	if rockNumber <> 1:
		rockscanMotor = jythonNameMap['dkphi_rockscan']
		msg = "rockNumber > 1 so performing unsynchronised rockscan using %s. Moving to start position %r" % (rockscanMotor.name, rockCentre-rockAngle)
		logger.error(msg)
		print "-"*80
		print msg
		print "-"*80
		
		rockMotor.moveTo(rockCentre-rockAngle) # Go to start position
		rockscanMotor.setupScan(centre=rockCentre, rockSize=rockAngle, noOfRocksPerExposure=rockNumber)
		scan_params=_staticExposeScanParams(detector, exposeTime, exposeNumber, fileName, dark=False)
		scan_params.extend([rockscanMotor, exposeTime])
		return scan_params
	
	# TODO: There should also be feedback (error message of sorts) if the combination of exposure time and rock angle either requires the motor (dkphi) to move slower than it can or faster than it can.
	"""
	msg = "Note: There is currently no check that the combination of exposure time and rock angle either requires the motor (dkphi) to move slower than it can or faster than it can."
	logger.error(msg)
	print "-"*80
	print msg
	print "-"*80
	"""
	
	hardwareTriggeredNXDetector = _configureDetector(detector=detector, exposureTime=exposeTime, noOfExposures=exposeNumber,
													 sampleSuffix=fileName, dark=False)
	continuouslyScannableViaController, continuousMoveController = _configureConstantVelocityMove(axis=rockMotor)

	# TODO: We should probably also check that lineMotor and rockMotor aren't both the same!'
	sc1=ConstantVelocityScanLine([continuouslyScannableViaController, rockCentre, rockCentre, abs(2*rockAngle),
								  continuousMoveController,
								  hardwareTriggeredNXDetector, exposeTime,
								])
	
	return [sc1]

def _vertScanParams(vertMotor, AbsoluteVertStart, AbsoluteVertEnd, vertStep, vertStepNumber):
	if vertMotor==None:
		return []
	
	if  vertStep == None and vertStepNumber != None:
		vertStep =  _calcStepSize(start=AbsoluteVertStart,  stop=AbsoluteVertEnd,  numPoints=vertStepNumber)
	
	if vertStepNumber != None: print "Number of vertical positions is vertStepNumber+1 (%r)" % (vertStepNumber+1.)
	
	# TODO: Do we need to check that vertMotor.level < numExposuresPD.level?
	return [vertMotor,  AbsoluteVertStart,  AbsoluteVertEnd,  vertStep]

def _horizScanParams(horizMotor, AbsoluteHorizStart, AbsoluteHorizEnd, horizStep, horizStepNumber):
	if horizMotor==None:
		return []
	
	if horizStep == None and horizStepNumber != None:
		horizStep = _calcStepSize(start=AbsoluteHorizStart, stop=AbsoluteHorizEnd, numPoints=horizStepNumber)
	
	if horizStepNumber != None: print "Number of horizontal points is horizStepNumber+1 (%r)" % (horizStepNumber+1.)

	# TODO: Do we need to check that horizMotor.level < numExposuresPD.level?
	return [horizMotor, AbsoluteHorizStart, AbsoluteHorizEnd, horizStep]
	

def _exposeN(exposeTime, exposeNumber, fileName, rockMotor=None, rockAngle=None, rockNumber=None,
			 horizMotor=None, AbsoluteHorizStart=None, AbsoluteHorizEnd=None, horizStep=None, horizStepNumber=None,
			 vertMotor=None, AbsoluteVertStart=None, AbsoluteVertEnd=None, vertStep=None, vertStepNumber=None):
	"""
	An expose uses no motors and exposeDetector
	A Rock is an arbitrary grid with 1 row and column, rocking over rockMotor (dkphi)
	A Line is an arbitrary grid with 1 row, using lineMotor
	A grid is an arbitrary grid with dx/dy as axes
	"""
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	logger = LoggerFactory.getLogger("_exposeN")
	
	detector = _exposeDetector()
	
	detectorShield = jythonNameMap.ds
	exposure = jythonNameMap.exposure # DummyPD("exposure")
	
	scan_params=[]
	scan_params.extend(_vertScanParams(vertMotor, AbsoluteVertStart, AbsoluteVertEnd, vertStep, vertStepNumber))
	scan_params.extend(_horizScanParams(horizMotor, AbsoluteHorizStart, AbsoluteHorizEnd, horizStep, horizStepNumber))
	# Note that the first element in a scan must be a start/stop/step so always add exposure if neither horiz nor vert are present
	scan_params.extend([exposure, 1, exposeNumber, 1] if len(scan_params)==0 or exposeNumber > 1 else [])
	scan_params.extend([detectorShield, DiodeController(True, True)])

	totalExposures = exposeNumber * (1 if horizStep == None else horizStep) * (1 if vertStep == None else vertStep)
	
	if rockMotor == None:
		scan_params.extend(_staticExposeScanParams(detector, exposeTime, totalExposures, fileName, dark=False))
	else:
		rockCentre=_rockCentre()
		totalExposures *= rockNumber
		scan_params.extend(_rockScanParams(detector, exposeTime, totalExposures, fileName, rockMotor, rockCentre, rockAngle, rockNumber))
	
	logger.info("Scan parameters: %r" % scan_params)
	
	scan = ConcurrentScan(scan_params)
	scan.runScan()
	
	if rockMotor != None:
		print "Moving %s back to %r" % (rockMotor.name, rockCentre)
		rockMotor.moveTo(rockCentre)

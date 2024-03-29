from gdascripts.parameters import beamline_parameters
from gda.scan import ConcurrentScan, ConstantVelocityScanLine, MultiRegionScan
from localStationScripts.detector_scan_commands import DiodeController, _configureDetector, _configureConstantVelocityMove, _darkExpose
from scisoftpy import arange
from org.slf4j import LoggerFactory
from gda.device.scannable import ScannableBase
from gda.util import VisitPath
from uk.ac.diamond.daq.persistence.jythonshelf import LocalParameters
from java.io import File
from java.util import NoSuchElementException
from shutil import copyfile
from time import sleep
import os.path

supported_line_motors = ('dx', 'dy', 'dz', 'ssx', 'sy', 'ssz')

supportedLineMotorHelp = ", ".join(supported_line_motors[:-1])+" or "+supported_line_motors[len(supported_line_motors)-1]

# Help definitions

_exposeHelp = """
	exposeTime is the time of each exposure in seconds, fileName is the suffix added to file names in order to help identify them, while processing is optional and allows you to chose specific processing for this scan.
	"""

_exposeNHelp = """
	exposeNumber is the number of exposures to take at each point.
	"""

_lineHelp = """
	lineMotor is the motor to scan (%r supported). stepNumber is the number of steps, so the number of points is this plus one.
	""" % supportedLineMotorHelp

_rockHelp = """
	exposeRockMotor is assumed (default) to be dkphi, rockCentre is assumed (default) to be 58.0.
	"""

_rockNHelp = """
	rockNumber is the number of rocks per exposure. Note that if this is > 1 then the image acquisition will not be synchronised with motion.
	"""

_sweepHelp = """
	exposeSweepMotor is assumed (default) to be dkphi.
	"""

_sweepNHelp = """
	exposeNumber is the number of swept exposures to take.
	"""

_gridHelp = """
	exposeHorizMotor defaults to dx (inner loop) and exposeVertMotor efaults to dz (outer loop). horizStepNumber, vertStepNumber are the number of steps, so the number of positions are these numbers plus one.
	"""


aliasList=[]

# Static exposure

def expose(exposeTime, fileName, processing=None):
	"""
	Static exposure
	"""
	exposeN(exposeTime, 1, fileName, processing)

expose.__doc__ += _exposeHelp
aliasList.append("expose")


def exposeN(exposeTime, exposeNumber, fileName, processing=None):
	"""
	Multiple static exposures
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName)
	if len(verification)>0:
		return verification
	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, processing=processing)

exposeN.__doc__ += _exposeHelp + _exposeNHelp
aliasList.append("exposeN")


def exposeDark(exposeTime, fileName):
	"""
	Multiple static exposures
	"""
	verification = verifyParameters(exposeTime=exposeTime, fileName=fileName)
	if len(verification)>0:
		return verification

	_darkExpose(detector=_exposeDetector(),
			exposeSuppressOpenDetectorShieldAtScanStart = _exposeSuppressOpenDetectorShieldAtScanStart(),
			exposeSuppressCloseDetectorShieldAtScanEnd  = _exposeSuppressCloseDetectorShieldAtScanEnd(),
			exposureTime=exposeTime, sampleSuffix=fileName)

exposeDark.__doc__ += _exposeHelp
aliasList.append("exposeDark")


# Line scans

def exposeLineAbs(exposeTime, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName, processing=None):
	"""
	Line scan using absolute motor positions and stepNumber (which then defines a stepSize)
	"""
	exposeNLineAbs(exposeTime, 1, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName, processing)

exposeLineAbs.__doc__ += _exposeHelp + _lineHelp
aliasList.append("exposeLineAbs")

def exposeLineStep(exposeTime, lineMotor, stepSize, stepNumber, fileName, processing=None):
	"""
	Line scan using stepSize and stepNumber relative to the current motor position
	"""
	exposeNLineStep(exposeTime, 1, lineMotor, stepSize, stepNumber, fileName, processing)

exposeLineStep.__doc__ += _exposeHelp + _lineHelp
aliasList.append("exposeLineStep")


def exposeNLineAbs(exposeTime, exposeNumber, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName, processing=None):
	"""
	Line scan with multiple exposures at each position using absolute motor positions and stepNumber
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, lineMotor=lineMotor, AbsoluteStartPos=AbsoluteStartPos, AbsoluteEndPos=AbsoluteEndPos, stepNumber=stepNumber, fileName=fileName)
	if len(verification)>0:
		return verification

	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, processing=processing, horizMotor=lineMotor, AbsoluteHorizStart=AbsoluteStartPos, AbsoluteHorizEnd=AbsoluteEndPos, horizStepNumber=stepNumber)

exposeNLineAbs.__doc__ += _exposeHelp + _exposeNHelp + _lineHelp
aliasList.append("exposeNLineAbs")


def exposeNLineStep(exposeTime, exposeNumber, lineMotor, stepSize, stepNumber, fileName, processing=None):
	"""
	Line scan with multiple exposures at each position using stepSize and stepNumber relative to the current motor position
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber,
		lineMotor=lineMotor, stepSize=stepSize, stepNumber=stepNumber, fileName=fileName)
	if len(verification)>0:
		return verification

	AbsoluteStartPos, AbsoluteEndPos=_calcAbsPositions(motor=lineMotor, stepSize=stepSize, numSteps=stepNumber)

	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, processing=processing, horizMotor=lineMotor, AbsoluteHorizStart=AbsoluteStartPos, AbsoluteHorizEnd=AbsoluteEndPos, horizStep=stepSize, horizStepNumber=stepNumber)

exposeNLineStep.__doc__ += _exposeHelp + _exposeNHelp + _lineHelp
aliasList.append("exposeNLineStep")


# Grid scans

def exposeGridAbs(exposeTime, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName, processing=None):
	"""
	Grid scan (in effect 2 dimensional line scans), absolute
	"""
	exposeNGridAbs(exposeTime, 1, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName, processing)

exposeGridAbs.__doc__ += _exposeHelp + _gridHelp
aliasList.append("exposeGridAbs")


def exposeGridStep(exposeTime, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName, processing=None):
	"""
	Grid scan (in effect 2 dimensional line scans), relative
	"""
	exposeNGridStep(exposeTime, 1, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName, processing)

exposeGridStep.__doc__ += _exposeHelp + _gridHelp
aliasList.append("exposeGridStep")


def exposeNGridAbs(exposeTime, exposeNumber, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName, processing=None):
	"""
	Grid scan (in effect 2 dimensional line scans), absolute, with multiple exposures at each position
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStepNumber=horizStepNumber, AbsoluteVertStart=AbsoluteVertStart, AbsoluteVertEnd=AbsoluteVertEnd, vertStepNumber=vertStepNumber, fileName=fileName)
	if len(verification)>0:
		return verification

	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, processing=processing, horizMotor=_horizMotor(), AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStepNumber=horizStepNumber, vertMotor=_vertMotor(),   AbsoluteVertStart=AbsoluteVertStart,   AbsoluteVertEnd=AbsoluteVertEnd,   vertStepNumber=vertStepNumber)

exposeNGridAbs.__doc__ += _exposeHelp + _exposeNHelp + _gridHelp
aliasList.append("exposeNGridAbs")


def exposeNGridStep(exposeTime, exposeNumber, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName, processing=None):
	"""
	Grid scan (in effect 2 dimensional line scans), relative, with multiple exposures at each position
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, horizStep=horizStep, horizStepNumber=horizStepNumber, vertStep=vertStep, vertStepNumber=vertStepNumber, fileName=fileName)
	if len(verification)>0:
		return verification

	AbsoluteHorizStart, AbsoluteHorizEnd = _calcAbsPositions(motor=_horizMotor(), stepSize=horizStep, numSteps=horizStepNumber)
	AbsoluteVertStart,  AbsoluteVertEnd  = _calcAbsPositions(motor=_vertMotor(),  stepSize=vertStep,  numSteps=vertStepNumber)

	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, processing=processing, horizMotor=_horizMotor(), AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStep=horizStep, horizStepNumber=horizStepNumber, vertMotor=_vertMotor(),   AbsoluteVertStart=AbsoluteVertStart,   AbsoluteVertEnd=AbsoluteVertEnd,   vertStep=vertStep,   vertStepNumber=vertStepNumber)

exposeNGridStep.__doc__ += _exposeHelp + _exposeNHelp + _gridHelp
aliasList.append("exposeNGridStep")


# Rocking during exposure:

def exposeRock(exposeTime, rockAngle, fileName, processing=None):
	"""
	Single exposure while rocking
	"""
	exposeRockN(exposeTime, rockAngle, 1, fileName, processing)

exposeRock.__doc__ += _exposeHelp + _rockHelp
aliasList.append("exposeRock")


def exposeRockN(exposeTime, rockAngle, rockNumber, fileName, processing=None):
	"""
	Multiple rocks while exposing
	"""
	exposeNRockN(exposeTime, 1, rockAngle, rockNumber, fileName, processing)

exposeRockN.__doc__ += _exposeHelp + _rockHelp + _rockNHelp
aliasList.append("exposeRockN")


def exposeNRockN(exposeTime, exposeNumber, rockAngle, rockNumber, fileName, processing=None):
	"""
	Multiple exposures while rocking several times per exposure
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, rockAngle=rockAngle, rockNumber=rockNumber, fileName=fileName)
	if len(verification)>0:
		return verification

	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, processing=processing, rockMotor=_rockMotor(), rockAngle=rockAngle, rockNumber=rockNumber)

exposeNRockN.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _rockNHelp
aliasList.append("exposeNRockN")


# Sweeping during exposure

def exposeSweep(exposeTime, sweepStart, sweepEnd, sweepAngle, fileName, processing=None):
	"""
	Single exposure per segment of sweep
	"""
	exposeNSweep(exposeTime, 1, sweepStart, sweepEnd, sweepAngle, fileName, processing)

exposeSweep.__doc__ += _exposeHelp + _sweepHelp
aliasList.append("exposeSweep")

def exposeNSweep(exposeTime, exposeNumber, sweepStart, sweepEnd, sweepAngle, fileName, processing=None):
	"""
	Multiple exposures per segment of sweep. This does not currently work.
	"""
	verification = verifyParameters(exposeTime=exposeTime, sweepStart=sweepStart, sweepEnd=sweepEnd, sweepAngle=sweepAngle, fileName=fileName)
	if len(verification)>0:
		return verification
	_exposeN(exposeTime=exposeTime, exposeNumber=1, fileName=fileName, processing=processing, sweepMotor=_sweepMotor(), sweepStart=sweepStart, sweepEnd=sweepEnd, sweepAngle=sweepAngle)

exposeNSweep.__doc__ += _exposeHelp + _sweepHelp + _sweepNHelp
aliasList.append("exposeNSweep")

# Combining exposure, line or grid scans, and rocking

def exposeRockLineAbs(exposeTime, rockAngle, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName, processing=None):
	"""
	Rocking at every position during line scan, absolute
	"""
	exposeNRockLineAbs(exposeTime, 1, rockAngle, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName, processing)

exposeRockLineAbs.__doc__ += _exposeHelp + _rockHelp + _lineHelp
aliasList.append("exposeRockLineAbs")


def exposeRockLineStep(exposeTime, rockAngle, lineMotor, stepSize, stepNumber, fileName, processing=None):
	"""
	Rocking at every position during line scan, relative
	"""
	exposeNRockLineStep(exposeTime, 1, rockAngle, lineMotor, stepSize, stepNumber, fileName, processing)

exposeRockLineStep.__doc__ += _exposeHelp + _rockHelp + _lineHelp
aliasList.append("exposeRockLineStep")


def exposeRockGridAbs(exposeTime, rockAngle, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName, processing=None):
	"""
	Rocking at every position during grid scan, absolute
	"""
	exposeNRockGridAbs(exposeTime, 1, rockAngle, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName, processing)

exposeRockGridAbs.__doc__ += _exposeHelp + _rockHelp + _gridHelp
aliasList.append("exposeRockGridAbs")


def exposeRockGridStep(exposeTime, rockAngle, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName, processing=None):
	"""
	Rocking at every position during grid scan, relative
	"""
	exposeNRockGridStep(exposeTime, 1, rockAngle, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName, processing)

exposeRockGridStep.__doc__ += _exposeHelp + _rockHelp + _gridHelp
aliasList.append("exposeRockGridStep")


def exposeNRockLineAbs(exposeTime, exposeNumber, rockAngle, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName, processing=None):
	"""
	Multiple exposures at each position while rocking at every position during line scan, absolute
	"""
	exposeNRockNLineAbs(exposeTime, exposeNumber, rockAngle, 1, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName, processing)

exposeNRockLineAbs.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _lineHelp
aliasList.append("exposeNRockLineAbs")


def exposeNRockLineStep(exposeTime, exposeNumber, rockAngle, lineMotor, stepSize, stepNumber, fileName, processing=None):
	"""
	Multiple exposures at each position while rocking at every position during line scan, relative
	"""
	exposeNRockNLineStep(exposeTime, exposeNumber, rockAngle, 1, lineMotor, stepSize, stepNumber, fileName, processing)

exposeNRockLineStep.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _lineHelp
aliasList.append("exposeNRockLineStep")


def exposeNRockGridAbs(exposeTime, exposeNumber, rockAngle, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName, processing=None):
	"""
	Multiple exposures at each position while rocking at every position during grid scan, absolute
	"""
	exposeNRockNGridAbs(exposeTime, exposeNumber, rockAngle, 1, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName, processing)

exposeNRockGridAbs.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _gridHelp
aliasList.append("exposeNRockGridAbs")


def exposeNRockGridStep(exposeTime, exposeNumber, rockAngle, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName, processing=None):
	"""
	Multiple exposures at each position while rocking at every position during grid scan, relative
	"""
	exposeNRockNGridStep(exposeTime, exposeNumber, rockAngle, 1, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName, processing)

exposeNRockGridStep.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _gridHelp
aliasList.append("exposeNRockGridStep")


def exposeNRockNLineAbs(exposeTime, exposeNumber, rockAngle, rockNumber, lineMotor, AbsoluteStartPos, AbsoluteEndPos, stepNumber, fileName, processing=None):
	"""
	Multiple exposures while rocking several times per exposure at each position during line scan, absolute
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, rockAngle=rockAngle, rockNumber=rockNumber, lineMotor=lineMotor, AbsoluteStartPos=AbsoluteStartPos, AbsoluteEndPos=AbsoluteEndPos, stepNumber=stepNumber, fileName=fileName)
	if len(verification)>0:
		return verification

	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, processing=processing, rockMotor=_rockMotor(), rockAngle=rockAngle, rockNumber=rockNumber, horizMotor=lineMotor, AbsoluteHorizStart=AbsoluteStartPos, AbsoluteHorizEnd=AbsoluteEndPos, horizStepNumber=stepNumber)

exposeNRockNLineAbs.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _rockNHelp + _lineHelp
aliasList.append("exposeNRockNLineAbs")


def exposeNRockNLineStep(exposeTime, exposeNumber, rockAngle, rockNumber, lineMotor, stepSize, stepNumber, fileName, processing=None):
	"""
	Multiple exposures while rocking several times per exposure at each position during line scan, relative
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, rockAngle=rockAngle, rockNumber=rockNumber, lineMotor=lineMotor, stepSize=stepSize, stepNumber=stepNumber, fileName=fileName)
	if len(verification)>0:
		return verification

	AbsoluteStartPos, AbsoluteEndPos=_calcAbsPositions(motor=lineMotor, stepSize=stepSize, numSteps=stepNumber)

	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, processing=processing,
			rockMotor=_rockMotor(), rockAngle=rockAngle, rockNumber=rockNumber,
			horizMotor=lineMotor, AbsoluteHorizStart=AbsoluteStartPos, AbsoluteHorizEnd=AbsoluteEndPos, horizStep=stepSize, horizStepNumber=stepNumber)

exposeNRockNLineStep.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _rockNHelp + _lineHelp
aliasList.append("exposeNRockNLineStep")


def exposeNRockNGridAbs(exposeTime, exposeNumber, rockAngle, rockNumber, AbsoluteHorizStart, AbsoluteHorizEnd, horizStepNumber, AbsoluteVertStart, AbsoluteVertEnd, vertStepNumber, fileName, processing=None):
	"""
	Multiple exposures while rocking several times per exposure at each position during grid scan
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, rockAngle=rockAngle, rockNumber=rockNumber, AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStepNumber=horizStepNumber, AbsoluteVertStart=AbsoluteVertStart, AbsoluteVertEnd=AbsoluteVertEnd, vertStepNumber=vertStepNumber, fileName=fileName)
	if len(verification)>0:
		return verification

	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, processing=processing, rockMotor=_rockMotor(), rockAngle=rockAngle, rockNumber=rockNumber, horizMotor=_horizMotor(), AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStepNumber=horizStepNumber, vertMotor=_vertMotor(),   AbsoluteVertStart=AbsoluteVertStart,   AbsoluteVertEnd=AbsoluteVertEnd,   vertStepNumber=vertStepNumber)

exposeNRockNGridAbs.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _rockNHelp + _gridHelp
aliasList.append("exposeNRockNGridAbs")


def exposeNRockNGridStep(exposeTime, exposeNumber, rockAngle, rockNumber, horizStep, horizStepNumber, vertStep, vertStepNumber, fileName, processing=None):
	""" Multiple exposures while rocking several times per exposure at each position during grid scan
	horizontal is dx and vertical is dz
	"""
	verification = verifyParameters(exposeTime=exposeTime, exposeNumber=exposeNumber, rockAngle=rockAngle, rockNumber=rockNumber, horizStep=horizStep, horizStepNumber=horizStepNumber, vertStep=vertStep, vertStepNumber=vertStepNumber, fileName=fileName)
	if len(verification)>0:
		return verification

	AbsoluteHorizStart, AbsoluteHorizEnd = _calcAbsPositions(motor=_horizMotor(), stepSize=horizStep, numSteps=horizStepNumber)
	AbsoluteVertStart,  AbsoluteVertEnd  = _calcAbsPositions(motor=_vertMotor(), stepSize=vertStep,  numSteps=vertStepNumber)

	_exposeN(exposeTime=exposeTime, exposeNumber=exposeNumber, fileName=fileName, processing=processing, rockMotor=_rockMotor(), rockAngle=rockAngle, rockNumber=rockNumber, horizMotor=_horizMotor(), AbsoluteHorizStart=AbsoluteHorizStart, AbsoluteHorizEnd=AbsoluteHorizEnd, horizStep=horizStep, horizStepNumber=horizStepNumber, vertMotor=_vertMotor(),   AbsoluteVertStart=AbsoluteVertStart,   AbsoluteVertEnd=AbsoluteVertEnd,   vertStep=vertStep,   vertStepNumber=vertStepNumber)

exposeNRockNGridStep.__doc__ += _exposeHelp + _exposeNHelp + _rockHelp + _rockNHelp + _gridHelp
aliasList.append("exposeNRockNGridStep")


# User input verification functions

def _sanitise(fileName, detector):
	try:
		fileNameCheck = filter(lambda char: char.isalnum() or char in ['-','_'], fileName)
		if fileName != fileNameCheck:
			msg = "Filenames should be alphanumeric strings plus underscores (except for the Mar detector) or dashes. Using %s rather than %s" % (fileNameCheck, fileName)
			print "-"*80
			print msg
			print "-"*80
			LoggerFactory.getLogger("_sanitise").warn(msg)
			fileName = fileNameCheck
	except Exception, e:
		LoggerFactory.getLogger("_sanitise").error("Failure checking {}", fileName, e)

	if fileName == None or not "_" in fileName:
		return fileName

	if ('mar' in detector.name):
		sanitised = fileName.replace("_", "-")
		msg = "Underscores not supported in fileName for %s detector. Using %s rather than %s" % (detector.name, sanitised, fileName)
		print "-"*80
		print msg
		print "-"*80
		LoggerFactory.getLogger("_sanitise").warn(msg)
		return sanitised
	else:
		LoggerFactory.getLogger("_sanitise").info("Underscores detected in '{}', but {} detector is fine with that.", fileName, detector.name)
		return fileName

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
					 rockAngle=None, rockNumber=None, sweepStart=None, sweepEnd=None, sweepAngle=None, lineMotor=None,
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

	if sweepStart			and not (isfloat(sweepStart)):								failures.append("sweepStart should be a number: %r" % sweepStart)
	if sweepEnd				and not (isfloat(sweepEnd)):								failures.append("sweepEnd should be a number: %r" % sweepEnd)
	if sweepAngle			and not (isfloat(sweepAngle)):								failures.append("sweepAngle should be a number: %r" % sweepAngle)

	if lineMotor			and not (hasattr(lineMotor, 'name') and
									lineMotor.name in supported_line_motors):			failures.append("lineMotor `%r` invalid. Supported motors: %r" % (lineMotor, supportedLineMotorHelp))

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

def _d1out():
	return _defaultParameter("expose_d1out", False, " to change the default.")

def _d2out():
	return _defaultParameter("expose_d2out", True, " to change the default.")

def _d3out():
	return _defaultParameter("expose_d3out", True, " to change the default.")

def _exposeSuppressOpenEHShutterAtScanStart():
	return _defaultParameter("exposeSuppressOpenEHShutterAtScanStart", False, " to change the default.")

def _exposeSuppressCloseEHShutterAtScanEnd():
	return _defaultParameter("exposeSuppressCloseEHShutterAtScanEnd", False, " to change the default.")

def _exposeSuppressOpenDetectorShieldAtScanStart():
	return _defaultParameter("exposeSuppressOpenDetectorShieldAtScanStart", False, " to change the default.")

def _exposeSuppressCloseDetectorShieldAtScanEnd():
	return _defaultParameter("exposeSuppressCloseDetectorShieldAtScanEnd", False, " to change the default.")

def _horizMotor():
	return _defaultParameter("exposeHorizMotor", "dx", " to define horizontal axis motor.")

def _vertMotor():
	return _defaultParameter("exposeVertMotor", "dz", " to define vertical axis motor.")

def _rockMotor():
	return _defaultParameter("exposeRockMotor", "dkphi", " to define the rock axis motor.")

def _sweepMotor():
	return _defaultParameter("exposeSweepMotor", "dkphi", " to define the sweep axis motor.")

def _rockCentre():
	return _defaultParameter("rockCentre", 58., " for another centre position.")

def _exposeDetector():
	return _defaultParameter("exposeDetector", None, ", where 'xx' is 'pe' or 'mar' etc.")

def _defaultParameter(parameter, parameter_default, help_text):
	logger = LoggerFactory.getLogger("_defaultParameter")
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()

	if jythonNameMap[parameter] == None:
		if parameter_default == None:
			msg = "%s not defined, please add %s='xx' to localStationUser.py%s" % (
				parameter, parameter, help_text)
			logger.error(msg)
			print msg
			raise Exception(msg)
		msg = "%s is not defined, assuming %r. Add %s='xx' to localStationUser.py%s" % (
			parameter, parameter_default, parameter, help_text)
		logger.info(msg)
		print msg
		if isinstance(parameter_default, str) or isinstance(parameter_default, unicode):
			logger.trace("Returning default scannable %s" % parameter_default)
			return jythonNameMap[parameter_default]
		logger.trace("Returning default %r" % parameter_default)
		return parameter_default

	if isinstance(jythonNameMap[parameter], str) or isinstance(jythonNameMap[parameter], unicode):
		if jythonNameMap[jythonNameMap[parameter]]==None:
			raise Exception('Cannot find %s in the jython namespace when trying to lookup %s' % (jythonNameMap[parameter], parameter))
		logger.trace("Returning scannable defined by %s as '%s': %s" % (parameter, jythonNameMap[parameter], jythonNameMap[jythonNameMap[parameter]].name))
		return jythonNameMap[jythonNameMap[parameter]]

	if isinstance(jythonNameMap[parameter], ScannableBase):
		logger.trace("Returning scannable defined by %s as %s" % (parameter, jythonNameMap[parameter].name))
		return jythonNameMap[parameter]

	logger.trace("Returning value defined by %s as %r" % (parameter, jythonNameMap[parameter]))
	return jythonNameMap[parameter]

def _staticExposeScanParams(detector, exposeTime, fileName, totalExposures, dark):
	logger = LoggerFactory.getLogger("_staticExposeScanParams")
	logger.trace("detector={}, exposeTime={}, fileName={}, totalExposures={}, dark={}",
				detector, exposeTime, fileName, totalExposures, dark)

	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	zebraFastShutter = jythonNameMap.zebraFastShutter
	i0Monitor = jythonNameMap.etlZebraScannableMonitor
	#continuousMonitorController = jythonNameMap.zebra2ZebraMonitorController

	_configureDetector(detector=detector, exposureTime=exposeTime, noOfExposures=totalExposures, sampleSuffix=fileName, dark=False)
	# Disable i0Monitor and fastShutterFeedback for the moment as the stream is seems to be empty, due to the fact that
	# we are controlling the shutter via the zebraFastShutter scannable, rather than via the zebraContinuousMoveController
	#return [detector, exposeTime, zebraFastShutter, exposeTime , i0Monitor, continuousMonitorController, fastShutterFeedback]
	return [detector, exposeTime, zebraFastShutter, exposeTime]

def _rockScanParams(detector, exposeTime, fileName, rockMotor, rockCentre, rockAngle, rockNumber, totalExposures):
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	logger = LoggerFactory.getLogger("_rockScanParams")
	logger.trace("(detector={}, exposeTime={}, fileName={}, rockMotor={}, rockCentre={}, rockAngle={}, rockNumber={}, totalExposures={}",
				detector, exposeTime, fileName, rockMotor, rockCentre, rockAngle, rockNumber, totalExposures)

	if type(rockMotor) is str:
		rockMotor = jythonNameMap[rockMotor]

	if rockNumber <> 1:
		if not rockMotor.name == 'dkphi':
			raise Exception('Only dkphi currently supported for rockNumber > 1, not %r' % (rockMotor.name))

		rockscanMotor = jythonNameMap['dkphi_rockscan']
		msg = "rockNumber > 1 so performing unsynchronised rockscan using %s. Moving to start position %r" % (rockscanMotor.name, rockCentre-rockAngle)
		logger.info(msg)
		print "-"*80
		print msg
		print "-"*80

		rockMotor.moveTo(rockCentre-rockAngle) # Go to start position
		rockscanMotor.setupScan(centre=rockCentre, rockSize=rockAngle, noOfRocksPerExposure=rockNumber)
		scan_params=_staticExposeScanParams(detector, exposeTime, fileName, totalExposures, dark=False)
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
	hardwareTriggeredNXDetector = _configureDetector(detector=detector, exposureTime=exposeTime, noOfExposures=totalExposures,
													 sampleSuffix=fileName, dark=False)
	continuouslyScannableViaController, continuousMoveController = _configureConstantVelocityMove(
													axis=rockMotor, detector=hardwareTriggeredNXDetector)
	if len(continuousMoveController.getTriggeredControllers()) > 0 and not disableZebra2:
		msg = "For rock scans, you may need to set disableZebra2=True in localStationConfiguration"
		print "-"*80
		print msg
		print "-"*80
		logger.warn(msg+"\nlen(continuousMoveController.getTriggeredControllers()) = {} and disableZebra2 = {}",
				len(continuousMoveController.getTriggeredControllers()), disableZebra2)
	if False: # len(continuousMoveController.getTriggeredControllers()) > 0:
		# Note disableZebra2=True should do this anyway!
		i0Monitor, continuousMonitorController = jythonNameMap.etlZebraScannableMonitor, jythonNameMap.zebra2ZebraMonitorController
		fastShutterFeedback = jythonNameMap.fastShutterFeedbackScannableMonitor
		zebra2info = ",\n %r,\n %r,\n %r" % (i0Monitor.name, fastShutterFeedback.name, continuousMonitorController.name)
		zebra2params = [                     i0Monitor,      fastShutterFeedback,      continuousMonitorController]
	else:
		zebra2info = ""
		zebra2params = []

	logger.info("_rockScanParams: [%r, %r, %r, %r,\n %r,\n %r, %r%s]" % (
								  continuouslyScannableViaController.name, rockCentre, rockCentre, abs(2*rockAngle),
								  continuousMoveController.name,
								  hardwareTriggeredNXDetector.name, exposeTime,
								  zebra2info
								))
	# TODO: We should probably also check that lineMotor and rockMotor aren't both the same!'
	sc1=ConstantVelocityScanLine([continuouslyScannableViaController, rockCentre, rockCentre, abs(2*rockAngle),
								  continuousMoveController,
								  hardwareTriggeredNXDetector, exposeTime,
								]+zebra2params)

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

def _sweepScanParams(detector, exposeTime, fileName, sweepMotor, sweepStart, sweepEnd, sweepAngle, totalExposures):
	logger = LoggerFactory.getLogger("_sweepScanParams")
	logger.info("Continuous sweep scan on {} using {}: start={}, stop={}, angle={}",
				sweepMotor.name, detector.name, sweepStart, sweepEnd, sweepAngle)
	logger.debug("detector.getCollectionStrategy()={} exposeTime={} fileName={} totalExposures={}",
				  detector.getCollectionStrategy(),   exposeTime,   fileName,   totalExposures)

	totalExposures *= len(arange(sweepStart, sweepEnd, sweepAngle))

	logger.debug("totalExposures={} after sweep images accounted for", totalExposures)

	# TODO: There should also be feedback (error message of sorts) if the combination of exposure time and sweep angle either
	#       result in the motor (dkphi) to move slower than it can or faster than it can.
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	hardwareTriggeredNXDetector = _configureDetector(detector=detector, exposureTime=exposeTime, noOfExposures=totalExposures,
													 sampleSuffix=fileName, dark=False)
	continuouslyScannableViaController, continuousMoveController = _configureConstantVelocityMove(
													axis=sweepMotor, detector=hardwareTriggeredNXDetector)
	if len(continuousMoveController.getTriggeredControllers()) > 0:
		i0Monitor, continuousMonitorController = jythonNameMap.etlZebraScannableMonitor, jythonNameMap.zebra2ZebraMonitorController
		fastShutterFeedback = jythonNameMap.fastShutterFeedbackScannableMonitor
		zebra2info = ",\n %r,\n %r,\n %r" % (i0Monitor.name, fastShutterFeedback.name, continuousMonitorController.name)
		zebra2params = [                     i0Monitor,      fastShutterFeedback,      continuousMonitorController]
	else:
		zebra2info = ""
		zebra2params = []

	logger.info("_sweepScanParams: [%r, %r, %r, %r,\n %r,\n %r, %r%s]" % (
									continuouslyScannableViaController.name, sweepStart, sweepEnd, sweepAngle,
									continuousMoveController.name,
									hardwareTriggeredNXDetector.name, exposeTime,
									zebra2info
								))
	# TODO: We should probably also check that lineMotor and rockMotor aren't both the same!'
	sc1=ConstantVelocityScanLine([continuouslyScannableViaController, sweepStart, sweepEnd, sweepAngle,
								  continuousMoveController,
								  hardwareTriggeredNXDetector, exposeTime,
								]+zebra2params)

	return [sc1]

def _sweepScan(detector, exposeTime, fileName, sweepMotor, sweepStart, sweepEnd, sweepAngle,
				totalExposures, scan_params):
	logger = LoggerFactory.getLogger("_sweepScan")
	logger.info("Sweep scan on %s using %s: start=%f, stop=%f, angle=%f" % (sweepMotor.name, detector.name, sweepStart, sweepEnd, sweepAngle))
	logger.info("detector.getCollectionStrategy()=%r" % detector.getCollectionStrategy())

	rockStartPositions = arange(sweepStart, sweepEnd, sweepAngle)
	totalExposures *= len(rockStartPositions) # *2 # TODO: Is this needed?

	logger.info("rockStartPositions=%r" % rockStartPositions)

	mrs=MultiRegionScan()
	for rockStart in rockStartPositions:
		rockAngle = sweepAngle/2.
		rockCentre = rockStart + rockAngle
		rockScanParams=_rockScanParams(detector, exposeTime, fileName, sweepMotor, rockCentre, rockAngle, 1, totalExposures)
		inner_scan = ConcurrentScan(scan_params + rockScanParams)
		logger.debug("Scan parameters for rockStart %r: %r" % (rockStart, scan_params + rockScanParams))
		mrs.addScan(inner_scan)
	logger.info("MultiRegionScan: {}", mrs)
	mrs.runScan()

def _exposeN(exposeTime, exposeNumber, fileName, processing,
			 rockMotor=None, rockAngle=None, rockNumber=None,
			 sweepMotor=None, sweepStart=None, sweepEnd=None, sweepAngle=None,
			 horizMotor=None, AbsoluteHorizStart=None, AbsoluteHorizEnd=None, horizStep=None, horizStepNumber=None,
			 vertMotor=None, AbsoluteVertStart=None, AbsoluteVertEnd=None, vertStep=None, vertStepNumber=None):
	"""
	An expose uses no motors and exposeDetector
	A Rock is an arbitrary grid with 1 row and column, rocking over rockMotor (dkphi)
	A Sweep is a series of rocks covering the range from start to end
	A Line is an arbitrary grid with 1 row, using lineMotor
	A grid is an arbitrary grid with dx/dy as axes
	"""
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	logger = LoggerFactory.getLogger("_exposeN")

	detector = _exposeDetector()
	fileName = _sanitise(fileName, detector)

	detectorShield = jythonNameMap.ds
	detectorShield.suppressOpenDetectorShieldAtScanStart = _exposeSuppressOpenDetectorShieldAtScanStart()
	detectorShield.suppressCloseDetectorShieldAtScanEnd = _exposeSuppressCloseDetectorShieldAtScanEnd()

	exposure = jythonNameMap.exposure # DummyPD("exposure")

	scan_params=[]
	scan_params.extend(_vertScanParams(vertMotor, AbsoluteVertStart, AbsoluteVertEnd, vertStep, vertStepNumber))
	scan_params.extend(_horizScanParams(horizMotor, AbsoluteHorizStart, AbsoluteHorizEnd, horizStep, horizStepNumber))
	# Note that the first element in a scan must be a start/stop/step so always add exposure if neither horiz nor vert are present
	scan_params.extend([exposure, 1, exposeNumber, 1] if len(scan_params)==0 or exposeNumber > 1 else [])
	scan_params.extend([detectorShield, DiodeController(_d1out(), _d2out(), _d3out(),
					suppressOpenEHShutterAtScanStart=_exposeSuppressOpenEHShutterAtScanStart(),
					suppressCloseEHShutterAtScanEnd=_exposeSuppressCloseEHShutterAtScanEnd() )])

	if processing != None:
		scan_params.extend([processing])
		logger.info("Added %r to scan...", processing)
	elif (jythonNameMap['enableExposeProcessingRequests'] and
							jythonNameMap['processing']):
		scan_params.extend([jythonNameMap['processing']])
		logger.info("Added processing to scan...")

	totalExposures = (exposeNumber * (1 if horizStepNumber == None else horizStepNumber + 1) *
									 (1 if vertStepNumber == None else vertStepNumber + 1) )

	if rockMotor:
		rockMotorPosition = rockMotor.getMotor().getTargetPosition()
		rockCentre=_rockCentre()
		scan_params.extend(_rockScanParams(detector, exposeTime, fileName, rockMotor, rockCentre, rockAngle, rockNumber, totalExposures))
	elif sweepMotor:
		sweepMotorPosition = sweepMotor.getMotor().getTargetPosition()
		if detector.name in ['pil3cbf', 'pil3', 'pil3HWT']:
			logger.info("Detector %s supports continuous sweep scans..." % (detector.name))
			scan_params.extend(_sweepScanParams(detector, exposeTime, fileName,
				sweepMotor, sweepStart, sweepEnd, sweepAngle, totalExposures))
		else:
			logger.info("Detector %s does not support continuous sweep scans, doing each rock individually..." % (detector.name))
			_sweepScan(detector, exposeTime, fileName, sweepMotor, sweepStart, sweepEnd, sweepAngle,
				totalExposures, scan_params)
			scan_params=[] # Delete original scan_params so the ConcurrentScan isn't performed too.
	else:
		scan_params.extend(_staticExposeScanParams(detector, exposeTime, fileName, totalExposures, dark=False))

	if scan_params:
		logger.info("Scan parameters: %r" % scan_params)

		scan = ConcurrentScan(scan_params)
		scan.runScan()

	if rockMotor:
		print "Moving %s back to %r after rock scan" % (rockMotor.name, rockMotorPosition)
		rockMotor.moveTo(rockMotorPosition)
	elif sweepMotor:
		print "Moving %s back to %r after sweep scan" % (sweepMotor.name, sweepMotorPosition)
		sweepMotor.moveTo(sweepMotorPosition)

def exposeAliases(alias):
	for command in aliasList:
		alias(command)
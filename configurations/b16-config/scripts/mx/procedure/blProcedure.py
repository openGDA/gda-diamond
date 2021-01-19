from java.lang import Math

from gda.device import DeviceException

from gdascripts.parameters import beamline_parameters

from framework import script_utilities # @UnresolvedImport

from org.slf4j import LoggerFactory

MIN_SETTLE_TIME = 2.0
TOLERANCE_DEFAULT = 0.2

logger = LoggerFactory.getLogger(__name__)


def blParameters():
	return beamline_parameters.Parameters()


def checkedMove(scannable, target=0.0, tolerance=0.2):
		try:
			logger.debug('checkedMove of axis %s to target %.2f' % (scannable.getName(), target))
			checkedOK = False
			scannable.moveTo(target) # synchronous
			
			logger.debug('checkedMove check arrival of axis %s to target %.2f' % (scannable.getName(), target))
			checkedOK = checkTolerance(scannable, target, tolerance)
		
		except KeyboardInterrupt:
			message = "Controlled stage movement interrupted"
			logger.warn(message)
			raise DeviceException(message)
		
		except Exception:
			message = "Controlled stage movement failed"
			logger.warn(message)
			raise DeviceException(message)
			
		finally:
			return checkedOK


def checkTolerance(scannable, target, tolerance):
	in_tolerance = False
	message=None
	try:
		if scannable:
			stats = (scannable.getName(), scannable.getPosition(), target, tolerance)
			difference = Math.abs(scannable.getPosition() - target)
			in_tolerance = difference <= Math.abs(tolerance)
			
			if not in_tolerance:
				message = "scannable %s FAILED move tolerance: pos=%g : target %g +/- %g" % stats
		else:
			message = "WARNING: FAILED to check position tolerance"
		
		if message:
			print (message)
			logger.warn(message)
		
	except:
		message = "FAILED to check position tolerance"
		raise DeviceException(message)
		
	return in_tolerance


def queueCloseFastShutter():
	command = 'from component.shutter_control import shutterControl as sc; sc.closeFastShutter()'
	script_utilities.enqueueCommandString(command, 'Close Fast Shutter')


def queueOpenFastShutter():
	command = 'from component.shutter_control import shutterControl as sc; sc.openFastShutter()'
	script_utilities.enqueueCommandString(command, 'Open Fast Shutter')


def stopall():
	pass

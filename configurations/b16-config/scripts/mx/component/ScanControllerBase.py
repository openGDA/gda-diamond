import sys
import time

from gda.device import DeviceException
from procedure.blProcedure import checkedMove

from datacollection.RunMetadata import RunMetadata # @UnusedImport for reference
from framework.script_utilities import not_implemented

from org.slf4j import LoggerFactory


class ScanControllerBase():
	
	DEFAULT_START_DELTA = 1.0
	MIN_SETTLE_TIME = 1.0
	
	def __init__(self):
		self.logger = LoggerFactory.getLogger(__name__)
		self.scan_axis = None
		self.axis_name = None
		self.gonio_det = None
		self.gonio_twotheta = None
		self.gonio_omega = None
		self.gonio_phi = None
		self.gonio_kappa = None


	def	_minimum_wait_to_set_motors_busy(self):
		time.sleep(0.05)


	def _reset_speeds(self):
		self.logger.debug('_reset_speeds')
		try:
			# if self.gonio_phi:
			#	self.gonio_phi.resetSpeed()
			self.gonio_omega.getMotor().setSpeed(1000.0)
			# self.gonio_det.resetSpeed()
		except:
			raise DeviceException('FAIL to reset speed for goniometer axes', sys.exc_info()[1])


	def _set_scan_speed(self, scan_axis, run_data):
		scan_speed = run_data.speed()
		self.logger.debug('setting scan speed to %.2f deg/sec...' % scan_speed)
		scan_axis.getMotor().setSpeed(scan_speed)
		self._minimum_wait_to_set_motors_busy()


	def checked_move(self, scannable, target=0.0, tolerance=0.2):
		return checkedMove(scannable, target, tolerance)


	def configureScan(self, run_data, metadata=None):
		self.logger.debug('configureScan')
		self.scan_axis = self.get_scan_axis_scannable(run_data)
		self.axis_name = self.scan_axis.getName()
		return self.isConfigured()


	def get_scan_axis_scannable(self, run_data):
		axis_choice = run_data.axisChoice()
		if axis_choice:
			if run_data.isRotationOmega():
				axis_scannable = self.gonio_omega
			elif run_data.isRotationPhi():
				axis_scannable = self.gonio_phi
			else:
				axis_scannable = None
		
		else:
			axis_scannable = None
		
		if axis_scannable:
			self.logger.debug('scannable axis : %s' % (axis_scannable.getName()))
		else:
			self.logger.warn('FAIL to identify scannable axis from run metadata')
			self.logger.debug(str(run_data))
		
		return axis_scannable


	def isConfigured(self):
		return self.scan_axis is not None


	def isMoving(self):
		not_implemented("ScanControllerBase.isMoving()")


	def runScan(self, run_data):
		# Should be asynchronous
		not_implemented("ScanControllerBase.runScan()")


	def setupScanPosition(self, run_data):
		not_implemented("ScanControllerBase.runScan()")


	def stop(self):
		if self.scan_axis and self.scan_axis.isBusy():
			self.scan_axis.stop()


	def waitWhileBusy(self):
		not_implemented("ScanControllerBase.waitWhileBusy()")


	def waitWhileScanning(self):
		not_implemented("ScanControllerBase.waitWhileScanning()")


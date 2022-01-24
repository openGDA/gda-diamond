from gda.device import DeviceException

# from gda.device import Stoppable
from gda.device.zebra.controller import Zebra # API constants
# from gda.device.zebra.controller.impl import ZebraImpl

from datacollection.scan_gate import compute_gate
from framework.script_utilities import not_implemented

from datacollection.RunMetadata import RunMetadata # @UnusedImport for reference
from component.ScanControllerBase import ScanControllerBase # @UnresolvedImport
from component.shutter_control import shutterControl

from org.slf4j import LoggerFactory

from gdaserver import zebra # @UnresolvedImport

class ScanControllerZebra(ScanControllerBase):

	def __init__(self):
		# super(ScanControllerZebra, self).__init__()
		self.logger = LoggerFactory.getLogger(__name__)
		self.scan_axis = None
		self.axis_name = None
		self.gonio_det = None
		self.gonio_twotheta = None
		self.gonio_omega = None
		self.gonio_phi = None
		self.gonio_kappa = None

		self.shutter_control = shutterControl
		self.zebra = zebra
		self.gate = None


	# base: def _reset_speeds(self):
	# base: def _set_scan_speed(self, scan_axis, run_data):

	def configureScan(self, run_data, metadata=None, time_to_velocity=0.5, shutter_delay=0.03):
		# super(ScanControllerZebra, self).configureScan(run_data, metadata)
		self.logger.debug('configureScan')
		self.scan_axis = self.get_scan_axis_scannable(run_data)
		self.axis_name = self.scan_axis.getName()

		# Determine any zebra variant configuration here based on 
		# experiment mode, experiment type and parameters
		self.setup_position_compare(run_data, time_to_velocity, shutter_delay)
		return self.isConfigured()


	def disarm(self):
		self.logger.info("disarm zebra...")
		self.zebra.pcDisarm()
		self.logger.info("disarmed zebra")


	# base: def get_scan_axis_scannable(self, runData)

	def isConfigured(self):
		return self.gate is not None


	def isMoving(self):
		return self.scan_axis is not None and self.scan_axis.isBusy()


	def isTriggered(self):
		not_implemented("ScanControllerZebra.isTriggered()")


	def move_prescan_position(self, run_data):
		try: # move end-station axes to pre-scan position
			self.logger.debug('set sequence of checked moves')
			axes=[]
			
			self.logger.debug('axis choice : %s' % (run_data.axisChoice()))
			# if run_data.isRotationOmega():
			omega_target = run_data.preScanPosition()
			
			# self.logger.debug('phi target : %f' % (phi_target))
			self.logger.debug('omega target : %f' % (omega_target))
			# axes.append((self.gonio_phi, phi_target))
			# axes.append((self.gonio_twotheta, run_data.twoThetaVal()))
			axes.append((self.gonio_omega, omega_target))
			# axes.append((self.gonio_kappa, run_data.kappaVal()))
			# axes.append((self.gonio_det, run_data.detDistance()))
			
			self._reset_speeds()
			
			# self.logger.debug('kappa %f' % (self.gonio_kappa.getPosition()))
			if True: # mode normal
				for (axis, target) in axes:
					self.logger.debug('moving axis %s to start angle %.2f' % (str(axis), target))
					if not self.checked_move(axis, target):
						message = 'FAIL to check move of %s to %2f' % (str(axis), target)
						raise DeviceException(message)
				
				self.logger.info('Goniometer in pre-scan position.')
				
		except:
			self.stop()
			prescan = run_data.preScanPosition()
			axis_choice = run_data.axisChoice()
			message = 'FAIL to move to gonio to pre-scan position : %s = %s' % (axis_choice, prescan)
			self.logger.error(message)
			raise DeviceException(message)


	def reset(self):
		self.disarm()
		# self.resetOscillationParameters()
		self.zebra.setPCDir(Zebra.PC_DIR_POSITIVE)
		self.shutter_control.closeFastShutter()
		self.gate = None


	def runScan(self, run_data, collect_mode="normal"):
		if self.isConfigured():
			self.logger.debug('Collection mode: %s' % str(collect_mode))
			#' self.logger.info('Asynchronous scan %s to end angle(%2.4f)' % (str(self.axis_name), self.gate.scan_end))
			self.zebra.pcArm() #  arm_zebra() # enable position compare
			self.logger.info(">>>> Set scan axis")
			self.scan_axis = self.gonio_omega # if run_data.isRotationOmega() else self.gonio_phi
			self.logger.info(">>>> Start scan speed")
			self._set_scan_speed(self.scan_axis, run_data)
			self.logger.info(">>>> Start scan sweep")
			self.scan_axis.asynchronousMoveTo(self.gate.axis_terminus)
		else:
			self.logger.info('ScanController NOT configured - runScan aborting')
		
		return self.isConfigured()


	def set_gonio_det_axis(self, det_axis):
		self.gonio_det = det_axis


	def set_gonio_kappa_axis(self, kappa_axis):
		self.gonio_kappa = kappa_axis


	def set_gonio_omega_axis(self, omega_axis):
		self.gonio_omega = omega_axis


	def set_gonio_phi_axis(self, phi_axis):
		self.gonio_phi = phi_axis


	def set_gonio_twotheta_axis(self, twotheta_axis):
		self.gonio_twotheta = twotheta_axis


	def setup_position_compare(self, run_data, time_to_velocity, shutter_delay):
		self.logger.debug('setup_position_compare')
		
		self.zebra.setPCCaptureBitField(3)
		self.zebra.setPCTimeUnit(Zebra.PC_TIMEUNIT_SEC)
		self.zebra.setPCArmSource(int(Zebra.PC_ARM_SOURCE_SOFT))
		
		self.zebra.setPCEnc(Zebra.PC_ENC_ENC4) # CHECK: omega encoder
		
		# Gate Start
		try:
			gate = compute_gate(run_data, time_to_velocity, shutter_delay)
			gate.log()
			self.gate = gate
			run_data.setPreScanPosition(gate.prescan)
		except:
			self.logger.debug(str(run_data))
			raise DeviceException('FAIL to calculate pre-scan position\n %s' % (str(run_data.start())))
		
		self.zebra.setPCDir(Zebra.PC_DIR_POSITIVE) # CHECK:
		self.zebra.setPCGateSource(Zebra.PC_GATE_SOURCE_POSITION) # gate based on position
		self.zebra.setPCGateStart(gate.shutter_open)
		self.zebra.setPCGateWidth(gate.shutter_interval + gate.scan_width)
		self.zebra.setPCGateStep(0.0)
		self.zebra.setPCGateNumberOfGates(1)
		
		# Pulse
		self.zebra.setPCPulseSource(Zebra.PC_PULSE_SOURCE_TIME)
		self.zebra.setPCPulseStart(gate.shutter_delay)
		# self.zebra.setPCPulseWidth(4.0)
		# self.zebra.setPCPulseDelay(0.0)
		# self.zebra.setPCPulseStep(0.0)
		self.zebra.setPCPulseMax(1)


	def setupScanPosition(self, run_data):
		self.move_prescan_position(run_data)


	def stop(self):
		self.shutter_control.closeFastShutter()
		if self.scan_axis and self.scan_axis.isBusy():
			self.scan_axis.stop()
		self._reset_speeds()


	def waitWhileBusy(self):
		if self.scan_axis:
			self._minimum_wait_to_set_motors_busy()
			self.scan_axis.waitWhileBusy()


	def waitWhileScanning(self):
		self.waitWhileBusy()


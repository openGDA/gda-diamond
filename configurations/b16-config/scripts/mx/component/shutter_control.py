import time

from gda.device import Stoppable, DeviceException

from framework.stage_control import StageControl, device, beamline_parameters # @UnusedImport
from framework.stage_control import STATE_ERROR, STATE_IDLE, STATE_PREP, STATE_TRANSIT # list all states @UnusedImport

from gda.configuration.properties.LocalProperties import isDummyModeEnabled

SHT_STATE_OPEN = "Open"
SHT_STATE_CLOSED = "Closed"

MON_STATE_BASEUP = "BASEUP"

OPEN_POS = 1 # "IN"
CLOSE_POS = 0 # "OUT"

OPEN_POS_VAL = "Yes"
CLOSE_POS_VAL = "No"

SHUTTER_OPEN = "Open"
SHUTTER_CLOSED = "Closed"
SHUTTER_CLOSE = "Close"
SHUTTER_RESET = "Reset"

FAST_SHUTTER_MODE = "fast_shutter_mode" # PVScannable
FAST_SHUTTER_STATE = "fast_shutter_state" # PVScannable
FAST_SHUTTER_DEMAND = "fast_shutter_demand" # PVScannable

FS_IS_CLOSED = "Closed"
FS_IS_OPEN = "Open"
FS_IS_AUTO = "Auto"
FS_IS_MANUAL = "Manual"
FS_TO_OPEN = FS_IS_OPEN if isDummyModeEnabled() else 1
FS_TO_CLOSED = FS_IS_CLOSED if isDummyModeEnabled() else 0
FS_TO_AUTO = FS_IS_AUTO if isDummyModeEnabled() else 0
FS_TO_MANUAL =  FS_IS_MANUAL if isDummyModeEnabled() else 1


class ShutterControl(StageControl, Stoppable):

	def _is_fast_shutter_auto(self):
		return FS_IS_AUTO == self.fast_shutter_mode()


	def _is_fast_shutter_manual(self):
		return FS_IS_MANUAL == self.fast_shutter_mode()


	def _is_fast_shutter_open(self):
		return 0.5 < self.fast_shutter_state()


	def _close_fast_shutter(self):
		self.fast_shutter_demand(FS_TO_CLOSED)
		time.sleep(1.0)


	def _mode_fast_shutter(self, mode):
		self.fast_shutter_mode(mode)


	def _open_fast_shutter(self):
		self.fast_shutter_demand(FS_TO_OPEN)
		time.sleep(0.1)


	def closeFastShutter(self):
		self._close_fast_shutter()
		if self._is_fast_shutter_open():
			self._mode_fast_shutter(FS_TO_MANUAL)
			self._close_fast_shutter()
		
		if self._is_fast_shutter_open():
			raise DeviceException("Fast Shutter FAILED to close.")


	def getFastShutterPosition(self):
		if self._is_fast_shutter_open():
			return FS_IS_OPEN
		else:
			return FS_IS_CLOSED


	def configure(self):
		self.state = STATE_PREP
		try:
			StageControl.configure(self)
			self.state = STATE_PREP
			# self.hutch_check = ActiveHutchApprover(ActiveHutchApprover.EH2)
			self.fast_shutter_mode = device(FAST_SHUTTER_MODE)
			self.fast_shutter_state = device(FAST_SHUTTER_STATE)
			self.fast_shutter_demand = device(FAST_SHUTTER_DEMAND)
			self.state = STATE_IDLE
		except:
			message = "FAILURE to configure ShutterControl"
			self.raiseError(message)
		
		return "Fast Shutter is %s" % (self.getFastShutterPosition())


	def isFastShutterModeAuto(self):
		return self._is_fast_shutter_auto()


	def isFastShutterModeManual(self):
		return self._is_fast_shutter_manual()


	def isFastShutterOpen(self):
		return self._is_fast_shutter_open()


	def openFastShutter(self):
		return self._open_fast_shutter()


	def operateFastShutter(self):
		if self._is_fast_shutter_open():
			self._close_fast_shutter()
		else:
			self._open_fast_shutter()


	def setFastShutterModeAuto(self):
		self._mode_fast_shutter(FS_TO_AUTO)


	def setFastShutterModeManual(self):
		self._mode_fast_shutter(FS_TO_MANUAL)


	def stop(self):
		self.closeFastShutter()


shutterControl = ShutterControl()
shutterControl.configure()

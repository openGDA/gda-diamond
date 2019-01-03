from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class BarcodeReader(ScannableMotionBase):

	def __init__(self, name, base_pv, robot_pv):
		self.name = name
		self._base_pv = base_pv
		self._code = CAClient(base_pv + 'CODE')
		self._status = CAClient(base_pv + 'STATUS')
		self._enable = CAClient(robot_pv + 'BCRCTRL')
		self._timeout = CAClient(base_pv + 'STATUS.HIGH')
		self._code.configure()
		self._status.configure()
		self._enable.configure()
		self._timeout.configure()

	def _get_code(self):
		return self._code.caget()

	def _get_valid(self):
		return self._status.caget() == '1'

	def enabled(self, enable=None):
		if enable is None: return self._enable.caget()
		self._enable.caput(1 if enable else 0)

	def rawGetPosition(self):
		if self.valid:
			return self.code
		else:
			return ''

	def _get_timeout(self):
		self._timeout.caget()

	def _set_timeout(self, time_out):
		self._timeout.caput(time_out)

	code = property(_get_code)
	valid = property(_get_valid)
	timeout = property(_get_timeout, _set_timeout)

from gda.device.scannable import ScannableBase
from __builtin__ import False
try:
	import json
except ImportError:
	import simplejson as json

from diffcalc.ub.calcstate import UBCalcStateEncoder

class UBCalcMetadata (ScannableBase):
	def __init__(self, name, ubcalc):
		self.name = name
		self.ubcalc = ubcalc

	def getPosition(self):
		if self.ubcalc is not None or self.ubcalc._state is not None:
			return json.dumps(self.ubcalc._state, cls=UBCalcStateEncoder)
		return None

	def rawAsynchronousMoveTo(self, position):
		pass

	def isBusy(self):
		return False
from gda.device.scannable import ScannableBase
try:
	import json
except ImportError:
	import simplejson as json

from diffcalc.ub.calcstate import UBCalcStateEncoder

class UBCalcMetadata (ScannableBase):
	def __init__(self, name, ubcalc):
		self.name = name
		self.setInputNames([])
		self.setExtraNames(['value', 'n_hkl'])
		self.setOutputFormat(['%s', '%6.4f'])
		self.ubcalc = ubcalc

	def getPosition(self):
		if self.ubcalc is not None or self.ubcalc._state is not None:
			return json.dumps(self.ubcalc._state, cls=UBCalcStateEncoder), self.getSurfaceVector()
		return None, self.getSurfaceVector()

	def getSurfaceVector(self):
		if self.ubcalc is not None and self.ubcalc.n_hkl is not None:
			ref_matrix = self.ubcalc.n_hkl # See I16-635
			surface_vector = ref_matrix.T.tolist()[0]
			return surface_vector
		return None

	def rawAsynchronousMoveTo(self, position):
		pass

	def isBusy(self):
		return False
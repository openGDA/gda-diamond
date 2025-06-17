from gda.device.scannable import ScannableBase
import math
import scisoftpy as np
from diffcalc.util import DiffcalcException
try:
	import json
except ImportError:
	import simplejson as json

from diffcalc.ub.calcstate import UBCalcStateEncoder

class UBCalcMetadata (ScannableBase):
	def __init__(self, name, ubcalc):
		self.name = name
		self.setInputNames([])
		self.setExtraNames(['value', 'n_hkl', 'unit_cell', 'ub_matrix'])
		self.setOutputFormat(['%s', '%6.4f', '%6.4f', '%6.4f'])
		self.ubcalc = ubcalc

	def getPosition(self):
		value = None
		if self.ubcalc is not None and self.ubcalc._state is not None:
			value = json.dumps(self.ubcalc._state, cls=UBCalcStateEncoder)

		return value, self.getSurfaceVector(), self.getUnitCell(), self.getUbMatrix()

	def getSurfaceVector(self):
		if self.ubcalc is not None and self.ubcalc.n_hkl is not None:
			ref_matrix = self.ubcalc.n_hkl # See I16-635
			surface_vector = ref_matrix.T.tolist()[0]
			return surface_vector
		return None

	def getUnitCell(self):
		if (self.ubcalc is not None and 
				self.ubcalc._state is not None and
				self.ubcalc._state.crystal is not None  and
				self.ubcalc._state.crystal.getLattice() is not None):

			xtal = self.ubcalc._state.crystal.getLattice()
			latticeParams = list(xtal[1:])
			return [latticeParams]
		return None

	def getUbMatrix(self):
		try :
			if self.ubcalc is not None and self.ubcalc.UB is not None:
				ubMatrix = self.ubcalc.UB.tolist()
				# Diffcalc's UB matrix is scaled up by 2*PI
				ubMatrix = [ [_u * 0.5/math.pi for _u in _r] for _r in ubMatrix ]
				#transform by [[1, 0, 0], [0, 0, -1], [0, 1, 0]] to get UB in lab frame
				ubMatrix = np.dot(np.array(ubMatrix), np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])).tolist()
				return [ubMatrix]
		except DiffcalcException :
			#TODO this should only print once per scan but can't use atScanStart or something because it's not actually in the scan.
			print "WARNING: Could not calculate UB Matrix, if this is required please check UB has been defined correctly"
		return None

	def rawAsynchronousMoveTo(self, position):
		pass

	def isBusy(self):
		return False
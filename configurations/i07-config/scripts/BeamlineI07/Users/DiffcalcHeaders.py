import math
from gda.device.scannable import ScannableMotionBase

class DiffcalcHeaders(ScannableMotionBase):
	def __init__(self, name):
		self.setName(name)
		self.setInputNames(['diffcalc_lattice', 'diffcalc_u', 'diffcalc_ub'])
		self.setOutputFormat(['%s', '%s', '%s'])

	def getPosition(self):
		try:
			d = ubcalc._state.crystal
			output_lattice = [d._a1, d._a2, d._a3, math.degrees(d._alpha1), math.degrees(d._alpha2), math.degrees(d._alpha3)]
		except(AttributeError, NameError, TypeError, diffcalc.util.DiffcalcException):
			output_lattice = 'None'
		try:
			output_u = ubcalc.U.tolist()
		except(AttributeError, NameError, TypeError, diffcalc.util.DiffcalcException):
			output_u = 'None'
		try:
			output_ub = ubcalc.UB.tolist()
		except(AttributeError, NameError, TypeError, diffcalc.util.DiffcalcException):
			output_ub = 'None'
		return [output_lattice, output_u, output_ub]

	def asynchronousMoveTo(self, position):
		return None

	def createsOwnFiles(self):
		return False

	def isBusy(self):
		return 0

	def toString(self):
		return str(self.getPosition())

diffcalchdr = DiffcalcHeaders("diffcalchdr")
meta_add(diffcalchdr)


# ubcalc._state.crystal._a3
# math.degrees(ubcalc._state.crystal._alpha3)
# ubcalc.U
# ubcalc.UB
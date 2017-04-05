class DiffcalcHeaders(PseudoDevice):
	def __init__(self, name):
		self.setName(name)
		self.setInputNames(['diffcalc_lattice', 'diffcalc_u', 'diffcalc_ub'])
		self.setOutputFormat(['%s', '%s', '%s'])

	def getPosition(self):
		try:
			d = diffcalc_object._ubcalc.getState()
			output_lattice = [d['crystal']['a'], d['crystal']['b'], d['crystal']['c'], d['crystal']['alpha'], d['crystal']['beta'], d['crystal']['gamma']]
		except(TypeError, diffcalc.utils.DiffcalcException):
			output_lattice = 'None'
		try:
			d_u = diffcalc_object._ubcalc.getUMatrix().array
			output_u = [[d_u[0][0], d_u[0][1], d_u[0][2]], [d_u[1][0], d_u[1][1], d_u[1][2]], [d_u[2][0], d_u[2][1], d_u[2][2]]]
		except(TypeError, diffcalc.utils.DiffcalcException):
			output_u = 'None'
		try:
			d_ub = diffcalc_object._ubcalc.getUBMatrix().array
			output_ub = [[d_ub[0][0], d_ub[0][1], d_ub[0][2]], [d_ub[1][0], d_ub[1][1], d_ub[1][2]], [d_ub[2][0], d_ub[2][1], d_ub[2][2]]]
		except(TypeError, diffcalc.utils.DiffcalcException):
			output_ub = 'None'
		return [str(output_lattice), str(output_u), str(output_ub)]

	def asynchronousMoveTo(self, position):
		return None

	def createsOwnFiles(self):
		return False

	def isBusy(self):
		return 0

	def toString(self):
		return str(self.getPosition())

diffcalchdr = DiffcalcHeaders("diffcalchdr")
fileHeader.add([diffcalchdr])
pilatusHeader.add([diffcalchdr])

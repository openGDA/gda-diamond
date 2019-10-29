from gda.device.scannable import PseudoDevice

class variableClass(PseudoDevice):
	'''
	Function PD Class
	Return value of a specified scalar variable or attribute
	'''
	def __init__(self, name, variable):
		self.setName(name)
		self.variable=variable
		self.setExtraNames([name])
		self.setInputNames([])
		self.Units=['Units']
		self.setOutputFormat(['%6.4f'])
		self.setLevel(3)
		self.currentposition=0

	def isBusy(self):
		return 0

	def getPosition(self):
		return self.variable

#ct=variableClass('count_time',ct3.count_time)

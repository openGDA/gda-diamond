from gda.device.scannable import ScannableMotionBase

class PDFromFunctionClass(ScannableMotionBase):
	'''
	wrap scalar function in PD for reading
	'''
	def __init__(self, name, function, format, level,help=None):
		self.setName(name)		
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help 
		self.function=function
		self.setInputNames([])
		self.setExtraNames([name])
		self.setOutputFormat([format])
		self.setLevel(level)
	
	def getPosition(self):
		return self.function()

	def isBusy(self):
		return 0


alpha=PDFromFunctionClass('alpha',calcalpha,'%4.4f',9,'PD to read alpha (incident beam to surface) angle, with surface normal defined by azir function')
beta=PDFromFunctionClass('beta',calcbeta,'%4.4f',9,'PD to read beta (incident beam to surface) angle, with surface normal defined by azir function')

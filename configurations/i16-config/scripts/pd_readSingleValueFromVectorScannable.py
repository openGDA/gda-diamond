from gda.device.scannable import ScannableMotionBase
class ReadSingleValueFromVectorPDClass(ScannableMotionBase):
	'''
	PD with single output and no imput
	Reads value from specified index of an existing PD
	'''
	def __init__(self,pd,index,name,format,help=None):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames([])
		self.setExtraNames([name]);
		self.setOutputFormat([format])
		self.setLevel(9)
		self.index=index
		self.pd=pd

	def getPosition(self):
		return self.pd()[self.index]
	
	def isBusy(self):
		return self.pd.isBusy()

class pd_minusval_class(ScannableMotionBase):
	'''
	return -1*specified collumn of PD
	'''
	def __init__(self,name,pd,nfield):
		self.setName(name);
		self.setLevel(11)
		self.pd=pd
		self.nfield=nfield
		self.setExtraNames([name])
		self.setInputNames([])
		self.setOutputFormat([self.pd.getOutputFormat()[self.nfield]])
#		self.setOutputFormat(['%f'])

	def isBusy(self):
		return 0

	def getPosition(self):
		return self.pd()[self.nfield]*-1.0

#last param is output field to use (-1 is last)
#roi2neg=pd_minusval_class('roi2neg',roi2,-1)
rtiltneg=pd_minusval_class('rtiltneg',nivel,2)

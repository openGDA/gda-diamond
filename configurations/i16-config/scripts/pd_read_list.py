class ReadListPDClass(PseudoDevice):
	'''Create PD to read elements of a list'''
	def __init__(self, name, list, unitstring, formatstring):
		self.setName(name);
		self.setInputNames(['index'])
		self.setExtraNames([name]);
		self.Units=['int', unitstring]
		self.setOutputFormat(['%.0f',formatstring])
		self.setLevel(8)
		self.list=list
		self.index=0

	def asynchronousMoveTo(self,index):
		self.index=int(index)

	def getPosition(self):
		return [self.index, float(self.list[self.index])]

	def isBusy(self):
		return 0



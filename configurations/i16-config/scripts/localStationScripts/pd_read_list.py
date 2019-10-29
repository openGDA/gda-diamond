class ReadListPDClass(PseudoDevice):
	'''
	Create PD to read elements of a list pdname.list
	Example:
	maxvalPD=ReadListPDClass('maxval','%.3f') #do this only once
	maxvalPD.list+=[maxval.result.maxval]	#add value to list
	scan maxvalPD 0 maxvalPD.max_ind 1	#scan values
	maxvalPD.list=[]			#reset list
	Note: if you want to scan multiple lists then create multiple ReadListPDClass PD's
	'''
	def __init__(self, name, formatstring):
		self.setName(name);
		self.setInputNames(['index'])
		self.setExtraNames([name]);
#		self.Units=['int', unitstring]
		self.setOutputFormat(['%.0f',formatstring])
		self.setLevel(8)
		self.list=[]
		self.index=0

	def max_ind(self):
		return len(self.list)-1

	def asynchronousMoveTo(self,index):
		self.index=int(index)

	def getPosition(self):
		if self.index>len(self.list)-1:
			self.index=len(self.list)-1
			print "=== Warning: index out of range - using last point"
		return [self.index, float(self.list[self.index])]

	def isBusy(self):
		return 0


class ReadListPDClassOld(PseudoDevice):
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

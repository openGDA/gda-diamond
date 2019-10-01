#experiment to see how a scan works
# It seems to move all devices and read back positions then finally read all positions again at the end of a scan line.

class WrapPDClass(PseudoDevice):
	'''
	Experimental - do not use!!
	'''
	def __init__(self,pd,name,help=None):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.pd=pd
		self.setOutputFormat(pd.getOutputFormat())
		self.setLevel(pd.getLevel())
		self.setInputNames(pd.getInputNames())		

	def asynchronousMoveTo(self,inpos):
		print "==Moving "+self.name
		self.pd.asynchronousMoveTo(inpos)

	def getPosition(self):
		print "==Reading "+self.name
		return self.pd()
	def isBusy(self):
		return self.pd.isBusy()

kthscript=WrapPDClass(kth,'kthscript')
wscript=WrapPDClass(w,'wscript')
kthshowscript=WrapPDClass(kthshow,'kthshowscript')

scan kthscript 0 .1 .001 wscript 10 kthshowscript
from gda.device.scannable import ScannableMotionBase
import java.lang.Exception

class ReadPDGroupClass(ScannableMotionBase):
	'''Output values of a group of PseudoDevices'''
	def __init__(self, name,pdlist):
		self.pdlist=pdlist
		self.setName(name);
		self.setInputNames([])
		names=[]; formats=[];
		for pd in self.pdlist:
			names+=pd.getInputNames()+pd.getExtraNames()
			formats+=pd.getOutputFormat()
		self.setExtraNames(names);
		self.setOutputFormat(formats)
		self.setLevel(7)

	def getPosition(self):
		outlist=[]
		for pd in self.pdlist:
			try:
				outlist+=pd()
			except:
				try:
					outlist+=[pd()]
				except (Exception, java.lang.Exception), e:
					print self.name + " could not record the position of " + pd.name + " as it's getPosition is throwing:"
					print e
					outlist+=['Unavailable']*len(pd.outputFormat)
		return outlist

	def isBusy(self):
		return 0
	
#things=ReadPDGroupClass('things',[eta, energy, ic1, hkl])
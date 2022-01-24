from gda.device.scannable import ScannableMotionBase
import java.lang.Exception

class ReadPDGroupClass(ScannableMotionBase):
	'''Output values of a group of PseudoDevices'''
	def __init__(self, name,pdlist,help=None):
		if help is not None: self.__doc__+='\nHelp specific to '+name+':\n'+help
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
			# Get a position
			try:
				position = pd()
			except (Exception, java.lang.Exception), e:
				#print self.name + ": The position of " + pd.name + " is 'Unavailable' as it's getPosition is throwing:", e
				#position = ['Unavailable'] * len(pd.outputFormat)
				#position = [float('nan')] * len(pd.outputFormat)
				position = [-9999999.99999999] * len(pd.outputFormat)
			
			# Create a list from the position
			try:
				position_list = list(position)
			except TypeError:
				position_list = [position]
			
			outlist += position_list
							
		return outlist

	def isBusy(self):
		return 0
	
#things=ReadPDGroupClass('things',[eta, energy, ic1, hkl])

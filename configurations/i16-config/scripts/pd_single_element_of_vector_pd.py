from gda.device.scannable import PseudoDevice
import misc_functions

class single_element_of_vector_pd_class(PseudoDevice):
	'''
	manipulate a single element of a vector PD
	'''
	def __init__(self, name, pd, fieldname, help=None):
		self.pd=pd
		self.fieldname=fieldname
		self.setName(name);
		self.setLevel(pd.getLevel())
		self.setExtraNames(pd.getInputNames()+pd.getExtraNames());
		i=-1; self.ifield=None
		for inputname in pd.getInputNames():
			i+=1
			if inputname==fieldname:
				self.ifield=i
		self.setOutputFormat([pd.getOutputFormat()[self.ifield]]+list(pd.getOutputFormat()))
		self.setInputNames([name])
		if help is not None:
			self.__doc__+='\nHelp specific to '+self.name+':\n'+str(help)

	def getPosition(self):
		return [self.pd.getPosition()[self.ifield]]+self.pd.getPosition()

	def isBusy(self):
		return self.pd.isBusy()

	def rawAsynchronousMoveTo(self,new_position):
		self.pos=self.pd.getPosition()
		self.pos[self.ifield]=new_position
		self.pd.asynchronousMoveTo(self.pos)





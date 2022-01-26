from gda.device.scannable import ScannableMotionBase
import misc_functions

class single_element_of_vector_pd_class(ScannableMotionBase):
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

class single_element_of_vector_pd_with_offset_and_scalefactor_class(ScannableMotionBase):
	'''
	manipulate a single element of a vector PD with an offset given by an offset PD
	Use set method to calibrate to a new value
	(this could be tidied up to replace single_element_of_vector_pd_class if offsetpd is taken as a keyword with default None and scalefact with default +1)
	'''
	def __init__(self, name, pd, fieldname, offsetpd, scalefac=+1.0, help=None):
		self.pd=pd
		self.offsetpd=offsetpd
		self.scalefac=scalefac
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
		#return [(self.scalefac*((self.pd.getPosition()[self.ifield]+self.offsetpd.getPosition())]+self.pd.getPosition()
		return [self.scalefac*(self.pd.getPosition()[self.ifield]+self.offsetpd.getPosition())]+self.pd.getPosition()

	def isBusy(self):
		return self.pd.isBusy()

	def rawAsynchronousMoveTo(self,new_position):
		self.pos=self.pd.getPosition()
		self.pos[self.ifield]=new_position/self.scalefac-self.offsetpd.getPosition()
		self.pd.asynchronousMoveTo(self.pos)

	def set(self, setval):
		'set pd to set value by changing offset pd'
		print "=== Recalibrating offset\n=== Old offset: ",self.offsetpd.getPosition()
		self.offsetpd.asynchronousMoveTo(setval/self.scalefac-self.pd.getPosition()[self.ifield])
		print "=== New offset: ",self.offsetpd.getPosition()




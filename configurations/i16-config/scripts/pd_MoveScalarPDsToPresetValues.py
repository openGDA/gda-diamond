from gda.device.scannable import ScannableMotionBase

class MoveScalarPDsToPresetValuesClass(ScannableMotionBase):
	'''Move a set of scalar PV's between pre-set vaues
	usage: devname=MoveScalarPDsToPresetValuesClass(name, pd_list,values_list)
	pd_list is a list of participating PD's
	values_list is a list of lists of values. First list in values_list is the values for position 1 etc
	'''
	def __init__(self, name, pd_list,values_list,help=None):
		self.setName(name);		
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.pd_list=pd_list
		self.values_list=values_list
		self.setInputNames([name])
		formats=['%.0f']; extranames=[];
		for pd in self.pd_list:
			formats+=pd.getOutputFormat()
			extranames+=pd.getInputNames()
			extranames+=pd.getExtraNames()
		self.setOutputFormat(formats)
		self.setExtraNames(extranames)
		self.setLevel(5)
		self.posn=-1

	def getPosition(self):
		self.positions=[float(self.posn)]
		for pd in self.pd_list:
			try:
				self.positions+=pd()
			except:
				self.positions+=[pd()]
		return self.positions		

	def asynchronousMoveTo(self,position):
		self.posn=position
		for pdnum in range(len(self.pd_list)):
			#print "moving",self.pd_list[pdnum].getName(),"to",self.values_list[position][pdnum]
			self.pd_list[pdnum].asynchronousMoveTo(self.values_list[int(self.posn)][pdnum])

	def isBusy(self):
		for pd in self.pd_list:
			if pd.isBusy():
				return 1
		return 0
	
	def stop(self):
		print "calling stop"
		for pd in self.pd_list:
			pd.stop()

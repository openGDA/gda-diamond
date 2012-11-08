from gda.device.scannable import PseudoDevice

class pd_acd_table_v(PseudoDevice):
	'''
	Assume no offsets
	'''
	def __init__(self,name,format,jack1PD,jack2PD,jack3PD,help=None):
		self.setName(name);
		if help is not None:	self.__doc__+='\nHelp specific to '+self.getName()+':\n'+help
		self.setLevel(3)
		self.setInputNames(['ADCj1'])
		self.setExtraNames(['ADCj2','ADCj3'])
		self.setOutputFormat([format,format,format])
		self.jack1PD=jack1PD
		self.jack2PD=jack2PD
		self.jack3PD=jack3PD

	def getPosition(self):
		return [self.jack1PD(), self.jack2PD(), self.jack3PD()]
	
	def asynchronousMoveTo(self,new_position):
		self.jack1PD.asynchronousMoveTo(new_position)
		self.jack2PD.asynchronousMoveTo(new_position)
		self.jack3PD.asynchronousMoveTo(new_position)

	def isBusy(self):
		return self.jack1PD.isBusy() or self.jack2PD.isBusy() or self.jack3PD.isBusy()

	def stop():
		self.jack1PD.stop()
		self.jack2PD.stop()
		self.jack3PD.stop()

class pd_acd_table_h(PseudoDevice):
	'''
	Assume no offsets
	'''
	def __init__(self,name,format,x1PD,x2PD,help=None):
		self.setName(name);
		if help is not None:	self.__doc__+='\nHelp specific to '+self.getName()+':\n'+help
		self.setLevel(3)
		self.setInputNames(['ADCx1'])
		self.setExtraNames(['ADCx2'])
		self.setOutputFormat([format,format])
		self.x1PD=x1PD
		self.x2PD=x2PD

	def getPosition(self):
		return [self.x1PD(), self.x2PD()]
	
	def asynchronousMoveTo(self,new_position):
		self.x1PD.asynchronousMoveTo(new_position)
		self.x2PD.asynchronousMoveTo(new_position)

	def isBusy(self):
		return self.x1PD.isBusy() or self.x2PD.isBusy()

	def stop():
		self.x1PD.stop()
		self.x2PD.stop()

adcv=pd_acd_table_v('adcv','%.3f',p2mj1,p2mj2,p2mj3,help='adc vert dist mm')
adch=pd_acd_table_h('adch','%.3f',p2mx1,p2mx2,help='adc horiz dist mm')

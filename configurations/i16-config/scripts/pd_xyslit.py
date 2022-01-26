from gda.device.scannable import ScannableMotionBase

class pd_xyslit(ScannableMotionBase):
	'''
	2d slit device
	input/output: [xgap(horizontal), ygap(vertical)]	
	This device also has individual x and y slit translation devices
	i.e. pos self.x allowes to move the x translation device
	'''
	def __init__(self,name,format,xgapPD,ygapPD,xtransPD,ytransPD,help=None):
		self.setName(name);
		if help is not None:	self.__doc__+='\nHelp specific to '+self.getName()+':\n'+help
		self.setLevel(3)
		self.setInputNames(['xgap','ygap'])
		self.setOutputFormat([format,format])
		self.xgap=xgapPD
		self.ygap=ygapPD
		self.x=xtransPD
		self.y=ytransPD

	def getPosition(self):
		return [self.xgap(), self.ygap()]	
	
	def asynchronousMoveTo(self,new_position):
		self.xgap.asynchronousMoveTo(new_position[0])
		self.ygap.asynchronousMoveTo(new_position[1])

	def isBusy(self):
		return self.xgap.isBusy() or self.ygap.isBusy()

#ds=pd_xyslit('Detector slits (s6)','%.3f',s6xgap,s6ygap,s6xtrans,s6ytrans,help='Detector slit gaps\npos ds [1 2] to get 1 mm (h) x 2 mm(v) slit\npos ds.x .5 to translate x centre to 0.5 mm')
#ss=pd_xyslit('Sample slits (s5)','%.3f',s5xgap,s5ygap,s5xtrans,s5ytrans,help='Sample slit gaps\npos ss [1 2] to get 1 mm (h) x 2 mm(v) slit\npos ss.x .5 to translate x centre to 0.5 mm')

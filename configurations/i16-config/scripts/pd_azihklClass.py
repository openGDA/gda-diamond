from gda.device.scannable import ScannableMotionBase
class AzihklClass(ScannableMotionBase):
	'Azimuthal reference reciprocal lattice vector'
	def __init__(self,name):
		self.setName(name);
		self.setLevel(3)
		self.setInputNames(['azih','azik','azil'])
#		self.Units=[]
		self.setOutputFormat(['%4.4f', '%4.4f','%4.4f'])
		self.azir_function = None
		
	def asynchronousMoveTo(self,new_position):
		self.azir_function(new_position)

	def isBusy(self):
		return 0

	def getPosition(self):
		return list(self.azir_function())

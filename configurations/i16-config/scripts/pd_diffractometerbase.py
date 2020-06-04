from gda.device.scannable import ScannableMotionBase

class DiffoBaseClass(ScannableMotionBase):
	'''Create PD for diffractometer base'''
	def __init__(self, z1, z2, z3, offsets):
		self.offsets=offsets
		self.z1 = z1
		self.z2 = z2
		self.z3 = z3
		self.setName('Base_z');
		self.setInputNames(['Base_z'])
		self.setExtraNames(['Base_z1','Base_z2','Base_z3']);
		#self.Units=[unitstring]
		self.setOutputFormat(['%.3f', '%.3f','%.3f','%.3f'])
		self.setLevel(5)
	
	def getPosition(self):
		return([self.z1()-self.offsets[0],self.z1(),self.z2(),self.z3()])

	def asynchronousMoveTo(self,new_position):
		self.z1.asynchronousMoveTo(new_position+self.offsets[0])
		self.z2.asynchronousMoveTo(new_position+self.offsets[1])
		self.z3.asynchronousMoveTo(new_position+self.offsets[2])

	def isBusy(self):
		return(self.z1.isBusy() or self.z2.isBusy() or self.z3.isBusy())
	
	def stop(self):
		self.z1.stop()
		self.z2.stop()
		self.z3.stop()

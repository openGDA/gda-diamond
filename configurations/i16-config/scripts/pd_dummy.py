from gda.device.scannable import ScannableMotionBase

class dummyClass(ScannableMotionBase):
	'''Dummy PD Class'''
	def __init__(self, name):
		self.setName(name)
		self.setInputNames([name])
		self.Units=['Units']
		self.setOutputFormat(['%6.4f'])
		self.setLevel(3)
		self.currentposition = 0.

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,new_position):
		self.currentposition = float(new_position)

	def getPosition(self):
		return self.currentposition

class dummy2dClass(ScannableMotionBase):
	'''Dummy 2d PD Class'''
	def __init__(self, name):
		self.setName(name)
		self.setInputNames([name+'1',name+'2'])
		self.Units=['Units Units']
		self.setOutputFormat(['%6.4f','%6.4f'])
		self.setLevel(3)
		self.currentposition=[0,0]

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,new_position):
		self.currentposition = new_position

	def getPosition(self):
		return self.currentposition	

xy=dummy2dClass('xy')

from gda.device.scannable import ScannableMotionBase

class PD_TwoposClass(ScannableMotionBase):
	'''
	move pd between two positions with no status (to allow integration)
	inputs are the two positions to move between
	outputs are the position aimed for and the actual position
	'''
	def __init__(self,PD):
		self.PD=PD
		self.setName(PD.getName())

		init_names=[];
		for i in range(len(PD.getInputNames())):
			init_names+=[PD.getInputNames()[i]+'_i']
		#print init_names
		self.setInputNames(init_names+list(PD.getInputNames()))
		self.setOutputFormat(list(PD.getOutputFormat()+PD.getOutputFormat()))
		self.setExtraNames(list(PD.getExtraNames()+PD.getExtraNames()))
		self.setLevel(PD.getLevel())
		self.current_position=0

	
	def asynchronousMoveTo(self,positions):
		self.PD.stop()
		self.positions=positions
		if self.current_position==0:
			self.PD.asynchronousMoveTo(positions[1])
			self.current_position=1
		else:
			self.PD.asynchronousMoveTo(positions[0])
			self.current_position=0

	def getPosition(self):
#		print [self.positions(self.current_position),self.PD.getPosition()]
		return [self.positions[self.current_position],self.PD.getPosition()]

	def isBusy(self):
		return 0

sy_twopos=PD_TwoposClass(sy); sy_twopos.setLevel(7)

from CoordinatedMotionGroup import CoordinatedMotionGroup

class EpicsDeferredMotionGroup(CoordinatedMotionGroup):
	'''   
	
	'''
	def __init__(self, name, scnList, fieldNames, deferredMoveControlPoint):
		self.deferredMoveControlPoint = deferredMoveControlPoint
		CoordinatedMotionGroup.__init__(self, name, scnList, fieldNames)
		
	def asynchronousMoveTo(self, dest):
		
		self.checkDestination(dest)
		
		# Count non-None fields
		numToMove=0
		for dest in dest:
			if dest!=None:
				numToMove+=1

		# Perform move
		if numToMove>1:
			self.deferon()
		try:
			CoordinatedMotionGroup.asynchronousMoveTo(self, dest)
		except Exception, e:
			self.deferoff()
			raise e
		self.deferoff()	

	def stop(self):
		# Stop motors and turn off defer flag
		CoordinatedMotionGroup.stop(self)
		self.deferoff()

	def defer(self):
		return self.deferredMoveControlPoint.getValue()
		
	def deferon(self):
		self.deferredMoveControlPoint.setValue(1)
		
	def deferoff(self):
		self.deferredMoveControlPoint.setValue(0)
	


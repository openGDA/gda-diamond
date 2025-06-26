from gda.device.scannable.scannablegroup import ScannableGroup

class ScannableGroupSingleInput(ScannableGroup):
	""" Combined movement of all scannables in a group to the same position - requires only 1 position.
		Will print out only 1 position when queried for position.
	"""
	def asynchronousMoveTo(self, position):
		super(ScannableGroupSingleInput, self).asynchronousMoveTo([position]*len(self.getGroupMembers()))

	def getInputNames(self):
		return [self.name]

	def getOutputFormat(self):
		return ['%5.5g']

	def getPosition(self):
		"""	Return position of first scannable in a group """
		return self.getGroupMembers()[0].getPosition()

	def checkPositionValid(self, position):
		for motor in self.getGroupMembers():
			result = motor.checkPositionValid(position)
			if result:
				return result
		return None
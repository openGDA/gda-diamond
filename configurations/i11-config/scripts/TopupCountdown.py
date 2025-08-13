from gda.epics import CAClient

"""
    Purpose:     pause scan around topups
"""
 
class TopupCountdown(ScannableMotionBase):

	def __init__(self, name, secsBefore=2, secsAfter=5, maxTimeBetweenTopUps=587):

		self.setName(name)
		self.setInputNames([name])
		self.setOutputFormat(["%1.0f"])
		self.secsBefore=secsBefore
		self.secsAfter=secsAfter
		self.maxTimeBetweenTopUps=maxTimeBetweenTopUps
		self.tupv=CAClient("SR-CS-FILL-01:COUNTDOWN")
		self.tupv.configure()
		self.setLevel(7)

	def isBusy(self):
		p=self.getPosition()
		if (p < 0):
			return False
		if (p <= float(self.secsBefore) or (self.maxTimeBetweenTopUps-p) < self.secsAfter):
			return True
		return False

	def getPosition(self):
		return float(self.tupv.caget())

	def asynchronousMoveTo(self,newPosition):
		return 

if __name__ == "__main__":
	topup=TopupCountdown("topup")


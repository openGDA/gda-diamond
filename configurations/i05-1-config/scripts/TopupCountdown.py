from gda.epics import CAClient

"""
    Purpose:     pause scan around topups
"""
 
class TopupCountdown(PseudoDevice):

   def __init__(self, name):
	self.setName(name)
	self.setInputNames([name])
	self.setOutputFormat(["%1.0f"])
	self.secsBefore=2
	self.secsAfter=580
	self.tupv=CAClient("SR-CS-FILL-01:COUNTDOWN")
	self.tupv.configure()
	self.setLevel(7)

   def isBusy(self):
	p=self.getPosition()
	if (p < 0):
		return False
	if (p <= float(self.secsBefore) or p >= float(self.secsAfter)):
		return True
	return False

   def getPosition(self):
	return float(self.tupv.caget())

   def asynchronousMoveTo(self,newPosition):
	return 

topup=TopupCountdown("topup")


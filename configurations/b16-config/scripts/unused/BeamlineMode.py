import gda.device.scannable.ScannableMotionBase

"""
	Purpose:	   TO-DO
	Author:		TO-DO
	Date:		  TO-DO

	This class is a template for writing your own Psuedo Device.  It must contain
	at least a constructor and the  mandatory methods:
		isBusy(self)
		getPosition(self)
		asynchronousMoveTo(self,newPosition)
"""

class BeamlineMode(gda.device.scannable.ScannableMotionBase):

	def __init__(self, bcmpointer):
		self.setName("BeamlineMode")
		#self.setInputNames(["mode"])
		self.setInputNames(["mode"])
		self.setOutputFormat(['%s'])
		self.Units=['Units']
		self.bcm = bcmpointer
		print "!beamline PD constructor complete!"
	def isBusy(self):
		return 0

	
	def getPosition(self):
		return self.bcm.getMode() + "-" + self.bcm.getModeDescription()
		#return "hello"
	
	def asynchronousMoveTo(self,newMode):
		# Check mode number
		pass
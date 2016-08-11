import java
import gda.device.scannable.ScannableBase

class Feedback(gda.device.scannable.PseudoDevice):

	def __init__(self):
		deviceName = "feedback"
		self.name = deviceName
		self.setInputNames([deviceName])
		self.manual = 0
		self.auto = 1
		self.offValue = 0
		self.onValue = 1
		self.kp = -0.0013
		self.ki = 7000


	def isBusy(self):
		""" This dummy device is never busy"""
		return 0

	def getPosition(self):
		""" Return on or off"""
		if ( float(caget("BL22I-OP-DCM-01:FPMTR:FFB:AUTO")) == self.auto ) :
			return "Auto"
		if ( float(caget("BL22I-OP-DCM-01:FPMTR:FFB:AUTO")) == self.manual ):
			if ( float(caget("BL22I-OP-DCM-01:FPMTR:FFB.FBON")) == self.offValue):
				return "Off"
			if ( float(caget("BL22I-OP-DCM-01:FPMTR:FFB.FBON")) == self.onValue):
				return "On"
		return "Unknown"

	def asynchronousMoveTo(self,status):
		if ( status != "On" and status != "Off"):
			raise DeviceException("Choice are On or Off")
		if ( status == "On"):
			self.on()
		if ( status == "Off"):
			self.off()
		return 
	
	def on(self):
		caput("BL22I-OP-DCM-01:FPMTR:FFB:AUTO",self.manual)
		print "Feedback in manual mode"
		sleep(1.0)
		caput("BL22I-OP-DCM-01:FPMTR:FFB.FBON",self.offValue)
		print "Feedback is now off"
		sleep(1.0)
		caput("BL22I-OP-DCM-01:FPMTR:POUT", 0.0 )
		print "2nd Crystal fine pitch is now 0.0"
		sleep(1.0)
		caput("BL22I-OP-DCM-01:FPMTR:FFB.VAL" , 0 )
		print "Set point in feedback is now 0"
		sleep(1.0)
		
		p = float(caget("BL22I-OP-DCM-01:XTAL2:PITCH.VAL"))
		caput("BL22I-OP-DCM-01:XTAL2:PITCH.VAL", p)
		while( float(caget("BL22I-OP-DCM-01:XTAL2:PITCH.DMOV")) == 0 ):
			n=0
			
		print "Adjusting feedback please wait 10s"
		errorDrain = 0.0
		nPoints = 100
		for i in range (nPoints):
			errorDrain = errorDrain + float(caget("BL22I-OP-DCM-01:FPMTR:FFB.ERR"))
			sleep(0.1)
		errorDrain = errorDrain/nPoints
		print "Set point found at "+ str(errorDrain)
		caput ("BL22I-OP-DCM-01:FPMTR:FFB.VAL", -errorDrain)
		sleep(1.0)
		
		caput("BL22I-OP-DCM-01:FPMTR:FFB.FBON",self.onValue)
		print "Feedback is now on"
		sleep(1.0)
		
		caput("BL22I-OP-DCM-01:FPMTR:FFB:AUTO",self.auto)
		print "Feedback in auto mode"
		print "All done"

	def off(self):
		caput("BL22I-OP-DCM-01:FPMTR:FFB:AUTO",self.manual)
		caput("BL22I-OP-DCM-01:FPMTR:FFB.FBON",self.offValue)
		print "Feedback is now off"

feedback = Feedback()


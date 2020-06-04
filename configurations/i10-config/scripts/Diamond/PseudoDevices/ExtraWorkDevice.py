
from time import sleep

from gda.device.scannable import ScannableMotionBase;

class ExtraWorkDeviceClass(ScannableMotionBase):
	""" """

	def __init__(self, name, gdaDevice):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames([]);
#		self.Units=[strUnit]
		self.setOutputFormat(["%12.6f"])
		self.setLevel(7)
		
		self.device = gdaDevice;

#ScannableMotionBase Implementation
	def atScanStart(self):
		print "At Scan Start ---------------------------------------------->"

	def atScanEnd(self):
		print "At Scan End ------------------------------------------------>"
		return;

	def atScanLineStart(self):
		print "At Line Start ++++++++++++++++++++++++>"
		return;
		
	def atScanLineEnd(self):
		print "At Line End ++++++++++++++++++++++++++>";
		return;

	def atPointStart(self):
		print "At Point Start ........>"
		self.device.moveTo(100);
		sleep(5);
		return;
	
	def atPointEnd(self):
		print "At Point End ..........>";
		self.device.moveTo(-100);
		sleep(5);

	def getPosition(self):
		return 0;

	def asynchronousMoveTo(self,newPos):
		return;
	
	def toString(self):
		p=self.getPosition();
		return str(p);

	def stop(self):
		print self.getName() + ": Panic Stop Called"


autoShutter = ExtraWorkDeviceClass("autoShutter", testMotor2);

scan testMotor1 0 10 1 autoShutter

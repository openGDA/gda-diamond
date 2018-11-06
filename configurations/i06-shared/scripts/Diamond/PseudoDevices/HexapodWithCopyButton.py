from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable

#####################################################################################
#
#The Class is for creating OD hexapod scannable device based on the hexapod dofs
#Usage:
#	CorrespondentDeviceClass(name, lowLimit, highLimit, refObj, funForeward, funBackward)
#	HexapodWithCopyButtonClass(name, hexapodDOF, copyButtonPV);
#
#Parameters:
#   name:   Name of the new device
#	hexapodDOF: Name of the Hexapod DOF (for example: "m1x")
#	PV of the Copy Button
#
#####################################################################################
class HexapodWithCopyButtonClass(ScannableMotionBase):
#	def __init__(self, name, strUnit, strFormat):
	def __init__(self, name, hexapodDOF, strButtonPV):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([name]);
		#self.Units=[strUnit]
		#self.setOutputFormat([strFormat])
		#self.setLevel(5);
		self.buttonPV=CAClient(strButtonPV);
		self.hexapodDOF = globals()[hexapodDOF];

	def atScanStart(self):
		if not self.buttonPV.isConfigured():
			self.buttonPV.configure();

	def getPosition(self):
		x=self.hexapodDOF.getPosition();
		return x;

	def asynchronousMoveTo(self, new_position):
		self.pressCopyButton();
		self.hexapodDOF.asynchronousMoveTo(new_position);

	def isBusy(self):
		return self.hexapodDOF.isBusy();

	def stop(self):
		return self.hexapodDOF.stop();

	def atScanEnd(self):
		if self.buttonPV.isConfigured():
			self.buttonPV.clearup();
		return self.hexapodDOF.atEnd();

	def pressCopyButton(self):
		if self.buttonPV.isConfigured():
			tp = self.buttonPV.caput(1)
		else:
			self.buttonPV.configure()
			tp = self.buttonPV.caput(1)
			self.buttonPV.clearup()
			
			
#The "Copy readback to setpoint Button PV"
pvCopyButtonM1 = 'BL06I-OP-COLM-01:TCPUP.PROC';
pvCopyButtonM3 = 'BL06I-OP-FCMIR-01:TCPUP.PROC';
pvCopyButtonM6 = 'BL06I-OP-SWMIR-01:TCPUP.PROC';
pvCopyButtonM7 = 'BL06J-OP-FCMIR-01:TCPUP.PROC';


m1xc = HexapodWithCopyButtonClass("m1xc", "m1x", pvCopyButtonM1);
m1yc = HexapodWithCopyButtonClass("m1yc", "m1y", pvCopyButtonM1);
m1zc = HexapodWithCopyButtonClass("m1zc", "m1z", pvCopyButtonM1);
m1yawc = HexapodWithCopyButtonClass("m1yawc", "m1yaw", pvCopyButtonM1);
m1pitchc = HexapodWithCopyButtonClass("m1pitchc", "m1pitch", pvCopyButtonM1);
m1rollc = HexapodWithCopyButtonClass("m1xrollc", "m1roll", pvCopyButtonM1);

m3xc = HexapodWithCopyButtonClass("m3xc", "m3x", pvCopyButtonM3);
m3yc = HexapodWithCopyButtonClass("m3yc", "m3y", pvCopyButtonM3);
m3zc = HexapodWithCopyButtonClass("m3zc", "m3z", pvCopyButtonM3);
m3yawc = HexapodWithCopyButtonClass("m3yawc", "m3yaw", pvCopyButtonM3);
m3pitchc = HexapodWithCopyButtonClass("m3pitchc", "m3pitch", pvCopyButtonM3);
m3rollc = HexapodWithCopyButtonClass("m3xrollc", "m3roll", pvCopyButtonM3);

m6xc = HexapodWithCopyButtonClass("m6xc", "m6x", pvCopyButtonM6);
m6yc = HexapodWithCopyButtonClass("m6yc", "m6y", pvCopyButtonM6);
m6zc = HexapodWithCopyButtonClass("m7zc", "m6z", pvCopyButtonM6);
m6yawc = HexapodWithCopyButtonClass("m6yawc", "m6yaw", pvCopyButtonM6);
m6pitchc = HexapodWithCopyButtonClass("m6pitchc", "m6pitch", pvCopyButtonM6);
m6rollc = HexapodWithCopyButtonClass("m6xrollc", "m6roll", pvCopyButtonM6);

m7xc = HexapodWithCopyButtonClass("m7xc", "m7x", pvCopyButtonM7);
m7yc = HexapodWithCopyButtonClass("m7yc", "m7y", pvCopyButtonM7);
m7zc = HexapodWithCopyButtonClass("m7zc", "m7z", pvCopyButtonM7);
m7yawc = HexapodWithCopyButtonClass("m7yawc", "m7yaw", pvCopyButtonM7);
m7pitchc = HexapodWithCopyButtonClass("m7pitchc", "m7pitch", pvCopyButtonM7);
m7rollc = HexapodWithCopyButtonClass("m7xrollc", "m7roll", pvCopyButtonM7);


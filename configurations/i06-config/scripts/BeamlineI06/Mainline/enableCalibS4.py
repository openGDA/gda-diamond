from gda.epics import CAClient
from java import lang
from gda.device.scannable import ScannableBase
from gda.device import Scannable

from time import sleep



##################################
def S4Yum(targetGap):
	import math
	
	def Sleep(time):
		lang.Thread.currentThread().sleep(time)
	#convert targetenergy and timedelay to float numbers
	targetGap = float(targetGap)
	timedelay=5000
	timedelay = long(timedelay)
	if (targetGap > 0.0) and (targetGap < 200.0):
		Openingmm = 14.5006 -0.01368*targetGap +3.62863E-5*targetGap**2 -1.20877E-7*targetGap**3 +3.10277E-10*targetGap**4  -5.53949E-13*targetGap**5  +6.55968E-16*targetGap**6 -4.87657E-19*targetGap**7 +2.05093E-22*targetGap**8 -3.71121E-26*targetGap**9
		
		print "Move S4 Y gap to ", targetGap, " um = positioning the motor to ",Openingmm,"mm"
	#	t.caput("BL06I-AL-SLITS-04:Y:GAP.VAL", Openingmm)
		Thread.sleep(timedelay)
	#	check_Set_Point=t.caget("BL06I-AL-SLITS-04:Y:GAP.VAL")
	#	check_Read_Back=t.caget("BL06I-AL-SLITS-04:Y:GAP.RBV")
		
		if (abs(check_Set_Point-check_Read_Back) < 0.01):
	
			print "motor positioned"

		else:

			print "Cannot get into position, check the slit"	

	else:
		print "Target opening must be between 0 and 200 um !"


##################################
#The Class for creating a scannable Motor directly from EPICS PV
class CalibS4YClass(ScannableBase):
	def __init__(self, name, strUnit, strFormat):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames([name]);
		self.Units=[strUnit]
		self.setOutputFormat([strFormat])
		self.setLevel(5)
		self.ydisp=0;

	def atScanStart(self):
		self.ydisp=s4y.getPosition();

	def getPosition(self):
		s4y.getPosition();
		
	def asynchronousMoveTo(self, new_position):
		output_move = 99
		if(self.delayTime >0):
			Thread.sleep(delayTime);
			
		try:
			if self.incli.isConfigured():
				self.incli.caput(new_position)
			else:
				self.incli.configure()
				self.incli.caput(new_position)
				self.incli.clearup()	
		except Exception,e :
			print "error in moveTo", e.getMessage(), e, e.class, output_move
			raise e
	

	def isBusy(self):
		try:
			if self.statecli.isConfigured():
				self.status=self.statecli.caget()
			else:
				self.statecli.configure()
				self.status=self.statecli.caget()
				self.statecli.clearup()	
			if self.status ==None:
				print  "null pointer exception in isBusy"
				raise Exception, "null pointer exception in isBusy"	
			elif self.status=='1':
				return 0
			elif self.status=='0':
				return 1
			elif type(self.status)==type(None):
				return 1
				print "return type is >>> none"
			else:
				print 'Error: Unexpected state: '+self.status
#			raise
		except Exception, e:
			print "error in isBusy", e.getMessage(), e, e.class
			print self.status
			raise e

	def stop(self):
		if self.outcli.isConfigured():
			self.stopcli.caput(1)
		else:
			self.stopcli.configure()
			self.stopcli.caput(1)
			self.stopcli.clearup()

	def atScanEnd(self):
		if self.incli.isConfigured():
			self.incli.clearup()
		if  self.outcli.isConfigured():
			self.outcli.clearup()
		if self.statecli.isConfigured():
			self.statecli.clearup()
		if self.stopcli.isConfigured():
			self.stopcli.clearup()
		
#Access the Motor directly via PV: BL06I-DI-IAMP-04:PHD2:I
#s1ctrSet = ScannableEpicsPVClass('s1ctrSet','BL16I-AL-SLITS-01:X:CENTER', 'mm', '%.4f')

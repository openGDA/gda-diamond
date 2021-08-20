from gda.device.scannable import ScannableMotionUnitsBase
from gda.epics import CAClient

#The Class for changing the grating on I10 PGM
class PGM_GratingClass(ScannableMotionUnitsBase):
	def __init__(self, name, get_pv, set_pv, grating_move_status_pv):
		self.setName(name)
		self.setInputNames([])
		self.setExtraNames([name])
		self.setLevel(7)
		self.chSetGrating=CAClient(set_pv)
		self.chGetGrating=CAClient(get_pv)
		self.chStatusGrating=CAClient(grating_move_status_pv)
		self.strGrating=""

	def atScanStart(self):
		if not self.chGetGrating.isConfigured():
			self.chGetGrating.configure()
		if not self.chSetGrating.isConfigured():
			self.chSetGrating.configure()
		if not self.chStatusGrating.isConfigured():
			self.chStatusGrating.configure()

	#Scannable Implementations
	def getPosition(self):
		return self.getGrating();
	
	def asynchronousMoveTo(self,newPos):
		self.setGrating(newPos);

	def isBusy(self):
		#sleep(60);
		return self.getStatus()==1
	
	def getUserUnits(self):
		return self.units
	
	def atScanEnd(self):
		if self.chGetGrating.isConfigured():
			self.chGetGrating.clearup()
		if self.chSetGrating.isConfigured():
			self.chSetGrating.clearup()
		if self.chStatusGrating.isConfigured():
			self.chStatusGrating.clearup()

	def getStatus(self):
		if self.chStatusGrating.isConfigured():
			g=self.chStatusGrating.caget()
		else:
			self.chStatusGrating.configure()
			g=self.chStatusGrating.caget()
			self.chStatusGrating.clearup()
		return int(float(g));
		
	def getGrating(self):
		if self.chGetGrating.isConfigured():
			g=self.chGetGrating.caget()
		else:
			self.chGetGrating.configure()
			g=self.chGetGrating.caget()
			self.chGetGrating.clearup()
		ng=int(float(g));
		if ng == 0:
			self.strGrating="400 lines/mm Au"
		elif ng == 1:
			self.strGrating="400 lines/mm Si"
		elif ng == 2:
			self.strGrating="1200 lines/mm Au"
		return self.strGrating

	def setGrating(self, x):
		if x == "400 lines/mm Au": #set to 150
			ng=0;
		elif x == "400 lines/mm Si":
			ng=1;
		elif x == "1200 lines/mm Au": # set to 1200
			ng=2;
		else:
			print("Wrong grating number, must be '400 lines/mm Au', '400 lines/mm Si' or '1200 lines/mm Au'")
			return;
		self.strGrating = x
			
		if self.chSetGrating.isConfigured():
			self.strSetGrating=self.chSetGrating.caput(ng)
		else:
			self.chSetGrating.configure()
			self.strGrating = self.chSetGrating.caput(ng)
			self.chSetGrating.clearup()

	def toString(self):
		ss=self.getName() + " :  " + str(self.getPosition())
		return ss


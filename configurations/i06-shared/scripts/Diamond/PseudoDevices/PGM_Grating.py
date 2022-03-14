from gda.device.scannable import ScannableMotionUnitsBase
from gda.epics import CAClient

#The Class for changing the grating on I06 PGM
class PGM_GratingClass(ScannableMotionUnitsBase):
	def __init__(self, name, strGetPV, strSetPV, strGratingMoveStatusPV, units="lines/mm"):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames([name]);
		self.units = units;
		self.setLevel(7);
#		self.setOutputFormat(["%20.12f"]);
		self.chSetGrating=CAClient(strSetPV);
		self.chGetGrating=CAClient(strGetPV);
		self.chStatusGrating=CAClient(strGratingMoveStatusPV);
		self.strGrating='';
		self.grating=0;
		self.target = 150

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
		self.target = int(newPos)
		self.setGrating(self.target);

	def isBusy(self):
		from time import sleep
		sleep(2);
		return self.target != self.getGrating()
	
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
			self.grating=150;
		elif ng == 1:
			self.grating=400;
		elif ng == 2:
			self.grating=1200;
		return self.grating;

	def setGrating(self, x):
		if x == 150: #set to 150
			self.strGrating=" 150 lines/mm";
			ng=0;
		elif x == 400:  #set to 400
			self.strGrating=" 400 lines/mm";
			ng=1;
		elif x == 1200: # set to 1200
			self.strGrating=" 1200 lines/mm";
			ng=2;
		else:
			print "Wrong grating number, must be 150, 400 or 1200 lines/mm";
			return;
			
		if self.chSetGrating.isConfigured():
			self.strSetGrating=self.chSetGrating.caput(ng)
		else:
			self.chSetGrating.configure()
			self.strGrating = self.chSetGrating.caput(ng)
			self.chSetGrating.clearup()

	def toString(self):
		ss=self.getName() + " :  " + str(self.getPosition()) +" lines/mm";
		return ss;


#gratingGetPV = 'BL06I-OP-PGM-01:NLINES';
#gratingSetPV = 'BL06I-OP-PGM-01:NLINES2';
#grating = PGM_GratingClass('grating', gratingGetPV, gratingSetPV);



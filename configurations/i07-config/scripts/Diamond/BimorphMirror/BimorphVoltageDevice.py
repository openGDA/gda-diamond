from gda.epics import CAClient
from gda.device.scannable import ScannableMotionBase
from gda.device.monitor import EpicsMonitor;
from time import sleep;

from Diamond.PseudoDevices.EpicsDevices import EpicsMonitorClass, EpicsSetterClass;
from Diamond.Objects.EpicsDevice import EpicsButtonDeviceClass


"""
Set individual voltages for HFM/VFM bimorphs from GDA

HFM Bimorph voltage channels: 0-7,  PVs: BL07I-OP-KBM-01:HFM:SET-VOUT00 - BL07I-OP-KBM-01:HFM:SET-VOUT07
VFM Bimorph voltage channels: 0-15, PVs: BL07I-OP-KBM-01:VFM:SET-VOUT00 - BL07I-OP-KBM-01:VFM:SET-VOUT15
"""

class BimorphVoltageDeviceClass(object):
	"""
	This class is a wrapper for setting the individual voltages for the bimporph PSU in the Horizontal Focusing Mirror (HFM)
	A script run at client staup time creates an instance called "hfmbm", which can be used to qyesry and set individual voltages.
	Sample use of this instance from the Jython terminal are given below:
	 
	"""
	
	def __init__(self, name, basePV, channelNumber, delayTime, statusPv=None):
		self.name = name;
		self.basePV = basePV;
		self.delay = delayTime;
		self.nChannels = channelNumber;
		self.statusPv = statusPv

		print "init bimorphs: " + self.name;
		self.initScannables();

	def initScannables(self):
		formatstring = '%.6f'
		self.bm_vs = [];
		self.bm_vms = [];
		self.bm_vts = []
		self.bm_vtms = []
		#hack around the fact that VFM bimorph doesn't update its status flag
		#can use HFM status instead instead
		if self.statusPv is None:
			self.status = CAClient( self.basePV + ":GET-STATUS" )
		else:
			self.status = CAClient( self.statusPv )
		self.status.configure()
		for i in range(self.nChannels):
			name = self.name + "_v%0d" % i
			# setter
			pvVoltage = '%s:SET-VOUT%02d' % (self.basePV, i);
			pvStatus  = '%s:GET-STATUS%02d' % (self.basePV, i);
			pvMonitor = '%s:GET-VOUT%02d' % (self.basePV, i);
			pvTarget  = '%s:SET-VTRGT%02d' % (self.basePV, i)
			pvTargetMonitor  = '%s:GET-VTRGT%02d' % (self.basePV, i)
			#print "initScannable, name: %s, pvName: %s" % (name, pvName)
#			self.bm_vs.append( BimorphVoltage(name, pvVoltage, pvStatus, formatstring) );
			self.bm_vs.append( EpicsSetterClass(name, pvVoltage, pvStatus, 'V', formatstring, timeout=None) );
			self.bm_vts.append( EpicsSetterClass(name, pvTarget, pvStatus, 'V', formatstring, timeout=None) )
			self.bm_vms.append( EpicsMonitorClass(name, pvMonitor, 'V', formatstring) );
			self.bm_vtms.append( EpicsMonitorClass(name, pvTargetMonitor, 'V', formatstring) )
			self.bm_vts[-1].delay = 0

		pvApplyProfile=self.basePV + ":SET-ALLTRGT";
		self.buttonApplyProfile=EpicsButtonDeviceClass(pvApplyProfile);
		self.setDelay(self.delay);

	def getPosPlusIncrement(self, increment):
		newPos=[];
		for v in self.bm_vms:
			newPos.append(v.getPosition()+increment);

		return newPos;

	def isBusy(self):
		return int(self.status.caget()) != 0

	def waitWhileBusy(self):
		while self.isBusy():
			sleep(0.1)

	def setVoltages(self, newPos):
		for v in self.bm_vs:
			v.moveTo( newPos[self.bm_vs.index(v)] );

		for v in self.bm_vs:
			v.waitWhileBusy()

	def getVoltages(self):
		newPos=[];
		for v in self.bm_vms:
			newPos.append(v.getPosition());
		for v in self.bm_vs:
			newPos.append(v.getPosition());
		return newPos;

	def setDelay(self, newDelay):
		for v in self.bm_vs:
			v.setDelay(newDelay);

	def setVoltageProfile(self, newPos):
		for v in self.bm_vts:
			v.asynchronousMoveTo( newPos[self.bm_vts.index(v)] );

		for i in xrange(0, len(self.bm_vts)):
			self.bm_vts[i].waitWhileBusy()
			while( self.bm_vts[i].getPosition() != self.bm_vtms[i].getPosition() ):
				sleep(0.1)

		self.buttonApplyProfile.press();

		while not self.isBusy():
			sleep(0.1)

		self.waitWhileBusy()


#####################
class BimorphVoltage(ScannableMotionBase):
	def __init__(self, name, pvVoltage, pvStatus, formatstring):
		self.setName(name)
		self.chVoltage = CAClient(pvVoltage);
		self.chStatus = CAClient(pvStatus);
		self.Units = ['V']
		self.setOutputFormat([formatstring])
		self.delay=5;
		self.timeout = 30;
	
	def setDelay(self, newDelay):
		self.delay = newDelay;
	
	def setTimeout(self, newTimeout):
		self.timeout = newTimeout;
			
	def getPosition(self):
		try:
			if self.chVoltage.isConfigured():
				return float(self.chVoltage.caget())
			else:
				self.chVoltage.configure()
				return float(self.chVoltage.caget())
		except:
			print "Error getting position"

	def asynchronousMoveTo(self, new_position):
		self.currentposition = new_position
		try:
			if self.chVoltage.isConfigured():
#				self.chVoltage.caput(new_position, self.timeout);
				self.chVoltage.caput(new_position);
			else:
				self.chVoltage.configure()
#				self.chVoltage.caput(new_position, self.timeout);
				self.chVoltage.caput(new_position);
				self.chVoltage.clearup()
		except:
			print "Error in moveTo"
		
		sleep(self.delay);

	def getStatus(self):
		try:
			if self.chStatus.isConfigured():
				return int(float(self.chStatus.caget()));
			else:
				self.chStatus.configure()
				return int(float(self.chStatus.caget()));
		except:
			print "Error getting status"


	def isBusy(self):
		if self.getStatus() == 1:#It's done
			return False;
		else:
			return True;

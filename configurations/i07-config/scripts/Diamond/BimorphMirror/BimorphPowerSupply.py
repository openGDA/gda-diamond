from gda.epics import CAClient
from gda.device.scannable import ScannableMotionBase
from time import sleep;

from Diamond.PseudoDevices.EpicsDevices import EpicsMonitorClass, EpicsSetterClass;

"""
Set individual voltages for Bimorph Poser Supply from GDA
Ref: http://serv0002.cs.diamond.ac.uk/cgi-bin/wiki.cgi/bimorphpsu
	http://serv0002.cs.diamond.ac.uk/cgi-bin/wiki.cgi/mcaGroup

"""

class BimorphPowerSupplyDeviceClass(ScannableMotionBase):
	"""
	This class is a wrapper for the Bimporph Mirror Power Supply Unit.
	Ref: http://serv0002.cs.diamond.ac.uk/cgi-bin/wiki.cgi/bimorphpsu
	"""
	
	def __init__(self, name, basePV):
		self.name = name;
		self.basePV = basePV;
		self.delay = 2;
		self.nChannels = channelNumber;

		print "init bimorphs: " + self.name;
		self.initScannables();
			
	def initScannables(self):
		formatstring = '%.6f'
		self.bm_vs = [];
		self.bm_vms = [];
		for i in range(self.nChannels):
			name = self.name + "_v%0d" % i
			# setter
			pvVoltage = '%s:SET-VOUT%02d' % (self.basePV, i);
			pvStatus  = '%s:GET-STATUS%02d' % (self.basePV, i);
			pvMonitor = '%s:GET-VOUT%02d' % (self.basePV, i);
			#print "initScannable, name: %s, pvName: %s" % (name, pvName)
#			self.bm_vs.append( BimorphVoltage(name, pvVoltage, pvStatus, formatstring) );
			self.bm_vs.append( EpicsSetterClass(name, pvVoltage, pvStatus, 'V', formatstring, timeout=None) );
			# read actual (current) voltage
			self.bm_vms.append( EpicsMonitorClass(name, pvMonitor, 'V', formatstring) );

		self.setDelay(self.delay);
		
	def getPosPlusIncrement(self, increment):
		newPos=[];
		for v in self.bm_vms:
			newPos.append(v.getPosition()+increment);
		
		return newPos;
	
	def setVoltages(self, newPos):
		for v in self.bm_vs:
			v.moveTo( newPos[self.bm_vs.index(v)] );
		
	def getVoltages(self):
		newPos=[];
		for v in self.bm_vms:
			newPos.append(v.getPosition());
		for v in self.bm_vs:
			newPos.append(v.getPosition());
		return newPos;

	def getStatus(self):
		

	def setDelay(self, newDelay):
		for v in self.bm_vs:
			v.setDelay(newDelay);


from gda.epics import CAClient
from gda.device.scannable import ScannableMotionBase
from gda.device.monitor import EpicsMonitor

"""
Set individual voltages for HFM/VFM bimorphs from GDA

HFM Bimorph voltage channels: 0-7,  PVs: BL07I-OP-KBM-01:HFM:SET-VOUT00 - BL07I-OP-KBM-01:HFM:SET-VOUT07
VFM Bimorph voltage channels: 0-15, PVs: BL07I-OP-KBM-01:VFM:SET-VOUT00 - BL07I-OP-KBM-01:VFM:SET-VOUT15
"""
# From Jun: look at /dls/i24/software/gda/config/scripts: 
#	KBMotorDeclarations.py
#	KBPositionClass.py
# These set an array of scannables of the same type, which can be positioned by array index

class HfmBm:
	"""
	This class is a wrapper for setting the individual voltages for the bimporph PSU in the Horizontal Focusing Mirror (HFM)
	A script run at client staup time creates an instance called "hfmbm", which can be used to qyesry and set individual voltages.
	Sample use of this instance from the Jython terminal are given below:
	 
	"""
	
	def __init__(self):
		print "init HFM bimorphs"
		self.initScannables()
			
	def initScannables(self):
		basePvName = "BL07I-OP-KBM-01:HFM:SET-VOUT"
		monitorBasePvName = "BL07I-OP-KBM-01:HFM:GET-VOUT"
		nChannels = 8
		unitstring = 'V'
		formatstring = '%.6f'
		self.bm_vs = []
		self.bm_vms = []
		for i in range(nChannels):
			name = "hfm_bm_v%0d" % i
			# setter
			pvName = '%s%02d' % (basePvName, i)
			#print "initScannable, name: %s, pvName: %s" % (name, pvName)
			self.bm_vs.append(BimorphVoltage(name, pvName, unitstring, formatstring))
			# read actual (current) voltage
			monitorPvName = '%s%02d' % (monitorBasePvName, i)
			self.bm_vms.append(BimorphVoltageMonitor(name, monitorPvName, unitstring, formatstring))
			

class VfmBm:
	
	def __init__(self):
		print "init VFM bimorphs"
		self.initScannables()
			
	def initScannables(self):
		basePvName = "BL07I-OP-KBM-01:VFM:SET-VOUT"
		monitorBasePvName = "BL07I-OP-KBM-01:VFM:GET-VOUT"
		nChannels = 16
		unitstring = 'V'
		formatstring = '%.6f'
		self.bm_vs = []
		self.bm_vms = []
		for i in range(nChannels):
			name = "vfm_bm_v%0d" % i
			# voltage setter
			pvName = '%s%02d' % (basePvName, i)
			self.bm_vs.append(BimorphVoltage(name, pvName, unitstring, formatstring))
			# read actual (current) voltage
			monitorPvName = '%s%02d' % (monitorBasePvName, i)
			self.bm_vms.append(BimorphVoltageMonitor(name, monitorPvName, unitstring, formatstring))	
			
				
	
class BimorphVoltage(ScannableMotionBase):
	
	def __init__(self, name, pvName, unitstring, formatstring):
		self.setName(name)
		self.voltagePv = CAClient(pvName)
		self.Units = [unitstring]
		self.setOutputFormat([formatstring])
		
	def getPosition(self):
		try:
			if self.voltagePv.isConfigured():
				return float(self.voltagePv.caget())
			else:
				self.voltagePv.configure()
				return float(self.voltagePv.caget())
		except:
			print "Error getting position"

	def asynchronousMoveTo(self, new_position):
		self.currentposition = new_position
		try:
			if self.voltagePv.isConfigured():
				self.voltagePv.caput(new_position)
			else:
				self.voltagePv.configure()
				self.voltagePv.caput(new_position)
				self.voltagePv.clearup()
		except:
			print "Error in moveTo"

	def isBusy(self):
		return 0	

	
	
class BimorphVoltageMonitor(ScannableMotionBase):
	
	def __init__(self, name, pvName, unitstring, formatstring):
		self.setName(name)
		self.voltageMonitorPv = CAClient(pvName)
		self.Units = [unitstring]
		self.setOutputFormat([formatstring])
	
	
	#def __init__(self, name, pvName, unitstring, formatstring):
	#	self.setName(name)
	#	self.voltageMonitorPv = CAClient(pvName)
	#	self.Units = [unitstring]
	#	self.setOutputFormat([formatstring])
		
	def getPosition(self):
		# return self.currentposition
		try:
			if self.voltageMonitorPv.isConfigured():
				return float(self.voltageMonitorPv.caget())
			else:
				self.voltageMonitorPv.configure()
				return float(self.voltageMonitorPv.caget())
		except:
			print "Error getting position"

	def asynchronousMoveTo(self, new_position):
		pass

	def isBusy(self):
		return 0



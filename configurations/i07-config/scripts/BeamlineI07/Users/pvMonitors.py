from gda.epics import CAClient
from java import lang
from gda.device.scannable import PseudoDevice
from time import sleep

#The Class for creating a Monitor directly from EPICS PV
class MonitorEpicsPVClass(PseudoDevice):
	def __init__(self, name, strPV, strUnit, strFormat):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[strUnit]
		self.setOutputFormat([strFormat])
		self.setLevel(7)
		self.cli=CAClient(strPV)

	def atScanStart(self):
		if not self.cli.isConfigured():
			self.cli.configure()

	def getPosition(self):
		if self.cli.isConfigured():
			return float(self.cli.caget())
		else:
			self.cli.configure()
			return float(self.cli.caget())

	def isBusy(self):
		return 0
	
	def atScanEnd(self):
		if self.cli.isConfigured():
			self.cli.clearup()

print 'Using iBeam for the Beam intensity on MBS1'
iBeam=MonitorEpicsPVClass('iBeam', 'BL07I-AL-SLITS-02:INTEN', 'uA', '%.10f');

print 'Using vac5p for presure on Vacum gauge 5'
vac5p=MonitorEpicsPVClass('vac5p', 'BL07I-VA-GAUGE-05:P', 'mBar', '%.10f');

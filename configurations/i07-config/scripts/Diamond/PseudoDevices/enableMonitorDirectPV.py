from gda.epics import CAClient
from java import lang
from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from time import sleep

#The Class for creating a Monitor directly from EPICS PV
class MonitorEpicsPVClass(ScannableMotionBase):
	def __init__(self, name, strPV, strUnit, strFormat):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[strUnit]
		self.setOutputFormat([strFormat])
		self.setLevel(3)
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


#Access the CA42 directly via PV: BL06I-DI-IAMP-04:PHD2:I
#currentMonitor = MonitorEpicsPVClass('currentMonitor', 'BL06I-DI-IAMP-04:PHD2:I', 'uA', '%.10f')

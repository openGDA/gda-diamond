from gda.epics import CAClient;
from gda.device.scannable import ScannableMotionBase;
from time import sleep

class PandaPVScannableClass(ScannableMotionBase):
	def __init__(self, name, basePV, strUnit, strFormat):
		self.basePV = basePV
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[strUnit];
		self.setOutputFormat([strFormat])
		self.setLevel(7)
		self.sleepTime = 0.05
		self.configure()

	def configure(self):
		self.value_cli=CAClient(self.basePV+":ATTR:1:Value_RBV");
		self.value_cli.configure();
		self.acquireCli = CAClient(self.basePV+":DRV:Acquire")
		self.acquireCli.configure()
		self.counterCli = CAClient(self.basePV+":DRV:POSBUS6:VAL")
		self.counterCli.configure()
		self.configured = True

	def atScanStart(self):
		if not self.isConfigured():
			self.configure()
		self.arm_pcap()

	def atScanEnd(self):
		# disarm position counter pcap via epics DRV plugin
		self.acquireCli.caput(0)

	def getPosition(self):
		# first get position call is coming for nexus metadata, scan not started
		if int(self.acquireCli.caget())==0:
			self.arm_pcap()
			return float(self.value_cli.caget())
		try:
			startIndex = float(self.counterCli.caget())
			while abs(float(self.counterCli.caget())-startIndex)<1.0:
				sleep(self.sleepTime)
			return float(self.value_cli.caget());
		except Exception as e:
			print(e)
			print "Error getting position"

	def asynchronousMoveTo(self, new_position):
		# not supposed to be moved anywhere
		pass;

	def isBusy(self):
		# false as scannable is not movable
		return False

	def arm_pcap(self):
		# arm position counter pcap via epics DRV plugin
		if self.acquireCli.caget()==0:
			self.acquireCli.caput(1)

	def stop(self):
		# disarm position counter pcap via epics DRV plugin
		self.atScanEnd()

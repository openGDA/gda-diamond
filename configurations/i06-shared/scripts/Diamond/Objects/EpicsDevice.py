from gda.epics import CAClient;
from gda.epics.interfaceSpec import GDAEpicsInterfaceReader



#####################################################################################
#
#The Class is for creating a simple object that can do the EPICS caput and caget quickly
#
#Parameters:
#	strPV: EPICS PV in String
#
#####################################################################################

class EpicsDeviceClass(object):
	def __init__(self, deviceName=None, pv=None):
		if deviceName is None:
			self.pv=pv;
		else:
			self.pv=GDAEpicsInterfaceReader.getPVFromSimplePVType(deviceName);
		self.ch=CAClient(self.pv);
		self.ch.configure();

	def caput(self, value):
		if self.ch.isConfigured():
			self.ch.caput(value);
		else:
			self.ch.configure();
			self.ch.caput(value);
			self.ch.clearup();

	def caget(self):
		if self.ch.isConfigured():
			result = self.ch.caget();
		else:
			self.ch.configure();
			result = self.ch.caget();
			self.ch.clearup();
		return result;

#####################################################################################
#
#The Class is for creating a simple object to access EPICS button
#
#Parameters:
#	strButtonPV: EPICS Button PV in String
#
#####################################################################################
class EpicsButtonDeviceClass(EpicsDeviceClass):
	def __init__(self, buttonDeviceName=None, buttonPv=None):
		EpicsDeviceClass.__init__(self, buttonDeviceName, buttonPv);

	def press(self):
		self.caput(1);


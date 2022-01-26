from gda.epics import CAClient;

#####################################################################################
#
#The Class is for creating a simple object that can do the EPICS caput and caget quickly
#
#Parameters:
#	strPV: EPICS PV in String
#
#####################################################################################

class EpicsPvClass(object):
	def __init__(self, strPV):
		self.pv=CAClient(strPV);
		self.pv.configure();

	def caput(self, value):
		if self.pv.isConfigured():
			self.pv.caput(value);
		else:
			self.pv.configure();
			self.pv.caput(value);
			self.pv.clearup();

	def caget(self):
		if self.pv.isConfigured():
			result = self.pv.caget();
		else:
			self.pv.configure();
			result = self.pv.caget();
			self.pv.clearup();
		return result;

#####################################################################################
#
#The Class is for creating a simple object to access EPICS button
#
#Parameters:
#	strButtonPV: EPICS Button PV in String
#
#####################################################################################
class EpicsButtonClass(EpicsPvClass):
	def __init__(self, strButtonPV):
		EpicsPvClass.__init__(self, strButtonPV);

	def press(self):
		self.caput(1);


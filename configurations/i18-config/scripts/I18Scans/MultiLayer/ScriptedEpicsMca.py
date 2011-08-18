from gda.epics import CAClient 
#
#
# A simple mca interface created for multilayer testing
#  17-11-07
#
class ScriptedEpicsMca:
	# pass an mca root name
	def __init__(self, mca_rootname_string):

		self.dwelltime_ca=CAClient(mca_rootname_string+'.DWEL')
		
		if not self.dwelltime_ca.isConfigured():
			self.dwelltime_ca.configure()

		self.noOfChannels_ca=CAClient(mca_rootname_string+'.NUSE')

		if not self.noOfChannels_ca.isConfigured():
			self.noOfChannels_ca.configure()

		self.roiLow_ca=CAClient(mca_rootname_string+'.R0LO')

		if not self.roiLow_ca.isConfigured():
			self.roiLow_ca.configure()

		self.roiHigh_ca=CAClient(mca_rootname_string+'.R0HI')
		if not self.roiHigh_ca.isConfigured():
			self.roiHigh_ca.configure()

		self.roiValue_ca=CAClient(mca_rootname_string+'.R0')
		if not self.roiValue_ca.isConfigured():
			self.roiValue_ca.configure()

		self.eraseAndStart_ca=CAClient(mca_rootname_string.replace('MCA','MCAEraseStart'))
		if not self.eraseAndStart_ca.isConfigured():
			self.eraseAndStart_ca.configure()



	def setCollectionTime(self,collectionTime):
		self.dwelltime_ca.caput(0.0)
		timestep = float(self.dwelltime_ca.caget())
		# Calculate how many channels we need to use in order to count for the
		# requested time.
		print timestep, self.dwelltime_ca.caget(),collectionTime
		channelsToCount = Math.round((collectionTime / 1000.0) / timestep)
		# Set the number of channels to count for.
		self.noOfChannels_ca.caput(channelsToCount)
		self.roiLow_ca.caput(0)
		self.roiHigh_ca.caput(channelsToCount-1)


	def readout(self):
		return float(self.roiValue_ca.caget())

	def eraseAndStart(self):
		self.eraseAndStart_ca.caput(1)

	def getDwellTime(self):
		return float(self.dwelltime_ca.caget())

	def getNoOfChannels(self):
		return int(self.noOfChannels_ca.caget())


	def closeAll(self):
		self.dwelltime_ca.clearup()
		self.noOfChannels_ca.clearup()
		self.roiLow_ca.clearup()
		self.roiHigh_ca.clearup()
		self.roiValue_ca.clearup()
		self.eraseAndStart_ca.clearup()


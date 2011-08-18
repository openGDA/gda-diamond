from gda.epics import CAClient 
#
#
# A simple mca interface created for multilayer testing
#  17-11-07
#
class ip330:
	# pass an mca root name
	def __init__(self, mca_rootname_string):

		self.scanmode=CAClient(mca_rootname_string+':ScanMode')
		
		if not self.scanmode.isConfigured():
			self.scanmode.configure()

	def closeAll(self):
		self.scanmode.clearup()


	def disable(self):
		self.scanmode.caput(0)
				
	def setBurstCont(self):
		self.scanmode.caput(3)

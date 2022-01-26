from gda.device.scannable import ScannableMotionBase
from time import ctime
import time
class MetadataCollector(ScannableMotionBase):
	"""
	>>>mds = MetadataCollector("mds", globals(), [phi,chi,eta])  # make a small one
	>>>mdb = MetadataCollector("mdb", globals(), [enf,hkl,euler])  # make a big one
	>>>scan x 1 10 1 mds mdb
	
	
	"""
	def __init__(self, name, rootNamespace, scannablesToRead):
		"""Create a MetadataCollector Scannable, for use with an SRSDataWriter"""
		self.name = name
		self.inputNames = []
		self.extraNames = []
		self.outputFormat =[]
		
		self._rootNamespace = rootNamespace
		self.scannables_to_read = scannablesToRead
		self.verbose = False
###
	def isBusy(self):
		return False

	def asynchronousMoveTo(self,_):
		pass

	def getPosition(self):
		pass
###
	def atScanStart(self):
		"""Create or append metadata pairs to the SRSWriteAtFileCreation string
		in the rootNamespace dict. SRSWriteAtFileCreation will then be ready for
		the SRSScanWriter to write into the header when it is created after the
		first point of the scan has been completed.
		"""
		headerString = self._rootNamespace.get('SRSWriteAtFileCreation', '')
		headerString += ("\ndatestring='" + time.ctime() +"'\n") # append time
		headerString += self.getStringOfPositions() # append motor positions
	
	def atScanEnd(self):
		self._clearHeaderString()
		
	def atCommandFailure(self):
		self._clearHeaderString()
		
	def _clearHeaderString(self):
		self._rootNamespace['SRSWriteAtFileCreation'] = ''
		
	def getStringOfPositions(self):
		s=""
		for i in range(len(self.scannables_to_read)):
			if self.verbose:
				t=time.time()
				print self.name + " reading " + self.scannables_to_read[i].name
			p = self.scannables_to_read[i].getPosition()
			#print "p: ", p, " ", type(p)
			if (type(p)==type(1.0)):
				s += (self.scannables_to_read[i].getName().split(".")[-1] + "=" + str(p) + "\n")
			else:
				namelist = self.scannables_to_read[i].getInputNames()+ self.scannables_to_read[i].getExtraNames()
				for nm in range(len(namelist)):
					s += (namelist[nm] + "=" + str(p[nm]) + "\n")
			if self.verbose:
				print "  %f s" % (time.time() - t)
		return s

from gda.device.scannable import ScannableMotionBase
from time import ctime
from gda.data.metadata import Metadata
from gda.data.metadata import GDAMetadataProvider
class MetaDataPD(ScannableMotionBase):
	'''Metadta writer.
	Usage:
	>>>run "MetaDataPD"
	>>>
	>>>mds = MetaDataPD("mds", [phi,chi,eta])  # make a small one
	>>>mdb = MetaDataPD("mdb", [enf,hkl,euler])  # make a big one
	>>>scan x 1 10 1 mds mdb
	'''
	def __init__(self, name, scannablesToRead):
		self.setName(name)
		self.scannablesToRead = scannablesToRead
		self.setInputNames([])
		self.setExtraNames([])
		self.setOutputFormat([])
		self.metadata = GDAMetadataProvider.getInstance(0);


	def atScanStart(self):
		# The gda does not create the datafile until it recors the first datapoint
		# At this time it looks for a variable named SRSWriteAtFileCreation in the
		# jython namespace, assumes its a string and writes into the header.
		# The PD then populates this at the start of the scan.
		
		# This needed to access the variable in the root namespace
		global SRSWriteAtFileCreation
		
		# Create String if need be
		try:
			SRSWriteAtFileCreation += ""
		except:
			SRSWriteAtFileCreation = ""
		
		#Example to add the time

		SRSWriteAtFileCreation += ("\ndatestring='" + ctime() +"'\n")
		
		#Example to add a list of motor positions
		SRSWriteAtFileCreation += self.getStringOfPositions()
	
	def atScanEnd(self):
		# clear the string at end of scan
		SRSWriteAtFileCreation = ""	
	
	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,new_position):
		pass

	def getPosition(self):
		pass
	
	def setScannablesToRead(self,scannableList):
		self.scannablesToRead = scannableList
		
	def getStringOfPositions(self):
		toReturn=""
		toReturn = "Scan Command="+self.metadata.getMetadataValue("gda_command")+"\n" 
		for i in range(len(self.scannablesToRead)):
			p = self.scannablesToRead[i].getPosition()
			#print "p: ", p, " ", type(p)
			if (type(p)==type(1.0)):
				toReturn += (self.scannablesToRead[i].getName().split(".")[-1] + "=" + str(p) + "\n")
			else:
				namelist = self.scannablesToRead[i].getInputNames()+ self.scannablesToRead[i].getExtraNames()
				for nm in range(len(namelist)):
					toReturn += (namelist[nm] + "=" + str(p[nm]) + "\n")
		return toReturn

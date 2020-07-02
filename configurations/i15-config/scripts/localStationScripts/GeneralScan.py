from gda.factory import Finder
from gda.scan import ScanBase
import java
import java.lang.NullPointerException
from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import *
			
class GeneralScan(ScanBase):

	def __init__(self,arguments):
		from gda.jython import Jython
		self.arguments = arguments
		self.dataHandler = None
		self.myserver= Finder.findSingleton(Jython)
	    
	def moveTo(self,name,position):
		try:
			mymoveable = self.myserver.getFromJythonNamespace(name)
		except NullPointerException:
			print "Not a valid name"
			if(isinstance(mymoveable,Scannable)):
				mymoveable.moveTo(position)
			else:
				print "This is not Scannable" + name
    
	def moveBy(self,name,amount):
		mymoveable = self.myserver.getFromJythonNamespace("name")
		mymoveable.moveBy(amount)

	def detectorSetup(self):
		print "Setup Detector"

	def detectorCollect(self):
		print "Collecting from Detector"
	
	def detectorEnd(self):
		print "Cleaning up Detector"

	def setupDataHandler(self):
		if self.dataHandler is None:
			# dataHandler isn't defined so created it
			dataHandlerTypeName = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
			if (dataHandlerTypeName==None):
				print "Cannot find a  data writer : Using DiamondDataWriter"
				self.dataHandler = DiamondDataWriter()
			else:
				dataHandlerTypeName = "gda.data.scan.datawriter." + dataHandlerTypeName
				dataHandlerType = java.lang.Class.forName(dataHandlerTypeName)
				self.dataHandler =  dataHandlerType.newInstance()

	def setupScan(self):
		print "Setup Scan"
		self.setupDataHandler()
		self.detectorSetup()

	def endScan(self):
		print "End of Scan"

	def userScan(self):
		print "User Scan"

	def scan(self):
		self.setupScan()
		self.userScan()
		self.endScan()	
		
	def checkIsScannable(self,name):
		try:
			mymoveable = self.myserver.getFromJythonNamespace(name)
		except  NullPointerException:
			print "Not a valid name"
#		if (!isinstance(mymoveable,Scannable)):
#			raise ValueError, 'Not a scannable name'
                		
		
		

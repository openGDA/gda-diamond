from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider
from gda.configuration.properties import LocalProperties

"""
This is a scannable intended to be added as a default scannable with
the purpose of aborting the scan if a specific datawriter is not enabled
when a scan is run that includes a specific detector

For example the NexusXmap requires the NexusDataWriter otherwise the
full spectrum data is not recorded.
"""
class CheckDataWriter(ScannableBase):

	def __init__(self, name, detectorName, datawriter):
		self.name = name

		"""Name of detector object to be checked if present in a scan"""
		self.detectorToMonitor = detectorName

		"""The data writer required to be enabled e.g. NexusDataWriter"""
		self.datawriter = datawriter

		self.setOutputFormat({})
		self.setInputNames({})

	def getDetectorNames(self):
		scanController = InterfaceProvider.getCurrentScanInformationHolder()
		return scanController.getCurrentScanInformation().getDetectorNames()

	def scanIncludesDetector(self):
		scannableNames = self.getDetectorNames()
		if self.detectorToMonitor in scannableNames:
			return True
		return False

	def getDataWriter(self):
		return LocalProperties.get("gda.data.scan.datawriter.dataFormat")

	def atScanStart(self) :
		if self.scanIncludesDetector() and self.getDataWriter() != self.datawriter:
			print("--- Warning the datawriter for {} is expected to be {} ---").format(self.detectorToMonitor, self.datawriter)
			txtInput = raw_input("Would you like continue the scan? (y/n)")
			if txtInput not in ['Y', 'y']:
				raise TypeError("Scan aborted on request by CheckDataWriter class")

	def isBusy(self):
		return False

	def rawAsynchronousMoveTo(self, position):
		pass

	def rawGetPosition(self):
		return None

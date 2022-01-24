from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider
from gda.factory import Finder

"""
This is a scannable intended to be added metadata for the purpose
of recording the external h5 datafile path as dat file metadata.
"""
class ExcaliburExtFileMeta(ScannableBase):

	def __init__(self, name, exc_name, detectors):
		self.name = name

		"""List of detector names to be checked if present in a scan"""
		self.detectors = detectors

		self.setInputNames({})
		self.setOutputFormat(["%s"])
		self.setExtraNames(["exc_path"])
		
		self.excalibur = Finder.find(exc_name)

	def getScanDetectorNames(self):
		scanController = InterfaceProvider.getCurrentScanInformationHolder()
		info = scanController.getCurrentScanInformation()
		if info is not None:
			return info.getDetectorNames()
		return []

	def scanIncludesDetectorOfInterest(self):
		detectorsInScan = self.getScanDetectorNames()
		return any(det in detectorsInScan for det in self.detectors)


	def isBusy(self):
		return False

	def rawAsynchronousMoveTo(self, position):
		pass

	def getPosition(self):
		# This relies on the fact that detector prepareForCollection is
		# called before scannable atScanStart for concurrent scans
		if self.scanIncludesDetectorOfInterest():
			return self.excalibur.getController().getLatestFilename()
		else:
			return "N/A"


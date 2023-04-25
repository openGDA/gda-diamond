from gda.device.scannable.scannablegroup import ScannableGroup
from gda.device.scannable import TwoDScanPlotter
from uk.ac.diamond.daq.server.rcpcontroller import RCPControllerImpl

class FluorescenceROIPlotter(ScannableGroup):
	"""
	Creates a TwoDScanPlotter for each ROI configured on the detector.
	"""
	def __init__(self, name, detector, roi_column_prefix=""):
		self.name = name
		self.detector = detector
		self.roi_column_prefix = roi_column_prefix
		
	def atScanStart(self):
		"""
		We reconfigure the group members based on detector parameters
		at the start of the scan.
		
		Previous group members will be garbage-collected 
		"""
		self.setConfigured(False)
		
		params = self.detector.getConfigurationParameters()
		rois = params.getDetector(0).getRegionList()
		
		children = [self._create_plotter(roi.getRoiName()) for roi in rois]
		
		self.setGroupMembersWithArray(children)
		self.configure()
		
		ScannableGroup.atScanStart(self)

	def _create_plotter(self, childName):
		return TwoDScanPlotter(name=childName,
							   plotViewname=childName,
							   z_colName=self.roi_column_prefix + childName)

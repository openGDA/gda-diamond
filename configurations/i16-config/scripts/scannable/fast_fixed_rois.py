from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableBase
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI, RectangularROIList
import pd_offset
from org.slf4j import LoggerFactory
from uk.ac.diamond.scisoft.analysis import SDAPlotter
from uk.ac.diamond.scisoft.analysis.plotserver import GuiParameters

class FixedRoiScannable(ScannableBase) :
	"""Allows regions of interest conforming to the old method of working (i.e. used as scannables) to be used with the
	   new nexus writing detectors.  When added to a scan command this will wait until the detector has taken the image
	   and then read it from the array pv.  This will be sliced to the region specified and the total will be returned.
	"""

	roi_logger = LoggerFactory.getLogger("FastFixedRoiScannable")
	defined_rois = {}
	def __init__(self, name, nxdetector_roi_holder, detname, roi_number, panel_name_rcp, xPos, yPos, width, height):
		self.setLevel(100)
		self.setName(name)
		self.setInputNames([name + "_max", name + "_sum"])
		self.setOutputFormat(["%4.4f","%4.4f"])
		self.panel = panel_name_rcp
		self.roi_number = roi_number
		self.nxdetector_roi_holder = nxdetector_roi_holder
		self.roi_plugin = nxdetector_roi_holder.getPluginMap().get(detname + "_roistats_holder_roi_" + str(roi_number))
		self.stats_plugin = nxdetector_roi_holder.getPluginMap().get(detname + "_roistats_holder_stats_" + str(roi_number))
		self.set_dimensions(xPos, yPos, width, height)
		if (panel_name_rcp not in FixedRoiScannable.defined_rois.keys()):
			FixedRoiScannable.defined_rois[panel_name_rcp] = {}
		FixedRoiScannable.defined_rois[panel_name_rcp][name] = self

	def set_dimensions(self, xPos, yPos, width, height):
		self.roi_plugin.prepareForCollection(1,None)
		self.roi_plugin.getRoi().setXstart(xPos)
		self.roi_plugin.getRoi().setXsize(width)
		self.roi_plugin.getRoi().setYstart(yPos)
		self.roi_plugin.getRoi().setYsize(height)
		dimensions = "X " +str(xPos) +" to " +str(xPos + width) +", Y " +str(yPos) +" to " +str(yPos + height)
		self.description = "Region " +self.getName() +": " +dimensions
		self.set_visible_roi(xPos, yPos, width, height)

	def atScanStart(self):
		scaninfo = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation()
		self.roi_plugin.prepareForCollection(1,scaninfo)
		self.stats_plugin.prepareForCollection(1,scaninfo)

	def getPosition(self):
		return [self.stats_plugin.getNdStats().getMaxValue_RBV(),self.stats_plugin.getNdStats().getTotal_RBV()]

	def isBusy(self):
		return False

	def show(self):
		update_ui()
		print(self.description)

	def set_visible_roi(self, xPos, yPos, width, height):
		self.rect_roi = RectangularROI(xPos, yPos, width, height, 0)
		self.rect_roi.setName(self.getName())
		self.rect_roi.setPlot(False)
		self.rect_roi.setFixed(True)

def update_ui():
	for panel in FixedRoiScannable.defined_rois.keys() :
		gui_bean = SDAPlotter.getGuiBean(panel)
		roi_list = RectangularROIList()
		for region in FixedRoiScannable.defined_rois[panel].values() :
			roi_list.append(region.rect_roi)
		gui_bean.put(GuiParameters.ROIDATALIST, roi_list);
		SDAPlotter.setGuiBean(panel, gui_bean)

def create_new_roi(name, plot_name, xPos, yPos, width, height):
	'''Creates a new roi for one of the nexus detectors.  Parameters:
		name: a unique name for the roi
		plot_name: either "Merlin" or "Pilatus"
		xPos, yPos: x (left to right) and y (up/down) coordinates of the top left corner of the new roi
		width, height: self explanatory
	'''
	from gdaserver import pil3_roistats_holder, merlin_roistats_holder
	if plot_name == "Merlin":
		statsholder = merlin_roistats_holder
		detname = "merlin"
	elif plot_name == "Pilatus" :
		statsholder = pil3_roistats_holder
		detname = "pil3"
	else :
		raise ValueError("Fixed ROIs only compatible with Merlin and Pilatus detectors.")

	to_return = FixedRoiScannable(name, statsholder, detname, find_first_unused_roi_number(plot_name), plot_name, xPos, yPos, width, height)
	update_ui()
	return to_return

def find_first_unused_roi_number(plot_name):
	new_roi_number = None
	for i in range(1, 7):
		if get_roi_with_number(i, plot_name) is None :
			new_roi_number = i
			break
	if new_roi_number == None :
		raise ValueError("Limit of 6 ROIs for each detector due to EPICS limitations, please move an existing one instead.")
	return new_roi_number

def get_roi_with_number(number, plot_name):
	if (plot_name not in FixedRoiScannable.defined_rois.keys()):
		return None
	existing_rois = FixedRoiScannable.defined_rois[plot_name].values()
	for numbered_roi in existing_rois :
		if number == numbered_roi.roi_number :
			return numbered_roi
	return None

def remove_roi(roi_to_remove, plot_name):
	'''
	Removes the given roi, or the roi with the given name if it is a string, from the given plot ("Pilatus" or "Merlin")
	'''
	if roi_to_remove in FixedRoiScannable.defined_rois[plot_name].keys() :
		FixedRoiScannable.defined_rois[plot_name].pop(roi_to_remove)
	elif roi_to_remove in FixedRoiScannable.defined_rois[plot_name].values() :
		FixedRoiScannable.defined_rois[plot_name].pop(roi_to_remove.getName())
	else :
		print("Could not find region to remove, please give the region or the name of the region.")
	update_ui()

FixedRoiScannable.defined_rois.clear()

merlin_centre_i = pd_offset.Offset('merlin_centre_i')()
merlin_centre_j = pd_offset.Offset('merlin_centre_j')()
mroi1 = create_new_roi("mroi1", "Merlin", int(merlin_centre_i - 15), int(merlin_centre_j - 15), 30, 30)
mroi2 = create_new_roi("mroi2", "Merlin", int(merlin_centre_i - 121), int(merlin_centre_j - 121), 242, 242)

ci = pd_offset.Offset('pil3_centre_i')()
cj = pd_offset.Offset('pil3_centre_j')()
iw=13; jw=15; roi1 = create_new_roi("roi1", "Pilatus", int(ci-iw/2.), int(cj-jw/2.), iw, jw)
iw=50; jw=50; roi2 = create_new_roi("roi2", "Pilatus", int(ci-iw/2.), int(cj-jw/2.), iw, jw)
iw=1; jw=maxj=194; roi3 = create_new_roi("roi3", "Pilatus", int(ci-iw/2.), 0, iw, jw)
iw=maxi=486; jw=1; roi4 = create_new_roi("roi4", "Pilatus", 0, int(cj-jw/2.), iw, jw)

update_ui()
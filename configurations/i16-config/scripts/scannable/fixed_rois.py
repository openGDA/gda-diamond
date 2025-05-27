from gda.device.detector.nexusprocessor.roistats import RegionOfInterest
from gda.device.scannable import ScannableBase
from gda.observable import Observer
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI, RectangularROIList
from org.eclipse.january.dataset import LongDataset, DatasetFactory
import pd_offset
from org.slf4j import LoggerFactory
from uk.ac.diamond.scisoft.analysis import SDAPlotter
from uk.ac.diamond.scisoft.analysis.plotserver import GuiParameters

class ArrayCounterObserver(Observer):

    def __init__(self, nd_array, ad_base, expected_pix):
        self.nd_array = nd_array
        self.ad_base = ad_base
        self.ready_to_read = False
        self.expected_pix = expected_pix

    def update(self, source, arg):
        if self.ad_base.getAcquire_RBV() == "0" :
            self.readout = self.nd_array.getImageData(self.expected_pix)
            self.ready_to_read = True
        else :
            self.readout = None
            self.ready_to_read = False

class FixedRoiScannable(ScannableBase) :
    """Allows regions of interest conforming to the old method of working (i.e. used as scannables) to be used with the
       new nexus writing detectors.  When added to a scan command this will wait until the detector has taken the image
       and then read it from the array pv.  This will be sliced to the region specified and the total will be returned.
    """

    roi_logger = LoggerFactory.getLogger("FixedRoiScannable")
    observers = {}
    defined_rois = {}

    def __init__(self, name, nd_array, ad_base, panel_name_rcp, xPos, yPos, width, height) :
        self.setName(name)
        self.setInputNames([name + "_max", name + "_sum"])
        self.setOutputFormat(["%4.4f","%4.4f"])
        self.nd_array = nd_array
        if ad_base not in FixedRoiScannable.observers :
            new_observable = ad_base.createAcquireStateObservable()
            new_observer = ArrayCounterObserver(nd_array, ad_base, nd_array.getPluginBase().getArraySize1_RBV() * nd_array.getPluginBase().getArraySize0_RBV())
            FixedRoiScannable.observers[ad_base] = (new_observable, new_observer)
            new_observable.addObserver(new_observer)
        self.observable = FixedRoiScannable.observers[ad_base][0]
        self.observer = FixedRoiScannable.observers[ad_base][1]
        self.panel = panel_name_rcp
        self.set_dimensions(xPos, yPos, width, height)
        self.setLevel(100)
        dimensions = "X " +str(xPos) +" to " +str(xPos + width) +", Y " +str(yPos) +" to " +str(yPos + height)
        self.description = "Region " +self.getName() +": " +dimensions
        FixedRoiScannable.defined_rois[name] = self

    def atPointStart(self):
        self.observer.readout = None
        self.observer.ready_to_read = False

    def getPosition(self) :
        if self.observer.readout == None :
            return [-1, -1]
        fullDataset = DatasetFactory.createFromObject(LongDataset, self.observer.readout, self.nd_array.getPluginBase().getArraySize1_RBV(), self.nd_array.getPluginBase().getArraySize0_RBV())
        roiDataset = fullDataset.getSliceView(self.roi.getSlice())
        return [roiDataset.max(), roiDataset.sum()]

    def isBusy(self) :
        return not self.observer.ready_to_read

    def show(self):
        update_ui()
        print(self.description)

    def set_dimensions(self, xPos, yPos, width, height):
        self.rect_roi = RectangularROI(xPos, yPos, width, height, 0)
        self.rect_roi.setName(self.getName())
        self.rect_roi.setPlot(False)
        self.rect_roi.setFixed(True)
        self.roi = RegionOfInterest(self.rect_roi);

def update_ui():
    rois_by_panel = {}
    for roi_to_add in FixedRoiScannable.defined_rois.values() :
        if roi_to_add.panel not in rois_by_panel :
            rois_by_panel[roi_to_add.panel] = []
        rois_by_panel[roi_to_add.panel].append(roi_to_add.rect_roi)

    for panel in rois_by_panel.keys() :
        gui_bean = SDAPlotter.getGuiBean(panel)
        roi_list = RectangularROIList()
        for rect_roi in rois_by_panel[panel] :
            roi_list.append(rect_roi)
        gui_bean.put(GuiParameters.ROIDATALIST, roi_list);
        SDAPlotter.setGuiBean(panel, gui_bean)

def create_new_roi(name, detector, plot_name, xPos, yPos, width, height):
    '''Creates a new roi for one of the nexus detectors.  Parameters:
        name: a unique name for the roi
        detector: either merlin or pil
        plot_name: either "Merlin" or "Pilatus"
        xPos, yPos: x (left to right) and y (up/down) coordinates of the top left corner of the new roi
        width, height: self explanatory
    '''
    if not (detector == merlin or detector == pil3_100k):
        raise ValueError("Fixed rois only compatible with Merlin and Pilatus detectors.")
    adbase = detector.getDetector().getCollectionStrategy().getAdBase()
    ndarray = detector.getDetector().getPluginMap().get("array").getNdArray()
    to_return = FixedRoiScannable(name, ndarray, adbase, plot_name, xPos, yPos, width, height)
    update_ui()
    return to_return

def remove_roi(roi_to_remove):
    '''
    Removes the given roi or the roi with the given name if it is a string
    '''
    if roi_to_remove in FixedRoiScannable.defined_rois.keys() :
        FixedRoiScannable.defined_rois.pop(roi_to_remove)
    if roi_to_remove in FixedRoiScannable.defined_rois.values() :
        FixedRoiScannable.defined_rois.pop(roi_to_remove.getName())
    update_ui()

for entry in FixedRoiScannable.observers.values() :
    entry[0].removeObserver(entry[1])
FixedRoiScannable.observers.clear()
FixedRoiScannable.defined_rois.clear()
from gdaserver import merlin, pil3_100k

merlin_adbase = merlin.getDetector().getCollectionStrategy().getAdBase()
merlin_ndarray = merlin.getDetector().getPluginMap().get("array").getNdArray()
merlin_centre_i = pd_offset.Offset('merlin_centre_i')()
merlin_centre_j = pd_offset.Offset('merlin_centre_j')()
mroi1 = FixedRoiScannable("mroi1", merlin_ndarray, merlin_adbase, "Merlin", int(merlin_centre_i - 15), int(merlin_centre_j - 15), 30, 30)
mroi2 = FixedRoiScannable("mroi2", merlin_ndarray, merlin_adbase, "Merlin", int(merlin_centre_i - 121), int(merlin_centre_j - 121), 242, 242)

pilatus3_adbase = pil3_100k.getDetector().getCollectionStrategy().getAdBase()
pilatus3_ndarray = pil3_100k.getDetector().getPluginMap().get("array").getNdArray()
ci = pd_offset.Offset('pil3_centre_i')()
cj = pd_offset.Offset('pil3_centre_j')()
iw=13; jw=15; roi1 = FixedRoiScannable("roi1", pilatus3_ndarray, pilatus3_adbase, "Pilatus", int(ci-iw/2.), int(cj-jw/2.), iw, jw)
iw=50; jw=50; roi2 = FixedRoiScannable("roi2", pilatus3_ndarray, pilatus3_adbase, "Pilatus", int(ci-iw/2.), int(cj-jw/2.), iw, jw)
iw=1; jw=maxj=194; roi3 = FixedRoiScannable("roi3", pilatus3_ndarray, pilatus3_adbase, "Pilatus", int(ci-iw/2.), 0, iw, jw)
iw=maxi=486; jw=1; roi4 = FixedRoiScannable("roi4", pilatus3_ndarray, pilatus3_adbase, "Pilatus", 0, int(cj-jw/2.), iw, jw)

update_ui()

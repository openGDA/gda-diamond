from gda.device import Scannable
from gda.device.scannable import PseudoDevice
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI
from uk.ac.diamond.scisoft.analysis import SDAPlotter
from uk.ac.diamond.scisoft.analysis.plotserver import GuiParameters

class ADRegionTracker(PseudoDevice):
    def __init__(self, name, det, plot):
        self.name = name
        self.det_name = det.name if isinstance(det, Scannable) else str(det)
        self.plot_name = plot

    def setExtraNames(self, extra_names):
        raise TypeError("Extra names are readonly")

    def setOutputFormat(self, output_format):
        raise TypeError("Output format is readonly")

    def setInputNames(self, input_names):
        raise TypeError("Input names are readonly")

    def getInputNames(self):
        return []

    def get_roi_data(self):
        guibean = SDAPlotter.getGuiBean(self.plot_name)
        rois = guibean[GuiParameters.ROIDATALIST]
        if rois is None:
            return []
        else:
            rois = list(rois)
        rois.sort(key = lambda roi: roi.name)
        return [{"x_start":_r.pointX, "y_start":_r.pointY,
            "x_size":_r.lengths[0], "y_size":_r.lengths[1],
            "name":_r.name} for _r in rois if isinstance(_r, RectangularROI)]


    def getExtraNames(self):
        extra_names = []
        for _r in self.get_roi_data():
            r_name = self.det_name + " " + _r["name"]
            extra_names += [r_name + " x start", r_name + " y start",
                    r_name + " x size", r_name + " y size"]
        return extra_names

    def getOutputFormat(self):
        rois = self.get_roi_data()
        return ["%d", "%d", "%d", "%d"] * len(rois)


    def getPosition(self):
        _p = []
        for _r in self.get_roi_data():
            _p += [_r["x_start"], _r["y_start"], _r["x_size"], _r["y_size"]]
        return _p

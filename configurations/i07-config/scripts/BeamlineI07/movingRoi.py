import math
import scisoftpy as dnp

from gda.device.scannable import ScannableBase
from uk.ac.diamond.scisoft.analysis import SDAPlotter
from uk.ac.diamond.scisoft.analysis.plotserver import GuiParameters
from org.eclipse.january.dataset import Dataset
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI, RectangularROIList


class DetectorInfo:
    def __init__(self, pixel_size=1.72e-04, pixel_length_x=1474, pixel_length_y=1679):
        self.pixel_size=pixel_size
        self.pixel_length_x = pixel_length_x
        self.pixel_length_y = pixel_length_y
        width = pixel_length_x * pixel_size
        height = pixel_length_y * pixel_size

DETECTOR_INFO = {
        'pilatus2' : DetectorInfo(pixel_size=1.72e-04, pixel_length_x=1474, pixel_length_y=1679),
        'pilatus1' : DetectorInfo(pixel_size=1.72e-04, pixel_length_x=487, pixel_length_y=195)
        }

DETECTOR_INFO['pil2'] = DETECTOR_INFO['pilatus2']
DETECTOR_INFO['pil1'] = DETECTOR_INFO['pilatus1']
DETECTOR_INFO['pil'] = DETECTOR_INFO['pilatus1']
DETECTOR_INFO['pil2roi'] = DETECTOR_INFO["pilatus2"]
DETECTOR_INFO['pil1roi'] = DETECTOR_INFO['pilatus1']
DETECTOR_INFO["fastpil1"] = DETECTOR_INFO["pilatus1"]
DETECTOR_INFO["fastpil2"] = DETECTOR_INFO["pilatus2"]

class MovingRoiPlottingManager:
    """
    Centralise the logic for moving regions on the plot view, otherwise
    multiple moving regions fight for it and only one appears to move during
    a scan
    """
    def __init__(self, panel_name):
        self.panel_name = panel_name
        self.mrois = set()
        self.mroi_positions = {}

    def startNewScan(self):
        self.mrois.clear()
        self.mroi_positions.clear()

    def endOfScan(self):
        self.mrois.clear()
        self.mroi_positions.clear()

    def registerMRoi(self, mroi):
        self.mrois.add(mroi)

    def moveMroi(self, mroi):
        self.mroi_positions[mroi.name] = (mroi.x_start, mroi.y_start,
                mroi.x_size, mroi.y_size)
        self.mrois.discard(mroi)
        if len(self.mrois) == 0:
            self.updatePlot(self.mroi_positions)
            self.mroi_positions.clear()

    def updatePlot(self, updated_rois):
        guibean = SDAPlotter.getGuiBean(self.panel_name)
        rois = guibean[GuiParameters.ROIDATALIST]
        if rois is None: rois = RectangularROIList()
        new_rois = [_r for _r in rois if _r.name not in updated_rois.keys()]
        for rname, (x_start, y_start, x_size, y_size) in updated_rois.items():
            roi = RectangularROI(x_start, y_start, x_size, y_size, 0)
            roi.name = rname
            roi.plot = True
            new_rois.append(roi)
        rois.clear()
        rois.addAll(new_rois)
        guibean[GuiParameters.ROIDATALIST] = rois
        guibean[GuiParameters.ROIDATA] = None
        SDAPlotter.setGuiBean(self.panel_name, guibean)

MROI_PLOT_MANAGERS = {
        "Area Detector":MovingRoiPlottingManager("Area Detector"),
        "Pilatus 1 Array":MovingRoiPlottingManager("Pilatus 1 Array"),
        "Pilatus 2 Array":MovingRoiPlottingManager("Pilatus 2 Array"),
        "Pilatus 3 Array":MovingRoiPlottingManager("Pilatus 3 Array")
}

class MovingRoiDatasetProvider:
    def __init__(self, detector):
        self.detector = detector
        self.dataset = None
        self.fileName = None

    def getData(self):
        fileName = self.detector.readout()
        if self.dataset == None or fileName != self.fileName:
            ds = dnp.io.load(fileName)[0]._jdataset()
            self.dataset = ds
            self.fileName = fileName
        return self.dataset

PROVIDERS = {
        pil1 : MovingRoiDatasetProvider(pil1),
        pil1roi: MovingRoiDatasetProvider(pil1roi),
        pil2 : MovingRoiDatasetProvider(pil2),
        pil2roi : MovingRoiDatasetProvider(pil2roi)
        }

class MRoi(ScannableBase):
    def __init__(self, name, detector, processors=[],
            displacement_func=lambda:(0, 0),
            panel_name="Area Detector", data_provider=None):
        self.mroi_plot_manager = MROI_PLOT_MANAGERS[panel_name]
        self.name = name
        self.detector = detector
        self.detectorInfo = DETECTOR_INFO[detector.name]
        self.processors = processors
        self.inputNames = []
        extraNames = [
                name + "_x_start", name + "_y_start",
                name + "_x_size", name + "_y_size"]
        outputFormat = ["%d", "%d", "%d", "%d"]
        self.displacement_func = displacement_func
        self.datasetProvider = data_provider
        for p in self.processors:
            for l in p.labelList:
                extraNames.append(self.name + "_" + l)
                outputFormat.append("%f")
        self.extraNames = extraNames
        self.outputFormat = outputFormat
        self.panel_name = panel_name

    def setBeamCentre(self, x_centre, y_centre, x_size, y_size):
        self.x_beam_centre, self.y_beam_centre = x_centre, y_centre
        self.x_size, self.y_size = x_size, y_size
        self.configure()

    def configure(self):
        self.prevBeamPos = self.calcBeamRoi()

    def calcBeamRoi(self):
        dx, dy = self.displacement_func()
        dx /= self.detectorInfo.pixel_size
        dy /= self.detectorInfo.pixel_size
        return (self.x_beam_centre + dx, self.y_beam_centre + dy)

    def moveRois(self):
        new_pos = self.calcBeamRoi()
        dx, dy = new_pos[0] - self.prevBeamPos[0], new_pos[1] - self.prevBeamPos[1]
        # y = old_y - dy because detector is "upside down" - 0 is at the top
        self.setRoi(self.x_start + dx, self.y_start - dy,
                self.x_size, self.y_size)
        self.prevBeamPos = new_pos

    def setRoi(self, x_start, y_start, x_size, y_size):
        self.x_start = x_start
        self.y_start = y_start
        self.x_size = x_size
        self.y_size = y_size
        self.mroi_plot_manager.moveMroi(self)

    def loadDataset(self):
        #should cover more cases but I'm in a rush
        if self.datasetProvider != None:
            dataset = self.datasetProvider.getData()
        elif self.detector.createsOwnFiles():
            filename = self.detector.readout()
            dataholder = dnp.io.load(filename)
            dataset = dataholder[0]._jdataset()
        else:
            dataset = self.detector.readout()

        self.dataset = dataset
        return dataset

    def getPosition(self):
        self.moveRois()
        result = [int(self.x_start), int(self.y_start), int(self.x_size), int(self.y_size)]
        [x, y, w, h] = result
        if self.processors != None and len(self.processors) > 0:
            dataset = self.loadDataset()
            try:
                roiDataset = dnp.array(dataset)[y:y+h, x:x+w]
                for processor in self.processors:
                    twodResult = processor.process(roiDataset, 0, 0).resultsDict
                    for key in processor.labelList:
                        result.append(twodResult[key])
            except java.lang.ArrayIndexOutOfBoundsException:
                print "ERROR: Region is beyond dataset bounds - likely moved off the detector"
                raise ValueError("Region is outside of dataset bounds")
        return result

    def atScanStart(self):
        self.mroi_plot_manager.startNewScan()

    def atPointStart(self):
        self.mroi_plot_manager.registerMRoi(self)

    def atScanEnd(self):
        self.mroi_plot_manager.endOfScan()

class mroiDummyDevice:
    def getPosition(self):
        return 0

def createMroiLinear(name, x_start, x_size, y_start, y_size,
        distance, x_device=mroiDummyDevice(), y_device=mroiDummyDevice(), detector=pil2):
    f = lambda: (distance * math.tan(math.radians(x_device.getPosition())),
            distance * math.tan(math.radians(y_device.getPosition())))
    exec "_temp = MRoi(name, detector, [MinMaxSumMeanDeviationProcessor()],\
            displacement_func=f, data_provider=PROVIDERS[detector])" in globals(), locals()
    _temp.setBeamCentre(0, 0, 50, 50) #we really don't care about beam centre
    _temp.setRoi(x_start, y_start, x_size, y_size)
    return _temp

def createMroiLinear_fastpil(name, x_start, x_size, y_start, y_size,
        distance, x_device=mroiDummyDevice(), y_device=mroiDummyDevice(), detector=fastpil2):
    f = lambda: (distance * math.tan(math.radians(x_device.getPosition())),
            distance * math.tan(math.radians(y_device.getPosition())))
    exec "_temp = MRoi(name, detector, [], displacement_func=f, \
            data_provider=None, panel_name='Pilatus 2 Array')" in globals(), locals()
    _temp.setBeamCentre(0, 0, 50, 50) #we really don't care about beam centre
    _temp.setRoi(x_start, y_start, x_size, y_size)
    return _temp

def createMroiForDcd(name, x_start, x_size, y_start, y_size,
        beam_x, beam_y, distance, omega=dcdomega, lmbda=dcm1lambda, detector=pil2):
    def displacement_rel(omega, wavelength):
        d111 = 3.740652394
        d220 = 2.290672418
        omega = math.radians(omega)
        dth = math.asin(wavelength / (2*d220)) - math.asin(wavelength / (2*d111))
        alpha = math.asin( math.sin(omega) * math.sin(2*dth) )
        beta = math.asin( math.sin(math.pi/2 - omega) * math.sin(2*dth) )
        return (distance * math.tan(beta), distance * math.tan(alpha))
    def displacement(omega, wavelength):
        d_at_omega = displacement_rel(omega, wavelength)
        d_at_0 = displacement_rel(0, wavelength)
        return (d_at_omega[0] - d_at_0[0], d_at_omega[1] - d_at_0[1])
    f = lambda: displacement(omega.getPosition(), lmbda.getPosition())
    exec "_temp = MRoi(name, detector, [MinMaxSumMeanDeviationProcessor()],\
            displacement_func = f, data_provider=PROVIDERS[detector])" in globals(), locals()
    _temp.setBeamCentre(beam_x, beam_y, 50, 50)
    _temp.setRoi(x_start, y_start, x_size, y_size)
    return _temp

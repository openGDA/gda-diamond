import math
import scisoftpy as dnp

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


class DcdRoiDatasetProvider:
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

class DcdRoi(ScannableBase):
    def __init__(self, name, detector, processors=[], panel_name='Area Detector',
            omega_device=None, wavelength_device=None, provider=None):
        self.detector = detector
        self.panel_name = panel_name
        self.processors = processors
        self.name = name
        self.inputNames = []
        extraNames = [name + "_x_start", name + "_y_start", name + "_x_size", name + "_y_size"]
        outputFormat = ["%d", "%d", "%d", "%d"]
        self.omegaDevice = omega_device
        self.wavelengthDevice = wavelength_device
        self.distance = 3
        self.detectorInfo = DETECTOR_INFO[detector.name]
        self.level = detector.level + 1
        self.datasetProvider = provider
        for processor in self.processors:
            for label in processor.labelList:
                extraNames.append(self.name + '_' + label)
                outputFormat.append("%f")
        self.outputFormat = outputFormat
        self.extraNames = extraNames

    def loadDataset(self):
        #should cover more cases but I'm in a rush
        if self.datasetProvider != None:
            dataset = self.datasetProvider.getData()
        elif self.detector.createsOwnFiles():
            fileName = self.detector.readout()
            dataholder = dnp.io.load(fileName)
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
            roiDataset = dnp.array(dataset)[y:y+h, x:x+w]
            for processor in self.processors:
                twodResult = processor.process(roiDataset, 0, 0).resultsDict
                for key in processor.labelList:
                    result.append(twodResult[key])
        return result

    def setBeamCentre(self, x_centre, y_centre, x_size, y_size):
        self.x_beam_centre = x_centre
        self.y_beam_centre = y_centre
        self.configure()

    def configure(self):
        self.prevBeamPos = self.calcBeamRoi()

    def calcBeamRoi(self):
        displacement = self.calcDisplacement(self.omegaDevice.getPosition(), self.wavelengthDevice.getPosition())
        x_centre = self.x_beam_centre + displacement[0]
        y_centre = self.x_beam_centre + displacement[1]
        return (x_centre, y_centre)

    def calcDTheta(self, wavelength, d1, d2):
        theta1 = math.asin(wavelength / (2 * d1))
        theta2 = math.asin(wavelength / (2 * d2))
        return math.degrees(theta2 - theta1)

    def calcDisplacementFromBeam(self, _omeg, wavelength):
        d111 = 3.740652394
        d220 = 2.290672418
        _omeg = math.radians(_omeg)
        dth = self.calcDTheta(wavelength, d111, d220)
        dth = math.radians(dth)
        _alpha = math.asin( (math.sin(_omeg)) * (math.sin(2 * dth)) )
        _beta = math.asin( math.sin(math.pi / 2 - _omeg) * math.sin(2 * dth) )

        v_rel_direct = self.distance * math.tan(_alpha)
        h_rel_direct = self.distance * math.tan(_beta)
        return (h_rel_direct, v_rel_direct)

    def calcDisplacement(self, _omeg, wavelength):
        d_at_omega = self.calcDisplacementFromBeam(_omeg, wavelength)
        d_at_0 = self.calcDisplacementFromBeam(0, wavelength)
        dh = d_at_omega[0] - d_at_0[0]
        dv = d_at_omega[1] - d_at_0[1] #should be 0?
        return (dh / self.detectorInfo.pixel_size, dv / self.detectorInfo.pixel_size)

    def moveRois(self):
        newBeamPos = self.calcBeamRoi()
        (xdiff, ydiff) = newBeamPos[0] - self.prevBeamPos[0], newBeamPos[1] - self.prevBeamPos[1]
        self.setRoi( self.x_start + xdiff, self.y_start - ydiff, self.x_size, self.y_size )
        self.prevBeamPos = newBeamPos

    def setRoi(self, x_start, y_start, x_size, y_size):
        guibean = SDAPlotter.getGuiBean(self.panel_name)
        roiList = guibean[GuiParameters.ROIDATALIST]
        if roiList is None:
            roiList = RectangularROIList()
        toPlot = [_r for _r in roiList if _r.name != self.name]
        roi = RectangularROI(x_start, y_start, x_size, y_size, 0)
        roi.name = self.name
        toPlot.append(roi)
        roiList.clear()
        roiList.addAll(toPlot)
        guibean[GuiParameters.ROIDATALIST] = roiList
        SDAPlotter.setGuiBean(self.panel_name, guibean)
        self.x_start = x_start
        self.y_start = y_start
        self.x_size = x_size
        self.y_size = y_size


PROVIDERS = {
        pil1 : DcdRoiDatasetProvider(pil1),
        pil2 : DcdRoiDatasetProvider(pil2)
        }


def createMroiForDcd(name, x_start, x_size, y_start, y_size,
        beam_x, beam_y, distance, omegaDevice=dcdomega, lambdaDevice=dcm1lambda, detector=pil2):
    #exec to get past the "overriding scannable" check
    exec("_temp = DcdRoi(name, detector, [MinMaxSumMeanDeviationProcessor()],\
        omega_device=omegaDevice, wavelength_device=lambdaDevice, provider=PROVIDERS[detector])")
    _temp.setBeamCentre(beam_x, beam_y, 50, 50)
    _temp.distance = distance
    _temp.setRoi(x_start, y_start, x_size, y_size)
    return _temp



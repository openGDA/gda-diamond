from xml.etree.ElementTree import ElementTree as ET
from gda.data.scan.datawriter import DataWriterExtenderBase
from gda.device.detector import NexusDetector
from gda.factory import Finder
from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
from org.eclipse.dawnsci.nexus import NexusUtils
from org.eclipse.dawnsci.hdf5.nexus import NexusFileHDF5
import org.eclipse.january.dataset.DatasetFactory as DF
import org.eclipse.january.dataset.LinearAlgebra as LA
from org.eclipse.january.dataset import Dataset
from org.slf4j import LoggerFactory
import java
import sys, traceback
import math
import re

#Copied from Python documentation since Jython does have this yet (added to Python in 2.6)
def cartesian_product(*args, **kwds):
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [ x + [y] for x in result for y in pool ]
    for prod in result:
        yield tuple(prod)

SAMPLE_NAME = 'Default Sample'
NEXUS_TITLE = 'Scan of sample with GDA'

def sample(sampleName = None):
    global SAMPLE_NAME
    if not sampleName == None:
        SAMPLE_NAME = sampleName
    return SAMPLE_NAME

def title(title = None):
    global NEXUS_TITLE
    if not title == None:
        NEXUS_TITLE = title
    return NEXUS_TITLE

def set_diffcalc_instance(diffcalc):
    global DIFFCALC
    DIFFCALC = diffcalc

def use_cryo(cryo):
    global USE_CRYO_GEOMETRY
    USE_CRYO_GEOMETRY = cryo

RAD_TO_DEG = 180 / math.pi
EVOLT_TO_JOULE = 1.60217657e-19
PLANCK = 6.62606957e-34
LIGHTSPEED = 299792458.

CALIBRATION_SCAN_DEF = -1
CALIBRATION_TIME_DEF = "0000-01-01 00:00:00"


GDA_SCAN = 3L
NXMX = 6L
#This value does not fit in a signed 64bit integer (and Java is uncivilised and has no unsigned types)
#SAMPLE_GEOMETRY = 13907096678176980974
SAMPLE_GEOMETRY = -4539647395532570642L #signed representation

DATA_SIZE = "dataSize"
DATA_ORIGIN = "dataOrigin"
FAST_PIXEL_DIRECTION = "fastPixelDirection"
FAST_PIXEL_UNITS = "fastPixelUnits"
FAST_PIXEL_SIZE = "fastPixelSize"
FAST_PIXEL_OFFSET = "fastPixelOffset"
SLOW_PIXEL_DIRECTION = "slowPixelDirection"
SLOW_PIXEL_UNITS = "slowPixelUnits"
SLOW_PIXEL_SIZE = "slowPixelSize"
SLOW_PIXEL_OFFSET = "slowPixelOffset"
OFFSET = "offset"
OFFSET_OFFSET = "offsetOffset"
OFFSET_VECTOR = "offsetVector"
OFFSET_UNITS = "offsetUnits"

SENSOR_SATURATION_VALUE = "saturationValue"
SENSOR_MATERIAL = "sensorMaterial"
SENSOR_THICKNESS = "sensorThickness"
SENSOR_THICKNESS_UNITS = "sensorThicknessUnits"
SENSOR_TYPE = "sensorType"
SENSOR_DESCRIPTION = "sensorDescription"
CALIBRATION_SCAN = "calibrationScan"
CALIBRATION_TIME = "calibrationTime"

TRANSFORMATION_NAME = "transformationName"
TRANSFORMATION_TYPE = "transformationType"
TRANSFORMATION_VECTOR = "transformationVector"
TRANSFORMATION_OFFSET = "transformationOffset"
TRANSFORMATION_SIZE = "transformationSize"
TRANSFORMATION_UNITS = "transformationUnits"
TRANSFORMATION_OFFSET_UNITS = "transformationOffsetUnits"
TRANSFORMATION_ROTATION = "rotation"
TRANSFORMATION_TRANSLATION = "translation"

DETECTOR_TRANSFORMATIONS = {
        "pilatus1" : [
            {
                TRANSFORMATION_NAME : 'origin_offset',
                TRANSFORMATION_TYPE : TRANSFORMATION_TRANSLATION,
                TRANSFORMATION_VECTOR : [50.40, -17.96, 525.95],
                TRANSFORMATION_OFFSET : [0., 0., 0.],
                TRANSFORMATION_SIZE : [1.],
                TRANSFORMATION_UNITS : 'mm',
                TRANSFORMATION_OFFSET_UNITS : 'mm',
            },
        ],
        "simad" : [
            {
                TRANSFORMATION_NAME : 'origin_offset',
                TRANSFORMATION_TYPE : TRANSFORMATION_TRANSLATION,
                TRANSFORMATION_VECTOR : [50.40, -17.96, 525.95],
                TRANSFORMATION_OFFSET : [0., 0., 0.],
                TRANSFORMATION_SIZE : [1.],
                TRANSFORMATION_UNITS : 'mm',
                TRANSFORMATION_OFFSET_UNITS : 'mm',
            },
        ],
        "pilatus3" : [
            {
                TRANSFORMATION_NAME : 'origin_offset',
                TRANSFORMATION_TYPE : TRANSFORMATION_TRANSLATION,
                TRANSFORMATION_VECTOR : [0., 0., 0.],
                TRANSFORMATION_OFFSET : [0., 0., 0.],
                TRANSFORMATION_SIZE : [1.],
                TRANSFORMATION_UNITS : 'mm',
                TRANSFORMATION_OFFSET_UNITS : 'mm',
            },
        ]
    }


DETECTOR_MODULES = {
        "simad" : {
            DATA_ORIGIN : [0., 0.],
            DATA_SIZE : [300, 200],
            FAST_PIXEL_DIRECTION : [0.0, -0.70716, 0.70716],
            FAST_PIXEL_SIZE : [0.000200],
            FAST_PIXEL_OFFSET : [0., 0., 0.],
            FAST_PIXEL_UNITS : 'm',
            SLOW_PIXEL_DIRECTION : [1., 0., 0.],
            SLOW_PIXEL_SIZE : [0.000200],
            SLOW_PIXEL_OFFSET : [0., 0., 0.],
            SLOW_PIXEL_UNITS : 'm',
            OFFSET : [0.],
            OFFSET_VECTOR : [0., 0., 0.],
            OFFSET_OFFSET: [0., 0., 0.],
            OFFSET_UNITS : 'mm'
        },
        "pilatus1" : {
            DATA_ORIGIN : [0, 0],
            DATA_SIZE : [487, 195],
            FAST_PIXEL_DIRECTION : [0.7191, -0.01268, -0.6948],
            FAST_PIXEL_SIZE : [0.000172],
            FAST_PIXEL_OFFSET : [0., 0., 0.],
            FAST_PIXEL_UNITS : 'm',
            SLOW_PIXEL_DIRECTION : [0.01198, 0.9999, -0.005853],
            SLOW_PIXEL_SIZE : [0.000172],
            SLOW_PIXEL_UNITS : 'm',
            SLOW_PIXEL_OFFSET : [0., 0., 0.],
            OFFSET : [0.],
            OFFSET_VECTOR : [0., 0., 0.],
            OFFSET_OFFSET : [0., 0., 0.],
            OFFSET_UNITS : 'mm'
        },
        "pilatus3" : {
            DATA_ORIGIN : [0, 0],
            DATA_SIZE : [487, 195],
            FAST_PIXEL_DIRECTION : [0., 0., 0.],
            FAST_PIXEL_SIZE : [0.000172],
            FAST_PIXEL_OFFSET : [0., 0., 0.],
            FAST_PIXEL_UNITS : 'm',
            SLOW_PIXEL_DIRECTION : [0., 0., 0.],
            SLOW_PIXEL_SIZE : [0.000172],
            SLOW_PIXEL_UNITS : 'm',
            SLOW_PIXEL_OFFSET : [0., 0., 0.],
            OFFSET : [0.],
            OFFSET_VECTOR : [0., 0., 0.],
            OFFSET_OFFSET : [0., 0., 0.],
            OFFSET_UNITS : 'mm'
        },
    }

DETECTOR_PROPERTIES = {
        "simad" : {
            SENSOR_SATURATION_VALUE : [1000000],
            SENSOR_MATERIAL : "Silicon",
            SENSOR_THICKNESS : [320.],
            SENSOR_THICKNESS_UNITS : "micron",
            SENSOR_TYPE : "Pixel",
            SENSOR_DESCRIPTION : "Simulated Detector",
            CALIBRATION_TIME : CALIBRATION_TIME_DEF,
            CALIBRATION_SCAN : CALIBRATION_SCAN_DEF
        },
        "pilatus1" : {
            SENSOR_SATURATION_VALUE : [1000000],
            SENSOR_MATERIAL : "Silicon",
            SENSOR_THICKNESS : [0.32],
            SENSOR_THICKNESS_UNITS : "mm",
            SENSOR_TYPE : "Pixel",
            SENSOR_DESCRIPTION : "Pilatus 100k",
            CALIBRATION_TIME : CALIBRATION_TIME_DEF,
            CALIBRATION_SCAN : CALIBRATION_SCAN_DEF
        },
        "pilatus3" : {
            SENSOR_SATURATION_VALUE : [1000000],
            SENSOR_MATERIAL : "Silicon",
            SENSOR_THICKNESS : [0.32],
            SENSOR_THICKNESS_UNITS : "mm",
            SENSOR_TYPE : "Pixel",
            SENSOR_DESCRIPTION : "Pilatus 100k",
            CALIBRATION_TIME : CALIBRATION_TIME_DEF,
            CALIBRATION_SCAN : CALIBRATION_SCAN_DEF
        },
    }

import copy

DETECTOR_MODULES["simd"] = DETECTOR_MODULES["simad"]
DETECTOR_PROPERTIES["simd"] = DETECTOR_PROPERTIES["simad"]
DETECTOR_TRANSFORMATIONS["simd"] = DETECTOR_TRANSFORMATIONS["simad"]

DETECTOR_MODULES["pil100k"] = DETECTOR_MODULES["pilatus1"]
DETECTOR_PROPERTIES["pil100k"] = DETECTOR_PROPERTIES["pilatus1"]
DETECTOR_TRANSFORMATIONS["pil100k"] = DETECTOR_TRANSFORMATIONS['pilatus1']
DETECTOR_MODULES["pil100ks"] = DETECTOR_MODULES["pilatus1"]
DETECTOR_PROPERTIES["pil100ks"] = DETECTOR_PROPERTIES["pilatus1"]
DETECTOR_TRANSFORMATIONS["pil100ks"] = DETECTOR_TRANSFORMATIONS['pilatus1']

DETECTOR_MODULES["pil3_100k"] = DETECTOR_MODULES["pilatus3"]
DETECTOR_PROPERTIES["pil3_100k"] = DETECTOR_PROPERTIES["pilatus3"]
DETECTOR_TRANSFORMATIONS["pil3_100k"] = DETECTOR_TRANSFORMATIONS['pilatus3']
DETECTOR_MODULES["pil3_100ks"] = DETECTOR_MODULES["pilatus3"]
DETECTOR_PROPERTIES["pil3_100ks"] = DETECTOR_PROPERTIES["pilatus3"]
DETECTOR_TRANSFORMATIONS["pil3_100ks"] = DETECTOR_TRANSFORMATIONS['pilatus3']

DETECTOR_PROPERTIES["swmr"] = copy.deepcopy(DETECTOR_PROPERTIES["simad"])
DETECTOR_MODULES["swmr"] = copy.deepcopy(DETECTOR_MODULES["simad"])
DETECTOR_TRANSFORMATIONS["swmr"] = copy.deepcopy(DETECTOR_TRANSFORMATIONS["simad"])
DETECTOR_PROPERTIES["smd"] = DETECTOR_PROPERTIES["swmr"]
DETECTOR_MODULES["smd"] = DETECTOR_MODULES["swmr"]
DETECTOR_TRANSFORMATIONS["smd"] = DETECTOR_TRANSFORMATIONS["swmr"]


class I16NexusExtender(DataWriterExtenderBase):

    def __init__(self, geometry_file):
        DataWriterExtenderBase.__init__(self)
        self.logger = LoggerFactory.getLogger("I16NexusExtender")
        self.complete = True
        self.updateFromGeometry(geometry_file)

    def updateFromGeometry(self, geometry_file):
        geometryXml = ET()
        geometryXml.parse(geometry_file)
        for detXml in geometryXml.findall("detector"):
            self.updateStaticDetectorProperties(detXml)

    def updateStaticDetectorProperties(self, detXml):
        detName = detXml.attrib['name']
        DETECTOR_PROPERTIES[detName][CALIBRATION_SCAN] = int(detXml.find("scan").text)
        DETECTOR_PROPERTIES[detName][CALIBRATION_TIME] = detXml.find("time").text
        positionXml = detXml.find("position")
        position = [ float(_e.text) for _e in positionXml.findall("vector/element") ]
        size = float(positionXml.find("size").text)
        units = positionXml.find("units").text
        DETECTOR_TRANSFORMATIONS[detName][0][TRANSFORMATION_VECTOR] = position
        DETECTOR_TRANSFORMATIONS[detName][0][TRANSFORMATION_UNITS] = units
        for axisXml in detXml.findall("axis"):
            axisName = axisXml.attrib['name']
            elements = axisXml.findall("vector/element")
            vector = [ float(_e.text) for _e in elements ]
            size = float(axisXml.find("size").text)
            units = axisXml.find("units").text
            if axisName == "fast":
                DETECTOR_MODULES[detName][FAST_PIXEL_DIRECTION] = vector
                DETECTOR_MODULES[detName][FAST_PIXEL_SIZE] = [size]
                DETECTOR_MODULES[detName][FAST_PIXEL_UNITS] = units
            elif axisName == "slow":
                DETECTOR_MODULES[detName][SLOW_PIXEL_DIRECTION] = vector
                DETECTOR_MODULES[detName][SLOW_PIXEL_SIZE] = [size]
                DETECTOR_MODULES[detName][SLOW_PIXEL_UNITS] = units

    # DataWriterExtenderBase Interface

    def addData(self, dwParent, scanDataPoint):
        self.complete = False
        self.scanDataPoint = scanDataPoint
        self.scanFileName = scanDataPoint.getCurrentFilename()
        #The SrsDataFile in NexusDataWriter will set the filename to .dat - we need .nxs
        self.scanFileName = self.scanFileName[:-3] + "nxs"
        DataWriterExtenderBase.addData(self, dwParent, scanDataPoint)

    def writeTitle(self, nFile, group, title):
        self.logger.debug("writeTitle({}, {}, {})", nFile, group, title)
        data = DF.createFromObject(title)
        data.name = "title_old"
        nFile.createData(group, data)

    def writeDetectorModule(self, nFile, group, detName, dependsOn):
        self.logger.debug("writeDetectorModule({}, {}, {}, {})", nFile, group, detName, dependsOn)
        if not DETECTOR_MODULES.has_key(detName):
            self.logger.warn("DETECTOR_MODULES does not have key {} - NeXuS file may not be valid", detName)
            return
        detModule = DETECTOR_MODULES[detName]
        moduleDependsOn = "/entry1/instrument/%s/module/module_offset" % detName #would like to avoid this path here
        moduleGroup = nFile.getGroup(group, "module", "NXdetector_module", True)

        data = DF.createFromObject(detModule[DATA_ORIGIN])
        data.name = "data_origin"
        nFile.createData(moduleGroup, data)

        data = DF.createFromObject(detModule[DATA_SIZE])
        data.name = "data_size"
        nFile.createData(moduleGroup, data)

        data = DF.createFromObject(detModule[FAST_PIXEL_SIZE])
        data.name = "fast_pixel_direction"
        node = nFile.createData(moduleGroup, data)
        NexusUtils.writeAttribute(nFile, node, "depends_on", moduleDependsOn)
        NexusUtils.writeAttribute(nFile, node, "offset", detModule[FAST_PIXEL_OFFSET])
        NexusUtils.writeAttribute(nFile, node, "transformation_type", "translation")
        NexusUtils.writeAttribute(nFile, node, "units", detModule[FAST_PIXEL_UNITS])
        NexusUtils.writeAttribute(nFile, node, "vector", detModule[FAST_PIXEL_DIRECTION])

        data = DF.createFromObject(detModule[SLOW_PIXEL_SIZE])
        data.name = "slow_pixel_direction"
        node = nFile.createData(moduleGroup, data)
        NexusUtils.writeAttribute(nFile, node, "depends_on", moduleDependsOn)
        NexusUtils.writeAttribute(nFile, node, "offset", detModule[SLOW_PIXEL_OFFSET])
        NexusUtils.writeAttribute(nFile, node, "transformation_type", "translation")
        NexusUtils.writeAttribute(nFile, node, "units", detModule[SLOW_PIXEL_UNITS])
        NexusUtils.writeAttribute(nFile, node, "vector", detModule[SLOW_PIXEL_DIRECTION])

        data = DF.createFromObject(detModule[OFFSET])
        data.name = "module_offset"
        node = nFile.createData(moduleGroup, data)
        NexusUtils.writeAttribute(nFile, node, "depends_on", dependsOn)
        NexusUtils.writeAttribute(nFile, node, "offset", detModule[OFFSET_OFFSET])
        NexusUtils.writeAttribute(nFile, node, "transformation_type", "translation")
        NexusUtils.writeAttribute(nFile, node, "units", detModule[OFFSET_UNITS])
        NexusUtils.writeAttribute(nFile, node, "vector", detModule[OFFSET_VECTOR])

    def writeDetectorProperties(self, nFile, group, detName):
        self.logger.debug("writeDetectorProperties({}, {}, {})", nFile, group, detName)
        if not DETECTOR_PROPERTIES.has_key(detName):
            self.logger.warn("DETECTOR_PROPERTIES does not have key {} - NeXuS file may not be valid", detName)
            return
        properties = DETECTOR_PROPERTIES[detName]

        data = DF.createFromObject(properties[CALIBRATION_TIME])
        data.name = "calibration_date"
        nFile.createData(group, data)

        data = DF.createFromObject(properties[CALIBRATION_SCAN])
        data.name = "calibration_scan_number"
        nFile.createData(group, data)

        data = DF.createFromObject(properties[SENSOR_SATURATION_VALUE])
        data.name = "saturation_value"
        nFile.createData(group, data)

        data = DF.createFromObject(properties[SENSOR_MATERIAL])
        data.name = "sensor_material"
        nFile.createData(group, data)

        data = DF.createFromObject(properties[SENSOR_THICKNESS])
        data.name = "sensor_thickness"
        nFile.createData(group, data)

        detObject = Finder.find(detName)
        #some more stuff has to be added if the detector is a NexusDetector
        if detObject != None and isinstance(detObject, NexusDetector):
            data = DF.createFromObject(properties[SENSOR_DESCRIPTION])
            data.name = "description"
            nFile.createData(group, data)

            data = DF.createFromObject(properties[SENSOR_TYPE])
            data.name = "type"
            nFile.createData(group, data)

    def writeDetector(self, nFile, group, name, dependsOn):
        self.logger.debug("writeDetector({}, {}, {}, {})", nFile, group, name, dependsOn)
        if not DETECTOR_TRANSFORMATIONS.has_key(name):
            self.logger.warn("DETECTOR_TRANSFORMATIONS does not have key {} - NeXuS file may not be valid", name)
            return
        transGroup = nFile.getGroup(group, "transformations", "NXtransformations", True)
        for properties in DETECTOR_TRANSFORMATIONS[name]:
            #NexusFile.writeAttribute(nFile, transGroup, "NX_class", "NXtransformations")
            detTrans = DF.createFromObject(properties[TRANSFORMATION_SIZE])
            detTrans.name = properties[TRANSFORMATION_NAME]
            data = nFile.createData(transGroup, detTrans)
            NexusUtils.writeAttribute(nFile, data, "vector", properties[TRANSFORMATION_VECTOR])
            NexusUtils.writeAttribute(nFile, data, "offset", properties[TRANSFORMATION_OFFSET])
            NexusUtils.writeAttribute(nFile, data, "offset_units", properties[TRANSFORMATION_OFFSET_UNITS])
            NexusUtils.writeAttribute(nFile, data, "units", properties[TRANSFORMATION_UNITS])
            NexusUtils.writeAttribute(nFile, data, "transformation_type", properties[TRANSFORMATION_TYPE])
            NexusUtils.writeAttribute(nFile, data, "depends_on", "/entry1/instrument/transformations/offsetdelta")
        detDependsOn = "/entry1/instrument/%s/transformations/origin_offset" % name #TODO avoid paths here
        dependsData = DF.createFromObject(detDependsOn)
        dependsData.name = "depends_on"
        nFile.createData(group, dependsData)
        self.writeDetectorModule(nFile, group, name, detDependsOn)
        self.writeDetectorProperties(nFile, group, name)

    def writeTifPaths(self, nFile, group, detName, fileTemplate):
        self.logger.debug("writeTifPaths({}, {}, {}, {})", nFile, group, detName, fileTemplate)
        numberDataset = nFile.getData(group, "path").getDataset().getSlice()
        dimensions = numberDataset.shape
        length = 1
        for d in dimensions:
            length *= d
        numberDataset.resize([length])
        paths = [ fileTemplate % n for n in numberDataset.getBuffer() if n > 0 ]
        pathDataset = DF.createFromObject(paths)
        #for some reason, jython cannot pass a java array to a java method that expects a java array (via varargs)
        pathDataset.resize(dimensions.tolist())
        pathDataset.name = "image_data"
        data = nFile.createData(group, pathDataset)
        self.logger.debug("writeTifPaths() data={}", data)
        NexusUtils.writeAttribute(nFile, data, "data_filename", [1])
        NexusUtils.writeAttribute(nFile, data, "signal", [1])

    def writeDynamicDetectors(self, nFile, instrument, detectors, dependsOn):
        self.logger.debug("writeDynamicDetectors({}, {}, {}, {})", nFile, instrument, detectors, dependsOn)
        for det in detectors:
            detName = det.getName()
            detGroup = nFile.getGroup(instrument, detName, "NXdetector", False)
            self.writeDetector(nFile, detGroup, detName, dependsOn)
            pathTemplate=None
            self.logger.debug("writeDynamicDetectors() calling isinstance({}, {})", det, ProcessingDetectorWrapper)
            # This isinstance is failing because det and ProcessingDetectorWrapper are both showing as 
            #  writeDynamicDetectors() calling isinstance(pil2m<
            #    class org.python.proxies.epics.detector.NxProcessingDetectorWrapper$NxProcessingDetectorWrapper$740>,
            #    class org.python.proxies.gdascripts.scannable.detector.ProcessingDetectorWrapper$ProcessingDetectorWrapper$732)
            #if isinstance(det, ProcessingDetectorWrapper):
            try: # Rather than checking type, just try to call the function
                #path = det.getFilepathRelativeToRootDataDir().split('/')[0] + "/"
                pathTemplate = det.getFilepathRelativeToRootDataDir()
            except java.lang.Exception, e:
                self.logger.debug("writeDynamicDetectors() failed calling {}.getFilepathRelativeToRootDataDir() [Java.lang.Exception]", det, e)
            except:
                self.logger.error('writeDynamicDetectors() failed calling {}.getFilepathRelativeToRootDataDir( [except]):\n {}', det,
                    ''.join(traceback.format_exception(*sys.exc_info())) )
            if pathTemplate:
                self.logger.debug("writeDynamicDetectors() pathTemplate={}", pathTemplate)
                #remove the "last" instance of 5 digits with "%05d" for template purposes
                pathTemplate = re.sub("[0-9]+", "%05d"[::-1], pathTemplate[::-1], 1)[::-1]
                self.writeTifPaths(nFile, detGroup, detName, pathTemplate)
                self.logger.debug("writeDynamicDetectors() writeTifPaths() completed")
            else:
                self.logger.debug("writeDynamicDetectors() pathTemplate={}, can't be a ProcessingDetectorWrapper", pathTemplate)

    def parseCrystalInfo(self, nFile, metadataGroup):
        self.logger.debug("parseCrystalInfo(nFile={}, metadataGroup={})", nFile, metadataGroup)
        xtalinfo = nFile.getGroup(metadataGroup, "xtalinfo", "NXcollection", False)
        self.logger.debug("parseCrystalInfo() xtalinfo={}", xtalinfo)
        ubMatrix = [0] * 9
        latticeVals = [0] * 6
        for i in xrange(0, 3):
            for j in xrange(0, 3):
                ubval = "UB" + str(i + 1) + str(j + 1)
                try:
                    self.logger.debug("parseCrystalInfo() nFile.getData(xtalinfo, ubval).getDataset().getSlice().getDouble(0)={}", nFile.getData(xtalinfo, ubval).getDataset().getSlice().getDouble(0))
                    ubMatrix[ 3 * i + j ] = nFile.getData(xtalinfo, ubval).getDataset().getSlice().getDouble(0)
                except:
                    ubMatrix[ 3 * i + j ] = nFile.getData(xtalinfo, ubval).getDataset().getSlice().getDouble()
                    self.logger.error("parseCrystalInfo() coudn't get nFile.getData(xtalinfo, ubval).getDataset().getSlice().getDouble(0) use getDouble() instead")
                    self.logger.debug("parseCrystalInfo() nFile.getData(xtalinfo, ubval).getDataset().getSlice().getDouble()={}", nFile.getData(xtalinfo, ubval).getDataset().getSlice().getDouble())
        for i, val in zip(xrange(0, 6), ["a", "b", "c", "alpha1", "alpha2", "alpha3"]):
            self.logger.debug("parseCrystalInfo() val={}", val)
            try:
                self.logger.debug("parseCrystalInfo() nFile.getData(xtalinfo, val).getDataset().getSlice().getDouble(0)={}", nFile.getData(xtalinfo, val).getDataset().getSlice().getDouble(0))
                latticeVals[i] = nFile.getData(xtalinfo, val).getDataset().getSlice().getDouble(0)
            except:
                latticeVals[i] = nFile.getData(xtalinfo, val).getDataset().getSlice().getDouble()
                self.logger.error("parseCrystalInfo() coudn't get nFile.getData(xtalinfo, val).getDataset().getSlice().getDouble(0) use getDouble() instead")
                self.logger.debug("parseCrystalInfo() nFile.getData(xtalinfo, val).getDataset().getSlice().getDouble()={}", nFile.getData(xtalinfo, val).getDataset().getSlice().getDouble())
        self.logger.info("parseCrystalInfo() returning latticeVals={}, ubMatrix={}", latticeVals, ubMatrix)
        return (latticeVals, ubMatrix)

    def extractTransmission(self, nFile, metadataGroup):
        atten = nFile.getGroup(metadataGroup, "gains_atten", "NXcollection", False)
        ds = nFile.getData(atten, "Transmission").getDataset().getSlice()
        ds.name = "attenuator_transmission"
        return ds

    def writeTransmission(self, nFile, instrument, transmission):
        attenGroup = nFile.getGroup(instrument, "attenuator", "NXattenuator", True)
        nFile.createData(attenGroup, transmission)


    def writeCrystalInfo(self, nFile, group, latticeParams, ubMatrix):
        self.logger.debug("writeCrystalInfo(nFile=%r, group=%r, latticeParams=%r, ubMatrix=%r)" %(nFile, group, latticeParams, ubMatrix))
        unit_cell = DF.createFromObject(latticeParams)
        unit_cell.name = "unit_cell"
        unit_cell.shape = [1, 6]
        data = nFile.createData(group, unit_cell)
        NexusUtils.writeAttribute(nFile, data, "angle_units", "deg")
        NexusUtils.writeAttribute(nFile, data, "length_units", "angstrom")
        ub_matrix = DF.createFromObject(ubMatrix)
        ub_matrix.shape = [3, 3]

        #transform by [[1, 0, 0], [0, 0, -1], [0, 1, 0]] to get UB in lab frame
        ub_matrix = LA.dotProduct(
                DF.createFromObject([[1, 0, 0], [0, 0, -1], [0, 1, 0]]),
                ub_matrix)
        ub_matrix.shape = [1, 3, 3]
        ub_matrix.name = "ub_matrix"

        nFile.createData(group, ub_matrix)

    def writeIncidentWavelength(self, nFile, group):
        self.logger.debug("writeIncidentWavelength(nFile={}, group={})", nFile, group)
        try:
            self.logger.debug("writeIncidentWavelength() nFile.getData(group, 'incident_energy').getDataset().getSlice().getDouble(0)={}",
                     nFile.getData(group, "incident_energy").getDataset().getSlice().getDouble(0) )
            energy = nFile.getData(group, "incident_energy").getDataset().getSlice().getDouble(0)
        except:
            energy = nFile.getData(group, "incident_energy").getDataset().getSlice().getDouble()
            self.logger.error("writeIncidentWavelength() coudn't get nFile.getData(group, 'incident_energy').getDataset().getSlice().getDouble(0) use getDouble() instead")
            self.logger.debug("writeIncidentWavelength() nFile.getData(group, 'incident_energy').getDataset().getSlice().getDouble()={}",
                     nFile.getData(group, "incident_energy").getDataset().getSlice().getDouble() )
        wavelength = 1e9 * PLANCK * LIGHTSPEED / (energy * 1000 * EVOLT_TO_JOULE)
        dataset = DF.createFromObject(wavelength)
        dataset.name = "incident_wavelength"
        data = nFile.createData(group, dataset)
        NexusUtils.writeAttribute(nFile, data, "units", "nm")

    def writeSample(self, nFile, group, sampleName, sampleDependsOn):
        dependsData = DF.createFromObject(sampleDependsOn)
        dependsData.name = "depends_on"
        nFile.createData(group, dependsData)
        nameData = DF.createFromObject(sampleName)
        nameData.name = "name"
        nFile.createData(group, nameData)

    def writeFeatures(self, nFile, group, features):
        data = DF.createFromObject(Dataset.INT64, features)
        data.name = "features"
        nFile.createData(group, data)

    def writeDefinition(self, nFile, group, definition):
        data = DF.createFromObject(definition)
        data.name = "definition"
        nFile.createData(group, data)

    def writeDeltaOffset(self, nFile, transformations, metadata):
        self.logger.debug("writeDeltaOffset(nFile={}, transformations={}, metadata={})", nFile, transformations, metadata)
        diffGroup = nFile.getGroup(metadata, "diffractometer_sample", "NXcollection", False)
        try:
            offsetValue = nFile.getData(diffGroup, "delta_axis_offset").getDataset().getSlice().getDouble(0)
        except:
            offsetValue = nFile.getData(diffGroup, "delta_axis_offset").getDataset().getSlice().getDouble()
            self.logger.error("writeDeltaOffset() coudn't get nFile.getData(diffGroup, delta_axis_offset').getDataset().getSlice().getDouble() use getDouble() instead")
        offsetData = DF.createFromObject([offsetValue])
        offsetData.name = "offsetdelta"
        data = nFile.createData(transformations, offsetData)
        NexusUtils.writeAttribute(nFile, data, "local_name", "delta_axis_offset.delta_axis_offset")
        NexusUtils.writeAttribute(nFile, data, "vector", [0., -1., 0.])
        NexusUtils.writeAttribute(nFile, data, "axis", 1)
        NexusUtils.writeAttribute(nFile, data, "units", "deg")
        NexusUtils.writeAttribute(nFile, data, "transformation_type", "rotation")
        NexusUtils.writeAttribute(nFile, data, "depends_on","/entry1/instrument/transformations/gamma")

    def writeStuffToFile(self, fileName):
        self.logger.debug("writeStuffToFile(fileName={})", fileName)
        nFile = NexusFileHDF5(fileName)
        nFile.openToWrite(False)
        try:
            entry = nFile.getGroup("/entry1", False)
            metadataGroup = nFile.getGroup("/entry1/before_scan", False)
            self.writeTitle(nFile, entry, NEXUS_TITLE)
            if DIFFCALC is not None:
                crystalInfo = None
                if DIFFCALC.ub.ub.ubcalc._state.name is None:
                    self.logger.debug("DIFFCALC.ub.ub.ubcalc._state.name is None, so crystalInfo = None")
                    print "** Require UB calculation to write sample information. **"
                    print "** Nexus file will not contain sample information. **"
                else:
                    # I16-181 (9.16) Fix Scans throw exception without UB matrix
                    try:
                        ubMat = DIFFCALC.ub.ub.ubcalc.UB.tolist()
                        #diffcalc's UB matrix is scaled up by 2*PI
                        ubMat = [ [_u * 0.5/math.pi for _u in _r] for _r in ubMat ]
                        xtal = DIFFCALC.ub.ub.ubcalc._state.crystal.getLattice()
                        latParams = list(xtal[1:])
                        crystalInfo = (latParams, ubMat)
                    except:
                        self.logger.error('writeStuffToFile() failed to get all crystalInfo so returning none:\n {}',
                            ''.join(traceback.format_exception(*sys.exc_info())) )
            else:
                crystalInfo = self.parseCrystalInfo(nFile, metadataGroup)
            sample = nFile.getGroup("/entry1/sample", False)
            if crystalInfo is not None:
                self.writeCrystalInfo(nFile, sample, crystalInfo[0], crystalInfo[1])
            else:
                self.logger.debug("crystalInfo is None, DIFFCALC is {}", DIFFCALC)
            beam = nFile.getGroup("/entry1/sample/beam", False)
            self.writeIncidentWavelength(nFile, beam)
            sampleDependsOn = "/entry1/sample/transformations/" + ("cryophi" if USE_CRYO_GEOMETRY else "phi")
            self.writeSample(nFile, sample, SAMPLE_NAME, sampleDependsOn)
            instrument = nFile.getGroup("/entry1/instrument", False)
            self.writeDynamicDetectors(nFile, instrument, self.scanDataPoint.getDetectors(), "/entry1/instrument/transformations/offsetdelta")
            self.writeDefinition(nFile, entry, "NXmx")
            self.writeFeatures(nFile, entry, [GDA_SCAN, NXMX, SAMPLE_GEOMETRY])
            transmission = self.extractTransmission(nFile, metadataGroup)
            self.writeTransmission(nFile, instrument, transmission)
        except:
            self.logger.error('writeStuffToFile() failed:\n {}', ''.join(traceback.format_exception(*sys.exc_info())))
        finally:
            nFile.close()

    # DataWriterExtenderBase Interface

    def completeCollection(self, dwParent):
        try:
            #if a multi-dimensional scan is stopped early then this will be called multiple times
            if not self.complete:
                self.complete = True
                self.writeStuffToFile(self.scanFileName)
        except Exception, e:
            self.logger.error("completeCollection({}) failed", dwParent, e)
            self.logger.error('completeCollection() failed:\n {}', ''.join(traceback.format_exception(*sys.exc_info())))
        DataWriterExtenderBase.completeCollection(self, dwParent)

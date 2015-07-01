from gda.data.scan.datawriter import DataWriterExtenderBase
from gda.device.detector import NexusDetector
from gda.factory import Finder
from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
from org.nexusformat import NexusFile
from jarray import array, zeros
import traceback

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


EVOLT_TO_JOULE = 1.60217657e-19
PLANCK = 6.62606957e-34
LIGHTSPEED = 299792458.


GDA_SCAN = 3
NXMX = 6
#This value does not fit in a signed 64bit integer (and Java is uncivilised and has no unsigned types)
#SAMPLE_GEOMETRY = 13907096678176980974
SAMPLE_GEOMETRY = -4539647395532570642 #signed representation

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

TRANSFORMATION_NAME = "transformationName"
TRANSFORMATION_TYPE = "transformationType"
TRANSFORMATION_VECTOR = "transformationVector"
TRANSFORMATION_OFFSET = "transformationOffset"
TRANSFORMATION_SIZE = "transformationSize"
TRANSFORMATION_UNITS = "transformationUnits"
TRANSFORMATION_OFFSET_UNITS = "transformationOffsetUnits"

TRANSFORMATION_ROTATION = "rotation"
TRANSFORMATION_TRANSLATION = "translation"

#We make all the attributes an array here since we have to add them as arrays to the nexus file
#Strings are already arrays (we pass them as byte arrays)

#list of transforamtions
#element n+1 will depend on element n
#element 0 will depend on delta
DETECTOR_TRANSFORMATIONS = {
        "pilatus1" : [
            {
                TRANSFORMATION_NAME : 'origin_offset',
                TRANSFORMATION_TYPE : TRANSFORMATION_TRANSLATION,
                TRANSFORMATION_VECTOR : [50.40, -17.96, 525.95],
                TRANSFORMATION_OFFSET : [0, 0, 0],
                TRANSFORMATION_SIZE : [1],
                TRANSFORMATION_UNITS : 'mm',
                TRANSFORMATION_OFFSET_UNITS : 'mm',
            },
            #{
            #    TRANSFORMATION_NAME : 'phi',
            #    TRANSFORMATION_TYPE : TRANSFORMATION_ROTATION,
            #    TRANSFORMATION_VECTOR : [0, 0, 1],
            #    TRANSFORMATION_OFFSET : [0, 0, 0],
            #    TRANSFORMATION_SIZE : [0.1],
            #    TRANSFORMATION_UNITS : "deg",
            #    TRANSFORMATION_OFFSET_UNITS : 'mm',
            #}
        ]
    }

DETECTOR_MODULES = {
        "simad" : {
            DATA_ORIGIN : [0, 0],
            DATA_SIZE : [300, 200],
            FAST_PIXEL_DIRECTION : [0.0, -0.70716, 0.70716],
            FAST_PIXEL_SIZE : [0.000172],
            FAST_PIXEL_OFFSET : [0],
            FAST_PIXEL_UNITS : 'm',
            SLOW_PIXEL_DIRECTION : [1, 0, 0],
            SLOW_PIXEL_SIZE : [0.000172],
            SLOW_PIXEL_OFFSET : [0],
            SLOW_PIXEL_UNITS : 'm',
            OFFSET : [0],
            OFFSET_OFFSET: [0],
            OFFSET_VECTOR : [1, 0, 0],
            OFFSET_UNITS : 'mm'
        },
        "pilatus1" : {
            DATA_ORIGIN : [0, 0],
            DATA_SIZE : [487, 195],
            FAST_PIXEL_DIRECTION : [0.7191, -0.01268, -0.6948],
            FAST_PIXEL_SIZE : [0.000172],
            FAST_PIXEL_OFFSET : [0],
            FAST_PIXEL_UNITS : 'm',
            SLOW_PIXEL_DIRECTION : [0.01198, 0.9999, -0.005853],
            SLOW_PIXEL_SIZE : [0.000172],
            SLOW_PIXEL_UNITS : 'm',
            SLOW_PIXEL_OFFSET : [0],
            OFFSET : [0],
            OFFSET_OFFSET : [0],
            OFFSET_VECTOR : [1, 0, 0],
            OFFSET_UNITS : 'mm'
        }
    }

DETECTOR_PROPERTIES = {
        "simad" : {
            SENSOR_SATURATION_VALUE : [1000000],
            SENSOR_MATERIAL : "Sillicon",
            SENSOR_THICKNESS : [320],
            SENSOR_THICKNESS_UNITS : "micron",
            SENSOR_TYPE : "Pixel",
            SENSOR_DESCRIPTION : "Simulated Detector"
        },
        "pilatus1" : {
            SENSOR_SATURATION_VALUE : [1000000],
            SENSOR_MATERIAL : "Sillicon",
            SENSOR_THICKNESS : [320],
            SENSOR_THICKNESS_UNITS : "micron",
            SENSOR_TYPE : "Pixel",
            SENSOR_DESCRIPTION : "Pilatus 100k (properties are dubious)"
        }
    }

DETECTOR_MODULES["simd"] = DETECTOR_MODULES["simad"]
DETECTOR_PROPERTIES["simd"] = DETECTOR_PROPERTIES["simad"]
DETECTOR_MODULES["pil100k"] = DETECTOR_MODULES["pilatus1"]
DETECTOR_PROPERTIES["pil100k"] = DETECTOR_PROPERTIES["pilatus1"]
DETECTOR_TRANSFORMATIONS["pil100k"] = DETECTOR_TRANSFORMATIONS['pilatus1']


class I16NexusExtender(DataWriterExtenderBase):

    def __init__(self, xtalinfo):
        DataWriterExtenderBase.__init__(self)
        self.xtalinfo = xtalinfo
        self.complete = True

    def addData(self, dwParent, scanDataPoint):
        self.complete = False
        self.scanDataPoint = scanDataPoint
        self.scanFileName = scanDataPoint.getCurrentFilename()
        #The SrsDataFile in NexusDataWriter will set the filename to .dat - we need .nxs
        self.scanFileName = self.scanFileName[:-3] + "nxs"
        DataWriterExtenderBase.addData(self, dwParent, scanDataPoint)

    def writeSample(self, nFile, sampleName, sampleDependsOn):
        dataDims = array([ len(sampleDependsOn) ], 'i')
        nFile.opengroup("sample", "NXsample")
        nFile.makedata("depends_on", NexusFile.NX_CHAR, 1, dataDims)
        nFile.opendata("depends_on")
        nFile.putdata( array(sampleDependsOn, 'b') )
        nFile.closedata()
        dataDims = array([ len(sampleName) ], 'i')
        nFile.makedata("name", NexusFile.NX_CHAR, 1, dataDims)
        nFile.opendata("name")
        nFile.putdata( array(sampleName, 'b') )
        nFile.closedata()
        nFile.closegroup()

    def writeFeatures(self, nFile, features):
        dataDims = array([ len(features) ], 'i')
        nFile.makedata("features", NexusFile.NX_UINT64, 1, dataDims)
        nFile.opendata("features")
        nFile.putdata( array(features, 'l') )
        nFile.closedata()

    def writeDefinition(self, nFile, definition):
        dataDims = array([ len(definition) ], 'i')
        nFile.makedata("definition", NexusFile.NX_CHAR, 1, dataDims)
        nFile.opendata("definition")
        nFile.putdata( array(definition, 'b') )
        nFile.closedata()

    #We assume a single module per detector - in reality there may be more (but not for I16, even their pil2m)
    def writeDetectorModule(self, nFile, detName):
        if not DETECTOR_MODULES.has_key(detName):
            return
        detModule = DETECTOR_MODULES[detName]
        moduleDependsOn = "/entry1/instrument/%s/transformations/origin_offset" % detName
        moduleDependsOn = moduleDependsOn.__str__() #unicode != str and we need raw bytes
        nFile.makegroup("module", "NXdetector_module")
        nFile.opengroup("module", "NXdetector_module")

        nFile.makedata("data_origin", NexusFile.NX_INT64, 1, array([2], 'i'))
        nFile.opendata("data_origin")
        nFile.putdata( array(detModule[DATA_ORIGIN], 'i') )
        nFile.closedata()

        nFile.makedata("data_size", NexusFile.NX_INT64, 1, array([2], 'i'))
        nFile.opendata("data_size")
        nFile.putdata( array(detModule[DATA_SIZE], 'i') )
        nFile.closedata()

        nFile.makedata("fast_pixel_direction", NexusFile.NX_FLOAT64, 1, array([1], 'i'))
        nFile.opendata("fast_pixel_direction")
        nFile.putdata( array(detModule[FAST_PIXEL_SIZE], 'd') )
        nFile.putattr(
                "depends_on",
                array(moduleDependsOn, 'b'),
                NexusFile.NX_CHAR
                )
        nFile.putattr(
                "offset",
                array(detModule[FAST_PIXEL_OFFSET], 'l'),
                NexusFile.NX_FLOAT64
                )
        nFile.putattr(
                "transformation_type",
                array("translation", 'b'),
                NexusFile.NX_CHAR
                )
        nFile.putattr(
                "units",
                array(detModule[FAST_PIXEL_UNITS], 'b'),
                NexusFile.NX_CHAR
                )
        nFile.putattr(
                "vector",
                array(detModule[FAST_PIXEL_DIRECTION], 'd'),
                array([3], 'i'),
                NexusFile.NX_FLOAT64
                )
        nFile.closedata()

        nFile.makedata("slow_pixel_direction", NexusFile.NX_FLOAT64, 1, array([1], 'i'))
        nFile.opendata("slow_pixel_direction")
        nFile.putdata( array(detModule[SLOW_PIXEL_SIZE], 'd') )
        nFile.putattr(
                "depends_on",
                array(moduleDependsOn, 'b'),
                NexusFile.NX_CHAR
                )
        nFile.putattr(
                "offset",
                array(detModule[SLOW_PIXEL_OFFSET], 'l'),
                NexusFile.NX_FLOAT64
                )
        nFile.putattr(
                "transformation_type",
                array("translation", 'b'),
                NexusFile.NX_CHAR
                )
        nFile.putattr(
                "units",
                array(detModule[SLOW_PIXEL_UNITS], 'b'),
                NexusFile.NX_CHAR
                )
        nFile.putattr(
                "vector",
                array(detModule[SLOW_PIXEL_DIRECTION], 'd'),
                array([3], 'i'),
                NexusFile.NX_FLOAT64
                )
        nFile.closedata()

        nFile.makedata("module_offset", NexusFile.NX_FLOAT64, 1, array([1], 'i'))
        nFile.opendata("module_offset")
        nFile.putdata( array(detModule[OFFSET], 'd') )
        nFile.putattr(
                "depends_on",
                array(moduleDependsOn, 'b'),
                NexusFile.NX_CHAR
                )
        nFile.putattr(
                "offset",
                array(detModule[OFFSET_OFFSET], 'l'),
                NexusFile.NX_FLOAT64
                )
        nFile.putattr(
                "transformation_type",
                array("translation", 'b'),
                NexusFile.NX_CHAR
                )
        nFile.putattr(
                "units",
                array(detModule[OFFSET_UNITS], 'b'),
                NexusFile.NX_CHAR
                )
        nFile.putattr(
                "vector",
                array(detModule[OFFSET_VECTOR], 'd'),
                array([3], 'i'),
                NexusFile.NX_FLOAT64
                )
        nFile.closedata()

        nFile.closegroup()

    def writeDetectorTransformations(self, nFile, detName, depends_on):
        if not DETECTOR_TRANSFORMATIONS.has_key(detName):
            return
        transformations = DETECTOR_TRANSFORMATIONS[detName]
        nFile.makegroup("transformations", "NXtransformations")
        nFile.opengroup("transformations", "NXtransformations")
        #depends_on = "/entry1/instrument/transformations/delta"
        depends_on = depends_on.__str__()
        for transformation in transformations:
            nFile.makedata(transformation[TRANSFORMATION_NAME], NexusFile.NX_FLOAT64, 1, array([1], 'i'))
            nFile.opendata(transformation[TRANSFORMATION_NAME])
            nFile.putdata(array(transformation[TRANSFORMATION_SIZE], 'd'))
            nFile.putattr(
                    "transformation_type",
                    array(transformation[TRANSFORMATION_TYPE], 'b'),
                    NexusFile.NX_CHAR
                    )
            nFile.putattr(
                    "vector",
                    array(transformation[TRANSFORMATION_VECTOR], 'd'),
                    array([3], 'i'),
                    NexusFile.NX_FLOAT64
                    )
            nFile.putattr(
                    "offset",
                    array(transformation[TRANSFORMATION_OFFSET], 'd'),
                    array([3], 'i'),
                    NexusFile.NX_FLOAT64
                    )
            nFile.putattr(
                    "units",
                    array(transformation[TRANSFORMATION_UNITS], 'b'),
                    NexusFile.NX_CHAR
                    )
            nFile.putattr(
                    "offset_units",
                    array(transformation[TRANSFORMATION_OFFSET_UNITS], 'b'),
                    NexusFile.NX_CHAR
                    )
            nFile.putattr(
                    "depends_on",
                    array(depends_on, 'b'),
                    NexusFile.NX_CHAR
                    )
            nFile.closedata()
            depends_on = "/entry1/instrument/" + detName + "/transformations/" + transformation[TRANSFORMATION_NAME]
            depends_on = depends_on.__str__()
        nFile.closegroup()

    def writeDetectorProperties(self, nFile, detName):
        if not DETECTOR_PROPERTIES.has_key(detName):
            return
        properties = DETECTOR_PROPERTIES[detName]

        nFile.makedata("saturation_value", NexusFile.NX_INT64, 1, array([1], 'i'))
        nFile.opendata("saturation_value")
        nFile.putdata( array(properties[SENSOR_SATURATION_VALUE], 'l') )
        nFile.closedata()

        nFile.makedata("sensor_material", NexusFile.NX_CHAR, 1, array([len(properties[SENSOR_MATERIAL])], 'i'))
        nFile.opendata("sensor_material")
        nFile.putdata( array(properties[SENSOR_MATERIAL], 'b') )
        nFile.closedata()

        nFile.makedata("sensor_thickness", NexusFile.NX_FLOAT64, 1, array([1], 'i'))
        nFile.opendata("sensor_thickness")
        nFile.putdata( array(properties[SENSOR_THICKNESS], 'd') )
        nFile.putattr("units", array(properties[SENSOR_THICKNESS_UNITS], 'b'), array([1], 'i'), NexusFile.NX_FLOAT64)
        nFile.closedata()


        detObject = Finder.getInstance().find(detName)
        #The following properties only need to be added if this is a NexusDetector
        if detObject != None and isinstance(detObject, NexusDetector):
            nFile.makedata("description", NexusFile.NX_CHAR, 1, array([len(properties[SENSOR_DESCRIPTION])], 'i'))
            nFile.opendata("description")
            nFile.putdata( array(properties[SENSOR_DESCRIPTION], 'b') )
            nFile.closedata()

            nFile.makedata("type", NexusFile.NX_CHAR, 1, array([len(properties[SENSOR_TYPE])], 'i'))
            nFile.opendata("type")
            nFile.putdata( array(properties[SENSOR_TYPE], 'b') )
            nFile.closedata()

    def writeDetector(self, nFile, detName, dependsOn):
        dataDims = array([ len(dependsOn) ], 'i')
        nFile.opengroup(detName, "NXdetector")
        nFile.makedata("depends_on", NexusFile.NX_CHAR, 1, dataDims)
        nFile.opendata("depends_on")
        nFile.putdata( array(dependsOn, 'b') )
        nFile.closedata()
        self.writeDetectorModule(nFile, detName)
        self.writeDetectorProperties(nFile, detName)
        self.writeDetectorTransformations(nFile, detName, dependsOn)
        nFile.closegroup()

    def writeTifPaths(self, nFile, detName, filePath):
        template = "%s%05d.tif"
        nFile.opengroup(detName, "NXdetector")
        nFile.opendata("path")
        scanInfo = self.scanDataPoint.getScanInformation()
        scanDimensions = scanInfo.getDimensions()
        #Scans can be ended early, so we have to work out the _real_ dimensions from the nexus file
        realDimensions = zeros( len(scanDimensions), 'i' )
        argArray = zeros( 2, 'i' )
        nFile.getinfo(realDimensions, argArray)

        length = 1
        for d in realDimensions:
            length *= d
        fileNumbers = zeros(length, 'd')
        nFile.getdata(fileNumbers)
        nFile.closedata()
        #path == 0 means no file was written (assuming starting at 1) and that the scan was ended early
        #write empty string in this case
        filePaths = [ template % (filePath, n) for n in fileNumbers if n > 0 ]
        filePaths += [ '' for n in fileNumbers if n <= 0 ]
        filePathLength = 255
        dimensions = [-1] * len(realDimensions) + [255]
        dimensions = array(dimensions, 'i')
        rank = len(dimensions)

        nFile.makedata("image_data", NexusFile.NX_CHAR, rank, dimensions)
        nFile.opendata("image_data")
        ranges = [range(n) for n in realDimensions] + [[0]]
        startPositions = cartesian_product(*ranges)
        bytesDim = [1] * len(realDimensions) + [255]
        bytesDim = array(bytesDim, 'i')
        for path, position in zip(filePaths, startPositions):
            filePathBytes = array( path.ljust(filePathLength, '\0'), 'b')
            nFile.putslab( filePathBytes, array(position, 'i'), bytesDim )

        #I have no idea what these are for, but DAWN seems to need it and detectors include it
        nFile.putattr("data_filename", array([1], 'i'), NexusFile.NX_INT32)
        nFile.putattr("signal", array([1], 'i'), NexusFile.NX_INT32)
        #unicode != str
        nFile.putattr("target", array("/entry1/instrument/%s/image_data" % detName.__str__(), 'b'), NexusFile.NX_CHAR)

        nFile.closedata()
        nFile.closegroup()

    def writeDynamicDetectors(self, nFile, detectors, dependsOn):
        nFile.opengroup("instrument", "NXinstrument")
        for det in detectors:
            detName = det.getName()
            self.writeDetector(nFile, detName, dependsOn)
        #we have to fix the tif file paths if it's a PDW
        pdwDetectors = [det for det in detectors if isinstance(det, ProcessingDetectorWrapper)]
        for det in pdwDetectors:
            path = det.getFilepathRelativeToRootDataDir().split('/')[0] + "/"
            self.writeTifPaths(nFile, det.getName(), path)
        nFile.closegroup()

    def writeIncidentWavelength(self, nFile):
        nFile.opengroup("sample", "NXsample")
        nFile.opengroup("beam", "NXbeam")

        incidentEnergy = array([0.], 'd') #we're expecting a single 64bit float
        nFile.opendata("incident_energy")
        nFile.getdata(incidentEnergy)
        nFile.closedata()
        incidentEnergy = incidentEnergy[0]

        #wavelength in nanometres - assumes energy is in keV
        wavelength = 1e9 * PLANCK * LIGHTSPEED / (incidentEnergy * 1000 * EVOLT_TO_JOULE)
        nFile.makedata("incident_wavelength", NexusFile.NX_FLOAT64, 1, array([1], 'i'))
        nFile.opendata("incident_wavelength")
        nFile.putdata( array([wavelength], 'd') )
        nFile.putattr("units", array("nm", 'b'), NexusFile.NX_CHAR)
        nFile.closedata()

        nFile.closegroup()
        nFile.closegroup()

    def writeCrystalInfo(self, nFile, uMatrix, latticeParams):
        nFile.opengroup("sample", "NXsample")
        nFile.makedata("orientation_matrix", NexusFile.NX_FLOAT64, 3, array([1, 3, 3], 'i'))
        nFile.opendata("orientation_matrix")
        nFile.putdata( array(uMatrix, 'd') )
        nFile.closedata()
        nFile.makedata("unit_cell", NexusFile.NX_FLOAT64, 2, array([1, 6], 'i'))
        nFile.opendata("unit_cell")
        nFile.putdata( array(latticeParams, 'd') )
        nFile.putattr("angle_units", array("deg", 'b'), NexusFile.NX_CHAR)
        nFile.putattr("length_units", array("angstrom", 'b'), NexusFile.NX_CHAR)
        nFile.closedata()
        nFile.closegroup()

    def writeTitle(self, nFile, title):
        dataDims = array([ len(title) ], 'i')
        nFile.makedata("title", NexusFile.NX_CHAR, 1, dataDims)
        nFile.opendata("title")
        nFile.putdata( array(title, 'b') )
        nFile.closedata()

    def writeStuffToFile(self, fileName):
        nFile = NexusFile(fileName, NexusFile.NXACC_RDWR)
        try:
            nFile.opengroup("entry1", "NXentry")
            self.writeSample(nFile, SAMPLE_NAME[:], "/entry1/sample/transformations/phi")
            self.writeTitle(nFile, NEXUS_TITLE[:])
            self.writeDynamicDetectors(nFile, self.scanDataPoint.getDetectors(), "/entry1/instrument/transformations/delta")
            self.writeFeatures(nFile, [GDA_SCAN, NXMX, SAMPLE_GEOMETRY])
            self.writeDefinition(nFile, "NXmx")
            self.writeIncidentWavelength(nFile)
            self.writeCrystalInfo(nFile, self.xtalinfo.link1.getU(), self.xtalinfo.link2.getLattice()) #will fail with diffcalc
            nFile.closegroup()
        finally:
            nFile.flush()
            try:
                nFile.finalize()
            finally:
                nFile.close()

    def completeCollection(self, dwParent):
        try:
            #if a multi-dimensional scan is stopped early then this will be called multiple times
            if not self.complete:
                self.writeStuffToFile(self.scanFileName)
                self.complete = True
        except Exception, e:
            print traceback.print_exc()
        DataWriterExtenderBase.completeCollection(self, dwParent)

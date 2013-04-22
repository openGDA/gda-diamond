"""
Performs software triggered tomography
"""

from time import sleep

from pcoDetectorWrapper import PCODetectorWrapper
from gda.jython.commands.ScannableCommands import inc, scan, pos, createConcurrentScan
from gda.scan import ConstantVelocityScanLine

import sys
import time
import shutil
import gda
from gdascripts.parameters import beamline_parameters
from gdascripts.messages import handle_messages
from gda.device.scannable import ScannableBase
from gda.device.detector import DetectorBase
from gda.scan import ScanPositionProvider
from gda.device.scannable import ScannableBase, ScannableUtils
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.factory import Finder
from uk.ac.gda.analysis.hdf5 import Hdf5Helper, Hdf5HelperData, HDF5HelperLocations

from gda.data.scan.datawriter.DefaultDataWriterFactory import createDataWriterFromFactory
from gda.data.scan.datawriter import *

class EnumPositionerDelegateScannable(ScannableBase):
    """
    Translate positions 0 and 1 to Close and Open
    """
    def __init__(self, name, delegate):
        self.name = name
        self.inputNames = [name]
        self.delegate = delegate
    def isBusy(self):
        return self.delegate.isBusy()
    def rawAsynchronousMoveTo(self,new_position):
        if int(new_position) == self.rawGetPosition():
            return
        if int(new_position) == 1:
            self.delegate.asynchronousMoveTo("Open")
        else:
            self.delegate.asynchronousMoveTo("Close")
        # wait for 1s
        sleep(1.)
    def rawGetPosition(self):
        pos = self.delegate.getPosition()
        if pos == "Open":
            return 1 
        return 0

def make_tomoScanDevice(tomography_theta, tomography_shutter, tomography_translation, 
                        image_key, tomography_imageIndex ):
    tomoScanDevice = ScannableGroup()
    tomoScanDevice.addGroupMember(tomography_theta)
    tomoScanDevice.addGroupMember(EnumPositionerDelegateScannable("tomography_shutter", tomography_shutter))
    tomoScanDevice.addGroupMember(tomography_translation)
    tomoScanDevice.addGroupMember(image_key)
    tomoScanDevice.addGroupMember(tomography_imageIndex)
    tomoScanDevice.setName("tomoScanDevice")
    tomoScanDevice.configure()
    return tomoScanDevice


class   tomoScan_positions(ScanPositionProvider):
    def __init__(self, start, stop, step, darkFieldInterval, imagesPerDark, flatFieldInterval, imagesPerFlat,
             inBeamPosition, outOfBeamPosition, points):
        self.start = start
        self.stop = stop
        self.step = step
        self.darkFieldInterval = darkFieldInterval
        self.imagesPerDark = imagesPerDark
        self.flatFieldInterval = flatFieldInterval
        self.imagesPerFlat = imagesPerFlat
        self.inBeamPosition = inBeamPosition
        self.outOfBeamPosition = outOfBeamPosition
        self.points = points

    def get(self, index):
        return self.points[index]
    
    def size(self):
        return len(self.points)
    
    def __str__(self):
        return "Start: %f Stop: %f Step: %f Darks every:%d imagesPerDark:%d Flats every:%d imagesPerFlat:%d InBeamPosition:%f OutOfBeamPosition:%f numImages %d " % \
            ( self.start, self.stop, self.step,self.darkFieldInterval,self.imagesPerDark, self.flatFieldInterval, self.imagesPerFlat, self.inBeamPosition, self.outOfBeamPosition, self.size() ) 
    def toString(self):
        return self.__str__()

def addNXTomoSubentry(scanObject, tomography_detector_name, tomography_theta_name):
    if scanObject is None:
        raise "Input scanObject must not be None"
   
    nxLinkCreator = NXTomoEntryLinkCreator()
   
    # detector independent items
    nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/ionc_i:NXpositioner/ionc_i:NXdata")
    nxLinkCreator.setInstrument_detector_image_key_target("entry1:NXentry/instrument:NXinstrument/tomoScanDevice:NXpositioner/image_key:NXdata")
    nxLinkCreator.setInstrument_source_target("entry1:NXentry/instrument:NXinstrument/source:NXsource")
   
    sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/tomoScanDevice:NXpositioner/"
    sample_rotation_angle_target += tomography_theta_name + ":NXdata"
    nxLinkCreator.setSample_rotation_angle_target(sample_rotation_angle_target);
   
    nxLinkCreator.setTitle_target("entry1:NXentry/title:NXdata")
   
    # detector dependent items
    if tomography_detector_name == "pco1_hw_hdf":
        # external file
        instrument_detector_data_target = "!entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "data:SDS"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
    elif tomography_detector_name == "pco1_hw_tif":
        # image filenames
        instrument_detector_data_target = "entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "image_data:NXdata"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
    else:
        print "Defaults used for unsupported tomography detector in addNXTomoSubentry: " + tomography_detector_name
   
    nxLinkCreator.afterPropertiesSet()
   
    dataWriter = createDataWriterFromFactory()
    subEntryWriter = NXSubEntryWriter(nxLinkCreator)
    dataWriter.addDataWriterExtender(subEntryWriter)
    scanObject.setDataWriter(dataWriter)

def reportJythonNamespaceMapping():
    jns=beamline_parameters.JythonNameSpaceMapping()
    objectOfInterest = {}
    objectOfInterest['tomography_theta'] = jns.tomography_theta
    objectOfInterest['tomography_shutter'] = jns.tomography_shutter
    objectOfInterest['tomography_translation'] = jns.tomography_translation
    objectOfInterest['tomography_detector'] = jns.tomography_detector
    objectOfInterest['tomography_beammonitor'] = jns.tomography_beammonitor
  
    for key, val in objectOfInterest.iteritems():
        print key + ' = ' + str(val)
    msg = "\n These mappings can be changed by editing a file named live_jythonNamespaceMapping, "
    msg += "\n located in i13i-config/scripts (this can be done by beamline staff)."
    print msg

from gda.device.scannable import SimpleScannable
image_key_dark=2
image_key_flat=1 # also known as bright
image_key_project=0 # also known as sample

def showNormalisedImage(outOfBeamPosition, exposureTime=None):
	try:
		showNormalisedImageEx(outOfBeamPosition, exposureTime=exposureTime)
	except :
		exceptionType, exception, traceback = sys.exc_info()
		handle_messages.log(None, "Error in showNormalisedImage", exceptionType, exception, traceback, False)

def showNormalisedImageEx(outOfBeamPosition, exposureTime=None):
    jns=beamline_parameters.JythonNameSpaceMapping()
    tomodet=jns.tomodet
    if tomodet is None:
	    raise "tomodet is not defined in Jython namespace"
    if exposureTime is not None:
        exposureTime = float(exposureTime)
    else:
        exposureTime = tomodet.getCurrentExposureTime()

    import scisoftpy as dnp
    tomography_theta=jns.tomography_theta
    if tomography_theta is None:
            raise "tomography_theta is not defined in Jython namespace"    
    tomography_translation=jns.tomography_translation
    if tomography_translation is None:
        raise "tomography_translation is not defined in Jython namespace"        

    tomography_detector=jns.tomography_detector
    if tomography_detector is None:
        raise "tomography_detector is not defined in Jython namespace"    
    currentTheta=tomography_theta()
    tomoScan(tomography_translation(), outOfBeamPosition, exposureTime, start=currentTheta, stop=currentTheta, step=1., imagesPerDark=1, imagesPerFlat=1)
    lsdp=jns.lastScanDataPoint()
    detName=tomography_detector.getName()

    nxdata=dnp.io.load(lsdp.currentFilename)[str('entry1/' + tomography_detector.getName())] 
    datakey=None
    for key in nxdata.keys():
        if key == "image_data":
            dataKey=key
            break
        if key == "data":
            dataKey=key
            break
    if dataKey == None:
        raise "Unable to find data in file"
    dataset=nxdata[dataKey]
    dark=dnp.array((dataset[0,:,:]).cast(6))
    flat=dnp.array((dataset[1,:,:]).cast(6))
    image=dnp.array((dataset[2,:,:]).cast(6))
    imageD=image-dark
    flatD=flat-dark
    t=imageD/dnp.select( dnp.not_equal(flatD,0), flatD, 1.)
    t.name="image-dark/flat-dark"
    hdfData = Hdf5HelperData(t.shape, t.getBuffer())
    locs = HDF5HelperLocations("entry1")
    locs.add(tomography_detector.getName())
    Hdf5Helper.getInstance().writeToFileSimple(hdfData, lsdp.currentFilename,locs , "normalisedImage")
    rcp=Finder.getInstance().find("RCPController")
    rcp.openView("uk.ac.gda.beamline.i13i.NormalisedImage")
    dnp.plot.image(t, name="Normalised Image")
    #turn camera back on
    return True
"""
perform a continuous tomogrpahy scan
"""
def tomoFlyScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1.):
    """
    Function to collect a tomogram
     Arguments:
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds ( default = 1)
    start - first rotation angle ( default=0.)
    stop  - last rotation angle (default=180.)
    step - rotation step size (default = 0.1)
    darkFieldInterval - number of projections between each dark field. Note that a dark is always taken at the start and end of a tomogram (default=0.)
    flatFieldInterval - number of projections between each flat field. Note that a dark is always taken at the start and end of a tomogram (default=0.)
    imagesPerDark - number of images to be taken for each dark (default=20)
    imagesPerFlat - number of images to be taken for each flat (default=20)
    min_i - minimum value of ion chamber current required to take an image (default is -1 . A negative value means that the value is not checked )

    """
    try:
        jns=beamline_parameters.JythonNameSpaceMapping()
        tomodet=jns.tomodet
        if tomodet is None:
	        raise "tomodet is not defined in Jython namespace"
        tomography_flyscan_theta=jns.tomography_flyscan_theta
        if tomography_flyscan_theta is None:
            raise "tomography_flyscan_theta is not defined in Jython namespace"

        tomography_flyscan_det=jns.tomography_flyscan_det
        if tomography_flyscan_det is None:
            raise "tomography_flyscan_det is not defined in Jython namespace"
        

        tomography_shutter=jns.tomography_shutter
        if tomography_shutter is None:
            raise "tomography_shutter is not defined in Jython namespace"

        #ensure the soft control of the shutter is open at the end of the scan
        tomography_shutter.moveTo( "Open")        

        scanObject=ConstantVelocityScanLine([tomography_flyscan_theta, start, stop, step, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
        tomodet.stop()
        
        scanObject.runScan()
        #turn camera back on
        tomodet.setupForAlignment()
        return scanObject;
    except :
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Error in tomoFlyScanScan", exceptionType, exception, traceback, False)


"""
perform a simple tomogrpahy scan
"""
def tomoScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1.):
    """
    Function to collect a tomogram
 	Arguments:
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds ( default = 1)
    start - first rotation angle ( default=0.)
    stop  - last rotation angle (default=180.)
    step - rotation step size (default = 0.1)
    darkFieldInterval - number of projections between each dark field. Note that a dark is always taken at the start and end of a tomogram (default=0.)
    flatFieldInterval - number of projections between each flat field. Note that a dark is always taken at the start and end of a tomogram (default=0.)
    imagesPerDark - number of images to be taken for each dark (default=20)
    imagesPerFlat - number of images to be taken for each flat (default=20)
    min_i - minimum value of ion chamber current required to take an image (default is -1 . A negative value means that the value is not checked )

    """
    try:
        darkFieldInterval=int(darkFieldInterval)
        flatFieldInterval=int(flatFieldInterval)
        
        jns=beamline_parameters.JythonNameSpaceMapping()
        tomodet=jns.tomodet
        if tomodet is None:
	        raise "tomodet is not defined in Jython namespace"

        tomography_theta=jns.tomography_theta
        if tomography_theta is None:
            raise "tomography_theta is not defined in Jython namespace"
        tomography_shutter=jns.tomography_shutter
        if tomography_shutter is None:
            raise "tomography_shutter is not defined in Jython namespace"
        tomography_translation=jns.tomography_translation
        if tomography_translation is None:
            raise "tomography_translation is not defined in Jython namespace"
        
        tomography_detector=jns.tomography_detector
        if tomography_detector is None:
            raise "tomography_detector is not defined in Jython namespace"

#        tomography_optimizer=jns.tomography_optimizer
#        if tomography_optimizer is None:
#            raise "tomography_optimizer is not defined in Jython namespace"

        tomography_time=jns.tomography_time
        if tomography_time is None:
            raise "tomography_time is not defined in Jython namespace"
        
        tomography_beammonitor=jns.tomography_beammonitor
        if tomography_beammonitor is None:
            raise "tomography_beammonitor is not defined in Jython namespace"

        camera_stage = jns.cs1
        if camera_stage is None:
            raise "camera_stage is not defined in Jython namespace"

        sample_stage = jns.sample_stage
        if sample_stage is None:
            raise "sample_stage is not defined in Jython namespace"

        index=SimpleScannable()
        index.setCurrentPosition(0.0)
        index.setInputNames(["imageNumber"])
        index.setName("imageNumber")
        index.configure()
        
        image_key=SimpleScannable()
        image_key.setCurrentPosition(0.0)
        image_key.setInputNames(["image_key"])
        image_key.setName("image_key")
        image_key.configure()

        tomoScanDevice = make_tomoScanDevice(tomography_theta, tomography_shutter, 
                                             tomography_translation, image_key, index)

#        return tomoScanDevice
        #generate list of positions
        numberSteps = ScannableUtils.getNumberSteps(tomography_theta, start, stop, step)
        theta_points = []
        theta_points.append(start)
        previousPoint = start
        for i in range(numberSteps):
            nextPoint = ScannableUtils.calculateNextPoint(previousPoint, step);
            theta_points.append(nextPoint)
            previousPoint = nextPoint
        
        shutterOpen=1
        shutterClosed=0
        scan_points = []
        theta_pos = theta_points[0]
        index=0
        for i in range(imagesPerDark):
            scan_points.append((theta_pos, shutterClosed, inBeamPosition, image_key_dark,index )) #dark
            index = index + 1
                    
        for i in range(imagesPerFlat):
            scan_points.append((theta_pos, shutterOpen, outOfBeamPosition, image_key_flat, index )) #flat
            index = index + 1        
        scan_points.append((theta_pos,shutterOpen, inBeamPosition, image_key_project, index )) #first
        index = index + 1        
        imageSinceDark=0
        imageSinceFlat=0
        for i in range(numberSteps):
            theta_pos = theta_points[i+1]
            scan_points.append((theta_pos, shutterOpen, inBeamPosition, image_key_project, index ))#main image
            index = index + 1        
            
            
            imageSinceFlat = imageSinceFlat + 1
            if imageSinceFlat == flatFieldInterval and flatFieldInterval != 0:
                for i in range(imagesPerFlat):
                    scan_points.append((theta_pos, shutterOpen, outOfBeamPosition,  image_key_flat, index ))
                    index = index + 1        
                    imageSinceFlat=0
            
            imageSinceDark = imageSinceDark + 1
            if imageSinceDark == darkFieldInterval and darkFieldInterval != 0:
                for i in range(imagesPerDark):
                    scan_points.append((theta_pos, shutterClosed, inBeamPosition, image_key_dark, index ))
                    index = index + 1        
                    imageSinceDark=0

        #add dark and flat only if not done in last steps
        if imageSinceFlat != 0:
            for i in range(imagesPerFlat):
                scan_points.append((theta_pos, shutterOpen, outOfBeamPosition,  image_key_flat, index )) #flat
                index = index + 1
        if imageSinceDark != 0:
            for i in range(imagesPerDark):
                scan_points.append((theta_pos, shutterClosed, inBeamPosition,  image_key_dark, index )) #dark
                index = index + 1        
                
        positionProvider = tomoScan_positions( start, stop, step, darkFieldInterval, imagesPerDark, flatFieldInterval, imagesPerFlat, \
                                               inBeamPosition, outOfBeamPosition, scan_points ) 
        scan_args = [tomoScanDevice, positionProvider, tomography_time, tomography_beammonitor, tomography_detector, exposureTime, camera_stage, sample_stage ]
        print `scan_args`
        if min_i > 0.:
            import gdascripts.scannable.beamokay
            ionc_i = jns.ionc_i
            if ionc_i is None:
                raise "ionc_i is not defined in Jython namespace"
            beamok=gdascripts.scannable.beamokay.WaitWhileScannableBelowThresholdMonitorOnly("beamok", ionc_i, min_i)
            scan_args.append(beamok)
            
        scanObject=createConcurrentScan(scan_args)
        addNXTomoSubentry(scanObject, tomography_detector.name, tomography_theta.name)
        tomodet.stop()
        scanObject.runScan()
        #ensure the soft control of the shutter is open at the end of the scan
        tomography_shutter.moveTo( "Open")	
        #turn camera back on
        tomodet.setupForAlignment()
        return scanObject;
    except :
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Error in tomoScan", exceptionType, exception, traceback, False)


from gda.commandqueue import JythonScriptProgressProvider
def updateProgress( percent, msg):
    JythonScriptProgressProvider.sendProgress( percent, msg)
    print "percentage %d %s" % (percent, msg)
    
from uk.ac.gda.tomography.scan.util import ScanXMLProcessor
from java.io import FileInputStream
from gdascripts.metadata.metadata_commands import setTitle
def ProcessScanParameters(scanParameterModelXML):
    print scanParameterModelXML
    scanXMLProcessor = ScanXMLProcessor();
    resource = scanXMLProcessor.load(FileInputStream(scanParameterModelXML), None);
    parameters = resource.getContents().get(0);
    setTitle(parameters.getTitle())
    updateProgress(0, "Starting tomoscan" + parameters.getTitle());
    print "Flyscan:" + `parameters.flyScan`
    if( parameters.flyScan ):
        tomoFlyScan(parameters.inBeamPosition, parameters.outOfBeamPosition, exposureTime=parameters.exposureTime, start=parameters.start, stop=parameters.stop, step=parameters.step, 
                 darkFieldInterval=parameters.darkFieldInterval,  flatFieldInterval=parameters.flatFieldInterval,
                  imagesPerDark=parameters.imagesPerDark, imagesPerFlat=parameters.imagesPerFlat, min_i=parameters.minI)    
    else:
        tomoScan(parameters.inBeamPosition, parameters.outOfBeamPosition, exposureTime=parameters.exposureTime, start=parameters.start, stop=parameters.stop, step=parameters.step, 
                 darkFieldInterval=parameters.darkFieldInterval,  flatFieldInterval=parameters.flatFieldInterval,
                  imagesPerDark=parameters.imagesPerDark, imagesPerFlat=parameters.imagesPerFlat, min_i=parameters.minI)    
        updateProgress(100,"Done");
    

def __test1_tomoScan():
    jns=beamline_parameters.JythonNameSpaceMapping()    
    sc=tomoScan(step=5, darkFieldInterval=5, flatFieldInterval=5,
             inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
    lsdp=jns.lastScanDataPoint()
    positions=lsdp.getPositionsAsDoubles()
    if positions[0] != 180. or positions[4] != 54.:
        print "Error - points are not correct :" + `positions`
    return sc

def __test2_tomoScan():
    jns=beamline_parameters.JythonNameSpaceMapping()    
    sc=tomoScan(step=5, darkFieldInterval=5, flatFieldInterval=0,
             inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
    lsdp=jns.lastScanDataPoint()
    positions=lsdp.getPositionsAsDoubles()
    if positions[0] != 180. or positions[4] != 47.:
        print "Error - points are not correct :" + `positions`
    return sc

def __test3_tomoScan():
    jns=beamline_parameters.JythonNameSpaceMapping()    
    sc=tomoScan(step=5, darkFieldInterval=0, flatFieldInterval=5,
             inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
    lsdp=jns.lastScanDataPoint()
    positions=lsdp.getPositionsAsDoubles()
    if positions[0] != 180. or positions[4] != 47.:
        print "Error - points are not correct :" + `positions`
    return sc

def __test4_tomoScan():
    jns=beamline_parameters.JythonNameSpaceMapping()    
    sc=tomoScan(step=5, darkFieldInterval=0, flatFieldInterval=0,
             inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
    lsdp=jns.lastScanDataPoint()
    positions=lsdp.getPositionsAsDoubles()
    if positions[0] != 180. or positions[4] != 40.:
        print "Error - points are not correct :" + `positions`
    return sc

def __test5_tomoScan():
    """
    Test optimizeBeamInterval=10
    """
    jns=beamline_parameters.JythonNameSpaceMapping()    
    sc=tomoScan(step=5, darkFieldInterval=0, flatFieldInterval=0,
             inBeamPosition=0., outOfBeamPosition=10., exposureTime=1., optimizeBeamInterval=10)
    lsdp=jns.lastScanDataPoint()
    positions=lsdp.getPositionsAsDoubles()
    if positions[0] != 180. or positions[4] != 43.:
        print "Error - points are not correct :" + `positions`
    return sc

def test_all():
    __test1_tomoScan()
    __test2_tomoScan()
    __test3_tomoScan()
    __test4_tomoScan()

def standardtomoScan():
    jns=beamline_parameters.JythonNameSpaceMapping()    
    sc=tomoScan(step=1, darkFieldInterval=0, flatFieldInterval=20,
             inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
    lsdp=jns.lastScanDataPoint()
    positions=lsdp.getPositionsAsDoubles()
    if positions[0] != 180. or positions[4] != 40.:
        print "Error - points are not correct :" + `positions`
    return sc

"""
Performs software triggered tomography
"""
from time import sleep
import datetime
import os
import sys

#from pcoDetectorWrapper import PCODetectorWrapper
from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import *
from gda.data.scan.datawriter.DataWriter import *
from gda.data.scan.datawriter.DefaultDataWriterFactory import \
    createDataWriterFromFactory
from gda.data.scan.datawriter.IDataWriterExtender import *
from gda.device.scannable import ScannableBase, ScannableUtils, SimpleScannable
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.jython import InterfaceProvider
from gda.jython.commands.ScannableCommands import createConcurrentScan
from gda.scan import ScanPositionProvider
from gda.util import OSCommandRunner
from gdascripts.messages import handle_messages
from gdascripts.metadata.metadata_commands import setTitle
from gdascripts.parameters import beamline_parameters
from java.lang import InterruptedException
from gdascripts.metadata.metadata_commands import meta_add


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
            print "Move To Open"
            self.delegate.asynchronousMoveTo("Open")
        else:
            print "Move To Close"
            self.delegate.asynchronousMoveTo("Close")
        # wait for 1s
        sleep(1.)
    def rawGetPosition(self):
        pos = self.delegate.getPosition()
        if pos == "Open":
            return 1 
        return 0

def make_tomoHelicalScanDevice(tomography_theta, tomography_shutter, tomography_translation, tomography_translation_vert,
                        image_key, tomography_imageIndex):

    tomoScanDevice = ScannableGroup()
    tomoScanDevice.addGroupMember(tomography_theta)
    tomoScanDevice.addGroupMember(EnumPositionerDelegateScannable("tomography_shutter", tomography_shutter))
    tomoScanDevice.addGroupMember(tomography_translation)
    tomoScanDevice.addGroupMember(tomography_translation_vert)
    tomoScanDevice.addGroupMember(image_key)
    tomoScanDevice.addGroupMember(tomography_imageIndex)
    tomoScanDevice.setName("tomoHelicalScanDevice")
    tomoScanDevice.configure()
    return tomoScanDevice

class   tomoHelicalScan_positions(ScanPositionProvider):
    def __init__(self, startVert, helicalPitch, start, totVertIncrInPitchUnits, step, darkFieldInterval, imagesPerDark, flatFieldInterval, imagesPerFlat,
             inBeamPosition, outOfBeamPosition, points):
        self.startVert = startVert
        self.helicalPitch = helicalPitch
        self.start = start
        self.totVertIncrInPitchUnits = totVertIncrInPitchUnits
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
        return "startVert: %f helicalPitch: %f start: %f totVertIncrInPitchUnits: %f step: %f Darks every: %d imagesPerDark: %d Flats every: %d imagesPerFlat: %d InBeamPosition: %f OutOfBeamPosition: %f numImages: %d " % \
            (self.startVert, self.helicalPitch, self.start, self.totVertIncrInPitchUnits, self.step, self.darkFieldInterval, self.imagesPerDark, self.flatFieldInterval, self.imagesPerFlat, self.inBeamPosition, self.outOfBeamPosition, self.size()) 
    def toString(self):
        return self.__str__()

def addNXTomoSubentry(scanObject, tomography_detector_name, tomography_theta_name):
    if scanObject is None:
        raise ValueError("Input scanObject must not be None")
   
    nxLinkCreator = NXTomoEntryLinkCreator()
   
    # detector independent items
    nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/ionc_i:NXpositioner/ionc_i:NXdata")
    nxLinkCreator.setInstrument_detector_image_key_target("entry1:NXentry/instrument:NXinstrument/tomoHelicalScanDevice:NXpositioner/image_key:NXdata")
    nxLinkCreator.setInstrument_source_target("entry1:NXentry/instrument:NXinstrument/source:NXsource")
   
    sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/tomoHelicalScanDevice:NXpositioner/"
    sample_rotation_angle_target += tomography_theta_name + ":NXdata"
    nxLinkCreator.setSample_rotation_angle_target(sample_rotation_angle_target);
    nxLinkCreator.setSample_x_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplex:NXdata")
    nxLinkCreator.setSample_y_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_sampley:NXdata")
    nxLinkCreator.setSample_z_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplez:NXdata")
   
    nxLinkCreator.setTitle_target("entry1:NXentry/title:NXdata")
   
    # detector dependent items
    if tomography_detector_name in ("pco1_hw_hdf", "pco1_hw_hdf_nochunking", "pco1_sw_hdf"):
        # external file
        instrument_detector_data_target = "!entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "data:SDS"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
    elif tomography_detector_name in ("pco1_hw_tif", "pco1_tif"):
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


def isLive():
    mode = LocalProperties.get("gda.mode")
    return mode =="live" or mode =="live_localhost"

image_key_dark = 2
image_key_flat = 1 # also known as bright
image_key_project = 0 # also known as sample



def tomoHelicalScan(description, inBeamPosition, outOfBeamPosition, exposureTime=1., startVert=0., helicalPitch=1., start=0., totVertIncrInPitchUnits=0.5, step=0.1, darkFieldInterval=0, flatFieldInterval=0,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1., addNXEntry=True, autoAnalyse=True, tomography_detector=None, additionalScannables=[]):
    """
    Function to perform a helical tomography step scan
    Arguments:
    description - description of the scan or the sample that is being scanned
        Note: This is generally user-specific information which gets saved in the NeXus file for reference
    inBeamPosition - position of X-motor to move sample into the beam to take a projection
    outOfBeamPosition - position of X-motor to move sample out of the beam to take a flat-field image
    exposureTime - exposure time in seconds (default = 1.0)
    startVert - position of Y-motor at the start of helical scan (default = 0.0)
    helicalPitch - pitch (linear length) of the helix along the Y direction (default = 1.0)
    start - first rotation angle (default = 0.0)
    totVertIncrInPitchUnits - total vertical increment measured in pitch units (default = 0.5)
    step - rotational step size (default = 0.1)
    darkFieldInterval - number of projections between each dark-field sub-sequence. 
        Note: At least 1 dark is ALWAYS taken both at the start and end of the scan, provided imagesPerDark > 0 
        (default = 0: use this value if you DON'T want to take any darks between projections)
    flatFieldInterval - number of projections between each flat-field sub-sequence. 
        Note: At least 1 flat is ALWAYS taken both at the start and end of the scan, provided imagesPerFlat > 0 
        (default = 0: use this value if you DON'T want to take any flats between projections)
    imagesPerDark - number of images to be taken for each dark-field sub-sequence (default = 20)
    imagesPerFlat - number of images to be taken for each flat-field sub-sequence (default = 20)
    
    General scan sequence is: D, F, P, ..., P, F, D
    where D stands for dark field, F - for flat field, and P - for projection.
    """
    print "Args START"
    if not tomography_detector is None:
        print "tomography_detector = %s" %(tomography_detector.getName()) 
    print "inBeamPosition = %.3f" %(inBeamPosition)
    print "outOfBeamPosition = %.3f" %(outOfBeamPosition)
    print "exposureTime = %.3f" %(exposureTime)
    print "start = %.3f" %(start)
    print "step = %.3f" %(step)
    
    print "startVert = %.3f" %(startVert)
    print "helicalPitch = %.3f" %(helicalPitch)
    print "totVertIncrInPitchUnits = %.3f" %(totVertIncrInPitchUnits)
    
    try:
        startTm = datetime.datetime.now();
        darkFieldInterval = int(darkFieldInterval)
        flatFieldInterval = int(flatFieldInterval)
        
        jns = beamline_parameters.JythonNameSpaceMapping()
        tomodet=jns.tomodet
        if tomodet is None:
	        raise NameError("tomodet is not defined in Jython namespace")

        tomography_theta = jns.tomography_theta
        if tomography_theta is None:
            raise NameError("tomography_theta is not defined in Jython namespace")
        tomography_shutter = jns.tomography_shutter
        if tomography_shutter is None:
            raise NameError("tomography_shutter is not defined in Jython namespace")
        tomography_translation = jns.tomography_translation
        if tomography_translation is None:
            raise NameError("tomography_translation is not defined in Jython namespace")
        
        tomography_translation_vert = jns.tomography_translation_vert
        if tomography_translation_vert is None:
            raise NameError("tomography_translation_vert is not defined in Jython namespace")
        
        tomography_detector = jns.tomography_detector
        if tomography_detector is None:
            raise NameError("tomography_detector is not defined in Jython namespace")

#        tomography_optimizer = jns.tomography_optimizer
#        if tomography_optimizer is None:
#            raise NameError("tomography_optimizer is not defined in Jython namespace")

        tomography_time = jns.tomography_time
        if tomography_time is None:
            raise NameError("tomography_time is not defined in Jython namespace")
        
        tomography_beammonitor = jns.tomography_beammonitor
        if tomography_beammonitor is None:
            raise NameError("tomography_beammonitor is not defined in Jython namespace")
        
        meta_add = jns.meta_add
        if meta_add is None:
            raise NameError("meta_add is not defined in Jython namespace")


        camera_stage = jns.cs1
        if camera_stage is None:
            raise NameError("camera_stage is not defined in Jython namespace")

        sample_stage = jns.sample_stage
        if sample_stage is None:
            raise NameError("sample_stage is not defined in Jython namespace")

        meta_add( camera_stage)
        meta_add( sample_stage)

        tomo_additional_scannables = jns.tomography_additional_scannables
        if tomo_additional_scannables is None:
            raise NameError("tomo_additional_scannables is not defined in Jython namespace")
        
        index = SimpleScannable()
        index.setCurrentPosition(0.0)
        index.setInputNames(["imageNumber"])
        index.setName("imageNumber")
        index.configure()
        
        image_key = SimpleScannable()
        image_key.setCurrentPosition(0.0)
        image_key.setInputNames(["image_key"])
        image_key.setName("image_key")
        image_key.configure()

        tomoScanDevice = make_tomoHelicalScanDevice(tomography_theta, tomography_shutter,
                                             tomography_translation, tomography_translation_vert, image_key, index)

#        return tomoScanDevice

        stop = start + (totVertIncrInPitchUnits * 360.0)
        
        #generate list of positions
        numberSteps = ScannableUtils.getNumberSteps(tomography_theta, start, stop, step)
        theta_points = []
        theta_points.append(start)
        previousPoint = start
        for i in range(numberSteps):
            nextPoint = ScannableUtils.calculateNextPoint(previousPoint, step);
            theta_points.append(nextPoint)
            previousPoint = nextPoint
               
        #print "theta_points..."
        #print theta_points
        
        numberStepsPerPitch = ScannableUtils.getNumberSteps(tomography_theta, 0.0, 360.0, step)
        stepVert = helicalPitch/numberStepsPerPitch
        stopVert = startVert + stepVert*numberSteps 
        
        #numberHelicalSteps = ScannableUtils.getNumberSteps(tomography_translation_vert, startVert, stopVert, stepVert)
        vert_points = [startVert]
        for v in range(numberSteps):
            vert_points.append(startVert + stepVert*(v+1))
            
        #print "vert_points..."
        #print vert_points
        
        #generateScanPoints
        shutterOpen = 1
        shutterClosed = 0
        scan_points = []
        theta_pos = theta_points[0]
        vert_pos = vert_points[0]
        tomoScanDevice.tomography_shutter.moveTo(shutterClosed)
        index = 0
        for d in range(imagesPerDark):
            scan_points.append((theta_pos, shutterClosed, inBeamPosition, vert_pos, image_key_dark, index)) #dark
            index = index + 1
                    
        for f in range(imagesPerFlat): 
            scan_points.append((theta_pos, shutterOpen, outOfBeamPosition, vert_pos, image_key_flat, index)) #flat
            index = index + 1        
        scan_points.append((theta_pos, shutterOpen, inBeamPosition, vert_pos, image_key_project, index)) #first proj
        index = index + 1        
        imageSinceDark = 1
        imageSinceFlat = 1
        for i in range(numberSteps):
            theta_pos = theta_points[i + 1]
            vert_pos = vert_points[i + 1]
            scan_points.append((theta_pos, shutterOpen, inBeamPosition, vert_pos, image_key_project, index))#main image
            index = index + 1        
            
            imageSinceFlat = imageSinceFlat + 1
            if imageSinceFlat == flatFieldInterval and flatFieldInterval != 0:
                for f in range(imagesPerFlat):
                    scan_points.append((theta_pos, shutterOpen, outOfBeamPosition, vert_pos, image_key_flat, index))
                    index = index + 1        
                    imageSinceFlat = 0
            
            imageSinceDark = imageSinceDark + 1
            if imageSinceDark == darkFieldInterval and darkFieldInterval != 0:
                for d in range(imagesPerDark):
                    scan_points.append((theta_pos, shutterClosed, inBeamPosition, vert_pos, image_key_dark, index))
                    index = index + 1        
                    imageSinceDark = 0
                
        #add dark and flat only if not done in last steps
        if imageSinceFlat != 0:
            for f in range(imagesPerFlat):
                scan_points.append((theta_pos, shutterOpen, outOfBeamPosition, vert_pos, image_key_flat, index)) #flat
                index = index + 1
        if imageSinceDark != 0:
            for d in range(imagesPerDark):
                scan_points.append((theta_pos, shutterClosed, inBeamPosition, vert_pos, image_key_dark, index)) #dark
                index = index + 1        

        #return None
        #print "scan_points..."
        #print scan_points
        #return
        #startVert=0., helicalPitch=1., start=0., totVertIncrInPitchUnits=0.5, step=0.1
        positionProvider = tomoHelicalScan_positions(startVert, helicalPitch, start, totVertIncrInPitchUnits, step, darkFieldInterval, imagesPerDark, flatFieldInterval, imagesPerFlat, \
                                               inBeamPosition, outOfBeamPosition, scan_points) 
        scan_args = [tomoScanDevice, positionProvider, tomography_time, tomography_beammonitor, tomography_detector, exposureTime]
        if min_i > 0.:
            import gdascripts.scannable.beamokay
            ionc_i = jns.ionc_i
            if ionc_i is None:
                raise NameError("ionc_i is not defined in Jython namespace")
            beamok=gdascripts.scannable.beamokay.WaitWhileScannableBelowThresholdMonitorOnly("beamok", ionc_i, min_i)
            scan_args.append(beamok)
       
        for scannable in additionalScannables:
            scan_args.append(scannable)

        if not (description is None): 
            setTitle(description)
        else :
            setTitle("undefined")
        
        scanObject = createConcurrentScan(scan_args)
        if addNXEntry:
            addNXTomoSubentry(scanObject, tomography_detector.name, tomography_theta.name)
        tomodet.stop()
        scanObject.runScan()
        if autoAnalyse:
            lsdp=jns.lastScanDataPoint()
            OSCommandRunner.runNoWait(["/dls_sw/apps/tomopy/tomopy/bin/gda/tomo_at_scan_end_kz", lsdp.currentFilename], OSCommandRunner.LOGOPTION.ALWAYS, None)
        
        #Close the fast shutter to prevent warming of sample
        tomography_shutter.moveTo( "Close")	
        #turn camera back on
        tomodet.setupForAlignment()
        
            
        return scanObject;
    except :
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Error in tomoScan", exceptionType, exception, traceback, True)
    finally:
        endTm = datetime.datetime.now()
        elapsedTm = endTm - startTm
        jns=beamline_parameters.JythonNameSpaceMapping()
        if isLive():
            print("This scan's data can be found in Nexus scan file %s." %(jns.lastScanDataPoint().currentFilename))
        print("Elapsed time (in the format [D day[s], ][H]H:MM:SS[.UUUUUU]): %s" %(str(elapsedTm)))


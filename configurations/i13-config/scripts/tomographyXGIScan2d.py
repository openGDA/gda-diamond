"""
Performs software triggered tomography
"""

from time import sleep
import datetime

from pcoDetectorWrapper import PCODetectorWrapper
from gda.jython.commands.ScannableCommands import inc, scan, pos, createConcurrentScan
from gda.scan import ConstantVelocityScanLine, MultiScanItem, MultiScanRunner, ConcurrentScan

import sys
import time
import shutil
import gda
from gdascripts.parameters import beamline_parameters
from gdascripts.messages import handle_messages
from gda.device.scannable import ScannableBase, SimpleScannable
from gda.device.detector import DetectorBase
from gda.scan import ScanPositionProvider
from gda.device.scannable import ScannableBase, ScannableUtils
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.factory import Finder
from gda.util import OSCommandRunner
from gda.data.scan.datawriter.DefaultDataWriterFactory import createDataWriterFromFactory
from gda.data.scan.datawriter import *

from gda.commandqueue import JythonScriptProgressProvider


def updateProgress( percent, msg):
    JythonScriptProgressProvider.sendProgress( percent, msg)
    print "percentage %d %s" % (percent, msg)


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


def make_tomoScanDeviceOLD(tomography_theta, tomography_shutter, tomography_translation, 
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


def make_tomoScanDevice(scannables, name="tomoScanDevice"):
    tomoScanDevice = ScannableGroup()
    for s in scannables:
        tomoScanDevice.addGroupMember(s)
    tomoScanDevice.setName(name)
    tomoScanDevice.configure()
    return tomoScanDevice


class   tomoScan_positions(ScanPositionProvider):
    def __init__(self, start, stop, step, startGratingOuter, stopGratingOuter, stepGratingOuter, startGratingInner, stopGratingInner, stepGratingInner, darkFieldInterval, imagesPerDark, flatFieldInterval, imagesPerFlat,
             inBeamPosition, outOfBeamPosition, points):
        self.start = start
        self.stop = stop
        self.step = step
        self.startGratingOuter = startGratingOuter
        self.stopGratingOuter = stopGratingOuter
        self.stepGratingOuter = stepGratingOuter
        self.startGratingInner = startGratingInner
        self.stopGratingInner = stopGratingInner
        self.stepGratingInner = stepGratingInner
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
        return "Start: %f Stop: %f Step: %f StartGratingOuter: %f StopGratingOuter: %f StepGratingOuter: %f StartGratingInner: %f StopGratingInner: %f StepGratingInner: %f Darks every:%d imagesPerDark:%d Flats every: %d imagesPerFlat: %d InBeamPosition: %f OutOfBeamPosition: %f numImages %d " % \
            ( self.start, self.stop, self.step, self.startGratingOuter, self.stopGratingOuter, self.stepGratingOuter, self.startGratingInner, self.stopGratingInner, self.stepGratingInner, self.darkFieldInterval,self.imagesPerDark, self.flatFieldInterval, self.imagesPerFlat, self.inBeamPosition, self.outOfBeamPosition, self.size() ) 
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
    nxLinkCreator.setSample_x_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplex:NXdata")
    nxLinkCreator.setSample_y_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_sampley:NXdata")
    nxLinkCreator.setSample_z_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplez:NXdata")
   
    nxLinkCreator.setTitle_target("entry1:NXentry/title:NXdata")
   
    # detector dependent items
    if tomography_detector_name == "pco1_hw_hdf" or tomography_detector_name == "pco1_hw_hdf_nochunking":
        # external file
        instrument_detector_data_target = "!entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "data:SDS"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
    elif tomography_detector_name == "pco1_hw_tif" or tomography_detector_name == "pco1_tif":
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


def addFlyScanNXTomoSubentry(scanObject, tomography_detector_name, tomography_theta_name, externalhdf=True):
    if scanObject is None:
        raise "Input scanObject must not be None"
   
    nxLinkCreator = NXTomoEntryLinkCreator()
   
    # detector independent items
    nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/ionc_i:NXpositioner/ionc_i:NXdata")
    nxLinkCreator.setInstrument_detector_image_key_target("entry1:NXentry/instrument:NXinstrument/image_key:NXpositioner/image_key:NXdata")
    nxLinkCreator.setInstrument_source_target("entry1:NXentry/instrument:NXinstrument/source:NXsource")
   
    sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/" + tomography_theta_name + ":NXpositioner/"
    sample_rotation_angle_target += tomography_theta_name + ":NXdata"
    nxLinkCreator.setSample_rotation_angle_target(sample_rotation_angle_target);
    nxLinkCreator.setSample_x_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplex:NXdata")
    nxLinkCreator.setSample_y_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_sampley:NXdata")
    nxLinkCreator.setSample_z_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplez:NXdata")
   
    nxLinkCreator.setTitle_target("entry1:NXentry/title:NXdata")
   
    # detector dependent items
    if externalhdf:
        # external file
        instrument_detector_data_target = "!entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "data:SDS"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
    else:
        # image filenames
        instrument_detector_data_target = "entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "image_data:NXdata"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
   
    nxLinkCreator.afterPropertiesSet()
   
    dataWriter = createDataWriterFromFactory()
    subEntryWriter = NXSubEntryWriter(nxLinkCreator)
    dataWriter.addDataWriterExtender(subEntryWriter)
    scanObject.setDataWriter(dataWriter)


def reportJythonNamespaceMapping():
    jns=beamline_parameters.JythonNameSpaceMapping()
    objectOfInterest = {}
    objectOfInterest['tomography_normalisedImage_detector']=jns.tomography_normalisedImage_detector
    
    objectOfInterestSTEP = {}
    objectOfInterestSTEP['tomography_theta'] = jns.tomography_theta
    objectOfInterestSTEP['tomography_shutter'] = jns.tomography_shutter
    objectOfInterestSTEP['tomography_translation'] = jns.tomography_translation
    objectOfInterestSTEP['tomography_detector'] = jns.tomography_detector
    objectOfInterestSTEP['tomography_beammonitor'] = jns.tomography_beammonitor

    objectOfInterestFLY = {}
    objectOfInterestFLY['tomography_flyscan_theta'] = jns.tomography_flyscan_theta
    objectOfInterestFLY['tomography_shutter'] = jns.tomography_shutter
    objectOfInterestFLY['tomography_translation'] = jns.tomography_translation
    objectOfInterestFLY['tomography_flyscan_det'] = jns.tomography_flyscan_det
    objectOfInterestFLY['tomography_flyscan_flat_dark_det'] = jns.tomography_flyscan_flat_dark_det

    objectOfInterestXGI = {}
    objectOfInterestFLY['tomography_grating_translation'] = jns.tomography_grating_translation
    objectOfInterestFLY['tomography_grating_translation_outer'] = jns.tomography_grating_translation_outer
    objectOfInterestFLY['tomography_grating_translation_inner'] = jns.tomography_grating_translation_inner
    
    msg = "\n These mappings can be changed by editing a file named live_jythonNamespaceMapping, "
    msg += "\n located in i13-config/scripts (this can be done by beamline staff).\n"

    print "****** NORMALISED IMAGE SETTINGS ******"
    idx=1
    for key, val in objectOfInterest.iteritems():
        name = "object undefined!"
        if val is not None:
            name = str(val.getName())
        print `idx` + "."+ key + ' = ' + name
        idx += 1
    print msg
    
    print "****** STEP-SCAN PRIMARY SETTINGS ******"
    idx=1
    for key, val in objectOfInterestSTEP.iteritems():
        name = "object undefined!"
        if val is not None:
            name = str(val.getName())
        print `idx` + "."+ key + ' = ' + name
        idx += 1
    print msg

    print "****** FLY-SCAN PRIMARY SETTINGS ******"
    idx=1
    for key, val in objectOfInterestFLY.iteritems():
        name = "object undefined!"
        if val is not None:
            name = str(val.getName())
        print `idx` + "."+ key + ' = ' + name
        idx += 1
    print msg

    print "****** XGI-SCAN PRIMARY SETTINGS ******"
    idx=1
    for key, val in objectOfInterestXGI.iteritems():
        name = "object undefined!"
        if val is not None:
            name = str(val.getName())
        print `idx` + "."+ key + ' = ' + name
        idx += 1
    print msg

def reportTomo():
    return reportJythonNamespaceMapping()

from gda.device.scannable import SimpleScannable
image_key_dark=2
image_key_flat=1 # also known as bright
image_key_project=0 # also known as sample


from java.lang import Runnable
class PreScanRunnable(Runnable):
    def __init__(self, msg, percentage, shutter, shutterPosition, xMotor, xMotorPosition, image_key, image_key_value, thetaMotor, thetaMotorPosition):
        self.msg = msg
        self.percentage = percentage
        self.shutter=shutter
        self.shutterPosition = shutterPosition
        self.xMotor = xMotor
        self.xMotorPosition =xMotorPosition
        self.image_key =image_key
        self.image_key_value =image_key_value
        self.thetaMotor = thetaMotor
        self.thetaMotorPosition =thetaMotorPosition
        
    def run(self):
        updateProgress(self.percentage, self.msg)
        updateProgress(self.percentage, "Move x")
        self.xMotor.moveTo(self.xMotorPosition)
        updateProgress(self.percentage, "Move theta")
        self.thetaMotor.moveTo(self.thetaMotorPosition)
        updateProgress(self.percentage, "Move shutter")
        self.shutter.moveTo(self.shutterPosition)
        self.image_key.moveTo(self.image_key_value)
        updateProgress(self.percentage, self.msg)



def testElapsedInterval(index, offset_dark, offset_flat, fieldInterval):
    return (index - offset_dark - offset_flat + 1) % (fieldInterval+1)

"""
perform a simple tomography scan
"""
def tomoXGIScan2d(inBeamPosition, outOfBeamPosition, exposureTime=1, start=-90., stop=90., step=0.1, startGratingOuter=0., stopGratingOuter=13.0, stepGratingOuter=1.0, startGratingInner=0., stopGratingInner=13.0, stepGratingInner=1.0, darkFieldInterval=0, flatFieldInterval=0,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1., addNXEntry=True, autoAnalyse=False,  flatFieldAngle=None, tomography_detector=None, additionalScannables=[]):
    """
    Function to collect 2-dim grating-interferometry tomogram
 	Arg(s):
    inBeamPosition - position of X-drive to move sample into the beam to take a projection frame
    outOfBeamPosition - position of X-drive to move sample out of the beam to take a flat-field frame
    exposureTime - exposure time in seconds (default = 1)
    start - first rotation angle (default = 0.)
    stop  - last rotation angle (default = 180.)
    step - angular step size for moving rotation stage (default = 0.1)
    startGratingOuter - first grating position for the outer translation loop (default = 0.)
    stopGratingOuter  - last grating position for the outer translation loop (default = 13.)
    stepGratingOuter - step size for moving the grating in the outer translation loop (default = 1.0)
         Note: the outer loop is sometimes referred to as the 'slow' axis
    startGratingInner - first grating position for the inner translation loop (default = 0.)
    stopGratingInner  - last grating position for the inner translation loop (default = 13.)
    stepGratingInner - step size for moving the grating in the inner translation loop (default = 1.0)
        Note: the inner loop is sometimes referred to as the 'fast' axis
    darkFieldInterval - number of projection frames to be collected between each dark-field series (default = 0, ie not taking any mid-scan darks) 
        Note: a single (contiguous) dark-field series is always collected both at the start and the end of scan, provided imagesPerDark > 0
    flatFieldInterval - number of projection frames to be collected between each flat-field series (default = 0, ie not taking any mid-scan flats))
        Note: a single (contiguous) flat-field series is always collected both at the start and the end of scan, provided imagesPerFlat > 0
    imagesPerDark - number of dark-field frames to be collected at every qualifying scan point (default = 20)
        Note: All frames belonging to the same (single) dark-field series are collected at the same (current) position of the grating (and the same (current) 
        angular position) and therefore each contiguous dark-field series is comprised of 
            imagesPerDark 
        frames only. 
    imagesPerFlat - number of flat-field frames to be collected at every qualifying scan point (default = 20)
        Note: Frames belonging to the same (single) flat-field series are collected at every position of the grating and therefore 
        each contiguous flat-field series is comprised of
            imagesPerFlat x [1 + (stopGratingOuter - startGratingOuter)/stepGratingOuter] x [1 + (stopGratingInner - startGratingInner)/stepGratingInner] 
        frames.
    min_i - minimum value of ion chamber current required to take an image (default = -1). A negative value means that the value is not checked
    flatFieldAngle - if equal to None, each flat-field frame is collected at the current angular position as the stage rotates during the scan 
        (with the first flat-field frame being taken at the start angle). If equal to a finite number, all flat-field frames (and series) are 
        collected at this particular angular position after rotating back to it (this option is useful if, for some reason, sample can't be moved out 
        of the beam for some angles).

    """
    try:
        startTm = datetime.datetime.now()
        if flatFieldAngle is None:
            print "Flat fields will be taken at the most recent angle as the stage rotates during the scan, with the first one being taken at the scan start angle of %.4f deg" %(start)
        else:
            print "All flat fields will be taken at the same, user-supplied angle of %.4f deg" %(flatFieldAngle)
            if start < stop:
                min_ang = start
                max_ang = stop
            else:
                min_ang = stop
                max_ang = start 
            if flatFieldAngle < min_ang or flatFieldAngle > max_ang:
                print "WARNING: All flat fields will be taken at the same, user-supplied angle of %.4f deg which is outside the scanning range of [%.4f, %.4f]!" %(flatFieldAngle, start, stop)

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
        

        if tomography_detector is None:
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

        tomography_grating_translation_outer=jns.tomography_grating_translation_outer
        if tomography_grating_translation_outer is None:
            raise "tomography_grating_translation_outer is not defined in Jython namespace"

        tomography_grating_translation_inner=jns.tomography_grating_translation_inner
        if tomography_grating_translation_inner is None:
            raise "tomography_grating_translation_inner is not defined in Jython namespace"

        meta_add = jns.meta_add
        if meta_add is None:
            raise "meta_add is not defined in Jython namespace"


        camera_stage = jns.cs1
        if camera_stage is None:
            raise "camera_stage is not defined in Jython namespace"

        sample_stage = jns.sample_stage
        if sample_stage is None:
            raise "sample_stage is not defined in Jython namespace"

        meta_add( camera_stage)
        meta_add( sample_stage)


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

        tomoScannables = [tomography_theta, EnumPositionerDelegateScannable("tomography_shutter", tomography_shutter), tomography_translation, tomography_grating_translation_outer, tomography_grating_translation_inner, image_key, index]

        tomoScanDevice = make_tomoScanDevice(tomoScannables)

#        return tomoScanDevice
        #generate list of positions
        numberSteps = ScannableUtils.getNumberSteps(tomography_theta, start, stop, step)
        print "numberSteps = %i" %(numberSteps)
        theta_points = []
        theta_points.append(start)
        previousPoint = start
        for i in range(numberSteps):
            nextPoint = ScannableUtils.calculateNextPoint(previousPoint, step);
            theta_points.append(nextPoint)
            previousPoint = nextPoint
            
        print "theta_points..."
        #print theta_points
        
        numberStepsGrating_outer = ScannableUtils.getNumberSteps(tomography_grating_translation_outer, startGratingOuter, stopGratingOuter, stepGratingOuter)
        print "numberStepsGrating_outer = %i" %(numberStepsGrating_outer)
        numberStepsGrating_inner = ScannableUtils.getNumberSteps(tomography_grating_translation_inner, startGratingInner, stopGratingInner, stepGratingInner)
        print "numberStepsGrating_inner = %i" %(numberStepsGrating_inner)
        grating_points_outer = []
        grating_points_outer.append(startGratingOuter)
        previousPoint_outer = startGratingOuter
        for i in range(numberStepsGrating_outer):
            nextPoint_outer = ScannableUtils.calculateNextPoint(previousPoint_outer, stepGratingOuter);
            grating_points_outer.append(nextPoint_outer)
            previousPoint_outer = nextPoint_outer
        print "grating_points_outer..."
        #print grating_points_outer

        grating_points_inner = []
        grating_points_inner.append(startGratingInner)
        previousPoint_inner = startGratingInner
        for j in range(numberStepsGrating_inner):
            nextPoint_inner = ScannableUtils.calculateNextPoint(previousPoint_inner, stepGratingInner);
            grating_points_inner.append(nextPoint_inner)
            previousPoint_inner = nextPoint_inner
        #print "grating_points_inner..."
        #print grating_points_inner

        grating_points = [] 
        for outerPt in grating_points_outer:
            for innerPt in grating_points_inner:
                grating_points.append((outerPt, innerPt))

        #print "grating_points..."
        #print grating_points


        shutterOpen=1
        shutterClosed=0
        scan_points = []
        theta_pos = theta_points[0]
        grating_pos = grating_points[0]
        tomoScanDevice.tomography_shutter.moveTo(shutterClosed) 
        index=0
        offset_dark=0
        offset_flat=0
        for d in range(imagesPerDark):
            scan_points.append((theta_pos, shutterClosed, inBeamPosition) + grating_pos + (image_key_dark, index)) #dark
            index = index + 1
            offset_dark += 1
        
        for f in range(imagesPerFlat):
            for pt in grating_points:
                grating_pos = pt
                scan_points.append((theta_pos if flatFieldAngle is None else flatFieldAngle, shutterOpen, outOfBeamPosition) + grating_pos + (image_key_flat, index)) #flat
                index = index + 1
                offset_flat += 1
        
        imageSinceDark=0
        imageSinceFlat=0
        print "at 1"
        for pt0 in grating_points:
            #print "first batch test flat = %i, index = %i " % (testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval), index)
            #if flatFieldInterval != 0 and (not testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval)):
            if (flatFieldInterval != 0) and (imageSinceFlat == flatFieldInterval):
                #print "adding first-batch mid-scan flats at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval))
                for f in range(imagesPerFlat):
                    for pt1 in grating_points:
                        grating_pos = pt1
                        scan_points.append((theta_pos if flatFieldAngle is None else flatFieldAngle, shutterOpen, outOfBeamPosition) + grating_pos + (image_key_flat, index))
                        index = index + 1
                        offset_flat += 1
                imageSinceFlat = 0
            #if darkFieldInterval != 0 and (not testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval)):
            if (darkFieldInterval != 0) and (imageSinceDark == darkFieldInterval):
                #print "adding first-batch mid-scan darks at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval))
                for d in range(imagesPerDark):
                    scan_points.append((theta_pos, shutterClosed, inBeamPosition) + grating_pos + (image_key_dark, index))
                    index = index + 1
                    offset_dark += 1
                imageSinceDark = 0
            grating_pos = pt0
            scan_points.append((theta_pos, shutterOpen, inBeamPosition) + grating_pos + (image_key_project, index)) #first sample batch
            index = index + 1
            imageSinceDark += 1
            imageSinceFlat += 1

        print "at 2"
        for i in range(numberSteps):
            theta_pos = theta_points[i+1]
            for pt0 in grating_points:
                #print "main test flat = %i, index = %i" % (testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval), index)
                #if flatFieldInterval != 0 and (not testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval)):
                if (flatFieldInterval != 0) and (imageSinceFlat == flatFieldInterval):
                    #print "adding main mid-scan flats at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval))
                    for f in range(imagesPerFlat):
                        for pt1 in grating_points:
                            grating_pos = pt1
                            scan_points.append((theta_pos if flatFieldAngle is None else flatFieldAngle, shutterOpen, outOfBeamPosition) + grating_pos + (image_key_flat, index))
                            index = index + 1
                            offset_flat += 1
                    imageSinceFlat = 0
                #if darkFieldInterval != 0 and (not testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval)):
                if (darkFieldInterval != 0) and (imageSinceDark == darkFieldInterval):
                    #print "adding main mid-scan darks at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval))
                    for d in range(imagesPerDark):
                        scan_points.append((theta_pos, shutterClosed, inBeamPosition) + grating_pos + (image_key_dark, index))
                        index = index + 1
                        offset_dark += 1
                    imageSinceDark = 0
                grating_pos = pt0
                scan_points.append((theta_pos, shutterOpen, inBeamPosition) + grating_pos + (image_key_project, index)) #main sample
                index = index + 1
                imageSinceDark += 1
                imageSinceFlat += 1
        
        print "at 3"
        #add dark and flat only if not done in last steps
        #print "after test flat = %i, index = %i" % (testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval), index)
        #if not testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval):
        if (imageSinceFlat != 0):
            #print "adding flats after at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval))
            for f in range(imagesPerFlat):
                for pt1 in grating_points:
                    grating_pos = pt1
                    scan_points.append((theta_pos if flatFieldAngle is None else flatFieldAngle, shutterOpen, outOfBeamPosition) + grating_pos + (image_key_flat, index)) #flat
                    index = index + 1
                    offset_flat += 1
        #if not testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval):
        if (imageSinceDark != 0):
            #print "adding darks after at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval))
            for d in range(imagesPerDark):
                scan_points.append((theta_pos, shutterClosed, inBeamPosition) + grating_pos + (image_key_dark, index)) #dark
                index = index + 1
                offset_dark += 1
                
        print "positionProvider"
        positionProvider = tomoScan_positions( start, stop, step, startGratingOuter, stopGratingOuter, stepGratingOuter, startGratingInner, stopGratingInner, stepGratingInner, darkFieldInterval, imagesPerDark, flatFieldInterval, imagesPerFlat, \
                                               inBeamPosition, outOfBeamPosition, scan_points )
        #print "scan_points..."
        #print "(Ang, Shut, xTran, GratOut, GratInn, ImgKey, index)"
        #for x in scan_points:
        #    print x
        #return 
        print "at 4"
        scan_args = [tomoScanDevice, positionProvider, tomography_time, tomography_beammonitor, tomography_detector, exposureTime ]
        if min_i > 0.:
            import gdascripts.scannable.beamokay
            ionc_i = jns.ionc_i
            if ionc_i is None:
                raise "ionc_i is not defined in Jython namespace"
            beamok=gdascripts.scannable.beamokay.WaitWhileScannableBelowThresholdMonitorOnly("beamok", ionc_i, min_i)
            scan_args.append(beamok)
            
        for scannable in additionalScannables:
            scan_args.append(scannable)
            
        print "Creating scan object"
        scanObject=createConcurrentScan(scan_args)
        print "Creating scan object - after"
        if addNXEntry and False:
            addNXTomoSubentry(scanObject, tomography_detector.name, tomography_theta.name)
        tomodet.stop()
        print "About to run the scan"
        scanObject.runScan()
        print "Finished running the scan"
        if autoAnalyse:
            lsdp=jns.lastScanDataPoint()
            OSCommandRunner.runNoWait(["/dls_sw/apps/tomopy/tomopy/bin/gda/tomo_at_scan_end", lsdp.currentFilename], OSCommandRunner.LOGOPTION.ALWAYS, None)
        
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
        print("Elapsed time (in the format [D day[s], ][H]H:MM:SS[.UUUUUU]): %s" %(str(elapsedTm)))


from gda.commandqueue import JythonScriptProgressProvider
def updateProgress( percent, msg):
    JythonScriptProgressProvider.sendProgress( percent, msg)
    print "percentage %d %s" % (percent, msg)
    
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

"""
Performs software triggered tomography
"""

from time import sleep

#from pcoDetectorWrapper import PCODetectorWrapper
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
    def __init__(self, start, stop, step, startGrating, stopsample_stageGrating, stepGrating, darkFieldInterval, imagesPerDark, flatFieldInterval, imagesPerFlat,
             inBeamPosition, outOfBeamPosition, points):
        self.start = start
        self.stop = stop
        self.step = step
        self.startGrating = startGrating
        self.stopGrating = stopGrating
        self.stepGrating = stepGrating
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
        return "Start: %f Stop: %f Step: %f StartGrating: %f StopGrating: %f StepGrating: %f Darks every:%d imagesPerDark:%d Flats every:%d imagesPerFlat:%d InBeamPosition:%f OutOfBeamPosition:%f numImages %d " % \
            ( self.start, self.stop, self.step, self.startGrating, self.stopGrating, self.stepGrating, self.darkFieldInterval,self.imagesPerDark, self.flatFieldInterval, self.imagesPerFlat, self.inBeamPosition, self.outOfBeamPosition, self.size() ) 
    def toString(self):
        return self.__str__()

def addNXTomoSubentry(scanObject, tomography_detector_name, tomography_theta_name):
    if scanObject is None:
        raise ValueError("Input scanObject must not be None")
   
    nxLinkCreator = NXTomoEntryLinkCreator()
    default_placeholder_target = "entry1:NXentry/scan_identifier:NXdata"
   
    # detector independent items
    #nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/ionc_i:NXpositioner/ionc_i:NXdata")
    nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/source:NXsource/current:NXdata")
    nxLinkCreator.setInstrument_detector_image_key_target("entry1:NXentry/instrument:NXinstrument/tomoScanDevice:NXpositioner/image_key:NXdata")
    nxLinkCreator.setInstrument_source_target("entry1:NXentry/instrument:NXinstrument/source:NXsource")
   
    sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/tomoScanDevice:NXpositioner/"
    sample_rotation_angle_target += tomography_theta_name + ":NXdata"
    nxLinkCreator.setSample_rotation_angle_target(sample_rotation_angle_target);
    #nxLinkCreator.setSample_x_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/t1_sx:NXdata")
    #nxLinkCreator.setSample_y_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/t1_sy:NXdata")
    #nxLinkCreator.setSample_z_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/t1_sz:NXdata")
    nxLinkCreator.setSample_x_translation_target(default_placeholder_target)
    nxLinkCreator.setSample_y_translation_target(default_placeholder_target)
    nxLinkCreator.setSample_z_translation_target(default_placeholder_target)
   
    nxLinkCreator.setTitle_target("entry1:NXentry/title:NXdata")
   
    # detector dependent items
    if tomography_detector_name in ("pco1_hw_hdf", "pco1_hw_hdf_nochunking", "pco1_sw_hdf_nochunking"):
        # external file
        instrument_detector_data_target = "!entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "data:SDS"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
    elif tomography_detector_name in ("pco1_hw_tif", "pco1_tif", "pco1_sw_tif"):
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
        raise ValueError("Input scanObject must not be None")
   
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
def tomoXGIScan(inBeamPosition, outOfBeamPosition, exposureTime=1., start=0.0, stop=180.0, step=0.1, startGrating=0., stopGrating=13.0, stepGrating=1.0, darkFieldInterval=0, flatFieldInterval=0,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1., addNXEntry=True, autoAnalyse=False, tomography_detector=None, additionalScannables=[], **kwargs):
    """
    Function to collect (1d) grating-interferometry tomogram
 	Arguments:
    inBeamPosition - position of linear motor to move sample into the beam to take a sample-projection image
    outOfBeamPosition - position of linear motor to move sample out of the beam to take a flat-field image
    exposureTime - exposure time in seconds (default = 1.)
    start - first rotation angle (default = 0.)
    stop  - last rotation angle (default = 180.)
    step - rotational step size (default = 0.1)
    startGrating - first grating position (default = 0.)
    stopGrating  - last grating position (default = 13.)
    stepGrating - step size for moving between any two consecutive grating positions (default = 1.0)
    darkFieldInterval - number of projection frames (as opposed to projection series) between any two consecutive dark-field collections (default = 0, for not taking any intermediate darks) 
        Note: A single dark-field collection (consisting of imagesPerDark frames) is always performed both at the start and the end of the scan, provided imagesPerDark > 0
    flatFieldInterval - number of projection frames (as opposed to projection series) between any two consecutive flat-field collections (default = 0, for not taking any intermediate flats))
        Note: A single flat-field series (consisting of imagesPerFlat x [1 + (stopGrating - startGrating)/stepGrating] frames) is always performed both at the start and the end of scan, provided imagesPerFlat > 0
    imagesPerDark - number of dark-field frames in each dark-field collection (default = 20)
        Note: the total number of dark-field frames in a single dark-field collection is equal to imagesPerDark
    imagesPerFlat - number of flat-field series in each flat-field collection (default = 20)
        Note: the total number of flat-field frames in a single flat-field series is equal to imagesPerFlat x [1 + (stopGrating - startGrating)/stepGrating]
    min_i - minimum value of ion chamber current required to take an image (default = -1). A negative value means that the value is not checked
    
    kwargs - for specifying any combination of the following optional key-word arguments: 
        tomography_theta, tomography_shutter, tomography_translation, tomography_beammonitor, tomography_time, sample_stage, tomography_grating_translation 
        Note(s): 
		(1) Note that tomography_detector is a dedicated positional argument (hence it is not included in kwargs) 
		(2) If no key-word arguments are supplied, the settings defined in live_jythonNamespaceMapping are used 
		(3) If a particular key-word argument is supplied, it will override the corresponding setting defined in live_jythonNamespaceMapping (if that setting is present)
		(4) Example: to specify pco1_sw_tif as tomography_detector and grt_theta as tomography_grating_translation, execute the following type of command:
			tomoXGIScan(inBeamPosition, outOfBeamPosition, exposureTime=1.,
 				start=0.0, stop=180.0, step=0.1,
				startGrating=0., stopGrating=13.0, stepGrating=1.0,
				darkFieldInterval=0, flatFieldInterval=0, imagesPerDark=20, imagesPerFlat=20,
				tomography_detector=pco1_sw_tif, tomography_grating_translation=grt_theta)     

    """
    try:
        darkFieldInterval=int(darkFieldInterval)
        flatFieldInterval=int(flatFieldInterval)

        objXGI = []
        objXGI.append('tomography_theta')
        objXGI.append('tomography_shutter')
        objXGI.append('tomography_translation')
        objXGI.append('tomography_detector')           # note this is a positional arg, so it has to be supplied as such as opposed being supplied in kwargs!
        objXGI.append('tomography_beammonitor')
        objXGI.append('tomography_time')
        objXGI.append('sample_stage')
        objXGI.append('tomography_grating_translation')
        
        if kwargs is not None and len(kwargs)>0:
            print "\n *** Found %i kwargs: " %(len(kwargs)) , kwargs
            #print kwargs, len(kwargs)
        else:
            print("\n *** kwargs not found")
        
        # use kwargs value to set obj or set it to None
        for k_str in objXGI:
            if (kwargs is not None) and kwargs.has_key(k_str) and (kwargs[k_str] is not None):
                exec("%s=Finder.getInstance().find(\"%s\")" %(kwargs[k_str].getName(), kwargs[k_str].getName()))
                exec(k_str + "=%s" %(kwargs[k_str].getName()))
                if eval(k_str +" is None"):
                    try:
                        print kwargs[k_str].getName() 
                        eval(kwargs[k_str].getName())
                        msg = k_str + "=%s" %(kwargs[k_str].getName())
                        print msg
                        exec(k_str + "=%s" %(kwargs[k_str].getName()))
                        print "this appears to have worked fine without Finder for %s and %s" %(k_str, kwargs[k_str].getName())
                        #sleep(10)
                        eval(k_str)
                        if eval(k_str +" is None"):
                            print "is None for %s!" %(k_str)
                    except Exception, ex:
                        print "got except..."
                        print k_str, ex
                else:
                    print "is not None for %s!" %(k_str)
            else:
                #if k_str != 'tomography_detector':
                #    print k_str
                #    exec(k_str + "=" + "None")
                try:
                    eval(k_str)
                    #print k_str
                except Exception, ex:
                    print k_str, ex
                    exec(k_str + "=" + "None")
        
        #print tomography_grating_translation.getName()
        jns=beamline_parameters.JythonNameSpaceMapping()
#        tomodet=jns.tomodet
#        if tomodet is None:
#	        raise NameError("tomodet is not defined in Jython namespace")


        # use jns values
        for k_str in objXGI:
            if eval(k_str +" is None"):
                exec(k_str + "=" + "jns."+k_str)
                print "imposing jns value for %s" %(k_str)
            else:
                print "keeping kwargs value for %s" %(k_str)
        
        # final sanity test
        print "\n *** This tomoXGIScan is set to use:" 
        for k_str in objXGI:
            if eval("%s is None" %(k_str)):
                msg = k_str + " is not defined"
                raise msg
            else:
                print "%s = %s" %(k_str, eval("%s.getName()" %(k_str)))

        #tomography_theta=jns.tomography_theta
        #if tomography_theta is None:
        #    raise NameError("tomography_theta is not defined in Jython namespace")
        #tomography_shutter=jns.tomography_shutter
        #if tomography_shutter is None:
        #    raise NameError("tomography_shutter is not defined in Jython namespace")
        #tomography_translation=jns.tomography_translation
        #if tomography_translation is None:
        #    raise NameError("tomography_translation is not defined in Jython namespace")
        

        #if tomography_detector is None:
	#        tomography_detector=jns.tomography_detector
        #if tomography_detector is None:
        #    raise NameError("tomography_detector is not defined in Jython namespace")

#        tomography_optimizer=jns.tomography_optimizer
#        if tomography_optimizer is None:
#            raise NameError("tomography_optimizer is not defined in Jython namespace")

        #tomography_time=jns.tomography_time
        #if tomography_time is None:
        #    raise NameError("tomography_time is not defined in Jython namespace")
        
        #tomography_beammonitor=jns.tomography_beammonitor
        #if tomography_beammonitor is None:
        #    raise NameError("tomography_beammonitor is not defined in Jython namespace")

        #tomography_grating_translation=jns.tomography_grating_translation
        #if tomography_grating_translation is None:
        #    raise NameError("tomography_grating_translation is not defined in Jython namespace")

        meta_add = jns.meta_add
        if meta_add is None:
            raise NameError("meta_add is not defined in Jython namespace")


#        camera_stage = jns.cs1
#        if camera_stage is None:
#            raise NameError("camera_stage is not defined in Jython namespace")

        sample_stage = jns.sample_stage
        if sample_stage is None:
            raise NameError("sample_stage is not defined in Jython namespace")

#        meta_add( camera_stage)
        meta_add( sample_stage)
        return

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

        tomoScannables = [tomography_theta, EnumPositionerDelegateScannable("tomography_shutter", tomography_shutter), tomography_translation, tomography_grating_translation, image_key, index]

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
            
        #print "theta_points..."
        #print theta_points
        
        numberStepsGrating = ScannableUtils.getNumberSteps(tomography_grating_translation, startGrating, stopGrating, stepGrating)
        print "numberStepsGrating = %i" %(numberStepsGrating)
        grating_points = []
        grating_points.append(startGrating)
        previousPoint = startGrating
        for i in range(numberStepsGrating):
            nextPoint = ScannableUtils.calculateNextPoint(previousPoint, stepGrating);
            grating_points.append(nextPoint)
            previousPoint = nextPoint
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
            scan_points.append((theta_pos, shutterClosed, inBeamPosition, grating_pos, image_key_dark, index )) #dark
            index = index + 1
            offset_dark += 1
        
        for f in range(imagesPerFlat):
            for j in range(numberStepsGrating+1):
                grating_pos = grating_points[j]
                scan_points.append((theta_pos, shutterOpen, outOfBeamPosition, grating_pos, image_key_flat, index )) #flat
                index = index + 1
                offset_flat += 1
        
        imageSinceDark=0
        imageSinceFlat=0
        for j in range(numberStepsGrating+1):
            #print "first batch test flat = %i, index = %i " % (testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval), index)
            #if flatFieldInterval != 0 and (not testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval)):
            if (flatFieldInterval != 0) and (imageSinceFlat == flatFieldInterval):
                #print "adding first-batch mid-scan flats at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval))
                for f in range(imagesPerFlat):
                    for jj in range(numberStepsGrating+1):
                        grating_pos = grating_points[jj]
                        scan_points.append((theta_pos, shutterOpen, outOfBeamPosition, grating_pos, image_key_flat, index ))
                        index = index + 1
                        offset_flat += 1
                imageSinceFlat = 0
            #if darkFieldInterval != 0 and (not testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval)):
            if (darkFieldInterval != 0) and (imageSinceDark == darkFieldInterval):
                #print "adding first-batch mid-scan darks at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval))
                for d in range(imagesPerDark):
                    scan_points.append((theta_pos, shutterClosed, inBeamPosition, grating_pos, image_key_dark, index ))
                    index = index + 1
                    offset_dark += 1
                imageSinceDark = 0
            grating_pos = grating_points[j]
            scan_points.append((theta_pos, shutterOpen, inBeamPosition, grating_pos, image_key_project, index )) #first sample batch
            index = index + 1
            imageSinceDark += 1
            imageSinceFlat += 1

        for i in range(numberSteps):
            theta_pos = theta_points[i+1]
            for j in range(numberStepsGrating+1):
                #print "main test flat = %i, index = %i" % (testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval), index)
                #if flatFieldInterval != 0 and (not testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval)):
                if (flatFieldInterval != 0) and (imageSinceFlat == flatFieldInterval):
                    #print "adding main mid-scan flats at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval))
                    for f in range(imagesPerFlat):
                        for jj in range(numberStepsGrating+1):
                            grating_pos = grating_points[jj]
                            scan_points.append((theta_pos, shutterOpen, outOfBeamPosition, grating_pos, image_key_flat, index ))
                            index = index + 1
                            offset_flat += 1
                    imageSinceFlat = 0
                #if darkFieldInterval != 0 and (not testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval)):
                if (darkFieldInterval != 0) and (imageSinceDark == darkFieldInterval):
                    #print "adding main mid-scan darks at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval))
                    for d in range(imagesPerDark):
                        scan_points.append((theta_pos, shutterClosed, inBeamPosition, grating_pos, image_key_dark, index ))
                        index = index + 1
                        offset_dark += 1
                    imageSinceDark = 0
                grating_pos = grating_points[j]
                scan_points.append((theta_pos, shutterOpen, inBeamPosition, grating_pos, image_key_project, index ))#main sample
                index = index + 1
                imageSinceDark += 1
                imageSinceFlat += 1
        
        #add dark and flat only if not done in last steps
        #print "after test flat = %i, index = %i" % (testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval), index)
        #if not testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval):
        if (imageSinceFlat != 0):
            #print "adding flats after at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, flatFieldInterval))
            for f in range(imagesPerFlat):
                for jj in range(numberStepsGrating+1):
                    grating_pos = grating_points[jj]
                    scan_points.append((theta_pos, shutterOpen, outOfBeamPosition, grating_pos, image_key_flat, index )) #flat
                    index = index + 1
                    offset_flat += 1
        #if not testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval):
        if (imageSinceDark != 0):
            #print "adding darks after at index %i and proj_index = %i; offset_dark = %i, offset_flat = %i; test = %i" %(index, (index - offset_dark - offset_flat), offset_dark, offset_flat, testElapsedInterval(index, offset_dark, offset_flat, darkFieldInterval))
            for d in range(imagesPerDark):
                scan_points.append((theta_pos, shutterClosed, inBeamPosition, grating_pos, image_key_dark, index )) #dark
                index = index + 1
                offset_dark += 1
                
        positionProvider = tomoScan_positions( start, stop, step, startGrating, stopGrating, stepGrating, darkFieldInterval, imagesPerDark, flatFieldInterval, imagesPerFlat, \
                                               inBeamPosition, outOfBeamPosition, scan_points )
        #print "scan_points..."
        #print "(Ang, Shut, xTran, Grat, ImgKey, index)"
        #for x in scan_points:
        #    print x
        #return 
        scan_args = [tomoScanDevice, positionProvider, tomography_time, tomography_beammonitor, tomography_detector, exposureTime ]
        if min_i > 0.:
            import gdascripts.scannable.beamokay
            ionc_i = jns.ionc_i
            if ionc_i is None:
                raise NameError("ionc_i is not defined in Jython namespace")
            beamok=gdascripts.scannable.beamokay.WaitWhileScannableBelowThresholdMonitorOnly("beamok", ionc_i, min_i)
            scan_args.append(beamok)
            
        for scannable in additionalScannables:
            scan_args.append(scannable)
            
        scanObject=createConcurrentScan(scan_args)
        if addNXEntry:
            addNXTomoSubentry(scanObject, tomography_detector.name, tomography_theta.name)
#        tomodet.stop()
        scanObject.runScan()

        if autoAnalyse:
            lsdp=jns.lastScanDataPoint()
            OSCommandRunner.runNoWait(["/dls_sw/apps/tomopy/tomopy/bin/gda/tomo_at_scan_end", lsdp.currentFilename], OSCommandRunner.LOGOPTION.ALWAYS, None)
        
        #Close the fast shutter to prevent warming of sample
        tomography_shutter.moveTo( "Close")	
        #turn camera back on
#        tomodet.setupForAlignment()
        
            
        return scanObject;
    except :
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Error in tomoScan", exceptionType, exception, traceback, True)


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

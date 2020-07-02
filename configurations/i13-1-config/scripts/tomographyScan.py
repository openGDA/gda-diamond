"""
Performs software triggered tomography
"""

from time import sleep


from gda.jython.commands.ScannableCommands import inc, scan, pos, createConcurrentScan
from gda.scan import ConstantVelocityScanLine, MultiScanItem, MultiScanRunner, ConcurrentScan
from gda.data.scan.datawriter import NXSubEntryWriter, NXTomoEntryLinkCreator

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
from org.slf4j import LoggerFactory
from i13j_utilities import isLive

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

def addNXTomoSubentry(scanObject, tomography_detector_name, tomography_theta_name, tomography_beammonitor_name):
    if scanObject is None:
        raise ValueError("Input scanObject must not be None")
   
    nxLinkCreator = NXTomoEntryLinkCreator()
   
    # detector independent items
    nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/" + tomography_beammonitor_name + ":NXpositioner/" + tomography_beammonitor_name + ":SDS")
    nxLinkCreator.setInstrument_detector_image_key_target("entry1:NXentry/instrument:NXinstrument/tomoScanDevice:NXpositioner/image_key:SDS")
    nxLinkCreator.setInstrument_source_target("entry1:NXentry/instrument:NXinstrument/source:NXsource")
   
    sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/tomoScanDevice:NXpositioner/"
    sample_rotation_angle_target += tomography_theta_name + ":SDS"
    nxLinkCreator.setSample_rotation_angle_target(sample_rotation_angle_target);
    #nxLinkCreator.setSample_x_translation_target("entry1:NXentry/before_scan:NXcollection/t1:NXcollection/t1_sx:SDS")
    #nxLinkCreator.setSample_y_translation_target("entry1:NXentry/before_scan:NXcollection/t1:NXcollection/t1_sy:SDS")
    #nxLinkCreator.setSample_z_translation_target("entry1:NXentry/before_scan:NXcollection/t1:NXcollection/t1_sz:SDS")
    nxLinkCreator.setSample_x_translation_target("entry1:NXentry/before_scan:NXcollection/t1_sx:SDS")
    nxLinkCreator.setSample_y_translation_target("entry1:NXentry/before_scan:NXcollection/t1_sx:SDS")
    nxLinkCreator.setSample_z_translation_target("entry1:NXentry/before_scan:NXcollection/t1_sx:SDS")
   
    nxLinkCreator.setTitle_target("entry1:NXentry/title:SDS")
   
    # detector dependent items
    if tomography_detector_name == "pco1_hw_hdf" or tomography_detector_name == "pco1_sw_hdf_nochunking":
        # external file
        instrument_detector_data_target = "!entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "data:SDS"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
    elif tomography_detector_name == "pco1_hw_tif" or tomography_detector_name == "pco1_tif":
        # image filenames
        instrument_detector_data_target = "entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        if isLive():
            instrument_detector_data_target += "image_data:SDS"
        else:
            instrument_detector_data_target += "data:SDS"
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
    nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/ionc_i:NXpositioner/ionc_i:SDS")
    nxLinkCreator.setInstrument_detector_image_key_target("entry1:NXentry/instrument:NXinstrument/image_key:NXpositioner/image_key:SDS")
    nxLinkCreator.setInstrument_source_target("entry1:NXentry/instrument:NXinstrument/source:NXsource")
   
    sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/zebraSM1:NXpositioner/"
    sample_rotation_angle_target += tomography_theta_name + ":SDS"
    nxLinkCreator.setSample_rotation_angle_target(sample_rotation_angle_target);
    nxLinkCreator.setSample_x_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplex:SDS")
    nxLinkCreator.setSample_y_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_sampley:SDS")
    nxLinkCreator.setSample_z_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplez:SDS")
   
    nxLinkCreator.setTitle_target("entry1:NXentry/title:SDS")
   
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
        instrument_detector_data_target += "image_data:SDS"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
   
    nxLinkCreator.afterPropertiesSet()
   
    dataWriter = createDataWriterFromFactory()
    subEntryWriter = NXSubEntryWriter(nxLinkCreator)
    dataWriter.addDataWriterExtender(subEntryWriter)
    scanObject.setDataWriter(dataWriter)


def reportJythonNamespaceMapping():
    jns=beamline_parameters.JythonNameSpaceMapping()
        
    objectOfInterestSTEP = {}
    objectOfInterestSTEP['tomography_theta'] = jns.tomography_theta
    objectOfInterestSTEP['tomography_shutter'] = jns.tomography_shutter
    objectOfInterestSTEP['tomography_translation'] = jns.tomography_translation
    objectOfInterestSTEP['tomography_detector'] = jns.tomography_detector
    objectOfInterestSTEP['tomography_beammonitor'] = jns.tomography_beammonitor

    objectOfInterestFLY = {}
    objectOfInterestFLY['tomography_theta'] = jns.tomography_theta
    objectOfInterestFLY['tomography_flyscan_theta'] = jns.tomography_flyscan_theta
    objectOfInterestFLY['tomography_shutter'] = jns.tomography_shutter
    objectOfInterestFLY['tomography_translation'] = jns.tomography_translation
    objectOfInterestFLY['tomography_flyscan_det'] = jns.tomography_flyscan_det
    objectOfInterestFLY['tomography_flyscan_flat_dark_det'] = jns.tomography_flyscan_flat_dark_det
    
    objectOfInterestXGI = {}
    objectOfInterestXGI['tomography_detector'] = jns.tomography_detector
    objectOfInterestXGI['tomography_theta'] = jns.tomography_theta
    objectOfInterestXGI['tomography_translation'] = jns.tomography_translation
    objectOfInterestXGI['tomography_shutter'] = jns.tomography_shutter
    objectOfInterestXGI['tomography_grating_translation'] = jns.tomography_grating_translation
    objectOfInterestXGI['tomography_grating_translation_outer'] = jns.tomography_grating_translation_outer
    objectOfInterestXGI['tomography_grating_translation_inner'] = jns.tomography_grating_translation_inner

    msg = "\n Any of these mappings can be changed by editing a file named live_jythonNamespaceMapping, "
    msg += "\n located in Scripts: Config/src (this can be done by beamline staff).\n"

    print "****** STEP-SCAN PRIMARY SETTINGS ******"
    idx=1
    for key, val in objectOfInterestSTEP.iteritems():
        name = "object undefined!"
        if val is not None:
            name = str(val.getName())
        print "%i. %s = %s" %(idx, key, name)
        idx += 1
    print "\n"

    print "****** FLY-SCAN PRIMARY SETTINGS ******"
    idx=1
    for key, val in objectOfInterestFLY.iteritems():
        name = "object undefined!"
        if val is not None:
            name = str(val.getName())
        print "%i. %s = %s" %(idx, key, name)
        idx += 1
    print "\n"
    
    print "****** XGI-SCAN PRIMARY SETTINGS ******"
    idx=1
    for key, val in objectOfInterestXGI.iteritems():
        name = "object undefined!"
        if val is not None:
            name = str(val.getName())
        reportln = "%i. %s = %s" %(idx,key,name)
        #print `idx` + "."+ key + ' = ' + name
        print reportln
        idx += 1
    print msg

def reportTomo():
    return reportJythonNamespaceMapping()


from gda.device.scannable import SimpleScannable
image_key_dark=2
image_key_flat=1 # also known as bright
image_key_project=0 # also known as sample

def showNormalisedImage(outOfBeamPosition, exposureTime=None, imagesPerDark=1, imagesPerFlat=1, getDataOnly=False):
	try:
		showNormalisedImageEx(outOfBeamPosition, exposureTime=exposureTime, imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat, getDataOnly=getDataOnly)
	except :
		exceptionType, exception, traceback = sys.exc_info()
		handle_messages.log(None, "Error in showNormalisedImage", exceptionType, exception, traceback, False)

def showNormalisedImageEx(outOfBeamPosition, exposureTime=.1, imagesPerDark=1, imagesPerFlat=1, getDataOnly=False):
    jns=beamline_parameters.JythonNameSpaceMapping()
#    tomodet=jns.tomodet
#    if tomodet is None:
#	    raise NameError("tomodet is not defined in Jython namespace")
#    if exposureTime is not None:
#        exposureTime = float(exposureTime)
#    else:
#        exposureTime = tomodet.getCurrentExposureTime()

    import scisoftpy as dnp
    tomography_theta=jns.tomography_theta
    if tomography_theta is None:
            raise NameError("tomography_theta is not defined in Jython namespace")
    tomography_translation=jns.tomography_translation
    if tomography_translation is None:
        raise NameError("tomography_translation is not defined in Jython namespace")

    tomography_detector=jns.tomography_normalisedImage_detector
    if tomography_detector is None:
        raise NameError("tomography_detector is not defined in Jython namespace")
    currentTheta=tomography_theta()
    tomoScan(tomography_translation(), outOfBeamPosition, exposureTime, start=currentTheta, stop=currentTheta, step=1., imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat, addNXEntry=False,autoAnalyse=False,tomography_detector=tomography_detector)

    if getDataOnly:
        return True
    
    lsdp=jns.lastScanDataPoint()
    detName=tomography_detector.getName()
    #wait for the image file to arrive from the detector system
#    time.sleep(5)
    found=False 
    attempt=0
    while not found and attempt<11: 
        attempt+=1
        try:
            nxdata=dnp.io.load(lsdp.currentFilename)[str('entry1/' + tomography_detector.getName())] 
            dataKey=None
            for key in nxdata.keys():
                if key == "image_data":
                    dataKey=key
                    break
                if key == "data":
                    dataKey=key
                    break
            if dataKey is None:
                raise IOError("Unable to find data in file")
            dataset=nxdata[dataKey]
            dark=dnp.array(dataset[0,:,:]).astype(dnp.float64)
            flat=dnp.array(dataset[imagesPerDark,:,:]).astype(dnp.float64)
            image=dnp.array(dataset[imagesPerDark+imagesPerFlat,:,:]).astype(dnp.float64)
            found = True
        except:
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Error in tomoFlyScanScan", exceptionType, exception, traceback, False)            
            updateProgress(90, "Wait 5 seconds for image file to arrive from the detector system")
            time.sleep(5)


    
    if not found:
        raise IOError("Unable to analyse data as it has not arrived from detector in time")

    imageD=image-dark
    flatD=flat-dark
    t=imageD/flatD
#    t=imageD/dnp.select( dnp.not_equal(flatD,0), flatD, 1.)
    t._jdataset().name="normalisedImage"
    from org.eclipse.dawnsci.hdf5 import HDF5Utils
    HDF5Utils.writeDataset(lsdp.currentFilename, "entry1", t._jdataset())
    t._jdataset().name=str(lsdp.getScanIdentifier()) + " (image-dark)/(flat-dark)"
#    from uk.ac.gda.analysis.hdf5 import Hdf5Helper, Hdf5HelperData, HDF5HelperLocations
#    hdfData = Hdf5HelperData(t.shape, t._jdataset().buffer)
#    locs = HDF5HelperLocations("entry1")
#    locs.add(tomography_detector.getName())
#    Hdf5Helper.getInstance().writeToFileSimple(hdfData, lsdp.currentFilename,locs , "normalisedImage")
#    rcp=Finder.find("RCPController")
#    rcp.openView("uk.ac.diamond.daq.tomography.datacollection.ui.NormalisedImage")
    dnp.plot.image(t, name="Normalised Image")
    #turn camera back on
    return True

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



"""
perform a continuous tomogrpahy scan
"""
def tomoFlyScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=False):
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
    updateProgress(0, "Starting scan")
    jns=beamline_parameters.JythonNameSpaceMapping()
    tomography_flyscan_flat_dark_det=jns.tomography_flyscan_flat_dark_det
    savename=tomography_flyscan_flat_dark_det.name
    try:
        #tomodet=jns.tomodet
        #if tomodet is None:
	    #    raise NameError("tomodet is not defined in Jython namespace")

        tomography_theta=jns.tomography_theta
        if tomography_theta is None:
            raise NameError("tomography_theta is not defined in Jython namespace")

        tomography_flyscan_theta=jns.tomography_flyscan_theta
        if tomography_flyscan_theta is None:
            raise NameError("tomography_flyscan_theta is not defined in Jython namespace")

        tomography_flyscan_det=jns.tomography_flyscan_det
        if tomography_flyscan_det is None:
            raise NameError("tomography_flyscan_det is not defined in Jython namespace")
        
        tomography_translation=jns.tomography_translation
        if tomography_translation is None:
            raise NameError("tomography_translation is not defined in Jython namespace")
        

        tomography_shutter=jns.tomography_shutter
        if tomography_shutter is None:
            raise NameError("tomography_shutter is not defined in Jython namespace")
        
        meta_add = jns.meta_add
        if meta_add is None:
            raise NameError("meta_add is not defined in Jython namespace")

        #camera_stage = jns.cs1
        #if camera_stage is None:
        #    raise NameError("camera_stage is not defined in Jython namespace")

        sample_stage = jns.sample_stage
        if sample_stage is None:
            raise NameError("sample_stage is not defined in Jython namespace")

        ionc_i = jns.ionc_i
        if ionc_i is None:
            raise NameError("ionc_i is not defined in Jython namespace")
        ionc_i_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(ionc_i)


        #meta_add( camera_stage)
        meta_add( sample_stage)
               

        index=SimpleScannable()
        index.setCurrentPosition(0.0)
        index.setName(tomography_flyscan_theta.name)
        index.inputNames = tomography_flyscan_theta.inputNames
        index.extraNames = tomography_flyscan_theta.extraNames
        index.configure()

#        index_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(index)


        image_key=SimpleScannable()
        image_key.setCurrentPosition(0.0)
        image_key.setInputNames(["image_key"])
        image_key.setName("image_key")
        image_key.configure()
        image_key_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(image_key)


#        ss=SimpleScannable()
#        ss.name = tomography_flyscan_theta.name
#        ss.currentPosition=0.
#        ss.inputNames = tomography_flyscan_theta.inputNames
#        ss.extraNames = tomography_flyscan_theta.extraNames
#        ss.configure()

        ss1=SimpleScannable()
        ss1.name = tomography_flyscan_theta.getContinuousMoveController().name
        ss1.currentPosition=0.
        ss1.inputNames = tomography_flyscan_theta.getContinuousMoveController().inputNames
        ss1.extraNames = tomography_flyscan_theta.getContinuousMoveController().extraNames
        ss1.configure()
        
        

        
        tomography_flyscan_flat_dark_det.name = tomography_flyscan_det.name
        
#        scanBackward=ConstantVelocityScanLine([tomography_flyscan_theta, stop, start, step, index_cont, image_key_cont, ionc_i_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
#        scanObject3=ConstantVelocityScanLine([tomography_flyscan_theta, start, stop, step,ix, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
        #tomodet.stop()
        
#        multiScanObj = MultiScan([darkFlatScan, scanObject, scanObject2,scanObject3])
        multiScanItems = []

        if imagesPerDark > 0:
            darkScan=ConcurrentScan([index, 0, imagesPerDark-1, 1, image_key, ionc_i, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
            multiScanItems.append(MultiScanItem(darkScan, PreScanRunnable("Preparing for darks", 0, tomography_shutter, "Close", tomography_translation, inBeamPosition, image_key, image_key_dark, tomography_theta, start)))
        if imagesPerFlat > 0:
            flatScan=ConcurrentScan([index, 0, imagesPerFlat-1, 1, image_key, ionc_i, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
            multiScanItems.append(MultiScanItem(flatScan, PreScanRunnable("Preparing for flats",10, tomography_shutter, "Open", tomography_translation, outOfBeamPosition, image_key, image_key_flat, tomography_theta, start)))
        
        scanForward=ConstantVelocityScanLine([tomography_flyscan_theta, start, stop, step,image_key_cont, ionc_i_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
#        scanBackward=ConstantVelocityScanLine([tomography_flyscan_theta, stop, start, step,image_key_cont, ionc_i_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
        multiScanItems.append(MultiScanItem(scanForward, PreScanRunnable("Preparing for projections",20, tomography_shutter, "Open",tomography_translation, inBeamPosition, image_key, image_key_project, tomography_theta, start)))
#        multiScanItems.append(MultiScanItem(scanBackward, PreScanRunnable("Preparing for projections backwards",60, tomography_shutter, "Open",tomography_translation, inBeamPosition, image_key, image_key_project)))
        multiScanObj = MultiScanRunner(multiScanItems)
        #must pass fist scan to be run
        addFlyScanNXTomoSubentry(multiScanItems[0].scan, tomography_flyscan_det.name, tomography_flyscan_theta.name)
        multiScanObj.runScan()
        tomography_shutter.moveTo("Close")
            
#        time.sleep(2)
        updateProgress(100, "Scan complete")
        return multiScanObj;
    except :
        exceptionType, exception, traceback = sys.exc_info()
        #turn camera back on
        tomography_flyscan_flat_dark_det.name = savename
        if setupForAlignment:
            #tomodet.setupForAlignment()
            pass
        handle_messages.log(None, "Error in tomoFlyScanScan", exceptionType, exception, traceback, True)




"""
perform a simple tomography scan
"""
def tomoScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1., addNXEntry=True, autoAnalyse=True, tomography_detector=None, approxCOR=(None,None), additionalScannables=[], **kwargs):
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
        
        objSTEP = []
        objSTEP.append('tomography_theta')
        objSTEP.append('tomography_shutter')
        objSTEP.append('tomography_translation')
        objSTEP.append('tomography_detector')           # note this is a positional arg, so can'be supplied in kwargs!
        objSTEP.append('tomography_beammonitor')
        objSTEP.append('tomography_time')
        objSTEP.append('sample_stage')
        
        if kwargs is not None and len(kwargs)>0:
            print "*** Found %i kwargs: " %(len(kwargs)) , kwargs
            #print kwargs, len(kwargs)
        else:
            print("*** kwargs not found")
        
        # use kwargs value to set obj or set it to None
        for k in objSTEP:
            if (kwargs is not None) and kwargs.has_key(k) and (kwargs[k] is not None):
                exec("%s=Finder.find(\"%s\")" %(kwargs[k].getName(), kwargs[k].getName()))
                exec(k + "=%s" %(kwargs[k].getName()))
            else:
                #if k != 'tomography_detector':
                #    print k
                #    exec(k + "=" + "None")
                try:
                    eval(k)
                    #print k
                except:
                    exec(k + "=" + "None")
        
        jns=beamline_parameters.JythonNameSpaceMapping()
#        tomodet=jns.tomodet
#        if tomodet is None:
#	        raise NameError("tomodet is not defined in Jython namespace")

        # use jns values
        for k in objSTEP:
            if eval(k +" is None"):
                exec(k + "=" + "jns."+k)
            #else:
            #    print "keeping kwargs value for %s" %(k)
        
        # final sanity test
        print "*** This tomoScan is set to use:" 
        for k in objSTEP:
            if eval("%s is None" %(k)):
                msg = k + " is not defined"
                raise msg
            else:
                print "%s = %s" %(k, eval("%s.getName()" %(k)))
        #return

#        if tomography_detector is None:
#	        tomography_detector=jns.tomography_detector
#        if tomography_detector is None:
#            raise NameError("tomography_detector is not defined in Jython namespace")

        meta_add = jns.meta_add
        if meta_add is None:
            raise NameError("meta_add is not defined in Jython namespace")

#        camera_stage = jns.cs1
#        if camera_stage is None:
#            raise NameError("camera_stage is not defined in Jython namespace")

#        meta_add( camera_stage)
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
        tomoScanDevice.tomography_shutter.moveTo(shutterClosed) 
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
        scan_args = [tomoScanDevice, positionProvider, tomography_time, tomography_beammonitor, tomography_detector, exposureTime ]

        
        #we need ionc_i for the NXTomoEntry
        if min_i > 0.:
            import gdascripts.scannable.beamokay
            #ionc_i = jns.ionc_i
            #if ionc_i is None:
            #    raise NameError("ionc_i is not defined in Jython namespace")
            beamok=gdascripts.scannable.beamokay.WaitWhileScannableBelowThresholdMonitorOnly("beamok", tomography_beammonitor, min_i)
            scan_args.append(beamok)
            
        for scannable in additionalScannables:
            scan_args.append(scannable)
        
        scanObject=createConcurrentScan(scan_args); #return
        if addNXEntry:
            addNXTomoSubentry(scanObject, tomography_detector.name, tomography_theta.name, tomography_beammonitor.name)
        tomography_detector.stop()
        scanObject.runScan()

        if autoAnalyse and isLive():
            lsdp=jns.lastScanDataPoint()
            OSCommandRunner.runNoWait(["/dls_sw/apps/tomopy/tomopy/bin/gda/tomo_at_scan_end", lsdp.currentFilename], OSCommandRunner.LOGOPTION.ALWAYS, None)
        
        #ensure the soft control of the shutter is open at the end of the scan
        tomography_shutter.moveTo( "Open")	
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
    
import json
from uk.ac.gda.tomography.scan import TomoScanParameters
    
def parameters_from_json(json_stash):
    
    logger = LoggerFactory.getLogger("tomographyScan.parameters_from_json()")
    logger.debug("processing scan parameters from " + json_stash)

    stash_file = open(json_stash, 'r')
    stash = json.load(stash_file)
    stash_file.close()
    
    model = TomoScanParameters()
    model.setTitle(stash.get('title'))
    model.setExposureTime(stash.get('exposureTime'))
    model.setMinI(stash.get('minI'))
    
    model.setInBeamPosition(stash.get('inBeamPosition'))
    model.setOutOfBeamPosition(stash.get('outOfBeamPosition'))
    
    model.setStart(stash.get('start'))
    model.setStop(stash.get('stop'))
    model.setStep(stash.get('step'))
    
    model.setImagesPerDark(stash.get('imagesPerDark'))
    model.setDarkFieldInterval(stash.get('darkFieldInterval'))
    model.setImagesPerFlat(stash.get('imagesPerFlat'))
    model.setFlatFieldInterval(stash.get('flatFieldInterval'))
    
    model.setFlyScan(stash.get('flyScan'))
    model.setExtraFlatsAtEnd(stash.get('extraFlatsAtEnd'))
    
    model.setNumFlyScans(stash.get('numFlyScans'))
    model.setFlyScanDelay(stash.get('flyScanDelay'))
    
    model.setCloseShutterAfterLastScan(stash.get('closeShutterAfterLastScan'))
    
    model.setRotationStage(stash.get('rotationStage'))
    model.setLinearStage(stash.get('linearStage'))
    
    model.setSendDataToTempDirectory(stash.get('sendDataToTempDirectory'))    
    
    model.setDetectorToSampleDistance(stash.get('detectorToSampleDistance'))
    model.setDetectorToSampleDistanceUnits(stash.get('detectorToSampleDistanceUnits'))
    model.setxPixelSize(stash.get('xPixelSize'))
    model.setxPixelSizeUnits(stash.get('xPixelSizeUnits'))
    model.setyPixelSize(stash.get('yPixelSize'))
    model.setyPixelSizeUnits(stash.get('yPixelSizeUnits'))
    model.setApproxCentreOfRotation(stash.get('approxCentreOfRotation'))
    
    ProcessScanParameters(model)
    
from gdascripts.metadata.metadata_commands import setTitle, getTitle

def ProcessScanParameters(model):
    logger = LoggerFactory.getLogger("tomographyScan.ProcessScanParameters()")
    logger.debug("processing scan parameters from " + model.toString())
    jns=beamline_parameters.JythonNameSpaceMapping()
    additionalScannables=jns.tomography_additional_scannables
    setTitle(model.getTitle())

    updateProgress(0, "Starting tomoscan " + model.getTitle());
    logger.info("Starting tomoscan with parameters: " + model.toString())

    cor_x = cor_y = None
    if (model.flyScan):
        logger.info("Fly scan not supported")
#         #cor_x = cor_y = None
#         if parameters.approxCentreOfRotation is not None:
#             print "Input CoR = %.3f" %(parameters.approxCentreOfRotation)
#         else:
#             print("Input CoR's type = " + type(parameters.approxCentreOfRotation))
#         cor_x, cor_y = getApproxCoR()
#         print("(cor_x, cor_y) = (%s, %s)" %(str(cor_x), str(cor_y)))   
#         qFlyScanBatch(parameters.numFlyScans, parameters.title, parameters.flyScanDelay, 
#                       parameters.inBeamPosition, parameters.outOfBeamPosition, exposureTime=parameters.exposureTime, start=parameters.start, stop=parameters.stop, step=parameters.step, 
#                       darkFieldInterval=parameters.darkFieldInterval,  flatFieldInterval=parameters.flatFieldInterval,
#                       imagesPerDark=parameters.imagesPerDark, imagesPerFlat=parameters.imagesPerFlat, min_i=parameters.minI,
#                       extraFlatsAtEnd=parameters.extraFlatsAtEnd, approxCOR=(cor_x,cor_y))
    else:
        tomoScan(model.inBeamPosition, model.outOfBeamPosition, exposureTime=model.exposureTime, start=model.start, stop=model.stop, step=model.step, 
                 darkFieldInterval=model.darkFieldInterval,  flatFieldInterval=model.flatFieldInterval,
                  imagesPerDark=model.imagesPerDark, imagesPerFlat=model.imagesPerFlat, min_i=model.minI, additionalScannables=additionalScannables, approxCOR=(cor_x,cor_y))
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

def getApproxCoR():
    # assuming camera is in the i13 default orientation wrt to the axis of rotation
    #cam_model = caget("BL13I-EA-DET-01:CAM:Model_RBV")
    cam_max_sensor_size_x = caget("BL13I-EA-DET-01:CAM:MaxSizeX_RBV")
    cor_x = float(cam_max_sensor_size_x) * 0.5
    cor_y = None
    return cor_x, cor_y

"""
Performs software triggered tomography
"""

from time import sleep
import datetime
import os

from pcoDetectorWrapper import PCODetectorWrapper
from gda.jython.commands.ScannableCommands import inc, scan, pos, createConcurrentScan
from gda.scan import ConstantVelocityScanLine, MultiScanItem, MultiScanRunner, ConcurrentScan
from epics_scripts.pv_scannable_utils import createPVScannable, caput, caget
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
from org.eclipse.dawnsci.hdf5.nexus import NexusFileHDF5
from org.eclipse.january.dataset import DatasetUtils
from org.eclipse.january.dataset import Dataset
from gda.configuration.properties import LocalProperties
from gda.commandqueue import JythonScriptProgressProvider
from gda.commandqueue import JythonCommandCommandProvider
from org.slf4j import LoggerFactory
import i13i_utilities

finder = Finder.getInstance()

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

def addNXTomoSubentry(scanObject, tomography_detector_name, tomography_theta_name, **kwargs):
    if scanObject is None:
        raise "Input scanObject must not be None"
   
    nxLinkCreator = NXTomoEntryLinkCreator()
   
    # detector independent items
    nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/ionc_i:NXpositioner/ionc_i:SDS")
    nxLinkCreator.setInstrument_detector_image_key_target("entry1:NXentry/instrument:NXinstrument/tomoScanDevice:NXpositioner/image_key:SDS")
    nxLinkCreator.setInstrument_source_target("entry1:NXentry/instrument:NXinstrument/source:NXsource")
   
    sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/tomoScanDevice:NXpositioner/"
    sample_rotation_angle_target += tomography_theta_name + ":SDS"
    nxLinkCreator.setSample_rotation_angle_target(sample_rotation_angle_target);
    nxLinkCreator.setSample_x_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplex:SDS")
    nxLinkCreator.setSample_y_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_sampley:SDS")
    nxLinkCreator.setSample_z_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplez:SDS")
   
    nxLinkCreator.setTitle_target("entry1:NXentry/title:SDS")
   
    # detector dependent items
    if tomography_detector_name in ("pco1_hw_hdf", "pco1_hw_hdf_nochunking", "merlin_sw_hdf"):
        # external file
        instrument_detector_data_target = "!entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "data:SDS"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
    elif tomography_detector_name in ("pco1_hw_tif", "pco1_tif", "merlin_sw_tif"):
        # image filenames
        instrument_detector_data_target = "entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "image_data:SDS"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
    elif tomography_detector_name == 'pco1_sw':
        instrument_detector_data_target = "entry1:NXentry/instrument:NXinstrument/"
        instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
        instrument_detector_data_target += "data:SDS"
        nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
    else:
        print "Defaults used for unsupported tomography detector in addNXTomoSubentry: " + tomography_detector_name

    _addNXTomoSubentryValues(nxLinkCreator, **kwargs)
    nxLinkCreator.afterPropertiesSet()
   
    dataWriter = createDataWriterFromFactory()
    subEntryWriter = NXSubEntryWriter(nxLinkCreator)
    dataWriter.addDataWriterExtender(subEntryWriter)
    scanObject.setDataWriter(dataWriter)


def addFlyScanNXTomoSubentry(scanObject, tomography_detector_name, tomography_theta_name, externalhdf=True, **kwargs):
    if scanObject is None:
        raise "Input scanObject must not be None"
    
    nxLinkCreator = NXTomoEntryLinkCreator()
   
    # detector independent items
    nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/ionc_i:NXpositioner/ionc_i:SDS")
    nxLinkCreator.setInstrument_detector_image_key_target("entry1:NXentry/instrument:NXinstrument/image_key:NXpositioner/image_key:SDS")
    nxLinkCreator.setInstrument_source_target("entry1:NXentry/instrument:NXinstrument/source:NXsource")
   
    sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/" + tomography_theta_name + ":NXpositioner/"
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
   
    _addNXTomoSubentryValues(nxLinkCreator, **kwargs)
    nxLinkCreator.afterPropertiesSet()
   
    dataWriter = createDataWriterFromFactory()
    subEntryWriter = NXSubEntryWriter(nxLinkCreator)
    dataWriter.addDataWriterExtender(subEntryWriter)
    scanObject.setDataWriter(dataWriter)


def reportJythonNamespaceMapping(modality='micro', verbose=False):
    """
    Fn to report relevant tomography object mappings found in live_jythonNamespaceMapping.
    Arg(s)
    modality - type of scan
        available options: 'all', 'micro', 'heli', 'xgi' or their first letters (all case insensitive)
    verbose - if True, PV names are displayed wherever appropriate
    """
    def _get_pv_name(obj):
        out = None
        if isinstance(obj, gda.device.scannable.ScannableMotor):
            try:
                out = obj.getMotor().getPvName()
            except Exception, e:
                pass
        elif isinstance(obj,(gda.device.scannable.EpicsScannable\
                             ,gda.device.scannable.PVScannable\
                             ,gda.device.scannable.SimplePVScannable\
                             ,gda.epics.EpicsBase\
                             ,gda.device.monitor.EpicsMonitor\
                             ,gda.device.enumpositioner.EpicsPneumaticCallback)):
            try:
                out = obj.getPvName()
            except Exception, e:
                pass
        elif 'dummy' in repr(type(obj)).lower() or 'dummy' in obj.getName().lower():
            out = 'WARNING: dummy object - is this intentional?'
#        else:
#            print("None of the above: %s" %(type(obj)))
        return out
    
    def get_pv_name(obj,verbose):
        name = _get_pv_name(obj)
        return '(%s)' %(name) if verbose and (not name is None) else ''
    
    m = modality.lower()
    #supported_dct = {} isinstance(obj, gda.device.scannable.DummyScannableMotor
    
    supported_names_lst = []
    supported_abbrevs_lst = []
    supported_desc_lst = []
    
    supported_names_lst.append('all')
    supported_desc_lst.append('all scanning modalities')
    supported_names_lst.append('micro')
    supported_desc_lst.append('micro-tomography (step & fly scans)')
    supported_names_lst.append('heli')
    supported_desc_lst.append('hellical micro-tomography step scan')
    supported_names_lst.append('xgi')
    supported_desc_lst.append('diffraction-grating interferometry (1d & 2d)')
    supported_abbrevs_lst = [s[0] for s in supported_names_lst]
    
    #supported_dct.update({'all': 'all scanning modalities'})
    #supported_dct.update({'micro': 'micro-tomography (step & fly scans)'})
    #supported_dct.update({'xgi': 'diffraction-grating interferometry (1d & 2d)'})
    #supported_dct.update({'heli': 'hellical micro-tomography step scan'})
    
    #supported_lst = []
    #supported_lst.append(('all', 'all scan modalities'))
    #supported_lst.append(('micro', 'micro-tomography (step & fly scans)'))
    #supported_lst.append(('xgi', 'diffraction-grating interferometry (1d & 2d)'))
    #supported_lst.append(('heli', 'hellical micro-tomography step scan'))
    
    modality_default = 'all'
    modality_desc_default = [kv[1] for kv in zip(supported_names_lst, supported_desc_lst) if kv[0]==modality_default][0]
    options_str='\n'.join(["'%s': %s" %(k,v) for k,v in zip(supported_names_lst, supported_desc_lst)])
    if not (m in supported_names_lst or m.startswith(tuple(supported_abbrevs_lst))):
    #if not (m in supported_dct or m.startswith(('a','m','x','h'))):
    #if not (m in supported_lst or m.startswith(('a','m','x','h'))):
        print("Unsupported input modality '%s' - using default option '%s' instead!" %(modality, modality_default))
        m = modality_default
        m_desc = modality_desc_default
        options_str='\n'.join(["'%s': %s" %(k,v) for k,v in zip(supported_names_lst, supported_desc_lst)])
        #options_str='\n'.join(["'%s': %s" %(k,v) for k,v in supported_dct.iteritems()])
        #options_str='\n'.join(["'%s': %s" %(kv[0],kv[1]) for kv in supported_lst])
        #print("Supported options: %s" %(supported_tpl,))
    else:
        m_idx = [i for i, s in enumerate(supported_abbrevs_lst) if m.startswith(s)][0]
        m_desc = supported_desc_lst[m_idx]
    print("Supported options: \n%s\n" %(options_str))
    
    print("REPORT on JYTHON NAMESPACE MAPPINGS for OPTION '%s' (%s):\n" %(m, m_desc))
    
    jns=beamline_parameters.JythonNameSpaceMapping()
    objectOfInterest = {}
    objectOfInterest['tomography_normalisedImage_detector']=jns.tomography_normalisedImage_detector
    objectOfInterest['tomography_theta'] = jns.tomography_theta
    objectOfInterest['tomography_translation'] = jns.tomography_translation
    
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
    
    objectOfInterestXGI_1D = {}
    objectOfInterestXGI_1D['tomography_detector'] = jns.tomography_detector
    objectOfInterestXGI_1D['tomography_theta'] = jns.tomography_theta
    objectOfInterestXGI_1D['tomography_translation'] = jns.tomography_translation
    objectOfInterestXGI_1D['tomography_shutter'] = jns.tomography_shutter
    objectOfInterestXGI_1D['tomography_grating_translation'] = jns.tomography_grating_translation
    
    objectOfInterestXGI_2D = {}
    objectOfInterestXGI_2D['tomography_detector'] = jns.tomography_detector
    objectOfInterestXGI_2D['tomography_theta'] = jns.tomography_theta
    objectOfInterestXGI_2D['tomography_translation'] = jns.tomography_translation
    objectOfInterestXGI_2D['tomography_shutter'] = jns.tomography_shutter
    objectOfInterestXGI_2D['tomography_grating_translation_outer'] = jns.tomography_grating_translation_outer
    objectOfInterestXGI_2D['tomography_grating_translation_inner'] = jns.tomography_grating_translation_inner
    
    objectOfInterestHELICAL = {}
    objectOfInterestHELICAL['tomography_theta'] = jns.tomography_theta
    objectOfInterestHELICAL['tomography_shutter'] = jns.tomography_shutter
    objectOfInterestHELICAL['tomography_translation'] = jns.tomography_translation
    objectOfInterestHELICAL['tomography_detector'] = jns.tomography_detector
    objectOfInterestHELICAL['tomography_beammonitor'] = jns.tomography_beammonitor
    objectOfInterestHELICAL['tomography_translation_vert'] = jns.tomography_translation_vert
    
    msg = "Any of these mappings can be changed by editing a file named live_jythonNamespaceMapping, "
    msg += "\nlocated in i13-config/scripts (this can be done by beamline staff).\n"

    verbose_template = ""
    header_template = "****** %s ******"
    if m in supported_names_lst or m.startswith(tuple(supported_abbrevs_lst)):
        print(header_template %("NORMALISED-IMAGE SETTINGS"))
        for idx, (key, val) in enumerate(objectOfInterest.iteritems()):
            name = "object undefined!"
            if val is not None:
                name = str(val.getName())
            #print("%d. %s = %s" %(idx+1, key, name))
            #print("%d. %s = %s %s" %(idx+1, key, name, '%s' %('('+get_pv_name(val)+')' if verbose and (not get_pv_name(val) is None) else '')))
            print("%d. %s = %s %s" %(idx+1, key, name, '%s' %(get_pv_name(val,verbose))))
        print("\n")
    
    if m in ('all', 'micro') or m.startswith(('a','m')): 
        print(header_template %("TOMO STEP-SCAN PRIMARY SETTINGS"))
        for idx, (key, val) in enumerate(objectOfInterestSTEP.iteritems()):
            name = "object undefined!"
            if val is not None:
                name = str(val.getName())
            #print("%d. %s = %s" %(idx+1, key, name))
            #print("%d. %s = %s %s" %(idx+1, key, name, '%s' %('('+get_pv_name(val)+')' if verbose and (not get_pv_name(val) is None) else '')))
            print("%d. %s = %s %s" %(idx+1, key, name, '%s' %(get_pv_name(val,verbose))))
        print("\n")

        print(header_template %("TOMO FLY-SCAN PRIMARY SETTINGS"))
        for idx, (key, val) in enumerate(objectOfInterestFLY.iteritems()):
            name = "object undefined!"
            if val is not None:
                name = str(val.getName())
            #print("%d. %s = %s" %(idx+1, key, name))
            #print("%d. %s = %s %s" %(idx+1, key, name, '(%s)' %(get_pv_name(val) if verbose and (not get_pv_name(val) is None) else '')))
            print("%d. %s = %s %s" %(idx+1, key, name, '%s' %(get_pv_name(val,verbose))))
        print("\n")

    if m in ('all', 'heli') or m.startswith(('a','h')): 
        print(header_template %("HELICAL TOMO STEP-SCAN PRIMARY SETTINGS"))
        for idx, (key, val) in enumerate(objectOfInterestHELICAL.iteritems()):
            name = "object undefined!"
            if val is not None:
                name = str(val.getName())
            #print("%d. %s = %s" %(idx+1, key, name))
            #print("%d. %s = %s %s" %(idx+1, key, name, '(%s)' %(get_pv_name(val) if verbose and (not get_pv_name(val) is None) else '')))
            print("%d. %s = %s %s" %(idx+1, key, name, '%s' %(get_pv_name(val,verbose))))
        print("\n")
    
    if m in ('all', 'xgi') or m.startswith(('a','x')): 
        print(header_template %("1D-XGI STEP-SCAN PRIMARY SETTINGS"))
        for idx, (key, val) in enumerate(objectOfInterestXGI_1D.iteritems()):
            name = "object undefined!"
            if val is not None:
                name = str(val.getName())
            #print("%d. %s = %s" %(idx+1, key, name))
            #print("%d. %s = %s %s" %(idx+1, key, name, '%s' %('('+get_pv_name(val)+')' if verbose and (not get_pv_name(val) is None) else '')))
            print("%d. %s = %s %s" %(idx+1, key, name, '%s' %(get_pv_name(val,verbose))))
        print("\n")   
        
        print(header_template %("2D-XGI STEP-SCAN PRIMARY SETTINGS"))
        for idx, (key, val) in enumerate(objectOfInterestXGI_2D.iteritems()):
            name = "object undefined!"
            if val is not None:
                name = str(val.getName())
            #print("%d. %s = %s" %(idx+1, key, name))
            #print("%d. %s = %s %s" %(idx+1, key, name, '%s' %('('+get_pv_name(val)+')' if verbose and (not get_pv_name(val) is None) else '')))
            print("%d. %s = %s %s" %(idx+1, key, name, '%s' %(get_pv_name(val,verbose))))
        print("\n")   
    print(msg)
    
def reportTomo(modality='micro', verbose=False):
    return reportJythonNamespaceMapping(modality, verbose)

reportTomo.__doc__ = reportJythonNamespaceMapping.__doc__

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

def showNormalisedImageEx(outOfBeamPosition, exposureTime=None, imagesPerDark=1, imagesPerFlat=1, getDataOnly=False):
    logger = LoggerFactory.getLogger('tomographyScan.showNormalisedImageEx()')
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

    tomography_detector=jns.tomography_normalisedImage_detector
    if tomography_detector is None:
        raise "tomography_detector is not defined in Jython namespace"
    else:
        print "tomography_detector = %s" %(tomography_detector.getName())    
    currentTheta=tomography_theta()
    tomoScan(tomography_translation(), outOfBeamPosition, exposureTime, start=currentTheta, stop=currentTheta, step=1., imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat, addNXEntry=False,autoAnalyse=False,tomography_detector=tomography_detector)

    if getDataOnly:
        return True
    
    lsdp=jns.lastScanDataPoint()
    found=False 
    attempt=0

    while not found and attempt<11: 
        attempt+=1
        try:
            tomo_det_name = tomography_detector.getName()
            nxentry = str('/entry1/' + tomo_det_name)
            logger.debug('Opening entry ' + nxentry + ' in file '+ lsdp.currentFilename)
            nxfile = NexusFileHDF5.openNexusFile(lsdp.currentFilename)
            nxgroup = nxfile.getGroup(nxentry, False)
            if (nxgroup.containsDataNode("image_data")):
                nxdata = nxgroup.getDataNode("image_data")
            elif (nxgroup.containsDataNode("data")):
                nxdata = nxgroup.getDataNode("data")
            else:
                hint = " - try using pco1_sw instead of "+tomo_det_name if tomo_det_name != "pco1_sw" else '' 
                raise "Unable to find data in file"+hint

            dataset = nxdata.getDataset();

            # Convert images to floating point for manipulation
            dark = DatasetUtils.copy(getSingleImage(dataset, 0), Dataset.FLOAT64)
            flat = DatasetUtils.copy(getSingleImage(dataset, imagesPerDark), Dataset.FLOAT64)
            image = DatasetUtils.copy(getSingleImage(dataset, imagesPerDark + imagesPerFlat), Dataset.FLOAT64)
            found = True

        except:
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Error in showNormalisedImageEx", exceptionType, exception, traceback, False)            
            updateProgress(90, "Wait 5 seconds for image file to arrive from the detector system")
            time.sleep(5)

    if not found:
        raise "Unable to analyse data as it has not arrived from detector in time"
 
    flat.isubtract(dark)
    image.isubtract(dark).idivide(flat)

    imageName = str(lsdp.getScanIdentifier()) + " (image-dark)/(flat-dark)"
    image.setName(imageName)
    logger.debug("Creating " + imageName + " at " + nxentry + "/normalisedImage")
    nxfile.createData(nxentry, "normalisedImage", image, True)
    nxfile.close()

    rcp=Finder.getInstance().find("RCPController")
    rcp.openView("uk.ac.diamond.daq.tomography.datacollection.ui.NormalisedImage")
    dnp.plot.image(image, name="Normalised Image")
    #turn camera back on
    return True

# Return single 2D image from dataset
def getSingleImage(dataset, index):
    shape = dataset.getShape();
    return dataset.getSlice([index, 0, 0], [index + 1, shape[1], shape[2]], None).reshape(shape[1], shape[2])


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
        updateProgress(self.percentage, "Preparing for " + self.msg)
        updateProgress(self.percentage, "Move x")
        self.xMotor.moveTo(self.xMotorPosition)
        updateProgress(self.percentage, "Move theta")
        self.thetaMotor.moveTo(self.thetaMotorPosition)
        updateProgress(self.percentage, "Move shutter")
        self.shutter.moveTo(self.shutterPosition)
        self.image_key.moveTo(self.image_key_value)
        updateProgress(self.percentage, self.msg)

class PostScanRunnable(Runnable):
    def __init__(self, msg, percentage, shutter, shutterPosition):
        self.msg = msg
        self.percentage = percentage
        self.shutter=shutter
        self.shutterPosition = shutterPosition
        
    def run(self):
        updateProgress(self.percentage, self.msg)
        updateProgress(self.percentage, "Move shutter")
        self.shutter.moveTo(self.shutterPosition)
        updateProgress(self.percentage, self.msg)

"""
perform a continuous tomography scan
"""
def tomoFlyScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=False, autoAnalyse=True, closeShutterAfterFlats=True, extraFlatsAtEnd=False, closeShutterAtEnd=True, **kwargs):
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
    setupForAlignment - advanced use
    autoAnalyse - advanced use
    closeShutterAfterFlats -
    extraFlatsAtEnd=False -
    closeShutterAtEnd
    approxCOR - approximate centre of tomography rotation in the image (x,y) coordinates which can be utilised as a hint by subsequent tomography reconstruction (default = (None,None))
        For example, use a pair (<finite float number>, None) to indicate a vertical rotation axis in the image (x,y) coordinates   
    """
    startTm = datetime.datetime.now()
    atTomoFlyScanStart(**kwargs)
    logger = LoggerFactory.getLogger("tomographyScan.tomoFlyScan()")
    
    logger.debug("inBeamPosition: {}, outOfBeamPosition: {}, exposureTime: {}, "
                 + "start: {}, stop: {}, step: {}, darkFieldInterval: {}, flatFieldInterval: {}, " 
                 + "imagesPerDark: {}, imagesPerFlat: {}, min_i: {}, setupForAlignment: {}, "
                 + "autoAnalyse: {}, closeShutterAfterFlats: {}, extraFlatsAtEnd: {}",
                 inBeamPosition, outOfBeamPosition, exposureTime,
                 start, stop, step, darkFieldInterval, flatFieldInterval,
                 imagesPerDark, imagesPerFlat, min_i, setupForAlignment,
                 autoAnalyse, closeShutterAfterFlats, extraFlatsAtEnd)
    
    updateProgress(0, "Starting scan")
    jns=beamline_parameters.JythonNameSpaceMapping()
    tomography_flyscan_flat_dark_det=jns.tomography_flyscan_flat_dark_det
    savename=tomography_flyscan_flat_dark_det.name
    try:
        tomodet=jns.tomodet
        if tomodet is None:
            raise "tomodet is not defined in Jython namespace"

        tomography_theta=jns.tomography_theta
        if tomography_theta is None:
            raise "tomography_theta is not defined in Jython namespace"

        tomography_flyscan_theta=jns.tomography_flyscan_theta
        if tomography_flyscan_theta is None:
            raise "tomography_flyscan_theta is not defined in Jython namespace"

        tomography_flyscan_det=jns.tomography_flyscan_det
        if tomography_flyscan_det is None:
            raise "tomography_flyscan_det is not defined in Jython namespace"
        
        tomography_translation=jns.tomography_translation
        if tomography_translation is None:
            raise "tomography_translation is not defined in Jython namespace"
        

        tomography_shutter=jns.tomography_shutter
        if tomography_shutter is None:
            raise "tomography_shutter is not defined in Jython namespace"
        
        meta_add = jns.meta_add
        if meta_add is None:
            raise "meta_add is not defined in Jython namespace"

        camera_stage = jns.cs1
        if camera_stage is None:
            raise "camera_stage is not defined in Jython namespace"

        sample_stage = jns.sample_stage
        if sample_stage is None:
            raise "sample_stage is not defined in Jython namespace"        

        ionc_i = jns.ionc_i
        if ionc_i is None:
            raise "ionc_i is not defined in Jython namespace"
        ionc_i_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(ionc_i)

        pcEnc = tomography_flyscan_theta.getPcEnc()
        zebraPrefix = tomography_flyscan_theta.getContinuousMoveController().getZebra().getZebraPrefix()
        print("pcEnc = %i" %(pcEnc))
        print("zebraPrefix = %s" %(zebraPrefix))
        zebraEncoderSetPosPV = zebraPrefix + 'M' + str(pcEnc) +':SETPOS.PROC'   # need dedicated function for building this string from prefix and pcEnc
        print("zebraEncoderSetPosPV = %s" %(zebraEncoderSetPosPV))
        zebra = finder.find("zebra")
        zebra.encCopyMotorPosToZebra(pcEnc+1)
        meta_add( camera_stage)
        meta_add( sample_stage)
        
        try:
            from i13i_utilities import StringDisplayEpicsPVClass
            from gda.device.scannable import DummyScannable
            from gda.jython import InterfaceProvider
            _dct = {}
            _dct.update({'BL13I-EA-DET-01': {}}) # pco 4000
            _dct['BL13I-EA-DET-01'].update({'model': 'BL13I-EA-DET-01:CAM:Model_RBV'})
            _dct['BL13I-EA-DET-01'].update({'focus_name': 'BL13I-MO-CAM-01:FOCUS:MP:RBV:CURPOS'})
            _dct['BL13I-EA-DET-01'].update({'focus': 'BL13I-MO-CAM-01:FOCUS.RBV'})
            _dct['BL13I-EA-DET-01'].update({'turret': 'BL13I-MO-CAM-01:TURRET:P:UPD.D'})
            _dct['BL13I-EA-DET-01'].update({'turret': 'BL13I-MO-CAM-01:TURRET:P:UPD.D'})
            _dct['BL13I-EA-DET-01'].update({'pixel_rate': 'BL13I-EA-DET-01:CAM:PIX_RATE'})
            _dct['BL13I-EA-DET-01'].update({'adc_mode': 'BL13I-EA-DET-01:CAM:ADC_MODE'})

            _dct.update({'BL13I-EA-DET-02': {}}) # pco EDGE
            _dct['BL13I-EA-DET-02'].update({'model': 'BL13I-EA-DET-02:CAM:Model_RBV'})
            _dct['BL13I-EA-DET-02'].update({'focus_name': 'BL13I-MO-CAM-02:FOCUS:MP:RBV:CURPOS'})
            _dct['BL13I-EA-DET-02'].update({'focus': 'BL13I-MO-CAM-02:FOCUS.RBV'})
            _dct['BL13I-EA-DET-02'].update({'turret': 'BL13I-MO-CAM-02:TURRET:P:UPD.D'})
            _dct['BL13I-EA-DET-02'].update({'pixel_rate': 'BL13I-EA-DET-02:CAM:PIX_RATE'})
            _dct['BL13I-EA-DET-02'].update({'adc_mode': 'BL13I-EA-DET-02:CAM:ADC_MODE'})

            det_base_pv=tomography_flyscan_det.getCollectionStrategy().getAdBase().getBasePVName()
            #meta_add(_dct[det_base_pv])
            #det_base_pv='BL13I-EA-DET-02'
            try:
                meta_rm = jns.meta_rm
                meta_rm(det_cfg)
                del det_cfg
            except Exception, e:
                print("from del: %s" %(str(e)))
                
            det_cfg = ScannableGroup()
            det_cfg.setName("det_cfg")
            for k, v in _dct[det_base_pv].iteritems():
                print k,v
                det_cfg.addGroupMember(StringDisplayEpicsPVClass(k,v))
            
            readout_time_sbl = DummyScannable('readout_time', tomography_flyscan_det.getReadOutTime())
            readout_time_sbl.setLowerGdaLimits(0)
            det_cfg.addGroupMember(readout_time_sbl)
            det_cfg.configure()
            cmdSrvr = InterfaceProvider.getJythonNamespace()
            cmdSrvr.placeInJythonNamespace("det_cfg",det_cfg)
            meta_add(det_cfg)
            
            from i13i_utilities import PseudoScannable 
            flyscan_cfg = ScannableGroup()
            flyscan_cfg.setName("flyscan_cfg")
            flyscan_cfg.addGroupMember(PseudoScannable('tomography_flyscan_det',tomography_flyscan_det.getName()))
            flyscan_cfg.addGroupMember(PseudoScannable('tomography_theta',tomography_theta.getName()))
            flyscan_cfg.addGroupMember(PseudoScannable('tomography_translation',tomography_translation.getName()))
            flyscan_cfg.addGroupMember(PseudoScannable('tomography_shutter',tomography_shutter.getName()))
            flyscan_cfg.configure()
            cmdSrvr.placeInJythonNamespace("flyscan_cfg",flyscan_cfg)
            meta_add(flyscan_cfg)
            
            #print "before added" 
            #print det_cfg()
            #print "added!!!!!!!!!!!"
        except:
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Error in tomoFlyScan", exceptionType, exception, traceback, True)
            #raise Exception("Error in tomoFlyScan" + repr(exception))
               
        index=SimpleScannable()
        index.setCurrentPosition(0.0)
        index.setName(tomography_flyscan_theta.name)
        index.inputNames = tomography_flyscan_theta.inputNames
        index.extraNames = tomography_flyscan_theta.extraNames
        index.configure()
        
        updateProgress(0, "Move theta")
        tomography_theta.moveTo(start)
        start_tpl = (tomography_theta.getPosition(),)

        image_key=SimpleScannable()
        image_key.setCurrentPosition(0.0)
        image_key.setInputNames(["image_key"])
        image_key.setName("image_key")
        image_key.configure()
        image_key_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(image_key)

        ss1=SimpleScannable()
        ss1.name = tomography_flyscan_theta.getContinuousMoveController().name
        ss1.currentPosition=0.
        ss1.inputNames = tomography_flyscan_theta.getContinuousMoveController().inputNames
        ss1.extraNames = tomography_flyscan_theta.getContinuousMoveController().extraNames
        ss1.configure()
        
        tomography_flyscan_flat_dark_det.name = tomography_flyscan_det.name
        tomodet.stop()
        
        multiScanItems = []

        if imagesPerDark > 0:
            darkScan=ConcurrentScan([index, start_tpl*imagesPerDark, image_key, ionc_i, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
            multiScanItems.append(MultiScanItem(darkScan, PreScanRunnable("Taking darks", 0, tomography_shutter, "Close", tomography_translation, inBeamPosition, image_key, image_key_dark, tomography_theta, start), None))
        if imagesPerFlat > 0:
            flatScan=ConcurrentScan([index, start_tpl*imagesPerFlat, image_key, ionc_i, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
            multiScanItems.append(MultiScanItem(flatScan, PreScanRunnable("Taking flats",10, tomography_shutter, "Open", tomography_translation, outOfBeamPosition, image_key, image_key_flat, tomography_theta, start), PostScanRunnable("Closing shutter after taking flats",10, tomography_shutter, "Close") if closeShutterAfterFlats else None))
        
        scanForward=ConstantVelocityScanLine([tomography_flyscan_theta, start, stop, step,image_key_cont, ionc_i_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
        scanForward.setSendUpdateEvents(False)
        multiScanItems.append(MultiScanItem(scanForward, PreScanRunnable("Taking projections",20, tomography_shutter, "Open",tomography_translation, inBeamPosition, image_key, image_key_project, tomography_theta, start), None))
        if extraFlatsAtEnd:
            if imagesPerFlat > 0:
                flatScan=ConcurrentScan([index, (tomography_theta.getPosition(),)*imagesPerFlat, image_key, ionc_i, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
                multiScanItems.append(MultiScanItem(flatScan, PreScanRunnable("Taking flats at end",90, tomography_shutter, "Open", tomography_translation, outOfBeamPosition, image_key, image_key_flat, tomography_theta, stop), PostScanRunnable("Closing shutter after taking flats at end",90, tomography_shutter, "Close") if closeShutterAfterFlats else None))
        
        multiScanObj = MultiScanRunner(multiScanItems)
        addFlyScanNXTomoSubentry(multiScanItems[0].scan, tomography_flyscan_det.name, tomography_flyscan_theta.name, **kwargs)
        multiScanObj.runScan()
        if closeShutterAtEnd:
            tomography_shutter.moveTo("Close")

        if extraFlatsAtEnd:
            print("Moving sample to in-beam position after taking flats at the end of scan")
            tomography_translation.moveTo(inBeamPosition)

        tomography_flyscan_flat_dark_det.name = savename
        if setupForAlignment:
            tomodet.setupForAlignment()
        updateProgress(100, "Scan complete")
        if autoAnalyse and isLive():
            lsdp=jns.lastScanDataPoint()
            OSCommandRunner.runNoWait(["/dls_sw/apps/tomopy/tomopy/bin/gda/tomo_at_scan_end_kz", lsdp.currentFilename], OSCommandRunner.LOGOPTION.ALWAYS, None)

        return multiScanObj;
    except :
        exceptionType, exception, traceback = sys.exc_info()
        #turn camera back on
        tomography_flyscan_flat_dark_det.name = savename
        if setupForAlignment:
            tomodet.setupForAlignment()
        if kwargs.has_key("sendDataToTempDirectory") and (kwargs["sendDataToTempDirectory"] is not None) and kwargs["sendDataToTempDirectory"]:
            print "*Restoring data path to the original data directory: %s" %(kwargs['data_path_saved'])
            LocalProperties.set("gda.data.scan.datawriter.datadir", kwargs['data_path_saved'])
        handle_messages.log(None, "Error in tomoFlyScan", exceptionType, exception, traceback, True)
        raise Exception("Error in tomoFlyScan" + repr(exception))
    finally :
        try:
            meta_rm(flyscan_cfg)
            meta_rm(det_cfg)
            del det_cfg     # local
            del flyscan_cfg # local
            # need to find it and delete it?
            #det_cfg = finder.find("det_cfg")
            #del det_cfg
            cmdSrvr = InterfaceProvider.getJythonNamespace()
            cmdSrvr.placeInJythonNamespace("det_cfg", PseudoScannable("det_cfg","det_cfg"))                 # or None?
            cmdSrvr.placeInJythonNamespace("flyscan_cfg", PseudoScannable("flyscan_cfg","flyscan_cfg"))     # or None?
        except:
            pass
        atTomoFlyScanEnd(**kwargs)
        endTm = datetime.datetime.now()
        elapsedTm = endTm - startTm
        jns=beamline_parameters.JythonNameSpaceMapping()
        if isLive():
            print("This scan's data can be found in Nexus scan file %s." %(jns.lastScanDataPoint().currentFilename))
        print("Elapsed time [D day[s], ][H]H:MM:SS[.UUUUUU]: %s" %(str(elapsedTm)))



"""
perform a simple tomography scan
"""
def tomoScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0, flatFieldInterval=0,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1., addNXEntry=True, autoAnalyse=True, flatFieldAngle=None, tomography_detector=None, additionalScannables=[], **kwargs):
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
    flatFieldAngle - if specified to be None, flat fields will be taken at the most recent angle as the stage rotates during the scan (with the first flat field being taken at the scan start angle). 
        If specified to be a finite number, all flat fields will be taken at this particular angle (this is useful if it is impossible to move the sample out of the beam for some angles). 
    approxCOR - approximate centre of tomography rotation in the image (x,y) coordinates which can be utilised as a hint by subsequent tomography reconstruction (default = (None,None))
        For example, use a pair (<finite float number>, None) to indicate a vertical rotation axis in the image (x,y) coordinates   

    """
    startTm = datetime.datetime.now();
    print "Args START"
    if not tomography_detector is None:
        print "tomography_detector = %s" %(tomography_detector.getName()) 
    print "inBeamPosition = %.3f" %(inBeamPosition)
    print "outOfBeamPosition = %.3f" %(outOfBeamPosition)
    print "exposureTime = %.3f" %(exposureTime)
    print "start = %.3f" %(start)
    print "stop = %.3f" %(stop)
    print "step = %.3f" %(step)
    
    print "darkFieldInterval = %i" %(darkFieldInterval)
    print "flatFieldInterval = %i" %(flatFieldInterval)
    print "imagesPerDark = %i" %(imagesPerDark)
    print "imagesPerFlat = %i" %(imagesPerFlat)
    
    print "min_i = %.3f" %(min_i)
    
    print "addNXEntry = %s" %(addNXEntry)
    print "autoAnalyse = %s" %(autoAnalyse)
        
    if flatFieldAngle is None:
        print "flatFieldAngle = None"
    else:
        print "flatFieldAngle = %s" %(str(flatFieldAngle))
        
    if tomography_detector is None:
        print "tomography_detector = None"
    else:
        print "tomography_detector = %s" %(tomography_detector.getName())
        
    print "additionalScannables:"
    print additionalScannables
    
    print "kwargs"
    for k, v in kwargs.items():
        print (k, v)
        
    print "Args END"
        
    atTomoScanStart(**kwargs)
    if flatFieldAngle is None:
        msg = "\n Each flat field will be taken at the most recent angle as the stage rotates during the scan, \n"
        msg += " with the first flat field being taken at the scan start angle of %.4f deg" %(start)
        print msg
    else:
        print "All flat fields will be taken at the same, user-specified angle of %.4f deg" %(flatFieldAngle)
        if start < stop:
            min_ang = start
            max_ang = stop
        else:
            min_ang = stop
            max_ang = start 
        if flatFieldAngle < min_ang or flatFieldAngle > max_ang:
            print "WARNING: All flat fields will be taken at the same, user-supplied angle of %.4f deg which is outside the scanning range of [%.4f, %.4f]!" %(flatFieldAngle, start, stop)
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
        
        if tomography_detector is None:
	        tomography_detector=jns.tomography_detector
        if tomography_detector is None:
            raise "tomography_detector is not defined in Jython namespace"

        tomography_time=jns.tomography_time
        if tomography_time is None:
            raise "tomography_time is not defined in Jython namespace"
        
        tomography_beammonitor=jns.tomography_beammonitor
        if tomography_beammonitor is None:
            raise "tomography_beammonitor is not defined in Jython namespace"

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

        tomoScanDevice = make_tomoScanDevice(tomography_theta, tomography_shutter, 
                                             tomography_translation, image_key, index)

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
            scan_points.append((theta_pos if flatFieldAngle is None else flatFieldAngle, shutterOpen, outOfBeamPosition, image_key_flat, index )) #flat
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
                    scan_points.append((theta_pos if flatFieldAngle is None else flatFieldAngle, shutterOpen, outOfBeamPosition,  image_key_flat, index ))
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
                scan_points.append((theta_pos if flatFieldAngle is None else flatFieldAngle, shutterOpen, outOfBeamPosition,  image_key_flat, index )) #flat
                index = index + 1
        if imageSinceDark != 0:
            for i in range(imagesPerDark):
                scan_points.append((theta_pos, shutterClosed, inBeamPosition,  image_key_dark, index )) #dark
                index = index + 1        
                
        positionProvider = tomoScan_positions( start, stop, step, darkFieldInterval, imagesPerDark, flatFieldInterval, imagesPerFlat, \
                                               inBeamPosition, outOfBeamPosition, scan_points ) 
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
            
        scanObject=createConcurrentScan(scan_args)
        if addNXEntry:
            addNXTomoSubentry(scanObject, tomography_detector.name, tomography_theta.name, **kwargs)
        tomodet.stop()
        scanObject.runScan()

        if autoAnalyse and isLive():
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
        atTomoScanEnd(**kwargs)
        endTm = datetime.datetime.now()
        elapsedTm = endTm - startTm
        jns=beamline_parameters.JythonNameSpaceMapping()
        if isLive():
            print("This scan's data can be found in Nexus scan file %s." %(jns.lastScanDataPoint().currentFilename))
        print("Elapsed time [D day[s], ][H]H:MM:SS[.UUUUUU]: %s" %(str(elapsedTm)))

def restore_path(**kwargs):
    if kwargs.has_key("sendDataToTempDirectory") and (kwargs["sendDataToTempDirectory"] is not None) and kwargs["sendDataToTempDirectory"]:
        print "Restoring data to the original data directory: %s" %(kwargs['data_path_saved'])
        LocalProperties.set("gda.data.scan.datawriter.datadir", kwargs['data_path_saved'])

def atTomoScanStart(**kwargs):
    """
    Function to perform beamline-specific tasks after fly scan, eg...
    """
    pass

def atTomoScanEnd(**kwargs):
    """
    Function to perform beamline-specific tasks before fly scan, eg...
    """
    restore_path(**kwargs)

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

    jns=beamline_parameters.JythonNameSpaceMapping()
    additionalScannables=jns.tomography_additional_scannables
    setTitle(model.getTitle())

    updateProgress(0, "Starting tomoscan " + model.getTitle());
    logger.info("Starting tomoscan with parameters from: " + model.toString())

    det_dist, det_dist_units = _process_scan_parameters_det_dist(model)
    x_pixel_size, x_pixel_size_units, y_pixel_size, y_pixel_size_units = _process_scan_parameters_pixel_size(model)
    cor_x, cor_y = _process_scan_parameters_cor(model)
    print("Input (cor_x, cor_y) = (%s, %s)" %(str(cor_x), str(cor_y)))
    lin_stage, rot_stage = _process_scan_parameters_stages(model)
    if not lin_stage is None:
        print("Input lin_stage: %s" %(lin_stage.getName()))
    if not rot_stage is None:
        print("Input rot_stage: %s" %(rot_stage.getName()))
    
    kwargs = {}
    kwargs.update({'approxCOR': (cor_x, cor_y)})
    kwargs.update({'detectorToSampleDistance': det_dist})
    kwargs.update({'detectorToSampleDistanceUnits': "\'%s\'" %(det_dist_units)})
    kwargs.update({'XPixelSize': x_pixel_size})
    kwargs.update({'XPixelSizeUnits': "\'%s\'" %(x_pixel_size_units)})
    kwargs.update({'YPixelSize': y_pixel_size})
    kwargs.update({'YPixelSizeUnits': "\'%s\'" %(y_pixel_size_units)})
    kwargs.update({'closeShutterAfterLastScan': model.closeShutterAfterLastScan})
    kwargs.update({'sendDataToTempDirectory': model.sendDataToTempDirectory})
    
    if model.sendDataToTempDirectory:
        data_path_saved = LocalProperties.get("gda.data.scan.datawriter.datadir")
        print "data_path_saved = %s" %(data_path_saved)
        kwargs.update({'data_path_saved': "\'%s\'" %(data_path_saved)})
        visit_tmp_path = os.path.join(getVisitPath(),'tmp')
        LocalProperties.set("gda.data.scan.datawriter.datadir", visit_tmp_path)
        print "Saving data to the throw-away TMP sub-directory! - %s!" %(visit_tmp_path)
        
    try:
        if (model.flyScan):
            qFlyScanBatch(model.numFlyScans, model.title, model.flyScanDelay, 
                          model.inBeamPosition, model.outOfBeamPosition, exposureTime=model.exposureTime, start=model.start, stop=model.stop, step=model.step, 
                          darkFieldInterval=model.darkFieldInterval,  flatFieldInterval=model.flatFieldInterval,
                          imagesPerDark=model.imagesPerDark, imagesPerFlat=model.imagesPerFlat, min_i=model.minI,
                          extraFlatsAtEnd=model.extraFlatsAtEnd, **kwargs)
        else:
            tomoScan(model.inBeamPosition, model.outOfBeamPosition, exposureTime=model.exposureTime, start=model.start, stop=model.stop, step=model.step, 
                     darkFieldInterval=model.darkFieldInterval,  flatFieldInterval=model.flatFieldInterval,
                      imagesPerDark=model.imagesPerDark, imagesPerFlat=model.imagesPerFlat, min_i=model.minI, additionalScannables=additionalScannables, **kwargs)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        if model.sendDataToTempDirectory:
            print "*Restoring data path to the original data directory: %s" %(data_path_saved)
            LocalProperties.set("gda.data.scan.datawriter.datadir", "\'%s\'" %(data_path_saved))
        handle_messages.log(None, "Error in ProcessScanParameters", exceptionType, exception, traceback, True)
    updateProgress(100,"Done");
    

def atTomoFlyScanEnd(**kwargs):
    """
    Function to tidy up anything that needs tidying up after a fly scan, eg
    setting the angular speed of p2r to 30 deg/sec 
    """ 
    jns=beamline_parameters.JythonNameSpaceMapping()
    tomography_theta=jns.tomography_theta
    if tomography_theta is None:
        raise "tomography_theta is not defined in Jython namespace"
    tomography_theta_name = tomography_theta.name
    #print tomography_theta_name
    tomography_flyscan_det = jns.tomography_flyscan_det
    if tomography_flyscan_det is None:
        raise "tomography_flyscan_det is not defined in Jython namespace"
    tomography_flyscan_det_name = tomography_flyscan_det.name
    #print tomography_flyscan_det_name
    # below is a workaround for the fact that the updated p2r reports the current (actual) speed (0.0 deg/s) instead of the set (demand) speed, 
    # so, after the scan, GDA restores the speed to 0.0 deg/s, which mmakes p2r difficult to operate afterwards
    if ("p2r" in tomography_flyscan_det_name) or ("p2r" in tomography_theta_name):
        tomography_flyscan_theta = jns.tomography_flyscan_theta
        try:
            # set angular speed to some decent non-zero value
            tomography_flyscan_theta.setSpeed(30)
        except:
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Error in atTomoFlyScanEnd", exceptionType, exception, traceback, True)
            tomography_flyscan_theta.motor.smc.bidiAsciiCommunicator.closeConnection()
            try:
                # the 1st attempt is usually unsuccessful
                tomography_flyscan_theta.setSpeed(30)
            except:
                # the 2nd attempt is usually successful
                tomography_flyscan_theta.setSpeed(30)
    restore_path(**kwargs)
                
def atTomoFlyScanStart(**kwargs):
    """
    Function to perform beamline-specific tasks before fly scan, eg...
    """
    pass

def tomoTRFlyScan(description, inBeamPosition, outOfBeamPosition, exposureTime=1, start=10., tomoRange=180., step=0.1, ntomo=1, nrot=0, locked=None,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=False, autoAnalyse=True, closeShutterAfterFlats=True, extraFlatsAtEnd=False):
    """
    Function to collect a series of identical tomography frames, where each frame is a continuous-rotation tomography scan, 
    and where any two consecutive frames are separated from one another by a specified number of complete (360-deg) rotations
     Arg(s):
    description - description of the scan (or the sample that is being scanned. This is generally user-specific information that may be used to map to this scan later and is available in the NeXus file)
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds (default = 1)
    start - first rotation angle (default=0.)
    tomoRange - angular range over which a single tomography frame is collected (default=180.)
    step - angular step size (default = 0.1)
    ntomo - integer number of tomography frames, each being collected over the same angular range specified by tomoRange (default = 1)
    nrot - integer number of full (360 deg) rotations between the start angles of any two consecutive tomography frames (default = 0)
           Note: if nrot = 0, a single tomography frame is collected over the angular range specified by tomoRange 
    locked - if None, no action is taken
             if True, p2r's Move Mode is set to MMPOSITION, ie linear and rotational axes move together
             if False, p2r's Move Mode is set to MMPOSITION-JOG, ie linear and rotational axes move independently from one another
             (default = None)
    imagesPerDark - integer number of images to be taken in each dark-field collection (default=20)
    imagesPerFlat - integer number of images to be taken in each flat-field collection (default=20)
    extraFlatsAtEnd - if True, flats are taken after the main scan has finished as well as before it
    closeShutterAfterScan - if True, shutter is closed at the end of this function
    """
    _fname = tomoTRFlyScan.__name__
    print "Running %s" %(_fname,)
    ntomo = int(ntomo)
    nrot = int(nrot)
    
    if not description is None:
        setTitle(description)
    else:
        setTitle("undefined")
    
    if nrot > 0:
        if tomoRange >= nrot * 360.0:
            msg = "The condition: tomoRange < nrot * 360.0 is violated as %s >= %s * 360.0 - no scan will be run!" %(tomoRange, nrot)
            raise ValueError(msg)
        stop = 360.0*(nrot*ntomo - nrot + 1)
        ngates = ntomo
    else:
        # assume nrot == 0, which is interpreted as single tomography acquisition from start to start + tomoRange * ntomo
        stop = start + tomoRange * ntomo
        ngates = 1
        
    print "start = %f, stop = %f, step = %f" %(start, stop, step)
    
    
    updateProgress(0, "Starting scan")
    jns=beamline_parameters.JythonNameSpaceMapping()
    tomography_flyscan_flat_dark_det=jns.tomography_flyscan_flat_dark_det
    savename=tomography_flyscan_flat_dark_det.name
    try:
        tomodet=jns.tomodet
        if tomodet is None:
            raise "tomodet is not defined in Jython namespace"

        tomography_theta=jns.tomography_theta
        if tomography_theta is None:
            raise "tomography_theta is not defined in Jython namespace"

        tomography_flyscan_theta=jns.tomography_flyscan_theta
        if tomography_flyscan_theta is None:
            raise "tomography_flyscan_theta is not defined in Jython namespace"

        tomography_flyscan_det=jns.tomography_flyscan_det
        if tomography_flyscan_det is None:
            raise "tomography_flyscan_det is not defined in Jython namespace"
        
        tomography_translation=jns.tomography_translation
        if tomography_translation is None:
            raise "tomography_translation is not defined in Jython namespace"
        

        tomography_shutter=jns.tomography_shutter
        if tomography_shutter is None:
            raise "tomography_shutter is not defined in Jython namespace"
        
        meta_add = jns.meta_add
        if meta_add is None:
            raise "meta_add is not defined in Jython namespace"

        camera_stage = jns.cs1
        if camera_stage is None:
            raise "camera_stage is not defined in Jython namespace"

        sample_stage = jns.sample_stage
        if sample_stage is None:
            raise "sample_stage is not defined in Jython namespace"        

        ionc_i = jns.ionc_i
        if ionc_i is None:
            raise "ionc_i is not defined in Jython namespace"
        ionc_i_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(ionc_i)
        
        print "imagesPerDark = %i, imagesPerFlat = %i" %(imagesPerDark, imagesPerFlat)
        nother = imagesPerDark + imagesPerFlat
        nother += (imagesPerFlat if extraFlatsAtEnd else 0)
        nprojs = ScannableUtils.getNumberSteps(tomography_flyscan_theta, start, start+tomoRange, step) + 1
        print "ngates = %i, nprojs = %i, nother = %i" %(ngates, nprojs, nother)
        #if is_p2r_used:
        _p2rcvmc = finder.find("p2rcvmc")
        _p2rcvmc.setNumberOfGates(ngates)
        _p2rcvmc.setNprojs(nprojs)
        _p2rcvmc.setNother(nother)
        _p2rcvmc.setP2R_start(start)
        _p2rcvmc.setP2R_end(start+tomoRange)
        _p2rcvmc.setP2R_step(step)
        _p2rcvmc.setP2R_end_eff(stop)
        _p2rcvmc.setTomoRange(tomoRange)
        _p2rcvmc.setNrot(nrot)
        _p2rcvmc.setP2R_gap(True)
        _p2rcvmc.setZindex(0)
        if not p2r_locked is None: 
            _p2rcvmc.setP2R_locked(p2r_locked)


        meta_add( camera_stage)
        meta_add( sample_stage)
               

        index=SimpleScannable()
        index.setCurrentPosition(0.0)
        index.setName(tomography_flyscan_theta.name)
        index.inputNames = tomography_flyscan_theta.inputNames
        index.extraNames = tomography_flyscan_theta.extraNames
        index.configure()
        
        updateProgress(0, "Move theta")
        tomography_theta.moveTo(start)
        start_tpl = (tomography_theta.getPosition(),)


        image_key=SimpleScannable()
        image_key.setCurrentPosition(0.0)
        image_key.setInputNames(["image_key"])
        image_key.setName("image_key")
        image_key.configure()
        image_key_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(image_key)
        
        ss1=SimpleScannable()
        ss1.name = tomography_flyscan_theta.getContinuousMoveController().name
        ss1.currentPosition=0.
        ss1.inputNames = tomography_flyscan_theta.getContinuousMoveController().inputNames
        ss1.extraNames = tomography_flyscan_theta.getContinuousMoveController().extraNames
        ss1.configure()
        
        

        
        tomography_flyscan_flat_dark_det.name = tomography_flyscan_det.name
        tomodet.stop()
        
        multiScanItems = []

        if imagesPerDark > 0:
            darkScan=ConcurrentScan([index, start_tpl*imagesPerDark, image_key, ionc_i, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
            multiScanItems.append(MultiScanItem(darkScan, PreScanRunnable("Taking darks", 0, tomography_shutter, "Close", tomography_translation, inBeamPosition, image_key, image_key_dark, tomography_theta, start), None))
        if imagesPerFlat > 0:
            flatScan=ConcurrentScan([index, start_tpl*imagesPerFlat, image_key, ionc_i, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
            multiScanItems.append(MultiScanItem(flatScan, PreScanRunnable("Taking flats",10, tomography_shutter, "Open", tomography_translation, outOfBeamPosition, image_key, image_key_flat, tomography_theta, start), PostScanRunnable("Closing shutter after taking flats",10, tomography_shutter, "Close") if closeShutterAfterFlats else None))
        
        scanForward=ConstantVelocityScanLine([tomography_flyscan_theta, start, stop, step,image_key_cont, ionc_i_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
        scanForward.setSendUpdateEvents(False)
        multiScanItems.append(MultiScanItem(scanForward, PreScanRunnable("Taking projections",20, tomography_shutter, "Open",tomography_translation, inBeamPosition, image_key, image_key_project, tomography_theta, start), None))
        if extraFlatsAtEnd:
            if imagesPerFlat > 0:
                flatScan=ConcurrentScan([index, (tomography_theta.getPosition(),)*imagesPerFlat, image_key, ionc_i, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
                multiScanItems.append(MultiScanItem(flatScan, PreScanRunnable("Taking flats at end",90, tomography_shutter, "Open", tomography_translation, outOfBeamPosition, image_key, image_key_flat, tomography_theta, stop), PostScanRunnable("Closing shutter after taking flats at end",90, tomography_shutter, "Close") if closeShutterAfterFlats else None))
        
        multiScanObj = MultiScanRunner(multiScanItems)
        #must pass fist scan to be run
        addFlyScanNXTomoSubentry(multiScanItems[0].scan, tomography_flyscan_det.name, tomography_flyscan_theta.name)
        multiScanObj.runScan()
        tomography_shutter.moveTo("Close")
            
        if extraFlatsAtEnd:
            print("Moving sample to in-beam position after taking flats at the end of scan")
            tomography_translation.moveTo(inBeamPosition)
        #turn camera back on
        tomography_flyscan_flat_dark_det.name = savename
        if setupForAlignment:
            tomodet.setupForAlignment()
        updateProgress(100, "Scan complete")
        if autoAnalyse and isLive():
            lsdp=jns.lastScanDataPoint()
            OSCommandRunner.runNoWait(["/dls_sw/apps/tomopy/tomopy/bin/gda/tomo_at_scan_end_kz", lsdp.currentFilename], OSCommandRunner.LOGOPTION.ALWAYS, None)

        return multiScanObj;
    except :
        exceptionType, exception, traceback = sys.exc_info()
        #turn camera back on
        tomography_flyscan_flat_dark_det.name = savename
        if setupForAlignment:
            tomodet.setupForAlignment()
        handle_messages.log(None, "Error in tomoFlyScan", exceptionType, exception, traceback, True)
    finally :
        atTomoFlyScanEnd()

    print "Finished running %s" %(_fname,)
    


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

def qFlyScanBatch(nScans, batchTitle, interWaitSec, inBeamPosition, outOfBeamPosition, exposureTime=1., start=-90., stop=90., step=0.1, darkFieldInterval=0., flatFieldInterval=0., imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=False, autoAnalyse=True, closeShutterAfterFlats=True, extraFlatsAtEnd=False, **kwargs):
    """
    Desc:
    Fn to submit a given number of identical tomoFlyScans to the queue for automatic execution with optional wait time between any two consecutive scans
        Note(s):
        (1) shutter is automatically closed before any wait period begins and then opened after that period has elapsed (ie before the next scan is executed) 
        (2) shutter is automatically closed after the entire batch has finished
    
    Arg(s):
    nScans = total number of identical scans to be executed in the batch
        Note(s):
        (1) nScans=1 is admissible
    batchTitle = description of the sample or this batch of scans to be recorded in each Nexus scan file (each scan gets a unique post-fix ID appended to its batch title) 
    interWaitSec = interval of time to wait between any two consecutive scans 
        Note(s): 
        (1) interWaitSec=0 is admissible (in which case no waiting is performed between scans) 
        (2) if interWaitSec is None, no waiting is performed between scans 
        (3) no waiting is performed after the last scan in the batch 
        (4) note that, irrespective of whether interWaitSec > 0 or not, some extra 'wait' time will always be spent on moving the rotation stage to the start angle before the next scan is able to proceed 
    """
    thisfn = qFlyScanBatch.__name__
    
    logger = LoggerFactory.getLogger("tomographyScan.qFlyScanBatch()")
    
    logger.debug("nScans: {}, batchTitle: {}, interWaitSec: {}, "
                 + "inBeamPosition: {}, outOfBeamPosition: {}, exposureTime: {}, "
                 + "start: {}, stop: {}, step: {}, darkFieldInterval: {}, flatFieldInterval: {}, " 
                 + "imagesPerDark: {}, imagesPerFlat: {}, min_i: {}, setupForAlignment: {}, "
                 + "autoAnalyse: {}, closeShutterAfterFlats: {}, extraFlatsAtEnd: {}",
                 nScans, batchTitle, interWaitSec,
                 inBeamPosition, outOfBeamPosition, exposureTime,
                 start, stop, step, darkFieldInterval, flatFieldInterval,
                 imagesPerDark, imagesPerFlat, min_i, setupForAlignment,
                 autoAnalyse, closeShutterAfterFlats, extraFlatsAtEnd)


    _args = []  # to store pairs (arg_name, arg_value) for executing tomoFlyScan
    _args.append(("inBeamPosition", inBeamPosition))
    _args.append(("outOfBeamPosition", outOfBeamPosition))
    _args.append(("exposureTime", exposureTime))
    _args.append(("start", start))
    _args.append(("stop", stop))
    _args.append(("step", step))
    _args.append(("darkFieldInterval", darkFieldInterval))
    _args.append(("flatFieldInterval", flatFieldInterval))
    _args.append(("imagesPerDark", imagesPerDark))
    _args.append(("imagesPerFlat", imagesPerFlat))
    _args.append(("min_i", min_i))
    _args.append(("setupForAlignment", setupForAlignment))
    _args.append(("autoAnalyse", autoAnalyse))
    _args.append(("closeShutterAfterFlats", closeShutterAfterFlats))
    _args.append(("extraFlatsAtEnd", extraFlatsAtEnd))
    
    _args_from_kwargs = []
    _args_from_kwargs = [(k,v) for k, v in kwargs.iteritems()]
    _args.extend(_args_from_kwargs) 

    def mysleep(secsToWait, v=True):
        if v:
            print "Waiting for %i sec..." %(secsToWait)  
        sleep(secsToWait)
        if v:
            print "Finished waiting for %i sec" %(secsToWait)
    
    jns=beamline_parameters.JythonNameSpaceMapping()
    tomography_shutter = jns.tomography_shutter
    if tomography_shutter is None:
        raise "tomography_shutter is not defined in Jython namespace"
    shutter_close_cmd = "%s.moveTo(\"%s\")" %(tomography_shutter.getName(), "Close")
    shutter_open_cmd = "%s.moveTo(\"%s\")" %(tomography_shutter.getName(), "Open")
    
    cqp = finder.find("commandQueueProcessor")
    
    if (batchTitle is None) or len(batchTitle)==0:
        batchTitle = thisfn
    
    title_saved = getTitle()
    if (title_saved is None) or len(title_saved)==0:
        title_saved = "undefined"
    print "title_saved = %s" %(title_saved)
    scan_cmd = ",".join(["%s=%s" %(p[0], str(p[1])) for p in _args])
    scan_cmd = "tomographyScan.tomoFlyScan(" + scan_cmd + ")"
    
    for i in range(nScans):
        title_tmp = batchTitle
        if nScans > 1:
            title_tmp += "_%s/%s" %(i+1, nScans)
            
        set_title_cmd = "setTitle(\"%s\")" %(title_tmp)
        cmd_tmp = set_title_cmd + ";" + scan_cmd
        sleep_cmd = None
        if (not (interWaitSec is None)) and interWaitSec > 0 and i < (nScans-1):
            sleep_cmd = "time.sleep(%f)" %(interWaitSec)
        if sleep_cmd is not None:
            sleep_cmd = shutter_close_cmd + ";" + sleep_cmd + ";" + shutter_open_cmd
            cmd_tmp = cmd_tmp + ";" + sleep_cmd
        print "scan %i (of %i): cmd_tmp = %s, title = %s" %(i+1, nScans, cmd_tmp, title_tmp)
        cmd_desc_tmp = set_title_cmd + ";" + "tomoFlyScan(...)" + (";" + sleep_cmd if sleep_cmd is not None else '')
        cqp.addToTail(JythonCommandCommandProvider(cmd_tmp, cmd_desc_tmp, None)) 
    
    # after all scans are finished
    set_title_saved_cmd = "setTitle(\"%s\")" %(title_saved)
    if kwargs.has_key("closeShutterAfterLastScan") and (kwargs["closeShutterAfterLastScan"] is not None) and kwargs["closeShutterAfterLastScan"]:
        batch_end_cmd = shutter_close_cmd + ";" + set_title_saved_cmd
    else:
        batch_end_cmd = set_title_saved_cmd
    print "batch_end_cmd = %s" %(batch_end_cmd)
    cqp.addToTail(JythonCommandCommandProvider(batch_end_cmd, batch_end_cmd, None))
    
def tomoScanWithFrames(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
              imagesPerDark=20, imagesPerFlat=20, frames=1, min_i=-1., addNXEntry=True, autoAnalyse=True, tomography_detector=None, additionalScannables=[], **kwargs):
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
        image_key_frame=4   # kz
        frames=int(frames)  # kz
        if frames < 1:      # kz
            frames = 1      # kz
        
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

        tomography_time=jns.tomography_time
        if tomography_time is None:
            raise "tomography_time is not defined in Jython namespace"
        
        tomography_beammonitor=jns.tomography_beammonitor
        if tomography_beammonitor is None:
            raise "tomography_beammonitor is not defined in Jython namespace"

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

        tomoScanDevice = make_tomoScanDevice(tomography_theta, tomography_shutter, 
                                             tomography_translation, image_key, index)

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
        for frm in range(frames):   # kz
            scan_points.append((theta_pos,shutterOpen, inBeamPosition, image_key_project if frm==0 else image_key_frame, index )) #first
            index = index + 1        
        imageSinceDark=0
        imageSinceFlat=0
        for i in range(numberSteps):
            theta_pos = theta_points[i+1]
            for frm in range(frames):   #kz
                scan_points.append((theta_pos, shutterOpen, inBeamPosition, image_key_project if frm==0 else image_key_frame, index ))#main image
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
        if min_i > 0.:
            import gdascripts.scannable.beamokay
            ionc_i = jns.ionc_i
            if ionc_i is None:
                raise "ionc_i is not defined in Jython namespace"
            beamok=gdascripts.scannable.beamokay.WaitWhileScannableBelowThresholdMonitorOnly("beamok", ionc_i, min_i)
            scan_args.append(beamok)
            
        for scannable in additionalScannables:
            scan_args.append(scannable)
            
        scanObject=createConcurrentScan(scan_args)
        if addNXEntry:
            addNXTomoSubentry(scanObject, tomography_detector.name, tomography_theta.name, **kwargs)
        tomodet.stop()
        scanObject.runScan()

        if autoAnalyse and isLive():
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
        
        
def getApproxCoR():
    # assuming camera is in the i13 default orientation wrt to the axis of rotation
    cam_max_sensor_size_x = finder.find("pco1_addetector").getAdBase().getMaxSizeX_RBV()
    cor_x = float(cam_max_sensor_size_x) * 0.5
    cor_y = None
    return cor_x, cor_y

def _process_scan_parameters_cor(parameters):
    cor_x = cor_y = None
    if len(parameters.approxCentreOfRotation) > 0:
        print "Input CoR = %s" %(parameters.approxCentreOfRotation)
        print "Input CoR len = %i" %(len(parameters.approxCentreOfRotation))
        print("Input CoR's type = %s" %(type(parameters.approxCentreOfRotation)))
        cor_y = None
        try:
            cor_x = float(parameters.approxCentreOfRotation)
        except Exception, e:
            cor_x, cor_y = getApproxCoR()
            print("cor_y type = %s" %(type(cor_y)))
            msg = "Error reading input cor_x: %s. Using default value of %.3f instead!" %(str(e), cor_x)
            print msg
    else:
        cor_x, cor_y = getApproxCoR()
    return cor_x, cor_y
    
def _process_scan_parameters_det_dist(parameters):
    det_dist = None
    if len(parameters.detectorToSampleDistance) > 0:
        print "Input detectorToSampleDistance = %s" %(parameters.detectorToSampleDistance)
        print "Input detectorToSampleDistance len = %i" %(len(parameters.detectorToSampleDistance))
        print("Input detectorToSampleDistance's type = %s" %(type(parameters.detectorToSampleDistance)))
        try:
            det_dist = float(parameters.detectorToSampleDistance)
        except Exception, e:
            msg = "Error reading input detectorToSampleDistance: %s. Using default value instead!" %(str(e))
            print msg
    else:
        print("No input detectorToSampleDistance. Using default value.")
    return det_dist, parameters.detectorToSampleDistanceUnits

def _process_scan_parameters_pixel_size(parameters):
    x_pixel_size = None
    if len(parameters.xPixelSize) > 0:
        print "Input XPixelSize = %s" %(parameters.xPixelSize)
        print "Input XPixelSize len = %i" %(len(parameters.xPixelSize))
        print("Input XPixelSize's type = %s" %(type(parameters.xPixelSize)))
        try:
            x_pixel_size = float(parameters.xPixelSize)
        except Exception, e:
            msg = "Error reading input XPixelSize: %s. Using default value instead!" %(str(e))
            print msg
    else:
        print("No input XPixelSize. Using default value.")
        
    y_pixel_size = None
    if len(parameters.yPixelSize) > 0:
        print "Input YPixelSize = %s" %(parameters.yPixelSize)
        print "Input YPixelSize len = %i" %(len(parameters.yPixelSize))
        print("Input YPixelSize's type = %s" %(type(parameters.yPixelSize)))
        try:
            y_pixel_size = float(parameters.yPixelSize)
        except Exception, e:
            msg = "Error reading input YPixelSize: %s. Using default value instead!" %(str(e))
            print msg
    else:
        print("No input YPixelSize. Using default value.")
    return x_pixel_size, parameters.xPixelSizeUnits, y_pixel_size, parameters.yPixelSizeUnits

def _process_scan_parameters_stages(parameters):
    lin_stage = None
    if len(parameters.linearStage) > 0:
        print "Input linearStage = %s" %(parameters.linearStage)
        print "Input linearStage len = %i" %(len(parameters.linearStage))
        print("Input linearStage's type = %s" %(type(parameters.linearStage)))
        try:
            lin_stage = finder.find(parameters.linearStage)
        except Exception, e:
            msg = "Error reading input linearStage: %s. Using value in live_JythonNamespaceMapping." %(str(e))
            print msg
    else:
        print("No input linearStage. Using value in live_JythonNamespaceMapping.")
    
    rot_stage = None
    if len(parameters.rotationStage) > 0:
        print "Input rotationStage = %s" %(parameters.rotationStage)
        print "Input rotationStage len = %i" %(len(parameters.rotationStage))
        print("Input rotationStage's type = %s" %(type(parameters.rotationStage)))
        try:
            rot_stage = finder.find(parameters.rotationStage)
        except Exception, e:
            msg = "Error reading input rotationStage: %s. Using value in live_JythonNamespaceMapping." %(str(e))
            print msg
    else:
        print("No input rotationStage. Using value in live_JythonNamespaceMapping.")
    return lin_stage, rot_stage


def _addNXTomoSubentryValues(nxLinkCreatorObj, **kwargs):
    if kwargs.has_key("approxCOR") and (kwargs["approxCOR"] is not None):
        approxCOR = kwargs["approxCOR"]
        print "approxCOR = "
        print approxCOR
        if approxCOR[0] is None:
            nxLinkCreatorObj.setInstrument_detector_x_rotation_axis_pixel_position(float('nan'))
        else:
            nxLinkCreatorObj.setInstrument_detector_x_rotation_axis_pixel_position(approxCOR[0])
            
        if approxCOR[1] is None:
            nxLinkCreatorObj.setInstrument_detector_y_rotation_axis_pixel_position(float('nan'))
        else:
            nxLinkCreatorObj.setInstrument_detector_y_rotation_axis_pixel_position(approxCOR[1])
    else:
        nxLinkCreatorObj.setInstrument_detector_x_rotation_axis_pixel_position(float('nan'))
        nxLinkCreatorObj.setInstrument_detector_y_rotation_axis_pixel_position(float('nan'))
        
    if kwargs.has_key("detectorToSampleDistance") and (kwargs["detectorToSampleDistance"] is not None):
        detectorToSampleDistance = kwargs["detectorToSampleDistance"]
        print "detectorToSampleDistance = %.3f" %(detectorToSampleDistance)
        if detectorToSampleDistance is None:
            nxLinkCreatorObj.setInstrument_detector_distance(float('nan'))
        else:
            nxLinkCreatorObj.setInstrument_detector_distance(detectorToSampleDistance)
    else:
        nxLinkCreatorObj.setInstrument_detector_distance(float('nan'))
    
    if kwargs.has_key("detectorToSampleDistanceUnits") and (kwargs["detectorToSampleDistanceUnits"] is not None):
        detectorToSampleDistanceUnits = kwargs["detectorToSampleDistanceUnits"]
        print "detectorToSampleDistanceUnits = "+ detectorToSampleDistanceUnits
        if detectorToSampleDistanceUnits is None or len(detectorToSampleDistanceUnits) == 0:
            nxLinkCreatorObj.setInstrument_detector_distance_units('undefined')
        else:
            nxLinkCreatorObj.setInstrument_detector_distance_units(detectorToSampleDistanceUnits)
    else:
        nxLinkCreatorObj.setInstrument_detector_distance_units('undefined')
    
    if kwargs.has_key("XPixelSize") and (kwargs["XPixelSize"] is not None):
        XPixelSize = kwargs["XPixelSize"]
        print "XPixelSize = %.3f" %(XPixelSize)
        if XPixelSize is None:
            nxLinkCreatorObj.setInstrument_detector_x_pixel_size(float('nan'))
        else:
            nxLinkCreatorObj.setInstrument_detector_x_pixel_size(XPixelSize)
    else:
        nxLinkCreatorObj.setInstrument_detector_x_pixel_size(float('nan'))
    
    if kwargs.has_key("XPixelSizeUnits") and (kwargs["XPixelSizeUnits"] is not None):
        XPixelSizeUnits = kwargs["XPixelSizeUnits"]
        print "XPixelSizeUnits = "+XPixelSizeUnits
        if XPixelSizeUnits is None or len(XPixelSizeUnits) == 0:
            nxLinkCreatorObj.setInstrument_detector_pixel_size_units('undefined')
        else:
            nxLinkCreatorObj.setInstrument_detector_pixel_size_units(XPixelSizeUnits)
    else:
        nxLinkCreatorObj.setInstrument_detector_pixel_size_units('undefined')
        
    if kwargs.has_key("YPixelSize") and (kwargs["YPixelSize"] is not None):
        YPixelSize = kwargs["YPixelSize"]
        print "YPixelSize = %.3f" %(YPixelSize)
        if YPixelSize is None:
            nxLinkCreatorObj.setInstrument_detector_y_pixel_size(float('nan'))
        else:
            nxLinkCreatorObj.setInstrument_detector_y_pixel_size(YPixelSize)
    else:
        nxLinkCreatorObj.setInstrument_detector_y_pixel_size(float('nan'))
    
    if kwargs.has_key("YPixelSizeUnits") and (kwargs["YPixelSizeUnits"] is not None):
        YPixelSizeUnits = kwargs["YPixelSizeUnits"]
        print "YPixelSizeUnits = "+YPixelSizeUnits
        if YPixelSizeUnits is None or len(YPixelSizeUnits) == 0:
            nxLinkCreatorObj.setInstrument_detector_pixel_size_units('undefined')
        else:
            nxLinkCreatorObj.setInstrument_detector_pixel_size_units(YPixelSizeUnits)
    else:
        nxLinkCreatorObj.setInstrument_detector_pixel_size_units('undefined')

def isLive():
    mode = LocalProperties.get("gda.mode")
    return mode =="live" or mode =="live_localhost"

def getVisitPath():
    data_path = LocalProperties.get("gda.data.scan.datawriter.datadir")
    data_path_split = data_path.rsplit('/')
    visit_path = '/'
    for i in range(1,6):
        visit_path = os.path.join(visit_path, data_path_split[i])
    return visit_path


from BeamlineParameters import JythonNameSpaceMapping, FinderNameMapping

from gda.scan import StaticScan
from uk.ac.gda.beans.exafs import XanesScanParameters
from gda.configuration.properties import LocalProperties
from gda.device import CounterTimer
from gda.device.detector.countertimer import CounterTimerBase
from gda.device.detector.xspress import XspressDetector
from gda.data.scan.datawriter import XasAsciiDataWriter, NexusExtraMetadataDataWriter
from gdascripts.messages.handle_messages import simpleLog

#from exafsscripts.exafs.i20_setup import setupI20, finishI20
from exafsscripts.exafs.configFluoDetector import configFluoDetector
from gda.jython.commands.ScannableCommands import scan, pos, add_default 
import string
from time import sleep
from gda.factory import Finder

from gda.data.scan.datawriter import NexusExtraMetadataDataWriter
from gda.data.scan.datawriter import NexusFileMetadata
from gda.data.scan.datawriter.NexusFileMetadata import EntryTypes, NXinstrumentSubTypes
from uk.ac.gda.beans import BeansFactory
from java.io import File
from gda.device.detector.xspress import ResGrades
from uk.ac.gda.beans.exafs import QEXAFSParameters

rootnamespace = {}

def finish():
    pass
    

def setup(beanGroup):
    if beanGroup.getDetector().getExperimentType() == "Fluorescence":
        if (beanGroup.getDetector().getFluorescenceParameters().getDetectorType() == "Germanium" ):
            fullFileName = beanGroup.getScriptFolder() + beanGroup.getDetector().getFluorescenceParameters().getConfigFileName()
            bean = BeansFactory.getBean(File(fullFileName));
            bean.setReadoutMode(XspressDetector.READOUT_MCA);
            bean.setResGrade(ResGrades.NONE);
            elements = bean.getDetectorList();
            for element in elements: 
                rois = element.getRegionList();
                element.setWindow(rois.get(0).getRegionStart(), rois.get(0).getRegionEnd())
        configFluoDetector(beanGroup)
    #setup topup
    scan = beanGroup.getScan()
    collectionTime = 0.0
    if isinstance(scan,XanesScanParameters):
        regions = scan.getRegions()        
        for region in regions:
            if(collectionTime < region.getTime()):
                collectionTime =region.getTime()
    elif isinstance(scan,QEXAFSParameters):
        pass
    else:
        collectionTime = scan.getExafsTime()
        if(scan.getExafsToTime() > collectionTime):
            collectionTime = scan.getExafsToTime()
    print "setting collection time to" , str(collectionTime)
    command_server = Finder.getInstance().find("command_server")    
    topupMonitor = command_server.getFromJythonNamespace("topupMonitor", None)    
    beam = command_server.getFromJythonNamespace("beam", None)
    add_default(beam)
    detectorFillingMonitor = command_server.getFromJythonNamespace("detectorFillingMonitor", None)
    trajBeamMonitor = command_server.getFromJythonNamespace("trajBeamMonitor", None)
    topupMonitor.setPauseBeforePoint(True)
    topupMonitor.setPauseBeforeLine(False)
    topupMonitor.setCollectionTime(collectionTime)
    beam.setPauseBeforePoint(True)
    beam.setPauseBeforeLine(True)
    if(beanGroup.getDetector().getExperimentType() == "Fluorescence" and beanGroup.getDetector().getFluorescenceParameters().getDetectorType() == "Germanium"): 
        add_default(detectorFillingMonitor)
        detectorFillingMonitor.setPauseBeforePoint(True)
        detectorFillingMonitor.setPauseBeforeLine(False) 
    trajBeamMonitor.setActive(False)
    sampleParameters = beanGroup.getSample()
    stage = sampleParameters.getSampleStageParameters()
    att1 = sampleParameters.getAttenuatorParameter1()
    att2 = sampleParameters.getAttenuatorParameter2()
    pos([rootnamespace['sc_MicroFocusSampleX'], stage.getX(), rootnamespace['sc_MicroFocusSampleY'], stage.getY(), rootnamespace['sc_sample_z'], stage.getZ()])
    pos([rootnamespace['D7A'], att1.getSelectedPosition(), rootnamespace['D7B'], att2.getSelectedPosition()])
    Finder.getInstance().find("RCPController").openPesrpective("org.diamond.exafs.ui.PlottingPerspective")
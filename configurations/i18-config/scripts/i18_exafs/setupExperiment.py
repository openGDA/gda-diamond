from BeamlineParameters import JythonNameSpaceMapping, FinderNameMapping

from gda.scan import StaticScan
from uk.ac.gda.beans.exafs import XanesScanParameters,OutputParameters
from gda.configuration.properties import LocalProperties
from gda.device import CounterTimer
from gda.device.detector.countertimer import CounterTimerBase
from gda.device.detector.xspress import XspressDetector
from gda.data.scan.datawriter import XasAsciiDataWriter, NexusExtraMetadataDataWriter
from gdascripts.messages.handle_messages import simpleLog

#from exafsscripts.exafs.i20_setup import setupI20, finishI20
from exafsscripts.exafs.configFluoDetector import configFluoDetector
from gda.jython.commands.ScannableCommands import scan, pos, add_default, remove_default 
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
	command_server = Finder.getInstance().find("command_server")
	beam = command_server.getFromJythonNamespace("beam", None)
	detectorFillingMonitor = command_server.getFromJythonNamespace("detectorFillingMonitor", None)
	remove_default(beam)
	remove_default(detectorFillingMonitor)
	#pass
	

def setup(beanGroup):
	if beanGroup.getDetector().getExperimentType() == "Fluorescence":
		if (beanGroup.getDetector().getFluorescenceParameters().getDetectorType() == "Germanium"):
			fullFileName = beanGroup.getScriptFolder() + beanGroup.getDetector().getFluorescenceParameters().getConfigFileName()
			bean = BeansFactory.getBean(File(fullFileName));
			bean.setReadoutMode(XspressDetector.READOUT_MCA);
			bean.setResGrade(ResGrades.NONE);
			elements = bean.getDetectorList();
			for element in elements: 
				rois = element.getRegionList();
				element.setWindow(rois.get(0).getRegionStart(), rois.get(0).getRegionEnd())
			BeansFactory.saveBean(File(fullFileName), bean)
		configFluoDetector(beanGroup)
		#setup topup
		scan = beanGroup.getScan()
		collectionTime = 0.0
		if isinstance(scan, XanesScanParameters):
			regions = scan.getRegions()		
			for region in regions:
				if(collectionTime < region.getTime()):
					collectionTime = region.getTime()
		elif isinstance(scan, QEXAFSParameters):
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
			detectorFillingMonitor.setCollectionTime(collectionTime)
		trajBeamMonitor.setActive(False)
		##set the file name for the output parameters
		outputBean=beanGroup.getOutput()
		sampleParameters = beanGroup.getSample()
		outputBean.setAsciiFileName(sampleParameters.getName())
		print "Setting the ascii file name as " ,sampleParameters.getName()
		stage = sampleParameters.getSampleStageParameters()
		att1 = sampleParameters.getAttenuatorParameter1()
		att2 = sampleParameters.getAttenuatorParameter2()
		pos([rootnamespace['sc_MicroFocusSampleX'], stage.getX(), rootnamespace['sc_MicroFocusSampleY'], stage.getY(), rootnamespace['sc_sample_z'], stage.getZ()])
		pos([rootnamespace['D7A'], att1.getSelectedPosition(), rootnamespace['D7B'], att2.getSelectedPosition()])
		#redefineNexusMetadata(beanGroup)
		Finder.getInstance().find("RCPController").openPesrpective("org.diamond.exafs.ui.PlottingPerspective")
		
	
def redefineNexusMetadata(beanGroup):

	from gda.data.scan.datawriter import NexusFileMetadata
	from gda.data.scan.datawriter.NexusFileMetadata import EntryTypes, NXinstrumentSubTypes
	
	jython_mapper = JythonNameSpaceMapping()
	
	if (LocalProperties.get("gda.mode") == 'dummy'):
		return
	
	# primary slits
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s1ygap", str(jython_mapper.s1ygap()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "primary slits"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s1xgap", str(jython_mapper.s1xgap()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "primary slits"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s1ypos", str(jython_mapper.s1ypos()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "primary slits"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s1xpos", str(jython_mapper.s1xpos()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "primary slits"))

	# secondary slits
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s2ygap", str(jython_mapper.s2ygap()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "secondary slits"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s2xgap", str(jython_mapper.s2xgap()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "secondary slits"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s2ypos", str(jython_mapper.s2ypos()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "secondary slits"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s2xpos", str(jython_mapper.s2xpos()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "secondary slits"))

	# post DCM slits
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s3ygap", str(jython_mapper.s3ygap()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "postDCM slits"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s3xgap", str(jython_mapper.s3xgap()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "postDCM slits"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s3ypos", str(jython_mapper.s3ypos()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "postDCM slits"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("s3xpos", str(jython_mapper.s3xpos()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXaperture, "postDCM slits"))

	# Sample Stage
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("MicroFocusSampleX", str(jython_mapper.sc_MicroFocusSampleX()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXsample_stage, "Sample Stage"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("MicroFocusSampleY", str(jython_mapper.sc_MicroFocusSampleY()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXsample_stage, "Sample Stage"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("sample_z", str(jython_mapper.sc_sample_z()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXsample_stage, "Sample Stage"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("sample_thetacoarse", str(jython_mapper.sc_sample_thetacoarse()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXsample_stage, "Sample Stage"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("sample_thetafine", str(jython_mapper.sc_sample_thetafine()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXsample_stage, "Sample Stage"))

	#attenustors
	
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("D7A", str(jython_mapper.D7A()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXattenuator, "Attenuators"))
	NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("D7B", str(jython_mapper.D7B()), EntryTypes.NXinstrument, NXinstrumentSubTypes.NXattenuator, "Attenuators"))

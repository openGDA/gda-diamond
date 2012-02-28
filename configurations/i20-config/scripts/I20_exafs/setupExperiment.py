from gda.configuration.properties import LocalProperties
from gda.exafs.scan import BeanGroup
from gda.exafs.scan import BeanGroups
from gda.factory import Finder
from uk.ac.gda.beans.exafs import XasScanParameters
from uk.ac.gda.beans.exafs import XesScanParameters
from uk.ac.gda.beans.exafs import XanesScanParameters

from BeamlineParameters import JythonNameSpaceMapping

from exafsscripts.exafs.configFluoDetector import configFluoDetector

def finish():
    # remove extra columns from ionchambers output
    jython_mapper = JythonNameSpaceMapping()
    jython_mapper.ionchambers.setOutputLogValues(False) 
    

def setup(beanGroup):
    print "Setting up beamline and detectors"
    from uk.ac.gda.beans.exafs.i20 import I20SampleParameters
    from gda.exafs.scan import I20SampleParametersManager
    from gda.exafs.scan import DetectorParametersManager
    sampMan = I20SampleParametersManager(beanGroup.getSample(), beanGroup.getController())
    sampMan.init()
    
    if beanGroup.getDetector().getIonChambers()[0].getChangeSensitivity():
        detMan = DetectorParametersManager(beanGroup.getDetector(), beanGroup.getController())
        detMan.init()

    if beanGroup.getDetector().getExperimentType() == "Fluorescence":
        print "Setting up Fluorescence detector"
        configFluoDetector(beanGroup)

    setDarkCurrentTime(beanGroup)

#    sampleEnvManager = I20SampleParametersManager(beanGroup.getSample(),None)
#    sampleEnvManager.init()
         
    redefineNexusMetadata(beanGroup)
    
    jython_mapper = JythonNameSpaceMapping()
    jython_mapper.ionchambers.setOutputLogValues(True) 

    # if microreactor, then add this to the list of detectors
    if beanGroup.getSample().getSampleEnvironment() == I20SampleParameters.SAMPLE_ENV[4] :
        return Finder.getInstance().find("cirrus")
    
         
def redefineNexusMetadata(beanGroup):

    from gda.data.scan.datawriter import NexusExtraMetadataDataWriter
    from gda.data.scan.datawriter import NexusFileMetadata
    from gda.data.scan.datawriter.NexusFileMetadata import EntryTypes, NXinstrumentSubTypes
    
    jython_mapper = JythonNameSpaceMapping()
    
    if (LocalProperties.get("gda.mode") == 'dummy'):
    	return
    
    # primary slits
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Xsize",str(jython_mapper.s1_hgap()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXaperture,"primary slits"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Xcentre",str(jython_mapper.s1_hoffset()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXaperture,"primary slits"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Ysize",str(jython_mapper.s1_vgap()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXaperture,"primary slits"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Ycentre",str(jython_mapper.s1_voffset()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXaperture,"primary slits"))

    # M1
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Pitch",str(jython_mapper.m1_pitch()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M1"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Stripe",str(jython_mapper.m1m2_stripe()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M1"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Y",str(jython_mapper.m1_height()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M1"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Curvature",str(jython_mapper.m1_bend()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M1"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Ellipticity",str(jython_mapper.m1_elip()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M1"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Sag",str(jython_mapper.m1_yaw()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M1"))

    # M2
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Pitch",str(jython_mapper.m2_pitch()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M2"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Y",str(jython_mapper.m2_height()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M2"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Curvature",str(jython_mapper.m2_bend()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M2"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Ellipticity",str(jython_mapper.m1_elip()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M2"))

    # ATNs 1,2&3
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Position",str(jython_mapper.atn1()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXattenuator,"ATN1"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Position",str(jython_mapper.atn2()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXattenuator,"ATN2"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Position",str(jython_mapper.atn3()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXattenuator,"ATN3"))
    
    #Y slits  ????
#    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("YPlus",str(jython_mapper.s1_voffset()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXaperture,"Y slits"))

    # Mono
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal Cut",str(jython_mapper.crystalcut()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmonochromator,"Mono"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal 1 pitch",str(jython_mapper.crystal1_pitch()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmonochromator,"Mono"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal 2 roll",str(jython_mapper.crystal2_roll()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmonochromator,"Mono"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Pair 2 roll",str(jython_mapper.pair2_roll()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmonochromator,"Mono"))
    
    # Mono slits S2
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Xsize",str(jython_mapper.s2_hgap()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXaperture,"mono slits"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Xcentre",str(jython_mapper.s2_hoffset()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXaperture,"mono slits"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Ysize",str(jython_mapper.s2_vgap()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXaperture,"mono slits"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Ycentre",str(jython_mapper.s2_voffset()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXaperture,"mono slits"))
    
    # M3
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal 3 Pitch",str(jython_mapper.m3_pitch()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M3"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal 3 Stripe",str(jython_mapper.m3_stripe()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M3"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal 3 Sag",str(jython_mapper.m3_yaw()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M3"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal 3 Y",str(jython_mapper.m3_height()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M3"))
    
    # M4
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal 4 Pitch",str(jython_mapper.m4_pitch()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M4"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal 4 Stripe",str(jython_mapper.m4_stripe()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M4"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal 4 Y",str(jython_mapper.m4_height()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M4"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal 4 Curvature",str(jython_mapper.m4_curvature()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M4"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Crystal 4 Ellipticity",str(jython_mapper.m4_yaw()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"M4"))
    
    # HR mirror
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Pitch",str(jython_mapper.hr_pitch()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"HR mirror"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Y",str(jython_mapper.hr_height()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"HR mirror"))
    NexusExtraMetadataDataWriter.addMetadataEntry(NexusFileMetadata("Stripe",str(jython_mapper.hr_stripe()),EntryTypes.NXinstrument,NXinstrumentSubTypes.NXmirror,"HR mirror"))
    
    # filter
    
    # mono slits
    
    # ST1?
    
    # Gain and HV for Io, it anf iref
    
    # pos of reference wheel
    
    # ring current
    
    # YSlits drian current
    
#    if isInstance(beanGroup.getScan,XesScanParameters):
        
        # analysertype and crystal cut
        
        # ST2 x and y pos
        
        # xes sample stage positions ??
        
        # xes bragg (deg)
        
        # detector x and y
        
        # analyser hor and rot    

def setDarkCurrentTime(beanGroup):
    
    # get ion chmabers
    jython_mapper = JythonNameSpaceMapping()
    ct = jython_mapper.ionchambers
    
    # determine max collection time
    scanBean = beanGroup.getScan()
    maxTime = 0;
    if isinstance(scanBean,XanesScanParameters):
        for region in scanBean.getRegions():
            if region.getTime() > maxTime:
                maxTime = region.getTime()
                
    elif isinstance(scanBean,XasScanParameters):
        if scanBean.getEdgeTime() > maxTime:
            maxTime = scanBean.getEdgeTime()
        if scanBean.getExafsToTime() > maxTime:
            maxTime = scanBean.getExafsToTime()
        if scanBean.getExafsFromTime() > maxTime:
            maxTime = scanBean.getExafsFromTime()
        if scanBean.getExafsTime() > maxTime:
            maxTime = scanBean.getExafsTime()
        if scanBean.getPreEdgeTime() > maxTime:
            maxTime = scanBean.getPreEdgeTime()
    
    # set dark current time and handle any errors here
    if maxTime > 0:
        print "Setting ionchambers dark current collectiom time to be",str(maxTime),"s"
        ct.setDarkCurrentCollectionTime(maxTime)
        

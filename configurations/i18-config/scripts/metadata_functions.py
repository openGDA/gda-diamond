from uk.ac.diamond.osgi.services import ServiceProvider
from org.eclipse.scanning.api.scan import IFilePathService
from gda.device.scannable import ScannableUtils
from gdascripts.scan.gdascans import Rscan

"""
This is used by Optics group for their wavefront meadurements.
It sets up filewriter to uses SRS scans and allow metadata values to be added to the header.
Scannables to be used for metadata are stored as a list (metadata_scannables), items are added, removed etc by the functions :
- add_metadata, rm_metadata ls_metadata
As well as the SRS file, the Ascii and Nexus also have the metadata added to them.
- clear_metadata clears the metadata
RscanWithMetadata is used for running rscan - it also generates metadata header string from current set of
scannables at the start of the scan.
"""

datawriterconfig=Finder.find("datawriterconfig")

def use_srs_datawriter(tf) :
    LocalProperties.set("gda.nexus.createSRS", tf)

def add_metadata(scannable=None) :
    if scannable is not None : 
        metadata_scannables.append(scannable)
    
    meta_add(scannable)
    
    for scn in metadata_scannables : 
        removeMetaDataEntry(datawriterconfig, scn.getName())
        ent=createAsciiMetaDataEntry(scn.getName()+" : "+scn.getOutputFormat()[0], [scn])
        addMetaDataEntry(datawriterconfig, ent)
            
def create_srs_metadata_string() :
    metadata_string=""
    for scn in metadata_scannables :
        scn_metadata=scn.getName()+"="+ScannableUtils.getFormattedCurrentPositionArray(scn)[0]+"\n"
        metadata_string += scn_metadata
    
    return metadata_string
    
def rm_metadata(scannable) :
    removeMetaDataEntry(datawriterconfig, scannable.getName())
    meta_rm(scannable)
    metadata_scannables.remove(scannable)

def ls_metadata() :
    for scn in metadata_scannables :
        print(scn)

def clear_metadata() :
    global metadata_scannables
    for scn in metadata_scannables : 
        meta_rm(scn)
        removeMetaDataEntry(datawriterconfig, scn.getName())
    metadata_scannables=[]
    use_srs_datawriter(False)

print("Use add_metadata(scannable), rm_metadata(scannable) and clear_metadata() to add remove and clear meta data for scannables")    

add_reset_hook(clear_metadata)

def removeMetaDataEntry(asciiConfig, label):
    ind = -1
    headerList = asciiConfig.getHeader()
    for header in headerList : 
        if label.upper() in header.getLabel().upper() :
            ind = headerList.indexOf(header)
    if ind > -1 :
        #print("Removing item %d from %s"%(ind, asciiConfig.getName()))
        headerList.remove(ind)

def createAsciiMetaDataEntry(label, values):
    from gda.data.scan.datawriter import AsciiMetadataConfig
    newEnt = AsciiMetadataConfig()  
    newEnt.setLabel(label)
    newEnt.setLabelValues(values)
    return newEnt
    
def addMetaDataEntry(asciiConfig, metadataEntry):
    ## Add the new/updated entry
    print("Adding %s"%(metadataEntry.getLabel()))
    asciiConfig.getHeader().add(metadataEntry)



# Rscan with __call__overridden to update SRS metadata string at start of each scan
# using current scannable list in metadata_scannables and the current command line string
class RscanWithMetadata(Rscan):
    
    def __init__(self, scanListeners = None):
        Rscan.__init__(self, scanListeners)
        
    def convertArgStruct(self, argStruct):
        return argStruct

    def __call__(self, *args) :
        cmdstring = "cmd="+self._constructUserCommand(args)
        metadata_string = create_srs_metadata_string()
        global SRSWriteAtFileCreation
        SRSWriteAtFileCreation = cmdstring+"\n"+metadata_string
        Rscan.__call__(self, args)

rscanWithMetadata = RscanWithMetadata()
alias(rscanWithMetadata)

metadata_scannables=[]
use_srs_datawriter(True)

# Add scannables to get values from Stats plugin (this works fine, but maybe we should create NDStatsImpl plugin in spring)
from gda.device.scannable import PVScannable
andor_roi_counts = PVScannable("andor_roi_counts", "BL18I-EA-DET-10:STAT:Total_RBV")
andor_roi_counts.setCanMove(False)
andor_roi_counts.configure()

andor_roi_mean = PVScannable("andor_roi_mean", "BL18I-EA-DET-10:STAT:MeanValue_RBV")
andor_roi_mean.setCanMove(False)
andor_roi_mean.configure()

andor_roi_sigma = PVScannable("andor_roi_sigma", "BL18I-EA-DET-10:STAT:Sigma_RBV")
andor_roi_sigma.setCanMove(False)
andor_roi_sigma.configure()

from gda.device.scannable.scannablegroup import ScannableGroup
andor_stats = ScannableGroup("andor_stats", [andor_roi_counts, andor_roi_mean, andor_roi_sigma])
andor_stats.configure()

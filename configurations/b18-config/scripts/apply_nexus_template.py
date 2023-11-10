from org.eclipse.dawnsci.nexus.template import TemplateServiceHolder
from org.slf4j import LoggerFactory

class TemplateHelperFunctions :
    @staticmethod
    def create_data_entry(entry_name, map_of_values) :
        """ 
        Create map representing NXdata entry using given name and values from map
        
        """
        
        data_entry = { "NX_class@" : "NXdata" }
        
        ## append all the key value pairs from map_of_value to data_entry map
        data_entry.update(map_of_values)
            
        return {"NX_class@" : "NXentry", TemplateHelperFunctions.sanitize_entry_name(entry_name) : data_entry}
    
    @staticmethod
    def sanitize_entry_name(entry_name):
         # Make sure entry name ends with a / 
        if not entry_name.endswith("/") :
            entry_name += "/"
        return entry_name
    
    ## Append a NXdata entry to Nexus template map
    @staticmethod
    def add_to_template_map(map, entry_name, values_map) :
        main_entry_name="entry1/"
    
        entry1 = map.get(main_entry_name)
        
        # Create top level 'entry1' item in map
        if entry1 is None :
            print("Creating "+main_entry_name)
            entry1 = {}
            map[main_entry_name] = entry1
            
        # Create NXdata node with map of values
        data_entry = TemplateHelperFunctions.create_data_entry(TemplateHelperFunctions.sanitize_entry_name(entry_name), values_map)
        
        # Add data_entry to the entry1 values map
        entry1.update(data_entry)
        # Evaluate map, where values are all method/function references ('suppliers'))
    
    # Returns new map containing result of the method evaluations
    @staticmethod
    def evaluate_map(map) :
        """
            map = key = name, value = method reference to be evaluated (supplier)
            return new map (key = name, value = result of method evaluation)
        """
        values_map = {}
        for item in map.items() :
            try :
                values_map[item[0]] = item[1]()
            except :
                # catch exception, so we can continue to populate in the map
                print("Problem getting value for item '"+item[0]+"' in map")
            
        return values_map


"""
'Default' Scannable that can be used to add metadata to Nexus file at end of a scan.
The metadata to be collected is specified by map of key value pairs (key = name, value = method reference)
The references are evaluated at run time to get the latest values, and these are placed in a map
which is used with NexusTemplateService to create the template and apply it to Nexus file.

metadataMap - map of metadata names a references
metadataEntryName - location where data will be written (inside /entry1, and can be nested, e.g. mydata/scan_metadata/)
detectorNames = template will be applied only if name of a detector used for scan match one of those in detectorNames list
 
imh 10/11/2023
"""
class TemplateScannable(ScannableBase):

    def __init__(self, name):
        self.name = name
        self.inputNames = [name]
        self.setOutputFormat({});
        self.setInputNames({});
        self.metadataMap = {}
        self.metadataEntryName=""
        self.detectorNames = []
        self.logger = LoggerFactory.getLogger("TemplateScannable")

    def atScanEnd(self):
        if not self.scanUsesDetector() :
            return
        
        self.logger.info("Applying Nexus template using {} at end of scan", self.name)
        template_map = self.generateTemplateMap()
        filename = self.getCurrentScanFilename()
        self.applyTemplate(template_map, filename)
        
    # Apply Nexus template map to specified Nexus file
    def applyTemplate(self, template_map, filename) :
        self.logger.info("Applying template to file {}", filename)
        template_service = TemplateServiceHolder.getNexusTemplateService()
        template = template_service.createTemplate("test template", template_map)  
        template.apply(filename)
        
    def generateTemplateMap(self):
        """
        Create map of metadata values from map of method references and put
        inside map that can passed to TemplateService
        """
        template_map = {}
        metadata_values = TemplateHelperFunctions.evaluate_map(self.metadataMap)
        self.logger.info("Generating Nexus template map from metadata values {}", metadata_values)
        TemplateHelperFunctions.add_to_template_map(template_map, self.metadataEntryName, metadata_values)
        return template_map
    
    def stop(self):
        self.atScanEnd()

    def atCommandFailure(self):
        self.atScanEnd()

    def isBusy(self):
        return False

    def rawAsynchronousMoveTo(self,new_position):
        pass

    def rawGetPosition(self):
        return None
    
    def getCurrentScanInfo(self) :
        return InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation()
    
    def getCurrentScanFilename(self) :
        info = self.getCurrentScanInfo()
        return info.getFilename()
    
    # Return True if detectors used by current scan matches one of those in 'detectorNames' list
    def scanUsesDetector(self):
        try :
            info = self.getCurrentScanInfo()
            for detName in self.detectorNames :
                if detName in info.getDetectorNames() :
                    return True
            return False
        except Exception as ex:
            self.logger.warn("Problem processing detector names in 'scanUsesDetector' method : {}", ex)
            pass
        return False



# Setup map of key-value pairs describing the metadata to be collected
# values are method references, which are evaluated in TemplateScannable to get latest values
cont = xspress4Odin.getController();
qexafs_metadata_map = {
    "number_of_scan_points" : qexafs_energy.getNumberOfDataPoints,
    "zebra_captured_points" : zebra_device.getPCNumberOfPointsCaptured,
    "xsp4_hdf_captured_frames" : cont.getHdfNumCapturedFrames,
    "xsp4_hdf_num_frames" : cont.getHdfNumFramesRbv,
    "xsp4_cam_num_frames" : cont.getNumImagesRbv,
    "xsp4_cam_array_counter" : cont.getTotalFramesAvailable
}

# Setup scannable to collect frame info from zebra and xspress4 at end of scan
qexafs_metadata_scn = TemplateScannable("qexafs_metadata_scn")
qexafs_metadata_scn.metadataMap =  qexafs_metadata_map
qexafs_metadata_scn.metadataEntryName = "after_scan/"
qexafs_metadata_scn.detectorNames = ["qexafs_xspress4Odin"]

add_default(qexafs_metadata_scn)

"""
template_map = {}
qexafs_metadata_values = TemplateHelperFunctions.evaluate_map(qexafs_metadata_map)
TemplateHelperFunctions.add_to_template_map(template_map, "qexafs_metadata4/", qexafs_metadata_values);

# Generate the template from the map 
template_service = TemplateServiceHolder.getNexusTemplateService()
template = template_service.createTemplate("test template", template_map)

# Apply Nexus template to Nexus file
template.apply("/scratch/users/data/2023/0-0/nexus/1_b18.nxs")
"""
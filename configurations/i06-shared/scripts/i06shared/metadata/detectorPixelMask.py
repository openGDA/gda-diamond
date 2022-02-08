'''
define command for upload detector mask from detector's configuration location.
This command or function will create a pixel_mask field under /entry/instrument/<detector-name>/ in any data file collected subsequently in scans,
until it is explicitly removed.

Created on Feb 08, 2022

@author: fy65
'''
from gda.configuration.properties import LocalProperties

RUN_IN_GDA = LocalProperties.check("run.in.gda", False)

quadrant_size = 256 #There are 4 quadrants of this detector of size (512,512) 
mask_file_location = "/dls_sw/i06/epics/dexterConfigTemp_2/config-246537-v2/" #this location need to be updated if and when detector's mask files are relocated.
mask_file_and_xy_offsets = [("mask_0",0,0), ("mask_1",0,quadrant_size-1), ("mask_2",quadrant_size-1,quadrant_size-1), ("mask_3",quadrant_size-1,0)]

if RUN_IN_GDA:
    from gdascripts.metadata.nexus_metadata_class import meta
    from org.eclipse.dawnsci.nexus import NXdetector

    def add_pixel_mask(detector, mask_files=mask_file_and_xy_offsets, mask_applied=True):
        '''add pixel mask data to the detector node as metadata in subsequent scan data files, and set true or false to state if these masks are already applied in detector hardware or not.
        '''
        lines = {}
        dataset = []    
        for mask in mask_files:
            with open(mask_file_location + mask[0]) as f:
                lines[mask] = [int(line) for line in f.readlines()]
        
        for key,values in lines.items():
            for value in values:
                x,y = divmod(value, quadrant_size)
                x += key[1]
                y += key[2]
                dataset.append((x,y))
                
        meta.addScalar(detector.getName(), NXdetector.NX_PIXEL_MASK, dataset)
        meta.addScalar(detector.getName(), NXdetector.NX_PIXEL_MASK_APPLIED, mask_applied)
        print("Detector masks are add at '/entry/instrument/%s/%s' in subsequent scan data files until it is removed.\n" % (detector.getName(), NXdetector.NX_PIXEL_MASK))
   
    from gda.jython.commands.GeneralCommands import alias   
    alias("add_pixel_mask")
  
    def remove_pixel_mask(detector):
        '''remove current flat field link metadata device
        '''
        meta.rm(str(detector.getName()), str(NXdetector.NX_PIXEL_MASK))
        meta.rm(str(detector.getName()), str(NXdetector.NX_PIXEL_MASK_APPLIED))

    alias("remove_pixel_mask")
    
def test_pixel_mask_conversion(mask_files=[]):
    '''add pixel mask data to the detector node as metadata in subsequent scan data files, and set true or false to state if these masks are already applied in detector hardware or not.
    '''
    lines = {}
    dataset = []    
    for mask in mask_files:
        print mask_file_location + mask[0]
        with open(mask_file_location + mask[0]) as f:
            lines[mask] = [int(line) for line in f.readlines()]
    
    for key,values in lines.items():
        for value in values:
            x,y = divmod(value, quadrant_size)
            x += key[1]
            y += key[2]
            print key[0], value, (x, y)
            dataset.append((x,y))
    print dataset
    
if __name__ == "__main__":
    test_pixel_mask_conversion(mask_files=mask_file_and_xy_offsets)

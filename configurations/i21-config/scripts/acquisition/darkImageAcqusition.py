'''
define command for acquiring dark image data.
This command or function will create an entry node link to the dark image file in any data file collected subsequently in scans,
until it is explicitly removed.

Created on May 6, 2022

@author: fy65
'''
import os

from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import NexusScanDataWriter
from gda.jython.commands.GeneralCommands import alias   
from gdascripts.metadata.nexus_metadata_class import meta
from gdaserver import fastshutter  # @UnresolvedImport
from org.eclipse.dawnsci.analysis.api.tree import Node
from shutters.detectorShutterControl import erio, primary
from utils.beamline import last_scan_file
from acquisition import acquireImages

NXDDETECTOR_DARK_IMAGE = "dark_image"

def acquire_dark_image(num_images, detector, acquire_time, *args):
    '''collect number of dark images from the given detector when shutter is closed, and then set up dark_image link in this detector's metadata device to be used in subsequent scans.
    '''
    erio()
    fastshutter('Closed')
    acquireImages(num_images, detector, acquire_time, *args)
    primary()
    fastshutter('Open')
    entry_name = str(LocalProperties.get(NexusScanDataWriter.PROPERTY_NAME_ENTRY_NAME, NexusScanDataWriter.DEFAULT_ENTRY_NAME)) 
    seq = ("", entry_name, str(NexusScanDataWriter.METADATA_ENTRY_NAME_INSTRUMENT), str(detector.getName()), "data")
    external_link_path = str(Node.SEPARATOR).join(seq)
    filename = os.path.basename(str(last_scan_file()))
    meta.addLink(detector.getName(), NXDDETECTOR_DARK_IMAGE, external_link_path, filename)
    print("A link to dark image data at '%s#%s' \nwill be added to detector '%s' as '%s' in subsequent scan data files \nwhen this detector is used until it is removed" % (filename, external_link_path, detector.getName(), NXDDETECTOR_DARK_IMAGE))
    
alias("acquire_dark_image")

    
def remove_dark_image(detector):
    '''remove current dark image link from the given detector's metadata device
    '''
    meta.rm(str(detector.getName()), NXDDETECTOR_DARK_IMAGE)

alias("remove_dark_image") 

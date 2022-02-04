'''
define command for acquiring flat field data.
This command or function will create an entry link to the flat field file in any data file collected subsequently in scans,
until it is explicitly removed.

Created on Nov 22, 2021

@author: fy65
'''
from gdascripts.metadata.nexus_metadata_class import meta
from i06shared.commands.beamline import lastscan
from org.eclipse.dawnsci.nexus import NXdetector
from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import NexusScanDataWriter
from org.eclipse.dawnsci.analysis.api.tree import Node
from gda.device.scannable import DummyScannable
import os


def acquire_flat_field(num_images, detector, acquire_time):
    '''collect number of images from detector under flat field condition, and then set up flat_field link metadata device to be used in subsequent scans.
    '''
    ds = DummyScannable("ds")
    scan(ds, 1, num_images, 1, detector, acquire_time)  # @UndefinedVariable
    entry_name = str(LocalProperties.get(NexusScanDataWriter.PROPERTY_NAME_ENTRY_NAME, NexusScanDataWriter.DEFAULT_ENTRY_NAME)) 
    seq = ("", entry_name, str(NexusScanDataWriter.METADATA_ENTRY_NAME_INSTRUMENT), str(detector.getName()), "data")
    external_link_path = str(Node.SEPARATOR).join(seq)
    filename = os.path.basename(str(lastscan()))
    meta.addLink(detector.getName(), NXdetector.NX_FLATFIELD, external_link_path, filename)
    print("A link to flat field image data at '%s#%s' \nwill be added to detector '%s' as '%s' in subsequent scan data files \nwhen this detector is used until it is removed" % (filename, external_link_path, detector.getName(), NXdetector.NX_FLATFIELD))

    
from gda.jython.commands.GeneralCommands import alias   
alias("acquire_flat_field")

    
def remove_flat_field(detector):
    '''remove current flat field link metadata device
    '''
    meta.rm(str(detector.getName()), str(NXdetector.NX_FLATFIELD))


alias("remove_flat_field") 

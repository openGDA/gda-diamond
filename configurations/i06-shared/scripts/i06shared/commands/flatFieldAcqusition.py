'''
define command for acquiring flat field data.
This command or function will create an entry link to the flat field file in any data file collected subsequently in scans,
until it is explicitly removed.

Created on Nov 22, 2021

@author: fy65
'''
from gdascripts.metadata.nexus_metadata_class import meta
from i06shared.commands.beamline import lastscan

def acquire_flat_field(num_images, detector, acquire_time):
    '''collect number of images from detector under flat field condition, and then set up flat_field link metadata device to be used in subsequent scans.
    '''
    scan(ds, 1, num_images, 1, detector, acquire_time)  # @UndefinedVariable
    meta.addLink("flat_field", "data", "/entry", str(lastscan()))

    
from gda.jython.commands.GeneralCommands import alias   
alias("acquire_flat_field")

    
def remove_flat_field():
    '''remove current flat field link metadata device
    '''
    meta.rm("flat_field", "data")

alias("remove_flat_field") 

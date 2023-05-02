'''
dynamically handle recording diffcalc active constraints as metadata in data file during scan data collection

The constraints metadata are updated at prepareForScan() method, which removes old constraints and add new constraints every time a scan is run.
 
Created on Apr 28, 2023

@author: fy65
'''
from gdascripts.scannable.installStandardScannableMetadataCollection import rmmeta,\
    addmeta
from gda.jython import InterfaceProvider
from gdascripts.scan.scanListener import ScanListener
from org.slf4j import LoggerFactory

constraints_in_metadata = []
def update_constraints_in_metadata():
    if constraints_in_metadata:
        #remove old metadata
        while constraints_in_metadata:
            rmmeta(constraints_in_metadata.pop())
    
    try:
        from gda.device.scannable import ScannableBase
    except ImportError:
        from diffcalc.gdasupport.minigda.scannable import ScannableBase
    from diffcalc.hkl.you.hkl import constraint_manager
    
    for each in constraint_manager.all.keys():  # @UndefinedVariable
        #add new metadata
        constraint = InterfaceProvider.getJythonNamespace().getFromJythonNamespace(str(each))
        if isinstance(constraint, ScannableBase):
            addmeta(constraint)
        else:
            addmeta(constraint, constraint)
        constraints_in_metadata.append(constraint)


class ContstraintsMetadataHandler(ScanListener):
    def __init__(self, name): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger(self.__class__.__name__)
        self.name = name

    def prepareForScan(self):
        update_constraints_in_metadata()
            
    def update(self, scan_object):
        pass
        
constraints_metadata_handler = ContstraintsMetadataHandler("constraints_metadata_handler")

def add_constraints_metadata_handler(scan_listeners):
    scan_listeners.append(constraints_metadata_handler)
    
        
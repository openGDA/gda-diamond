'''
Created on Apr 28, 2022

@author: fy65
'''
from gdascripts.scan.scanListener import ScanListener
from i06shared.commands.beamline import beamlinefunction, lastscan
from time import ctime
from org.eclipse.scanning.device.utils import NexusMetadataUtility
import scisoftpy as dnp
from org.slf4j import LoggerFactory

class ElogPosterScanListener(ScanListener):
    '''
    a Scan Listener used to observe GDA scan and inject additional behaviors before scan starts and after scan finishes.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.logger = LoggerFactory.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)
        self.startingTime = None
        
    def prepareForScan(self):
        '''called before scan starts
        '''
        self.logger.info("prepareForCVScan()")
        self.startingTime = ctime()
    
    def update(self,scan_object):
        '''called after scan finished.
        '''
        self.logger.info("update(%r)" % scan_object)
        self.logger.info("Post scan information to ELog") 
        metadata_string = self.create_metadata_string()
        formated_metadata_string =  '<div>' + metadata_string.replace("\n" , "</div><div>") + '</div>'
        beamlinefunction.logScan(self.startingTime, formated_metadata_string)

    def create_metadata_string(self):
        nexus_metadata_node_paths = NexusMetadataUtility.INSTANCE.getFieldNodePathsFromAllNexusMetadataDevices()
        fh = dnp.io.load(str(lastscan()), warn=False) # load last scan data file, which must be nexus file.
        ps = "";
        for path in nexus_metadata_node_paths:
            ds = fh[str(path)][...].tolist() # return dataset for the given path as list
            value = None
            if len(ds) == 1:
                value = ds[0]
            elif len(ds) > 1:
                value = ds
            ps += path + " = " + str(value) + "\n"

        return ps

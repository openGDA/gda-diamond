from gda.device.detector.hardwaretriggerable import HardwareTriggerableDetectorBase
from gda.device.scannable import PositionCallableProvider, PositionInputStream, \
    PositionStreamIndexer
from gda.epics import CAClient
from gda.device import Detector
import java.util.Vector
import time

#from gda.epics.connection import EpicsChannelManager
#from gda.epics.connection import InitializationListener
#from gda.epics.connection import EpicsController
#from gov.aps.jca.event import MonitorListener

# TODO: A copy has been made in mt-config

""" Note, a new implementation of this has been created in the the
    waveform_channel package, combining the requirements of i16 and i10.

TODO: Move to using mtscripts.scannable.waveform_channel
"""

class PollingMcaChannelInputStream(PositionInputStream):
    # the NORD Epics pv cannot be listed to, hence the polling
    
    def __init__(self, mca_root_pv, channel):
        # e.g. mca_root_pv = BL16I-EA-DET-01:MCA-01:
        self.pv_waveform = CAClient(mca_root_pv + 'mca' + `channel`)
        self.pv_nord = CAClient(mca_root_pv  + 'mca' + `channel` + '.NORD') 
        self.elements_read = 0 # none available
        
        self.configure()
        self.reset()
        
    def configure(self):
        self.pv_waveform.configure()
        self.pv_nord.configure()
        
    def reset(self):
        # nord should read 0 after an erase, but will not actually be reset
        # until an erase & start.        
        self.elements_read = -1
        
    def read(self, max_to_read_in_one_go):
        if self.elements_read == -1:
            self.elements_read = 0
            ##return java.util.Vector([0])
        new_available = self._waitForNewElements()
        all_data = self.pv_waveform.cagetArrayDouble(self.elements_read + new_available)
        new_data = all_data[self.elements_read:self.elements_read + new_available]
        self.elements_read += new_available
        return java.util.Vector([int(el) for el in new_data])
            
    def _waitForNewElements(self):
        """return the number of new elements available, polling until some are"""
        
        while True:
            elements_available = int(self.pv_nord.caget())
            if elements_available > self.elements_read:
                return elements_available - self.elements_read
            time.sleep(.2)
            

class McsController(object):
    # e.g. mca_root_pv = BL16I-EA-DET-01:MCA-01
    
    def __init__(self, mca_root_pv):
        self.pv_erasestart = CAClient(mca_root_pv + 'EraseStart')
        #self.pvs = PvManager(mca_root_pv)
        self.configure()
        self.exposure_time = 1
        
    def configure(self):
        self.pv_erasestart.configure()
    
    def erase_and_start(self):
        #self.pvs['EraseStart'].caput(1)
        self.pv_erasestart.caput(1)
        


class McsChannelScannable(HardwareTriggerableDetectorBase, PositionCallableProvider):
    # TODO: Assumes always hardware triggering

    def __init__(self, name, controller, mca_root_pv, channel):
        # channel from 1
        self.name = name
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%i']
        
        self.controller = controller
        self.mca_input_stream = PollingMcaChannelInputStream(mca_root_pv, channel)
        self.stream_indexer = None
        
    def integratesBetweenPoints(self):
        return True
    
    def collectData(self):
        pass
    
    def getStatus(self):
        return Detector.IDLE
    
    def setCollectionTime(self, t):
        # does not effect Epics controller
        self.controller.exposure_time = t
        
    def getCollectionTime(self):
        return self.controller.exposure_time
    
    def readout(self):
        # read the last element collected
        raise Exception(self.name + "for use only in Continuous scans")
    
    def atScanLineStart(self):
        self.controller.erase_and_start() # nord will read 0
        self.mca_input_stream.reset()
        self.stream_indexer = PositionStreamIndexer(self.mca_input_stream);
    
    def getPositionCallable(self):
        return self.stream_indexer.getPositionCallable()
    
    def createsOwnFiles(self):
        return False
    
    def getDescription(self):
        return ""

    def getDetectorID(self):
        return ""
    
    def getDetectorType(self):
        return ""
    
    def getDataDimensions(self):
        return (1,)

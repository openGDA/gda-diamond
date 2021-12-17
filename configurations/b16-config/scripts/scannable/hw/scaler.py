from gdascripts.scannable.epics.PvManager import PvManager

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

""" Note, a new implementation of this has been created in the the
    waveform_channel package, combining the requirements of i16 and i10.

This implementation was created to support raster (2d) scans in addition
to continuous (1d) scans.

TODO: This functionality should be added to waveform_channel.

This implementation also appears to support internal channel advance, but use
in this mode will have problems because the acquisition will start as soon as
atScanStart() is called (if no new_collection_per_line) or as soon as
atScanLineStart() is called (if new_collection_per_line).

For internal channel advance, erase_and_start should only be called from
collectData(), otherwise the waveform generator will start acquiring while the
continuous scan is being planned, not when it is being run.

TODO: This requirement needs to be reconciled with both raster and continuous scans.

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
            # Note that this results in stale data being returned in continuous scans.
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
    
    def __init__(self, mca_root_pv, internal_channel_advance=False):
        self.internal_channel_advance = internal_channel_advance
        self.pvs = PvManager(pvroot=mca_root_pv)
        self._exposure_time = 1
    
    def get_exposure_time(self):
        return self._exposure_time

    def set_exposure_time(self, t):
        self._exposure_time = t
        if self.internal_channel_advance:
            print "Setting dwell time to ", str(t)
            self.pvs['StopAll'].caput(10, 1)
            self.pvs['Dwell'].caput(10, t)
    
    exposure_time = property(get_exposure_time, set_exposure_time)
    
    def erase_and_start(self):
        self.pvs['EraseStart'].caput(1)
        
#    def stop(self):
#        self.pvs['StopAll'].caput(1)


class McsChannelScannable(HardwareTriggerableDetectorBase, PositionCallableProvider):
    # TODO: Assumes always hardware triggering

    def __init__(self, name, controller, mca_root_pv, channel, new_collection_per_line=True):
        # channel from 1
        self.name = name
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ['%i']
        
        self.controller = controller
        self.mca_input_stream = PollingMcaChannelInputStream(mca_root_pv, channel)
        self.stream_indexer = None
        self.new_collection_per_line = new_collection_per_line
        
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
    
    def atScanStart(self):
        if not self.new_collection_per_line:
            self._startCollection()
    
    def atScanLineStart(self):
        if self.new_collection_per_line:
            self._startCollection()
            
    def atScanLineEnd(self):
        pass
            
    def atScanEnd(self):
        pass
    
    def _startCollection(self):
        self.controller.erase_and_start() # nord will read 0
        self.mca_input_stream.reset()
        self.stream_indexer = PositionStreamIndexer(self.mca_input_stream)
#    def atScanLineEnd(self):
#        self.controller.stop()
    
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

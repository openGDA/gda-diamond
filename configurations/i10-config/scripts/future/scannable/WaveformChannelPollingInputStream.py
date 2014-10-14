# Based on gda-mt.git/configurations/i16-config/scripts/scannable/scaler.py

from datetime import datetime
from gda.device.detector.hardwaretriggerable import HardwareTriggerableDetectorBase
from gda.device.scannable import PositionCallableProvider, PositionInputStream, \
    PositionStreamIndexer
from gda.epics import CAClient
from gda.device import Detector
import java.util.Vector
import time

# TODO: This should be moved to mt-config and the requirements for both i16
# and i10 should be combined.

class PollingMcaChannelInputStream(PositionInputStream):

    def __init__(self, controller, channel):
        self.pv_waveform, self.pv_count = controller.getChannelInputStreamCAClients(channel)
        self.elements_read = 0 # none available
        self.type = controller.getChannelInputStreamType()
        self.configure()
        self.reset()

    def configure(self):
        self.pv_waveform.configure()
        self.pv_count.configure()

    def reset(self):
        # count should read 0 after an erase, but will not actually be reset
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
        return java.util.Vector([self.type(el) for el in new_data])

    def _waitForNewElements(self):
        """return the number of new elements available, polling until some are"""
        
        while True:
            elements_available = int(float(self.pv_count.caget()))
            if elements_available > self.elements_read:
                return elements_available - self.elements_read
            time.sleep(.2)


TIMEOUT = 5

class McsController(object):
    # e.g. mca_root_pv = BL16I-EA-DET-01:MCA-01

    def __init__(self, name, mca_root_pv, channelAdvanceInternalNotExternal=False):
        self.name = name
        self.mca_root_pv = mca_root_pv
        self.pv_stop= CAClient(mca_root_pv + 'StopAll')
        self.pv_dwell= CAClient(mca_root_pv + 'Dwell')
        self.pv_channeladvance= CAClient(mca_root_pv + 'ChannelAdvance')
        self.pv_presetReal = CAClient(mca_root_pv + 'PresetReal')
        self.pv_erasestart = CAClient(mca_root_pv + 'EraseStart')
        self.channelAdvanceInternalNotExternal = channelAdvanceInternalNotExternal
        self.channelAdvanceInternal = 0
        self.channelAdvanceExternal = 1

        self.configure()
        self.exposure_time = 1
        self.number_of_positions = 0
        self.verbose = True

    def configure(self):
        self.pv_stop.configure()
        self.pv_dwell.configure()
        self.pv_channeladvance.configure()
        self.pv_presetReal.configure()
        self.pv_erasestart.configure()

    def erase_and_start(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'erase_and_start...'
        self.pv_stop.caput(1)  # scaler won't start if already running
        if self.channelAdvanceInternalNotExternal:
            self.pv_dwell.caput(TIMEOUT, self.exposure_time) # Set the exposure time per nominal position
            self.pv_channeladvance.caput(TIMEOUT, self.channelAdvanceInternal)
            self.pv_presetReal.caput(self.number_of_positions * self.exposure_time) # Set the total capture time
        else:
            self.pv_channeladvance.caput(TIMEOUT, self.channelAdvanceExternal)
        self.pv_erasestart.caput(1)
        if self.verbose:
            print str(datetime.now()), self.name, '...erase_and_start'

    def stop(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'stop...'
        self.pv_stop.caput(1)
        if self.verbose:
            print str(datetime.now()), self.name, '...stop'

    def getChannelInputStream(self, channel):
        # The NORD Epics pv cannot be listened to, hence the polling
        # Channels numbered from 1
        return PollingMcaChannelInputStream(self, channel)

    def getChannelInputStreamFormat(self):
        return '%i'

    def getChannelInputStreamType(self):
        return int

    def getChannelInputStreamCAClients(self, channel):
        pv_waveform = CAClient(self.mca_root_pv + 'mca' + `channel`)
        pv_count =    CAClient(self.mca_root_pv + 'mca' + `channel` + '.NORD') 
        return pv_waveform, pv_count

class McsChannelScannable(HardwareTriggerableDetectorBase, PositionCallableProvider):

    def __init__(self, name, controller, channel):
        self.name = name
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = [controller.getChannelInputStreamFormat()]
        
        self.controller = controller
        self.channel_input_stream = controller.getChannelInputStream(channel)
        self.stream_indexer = None
        self.number_of_positions = 0
        self.verbose = True

    def integratesBetweenPoints(self):
        return True

    def collectData(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'collectData()...'
        self.controller.erase_and_start()
        if self.verbose:
            print str(datetime.now()), self.name, '...collectData()'

    def getStatus(self):
        return Detector.IDLE

    def setCollectionTime(self, t):
        if self.verbose:
            print str(datetime.now()), self.name, 'setCollectionTime(%r)' % t
        # does not effect Epics controller
        self.controller.exposure_time = t

    def getCollectionTime(self):
        return self.controller.exposure_time

    def readout(self):
        # read the last element collected
        raise Exception(self.name + "for use only in Continuous scans")

    def atScanLineStart(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'atScanLineStart...'
        self.channel_input_stream.reset()
        self.stream_indexer = PositionStreamIndexer(self.channel_input_stream);
        self.number_of_positions = 0
        if self.verbose:
            print str(datetime.now()), self.name, '...atScanLineStart'

    def atScanLineEnd(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'atScanLineEnd'
        pass
        # TODO: Must wait for all callables to have been called before doing this
        #self.controller.stop()

    def getPositionCallable(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'getPositionCallable(%i)' % self.number_of_positions
        self.number_of_positions += 1
        self.controller.number_of_positions = self.number_of_positions
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

# Based on gda-mt.git/configurations/i16-config/scripts/scannable/scaler.py

from datetime import datetime
from gda.device.detector.hardwaretriggerable import HardwareTriggerableDetectorBase
from gda.device.scannable import PositionCallableProvider, PositionStreamIndexer
from gda.device import Detector

# TODO: This should be moved to mt-config and the requirements for both i16
# and i10 should be combined.

class WaveformChannelScannable(HardwareTriggerableDetectorBase, PositionCallableProvider):

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

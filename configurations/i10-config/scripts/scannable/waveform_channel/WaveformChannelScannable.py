# Based on gda-mt.git/configurations/i16-config/scripts/scannable/scaler.py

from gda.device.detector.hardwaretriggerable import HardwareTriggerableDetectorBase
from gda.device.scannable import PositionCallableProvider, PositionStreamIndexer
from gda.device import Detector
from org.slf4j import LoggerFactory
from threading import Timer

class WaveformChannelScannable(HardwareTriggerableDetectorBase, PositionCallableProvider):

    def __init__(self, name, waveform_channel_controller, channel):
        self.logger = LoggerFactory.getLogger("WaveformChannelScannable:%s" % name)
        self.verbose = False
        
        self.name = name
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = [waveform_channel_controller.getChannelInputStreamFormat()]
        
        self.waveform_channel_controller = waveform_channel_controller

        self.channel_input_stream = waveform_channel_controller.getChannelInputStream(channel)
        self.stream_indexer = None
        self.number_of_positions = 0
        self.delayed_collection_timer = None

    def integratesBetweenPoints(self):
        return True
    
    def stop(self):
        self.waveform_channel_controller.stop()
        
    def collectData(self):
        if self.verbose: self.logger.info('collectData()...')
        # Here we need to wait for the motor runup to complete when our Triggerable Detector is actually
        # a Software triggerable detector rather than a Hardware one. We do this by getting the runup time
        # from the motion controller.
        motion_controller = self.getHardwareTriggerProvider()
        runupdown_time = motion_controller.getTimeToVelocity()
        if self.verbose: self.logger.info('motion_controller=%r, runupdown_time=%r' % (motion_controller, runupdown_time))
        if runupdown_time:
            self.delayed_collection_timer = Timer(motion_controller.getTimeToVelocity(), self._delayed_collectData)
            self.delayed_collection_timer.start()
            if self.verbose: self.logger.info('delayed start...')
        else:
            if self.verbose: self.logger.info('immediate start...')
            self.waveform_channel_controller.erase_and_start()
        
        if self.verbose: self.logger.info('...collectData()')

    def _delayed_collectData(self):
        self.waveform_channel_controller.erase_and_start()
        if self.verbose: self.logger.info('..._delayed_collectData()')

    def getStatus(self):
        return Detector.IDLE

    def setCollectionTime(self, t):
        if self.verbose: self.logger.info('setCollectionTime(%r)' % t)
        # does not effect Epics controller
        self.waveform_channel_controller.exposure_time = t

    def getCollectionTime(self):
        return self.waveform_channel_controller.exposure_time

    def readout(self):
        # read the last element collected
        raise RuntimeError(self.name + " for use only in Continuous scans")

    def atScanLineStart(self):
        if self.verbose: self.logger.info('atScanLineStart()...')
        
        #pass hardware trigger provider to waveform channel controller so WaveformChannelPollingInputStream can access to its property
        self.waveform_channel_controller.setHardwareTriggerProvider(self.getHardwareTriggerProvider())
        
        self.waveform_channel_controller.erase() # Prevent a race condition which results in stale data being returned
        self.channel_input_stream.reset()
        self.stream_indexer = PositionStreamIndexer(self.channel_input_stream);
        self.number_of_positions = 0
        if self.verbose: self.logger.info('...atScanLineStart()')

    def atScanLineEnd(self):
#         sleep(2) #https://jira.diamond.ac.uk/browse/I10-297?focusedCommentId=151337&page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel#comment-151337
        if self.verbose: self.logger.info('...atScanLineEnd()')
        # TODO: Must wait for all callables to have been called before doing this
        #self.waveform_channel_controller.stop()
        
    def getPositionCallable(self):
        if self.verbose: self.logger.info('getPositionCallable()... number_of_positions=%i' % self.number_of_positions)
        self.number_of_positions += 1
        self.waveform_channel_controller.number_of_positions = self.number_of_positions
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

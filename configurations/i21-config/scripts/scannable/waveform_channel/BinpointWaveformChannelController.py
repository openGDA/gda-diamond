""" 
define a Binpoint class to control data collection during continuous move.

Note that the Binpoint device is slaved from the ADC_ACQ_GRP, therefore there is no concept of exposure time.
However collection time is required for data pulling stream timing in order to retrieve collected data in
a more or less synchronised fashion between different channels.

@author: Fajin Yuan
@organization: Diamond Light Source Ltd
@since: 25 August 2020
"""
from gda.epics import CAClient
from scannable.waveform_channel.WaveformChannelPollingInputStream import WaveformChannelPollingInputStream
from org.slf4j import LoggerFactory
import installation

TIMEOUT = 5


class BinpointWaveformChannelController(object):

    def __init__(self, name, binpoint_root_pv):
        self.logger = LoggerFactory.getLogger("BinpointWaveformChannelController:%s" % name)
        self.verbose = False
        
        self.name = name
        #ADC_ACQ_GRP in EPICS doing the Binpoint reset comes after PGME waveform reset
        self.pv_reset = CAClient(binpoint_root_pv + 'BPTS:BINPOINTALL:RESET.PROC')
        self.binpoint_root_pv = binpoint_root_pv

        self.configure()
        self.exposure_time = 1
        self.number_of_positions = 0
        self.started = False
        self.hardware_trigger_provider=None
        self.stream=None
        
    def set_hardware_trigger_provider(self, hardwareTriggerProvider):
        self.hardware_trigger_provider=hardwareTriggerProvider
    
    def get_hardware_trigger_provider(self):
        return self.hardware_trigger_provider
    
    def configure(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'configure()...'))
        if installation.isLive():
            self.pv_reset.configure()

    def erase(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'erase()...'))
        self.started = False
        if self.verbose: self.logger.info("%s %s" % (self.name,'...erase()'))

    def erase_and_start(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'erase_and_start()...'))
        if installation.isLive():
            self.pv_reset.caput(1)
        self.started = True
        if self.verbose: self.logger.info("%s %s" % (self.name,'...erase_and_start()'))

    def stop(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'stop()...'))
        # Binpoint has no stop, since it is slaved from the ADC.
        if self.stream:
            self.stream.stop()
        self.started = False # added after I10-145
        if self.verbose: self.logger.info("%s %s" % (self.name,'...stop()'))

    # Provide functions to configure WaveformChannelScannable

    def getChannelInputStream(self, channel_pv_suffix):
        # Channel suffix assumes trailing :
        self.stream = WaveformChannelPollingInputStream(self, channel_pv_suffix)
        # TODO: Investigate if the NLAST.B can be listened to, if so we can avoid using this polling class
        self.stream.verbose = self.verbose
        return self.stream

    def getChannelInputStreamFormat(self):
        return '%f'

    # Provide functions to configure WaveformChannelPollingInputStream

    def getChannelInputStreamType(self):
        return float

    def getChannelInputStreamCAClients(self, channel_pv_suffix):
        if installation.isLive():
            pv_waveform = CAClient(self.binpoint_root_pv + channel_pv_suffix + 'BINPOINT')
            pv_count =    CAClient(self.binpoint_root_pv + channel_pv_suffix + 'BINPOINT:NLAST.B')
        else:
            pv_waveform = []
            pv_count = self.number_of_positions
        return pv_waveform, pv_count

    def getExposureTime(self):
        return self.exposure_time

    def getChannelInputStreamAcquiring(self):
        #return true when continuous move started
        return self.started and self.hardware_trigger_provider.continuousMovingStarted

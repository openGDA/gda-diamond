# Based on gda-diamond.git/configurations/i10-config/scripts/future/scannable/scaler.py at c35fcbb

from gda.epics import CAClient
from scannable.waveform_channel.WaveformChannelPollingInputStream import WaveformChannelPollingInputStream
from org.slf4j import LoggerFactory
import installation
import time

TIMEOUT = 5

""" Note that the Binpoint device is slaved from the MCA, therefore changing the collection time will have no effect other than
    changing the value returned by getCollectionTime().

    Also, its operation is triggered by the MCA and synchronised to it. If getPositionCallable() is called on this scannable more
    times than getPositionCallable() is called on the MCA, this will sit waiting forever for the points it has been asked to
    acquire.
"""

class BinpointWaveformChannelController(object):

    def __init__(self, name, binpoint_root_pv, all_pv_suffix):
        self.logger = LoggerFactory.getLogger("BinpointWaveformChannelController:%s" % name)
        self.verbose = False
        
        self.name = name
        self.pv_erasestart = CAClient(binpoint_root_pv + all_pv_suffix + 'RESET.PROC')
        self.binpoint_root_pv = binpoint_root_pv

        self.configure()
        self.exposure_time = 1
        self.number_of_positions = 0
        self.started = False
        self.hardware_trigger_provider=None
        self.stream=None
        
    def setHardwareTriggerProvider(self, hardwareTriggerProvider):
        self.hardware_trigger_provider=hardwareTriggerProvider
    
    def getHardwareTriggerProvider(self):
        return self.hardware_trigger_provider
    
    def configure(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'configure()...'))
        if installation.isLive():
            self.pv_erasestart.configure()

    def erase(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'erase()...'))
        if installation.isLive():
            self.pv_erasestart.caput(1)
            time.sleep(1.0)
        self.started = False
        if self.verbose: self.logger.info("%s %s" % (self.name,'...erase()'))

    def erase_and_start(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'erase_and_start()...'))
        if installation.isLive():
            self.pv_erasestart.caput(1)
        self.started = True
        if self.verbose: self.logger.info("%s %s" % (self.name,'...erase_and_start()'))

    def stop(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'stop()...'))
        # Binpoint has no stop, since it is slaved from the MCA.
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
        return self.started and self.hardware_trigger_provider.continuousMovingStarted


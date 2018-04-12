# Based on gda-mt.git/configurations/i10-config/scripts/future/scannable/scaler.py at c35fcbb

from gda.epics import CAClient
from mtscripts.scannable.waveform_channel.WaveformChannelPollingInputStream import \
                                          WaveformChannelPollingInputStream
from org.slf4j import LoggerFactory

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
#         self._collecting_data=False
    
#     def setCollectingData(self, b):
#         self._collecting_data=b
#     
#     def isCollectingData(self):
#         return self._collecting_data
        
    def configure(self):
        self.pv_erasestart.configure()

    def erase(self):
        if self.verbose: self.logger.info('erase()...')
        #self.pv_erasestart.caput(1)
        self.started = False
        if self.verbose: self.logger.info('...erase()')

    def erase_and_start(self):
        if self.verbose: self.logger.info('erase_and_start()...')
        self.pv_erasestart.caput(1)
        self.started = True
        if self.verbose: self.logger.info('...erase_and_start()')

    def stop(self):
        self.stream.stop()
        self.started = False # added after I10-145
        if self.verbose: self.logger.info('...stop()')
        # Binpoint has no stop, since it is slaved from the MCA.

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
        pv_waveform = CAClient(self.binpoint_root_pv + channel_pv_suffix + 'BINPOINT')
        pv_count =    CAClient(self.binpoint_root_pv + channel_pv_suffix + 'BINPOINT:NLAST.B')
        return pv_waveform, pv_count

    def getExposureTime(self):
        return self.exposure_time

    def getChannelInputStreamAcquiring(self):
        return self.started

# Based on gda-mt.git/configurations/i16-config/scripts/scannable/scaler.py

from gda.epics import CAClient
from mtscripts.scannable.waveform_channel.WaveformChannelPollingInputStream import \
                                          WaveformChannelPollingInputStream
from org.slf4j import LoggerFactory
from threading import Timer
from java.lang import Thread

TIMEOUT = 5

class McsWaveformChannelController(object):
    # e.g. mca_root_pv = BL16I-EA-DET-01:MCA-01

    def __init__(self, name, mca_root_pv, channelAdvanceInternalNotExternal=False):
        self.logger = LoggerFactory.getLogger("McsWaveformChannelController:%s" % name)
        self.verbose = False
        
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
        self.exposure_time_offset=.0
        self.number_of_positions = 0
        self.started = False

    def configure(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'configure()...'))
        self.pv_stop.configure()
        self.pv_dwell.configure()
        self.pv_channeladvance.configure()
        self.pv_presetReal.configure()
        self.pv_erasestart.configure()
        # Is there any reason why we can't EraseStart here?

    def erase(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'erase()...'))
        #self.pv_erasestart.caput(1)
        self.started = False
        if self.verbose: self.logger.info("%s %s" % (self.name,'...erase()'))

    def erase_and_start(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'erase_and_start()...'))
        self.pv_stop.caput(1)  # scaler won't start if already running
        if self.channelAdvanceInternalNotExternal:
            self.pv_dwell.caput(TIMEOUT, self.exposure_time) # Set the exposure time per nominal position
            self.pv_channeladvance.caput(TIMEOUT, self.channelAdvanceInternal)
            self.pv_presetReal.caput((self.number_of_positions * self.exposure_time)+self.exposure_time_offset) # Set the total capture time
        else:
            self.pv_channeladvance.caput(TIMEOUT, self.channelAdvanceExternal)
        self.pv_erasestart.caput(TIMEOUT, 1)
        # Since the mca NORD value could take some time to be updated and will continue returning the NORD of the last acquire,
        # wait before setting started to True, so WaveformChannelPollingInputStream doesn't try to use stale data.
        startedTimer = Timer(1.5, self._delayed_start_complete) # Failed at 0.5s, Ok at 1.5s.
        startedTimer.start()
        if self.verbose: self.logger.info("%s %s" % (self.name,'...erase_and_start()'))

    def _delayed_start_complete(self):
        self.started = True
        if self.verbose: self.logger.info("%s %s" % (self.name,'..._delayed_start_complete()'))

    def stop(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'stop()...'))
        self.pv_stop.caput(1)
        self.stream.stop() # enable stop the element polling loop when stop is called.
        self.started = False
        if self.verbose: self.logger.info("%s %s" % (self.name,'...stop()'))

    # Provide functions to configure WaveformChannelScannable

    def getChannelInputStream(self, channel):
        # Channels numbered from 1
        self.stream = WaveformChannelPollingInputStream(self, channel)
        # The NORD Epics pv cannot be listened to, hence the polling
        self.stream.verbose = self.verbose
        return self.stream

    def getChannelInputStreamFormat(self):
        return '%i'

    # Provide functions to configure WaveformChannelPollingInputStream

    def getChannelInputStreamType(self):
        return int

    def getChannelInputStreamCAClients(self, channel):
        pv_waveform = CAClient(self.mca_root_pv + 'mca' + `channel`)
        pv_count =    CAClient(self.mca_root_pv + 'mca' + `channel` + '.NORD') 
        return pv_waveform, pv_count

    def getExposureTime(self):
        return self.exposure_time

    def getChannelInputStreamAcquiring(self):
        #if self.verbose: self.logger.info('getChannelInputStreamAcquiring() = %r' % self.started)
        return self.started

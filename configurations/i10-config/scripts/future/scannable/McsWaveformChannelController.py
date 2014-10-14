# Based on gda-mt.git/configurations/i16-config/scripts/scannable/scaler.py

from datetime import datetime
from gda.epics import CAClient
from future.scannable.WaveformChannelPollingInputStream import WaveformChannelPollingInputStream

# TODO: This should be moved to mt-config and the requirements for both i16
# and i10 should be combined.

TIMEOUT = 5

class McsWaveformChannelController(object):
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

    # Provide functions to configure WaveformChannelScannable

    def getChannelInputStream(self, channel):
        # The NORD Epics pv cannot be listened to, hence the polling
        # Channels numbered from 1
        return WaveformChannelPollingInputStream(self, channel)

    def getChannelInputStreamFormat(self):
        return '%i'

    # Provide functions to configure WaveformChannelPollingInputStream

    def getChannelInputStreamType(self):
        return int

    def getChannelInputStreamCAClients(self, channel):
        pv_waveform = CAClient(self.mca_root_pv + 'mca' + `channel`)
        pv_count =    CAClient(self.mca_root_pv + 'mca' + `channel` + '.NORD') 
        return pv_waveform, pv_count

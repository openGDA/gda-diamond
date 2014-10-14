# Based on gda-mt.git/configurations/i10-config/scripts/future/scannable/scaler.py at c35fcbb

from datetime import datetime
from gda.epics import CAClient
from future.scannable.WaveformChannelPollingInputStream import WaveformChannelPollingInputStream

# TODO: This should be moved to mt-config and the requirements for both i16
# and i10 should be combined.

TIMEOUT = 5

""" Note that the Binpoint device is slaved from the MCA, therefore changing the collection time will have no effect other than
    changing the value returned by getCollectionTime().

    Also, its operation is triggered by the MCA and synchronised to it. If getPositionCallable() is called on this scannable more
    times than getPositionCallable() is called on the MCA, this will sit waiting forever for the points it has been asked to
    acquire.
"""

class BinpointWaveformChannelController(object):

    def __init__(self, name, binpoint_root_pv, all_pv_suffix):
        self.name = name
        self.pv_erasestart = CAClient(binpoint_root_pv + all_pv_suffix + 'RESET.PROC')
        self.binpoint_root_pv = binpoint_root_pv

        self.configure()
        self.exposure_time = 1
        self.number_of_positions = 0
        self.verbose = True

    def configure(self):
        self.pv_erasestart.configure()

    def erase_and_start(self):
        if self.verbose:
            print str(datetime.now()), self.name, 'erase_and_start...'
        self.pv_erasestart.caput(1)
        if self.verbose:
            print str(datetime.now()), self.name, '...erase_and_start'

    def stop(self):
        if self.verbose:
            print str(datetime.now()), self.name, '...stop'

    # Provide functions to configure WaveformChannelScannable

    def getChannelInputStream(self, channel_pv_suffix):
        # Channel suffix assumes trailing :
        # TODO: Investigate if the NLAST.B can be listened to, if so we can avoid using this polling class
        return WaveformChannelPollingInputStream(self, channel_pv_suffix)

    def getChannelInputStreamFormat(self):
        return '%f'

    # Provide functions to configure WaveformChannelPollingInputStream

    def getChannelInputStreamType(self):
        return float

    def getChannelInputStreamCAClients(self, channel_pv_suffix):
        pv_waveform = CAClient(self.binpoint_root_pv + channel_pv_suffix + 'BINPOINT')
        pv_count =    CAClient(self.binpoint_root_pv + channel_pv_suffix + 'BINPOINT:NLAST.B')
        return pv_waveform, pv_count

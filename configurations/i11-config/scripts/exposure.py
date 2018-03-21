from gda.factory import Finder
from gdascripts.pd.dummy_pds import ZeroInputExtraFieldsDummyPD
from gda.device.scannable import ScannablePositionChangeEvent
from gda.observable import IObserver
from collections import defaultdict, namedtuple
import logging
import datetime

LOG = logging.getLogger('exposure')
beamline = Finder.getInstance().find('beamline')
ZERO_TIME = datetime.timedelta(0)

class RadiationExposure(ZeroInputExtraFieldsDummyPD, IObserver):
    """Scannable to track the time samples are exposed to the beam

    To collect radiation exposure data, set new sample when the sample is loaded
    >>> radiation.new_sample('name_of_sample')

    then either add the scannable to the scans run or add it as a default scannable
    to include it in every scan (should be removed at the end of script)
    >>> add_default radiation
    radiation added to the list of default Scannables. Remove from the list by using command: remove_default radiation

    # or
    >>> scan delta 2 2.25 0.25 smythen 1 ocs Ic4 Io Ie radiation

    data on the most recent scan can be accessed via radiation.scan
    >>> print radiation.scan['start_exp'] # exposure at start of most recent scan
    0:00:58.686999
    >>> radiation.scan['end_exp'] # exposure at end of most recent scan
    0:01:09.977998

    To clear a sample (stop tracking exposure for this sample):
    >>> radiation.clear_sample()

    To get the data for a specific sample:
    >>> radiation['sample_name']
    {'exposure': datetime.timedelta(0, 73, 383999),
     'load_time': [datetime.datetime(2017, 10, 17, 16, 47, 3, 703000)],
     'scans': [{'end': datetime.datetime(2017, 10, 17, 16, 47, 14, 947000),
            'end_exp': datetime.timedelta(0, 11, 244000),
            'fileno': 644545,
            'start': datetime.datetime(2017, 10, 17, 16, 47, 3, 733000),
            'start_exp': datetime.timedelta(0, 0, 37000)},
           {'end': datetime.datetime(2017, 10, 17, 16, 48, 14, 918999),
            'end_exp': datetime.timedelta(0, 69, 977998),
            'fileno': 644546,
            'start': datetime.datetime(2017, 10, 17, 16, 48, 3, 621999),
            'start_exp': datetime.timedelta(0, 58, 686999)}]}

    If a new sample is loaded with the same name as a previous sample, any additional
    radiation exposure time is added to the previous time.

    To clear all collected radiation data:
    >>> radiation._records.clear()
    >>> radiation._sample = None
    >>> radiation._sample_id = None
    """
    def __init__(self, name, shutter):
        super(RadiationExposure, self).__init__(name)
        self._shutter = shutter
        self._current = shutter()
        self._sample = None
        self._sample_id = None
        self._records = defaultdict(lambda:defaultdict(list))
        self.exposure = ZERO_TIME
        self._last_open = _now()
        self._scan = {}

    def configure(self):
        self._shutter.addIObserver(self)

    def deconfigure(self):
        self._shutter.deleteIObserver(self)

    def update(self, src, evt):
        if isinstance(evt, ScannablePositionChangeEvent):
            LOG.debug('newPosition: %s, current: %s', evt.newPosition, self._current)
            if self._current != evt.newPosition:
                self._current = evt.newPosition
                if self._current.lower() == 'open':
                    self._last_open = _now()
                if self._current.lower() == 'close':
                    if self._sample is not None:
                        self._sample['exposure'] += _now() - self._last_open

    def atScanStart(self):
        LOG.debug('Scan starting')
        if self._sample is None:
            print('No sample loaded')
            self.new_sample('unknown')
        self._scan = {}
        self._scan['start'] = _now()
        self._scan['fileno'] = _get_file_number()
        self._scan['start_exp'] = self._exposure()
        self._sample['scans'].append(self._scan)

    def atScanEnd(self):
        LOG.debug('Scan ending')
        if self._scan is None:
            LOG.error('Scan was None at end of scan')
            return
        self._scan['end'] = _now()
        self._scan['end_exp'] = self._exposure()

    def new_sample(self, sample_id):
        """Load a new sample"""
        self.clear_sample()
        LOG.debug('Loading new sample (%s)', sample_id)
        self._sample = self._records[sample_id]
        self._sample['load_time'].append(_now())
        self._sample_id = sample_id
        if self.open:
            self._last_open = _now()
        if not self._sample['exposure']:
            self._sample['exposure'] = ZERO_TIME
    
    def clear_sample(self):
        LOG.debug('Clearing sample')
        if self._sample is not None:
            self._sample['unload_time'].append(_now())
            self._sample['exposure'] = self._exposure()
            self._sample = None
            self._sample_id = None
        
    def _exposure(self):
        """get total exposure time of current sample
        
        this is the total exposure so far plus the time since the shutter opened if
        the shutter is currently open"""

        if self._current.lower() == 'open':
            current = _now() - self._last_open
        else:
            current = ZERO_TIME
        if self._sample is not None:
            self._sample['exposure'] += current
            self._last_open = _now()
            return self._sample['exposure']
        else:
            return ZERO_TIME

    def _most_recent(self):
        return self._scan

    scan = property(_most_recent)

    def __repr__(self):
        return '%s:\n\tCurrent sample: %s\n\tCurrent exposure: %s' %(self.name, self._sample_id, self._exposure())

    def __getitem__(self, item):
        self._exposure() # force update of current sample
        return dict(self._records[item])

    def _open(self):
        return self._current.lower() == 'open'
    open = property(_open)


def _now():
    return datetime.datetime.now()

def _get_file_number():
    return beamline.getFileNumber()

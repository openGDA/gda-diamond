from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import ScannableUtils
from gda.data import NumTracker
from gda.data.metadata import GDAMetadataProvider
import json, zlib

''' A zero input and extraName (zie) scannable which records the current scan
    number and sample_id in a simple line separated json file.

    Note: this does nothing in Solstice (Malcolm) scans.

    from SampleID_recorder import SampleID_recorder
    sampleID_recorder = SampleID_recorder('sampleID_recorder',
        '/dls_sw/i15-1/software/gda_versions/var/samplog.json')
    /from uk.ac.diamond.daq.scanning import ScannableNexusWrapper
    /sampleID_recorder_wrapper = ScannableNexusWrapper()
    /sampleID_recorder_wrapper.setScannable(sampleID_recorder)
    /sampleID_recorder_wrapper.register()
'''
class SampleID_recorder(ScannableMotionBase):
	def __init__(self, name, logfile):
		self.setName(name)
		self.setInputNames(['sample_id'])
		self.setExtraNames([])
		self.setOutputFormat(['%d'])
		self.sample_id = None
		self.logfile=logfile

	def getPosition(self):
		return self.sample_id

	def asynchronousMoveTo(self, new_position):
		self.sample_id = new_position

	def isBusy(self):
		return False

	def atScanStart(self):
		scan_number = NumTracker(GDAMetadataProvider.getInstance().getMetadataValue("instrument", "gda.instrument", None)).getCurrentFileNumber()
		writeScanLog(self.logfile, scan_number, self.sample_id)

def writeSampleLog(logfile, scan_number, sample_id):
	with open(logfile, 'ab') as f:
		line_item = {'scan': scan_number, 'sample_id': sample_id}
		record = json.dumps(line_item).encode()
		checksum = '{:8x}'.format(zlib.crc32(record)).encode()
		f.write(record + b' ' + checksum + b'\n')

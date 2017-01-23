'''
converter of nexus files with i22 daresbury style detectors recorded in them to
the legacy otoko/bsl format

Ideally additional scannables found in the data are recorded as calibration data
'''
import logging
from datetime import datetime
import h5py
import os
import sys
import errno
import re
import numpy

DETECTOR_NUMBERS = {"SAXS": 1, "CALIB": 2, "WAXS": 3, "TIMES": 4}

class NexusBSL:
	def __init__(self, file_path):
		self.original_path = file_path
		self.logger = logging.getLogger('NexusBsl')
		self.logger.info('Reading file "%s"', file_path)

		self.nxs_file = h5py.File(self.original_path, 'r')
		self.entry = self.nxs_file.keys()[0]
		self.instrument_name = 'DLS'
		if 'name' in self.nxs_file[self.entry]['instrument']:
			self.instrument_name += '-' + self.nxs_file.get('entry1/instrument/name').value
		self._components = os.path.normpath(self.original_path).split(os.path.sep)
		if 'file_time' in self.nxs_file.attrs:
			self.file_time = datetime.strptime(self.nxs_file.attrs['file_time'][:-6], '%Y-%m-%dT%H:%M:%S')
		else:
			self.file_time = datetime.fromtimestamp(os.path.getmtime(self.original_path))

		self.scan_dimensions = list(self.nxs_file[self.entry]['scan_dimensions'])
		self.title = self._get_title()
		self.detectors = self._get_detectors()

		self.can_convert = {'SAXS', 'CALIB', 'WAXS'}.union(self.detectors.keys())

	def _is_in_dls_data(self):
		self.logger.debug('Testing dls directory. Components: %s', self._components)
		if len(self._components) <= 5:
			return False
		return (self._components[1] == 'dls'
				and self._components[3] == 'data'
				and self._components[4].isdigit()
				and len(self._components[4]) == 4)

	def is_commissioning(self):
		if not self._is_in_dls_data(): return False
		return self._components[5].startswith('cm')

	def _get_title(self):
		for key in ['title', 'scan_command']:
			if key in self.nxs_file[self.entry]:
				return str(self.nxs_file[self.entry][key][...])

	def _get_detectors(self):
		detectors = {}
		for det_name in self.nxs_file[self.entry]['instrument']:
			det = self.nxs_file[self.entry]['instrument'][det_name]
			if det.attrs.get('NX_class', '') == 'NXdetector':
				dtype = det['sas_type'][...][0]
				ddims = det['data'].shape
				detectors[dtype] = {'path': det.name, 'dimensions': ddims}
		return detectors

	def writeout(self):
		if not self.can_convert:
			self.logger.info('No ncd detectors found')
			return
		output_path_base = self.get_output_file_path()
		headerfile_name = output_path_base % 0
		self.logger.debug('headerfile name: %s', headerfile_name)
		try:
			os.makedirs(os.path.dirname(headerfile_name))
		except Exception, e:
			if isinstance(e, OSError) and getattr(e, 'errno', 0) == errno.EEXIST:
				self.logger.warn('Directory already exists, files will be overwritten')
			else:
				self.logger.error('Error creating directory %s', os.path.dirname(headerfile_name),  exc_info=e)
				return

		with open(headerfile_name, 'w') as headerfile:
			headerdate = self.file_time.strftime('%A %d/%m/%y at %H:%M:%S')
			headerfile.write('Created at %s on %s\r\n' %(self.instrument_name, headerdate))
			headerfile.write(self.title + '\r\n')
			for det in ['SAXS', 'CALIB', 'WAXS', 'TIMES']:
				if det not in self.detectors:
					self.logger.info('Ignoring %s detector, not in file', det)
					continue
				detinfo = self.detectors[det]
				detdims = len(detinfo['dimensions']) - len(self.scan_dimensions) - 1
				self.logger.info('%s: %sD, data_dimensions: %s, path: %s', det, str(detdims), str(detinfo['dimensions']), str(detinfo['path']))
				frames = 1
				detector_dimensions = []
				for i in xrange(len(detinfo['dimensions'])):
					if i < len(self.scan_dimensions):
						if self.scan_dimensions[i] != detinfo['dimensions'][i]:
							self.logger.warn('dimensions mismatch for %s: dimension %d has %d from scan and %d for detector', det, i, self.scan_dimensions[i], detinfo['dimensions'][i])
						frames *= detinfo['dimensions'][i]
					elif i == len(self.scan_dimensions):
						frames *= detinfo['dimensions'][i]
					else:
						detector_dimensions.insert(0, detinfo['dimensions'][i])
				self.logger.debug('Frames: %d, detector_dimensions: %s', frames, str(detector_dimensions))

				detfilename = output_path_base % DETECTOR_NUMBERS[det]
				indicator_format = 10 * ' % 7d' + '\r\n'
				endian = 1
				indicators = [endian, 0, 0, 0, 0, 0, 1]
				if det == 'TIMES':
					indicators[-1] = 0
				if det in ['TIMES', 'CALIB']:
					reversedims = True
					headerdims = [frames] + list(detector_dimensions)
				else:
					reversedims = False
					headerdims = list(detector_dimensions)
					headerdims.append(frames)
				if len(headerdims) == 2:
					headerdims.append(1)
				headerfile.write(indicator_format % tuple(headerdims + indicators))
				headerfile.write(os.path.basename(detfilename) + '\r\n')

				self.logger.info('Writing %s detector to %s', det, detfilename)
				self.writedet(detinfo, detfilename, reversedims)
		self.logger.info('Conversion complete')

	def get_output_file_path(self):
		#base = /dls/.../i22-12345, ext = .nxs
		base, ext = os.path.splitext(self.original_path)
		self.logger.debug('base: %s, ext: %s', base, ext)
		if ext != '.nxs':
			raise RuntimeError('File does not have nxs extension')
		components = os.path.normpath(base).split(os.path.sep)
		self.logger.debug('components: %s', components)
		if self._is_in_dls_data():
			# create bsl subdirectory at root of visit
			components.insert(6, 'bsl')
			self.logger.debug('Inserting bsl directory')
		bsl_dir = os.path.sep.join(components)
		self.logger.info('BSL directory is %s', bsl_dir)

		# scan_id is part after i22- eg 12345
		scan_id = components[-1].split('-', 1)[-1]
		scan_numbers = ''.join(re.findall('[0-9]', scan_id))
		scan_number = int(scan_numbers)

		bsl_letter = chr(ord('A') + (scan_number / 100) % 26)
		bsl_number = scan_number % 100
		bsl_date = "%X%02d" % (self.file_time.month, self.file_time.day)

		return "%s/%c%02d%%003d.%s" % (bsl_dir, bsl_letter, bsl_number, bsl_date)

	def writedet(self, detinfo, filename, transpose=False):
		data = self.nxs_file[detinfo['path']]['data'][...]
		f32_data = data.astype(numpy.float32)
		if transpose:
			f32_data = numpy.transpose(f32_data)
		with open(filename, 'w') as detfile:
			detfile.write(f32_data.tostring())

	def close(self):
		try:
			self.nxs_file.close()
			self.logger.info('Closing %s', self.original_path)
		except Exception, e:
			self.logger.error("Could not close nexus file", exc_info=e)


if __name__ == '__main__':
	LOG_FILENAME = '/dls_sw/i22/logs/nexusbsl.log'
	logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)-10s - %(message)s',
			filename=LOG_FILENAME,
			level=logging.DEBUG)
	log = logging.getLogger('main')
	for nxs_file in sys.argv[1:]:
		log.info('Converting %s', nxs_file)
		try:
			nxs_bsl = NexusBSL(nxs_file)
			if nxs_bsl.is_commissioning():
				log.debug('Ignoring commissioning file %s', nxs_file)
			else:
				nxs_bsl.writeout()
		except Exception, e:
			log.error('Could not convert file %s', nxs_file, exc_info=e)

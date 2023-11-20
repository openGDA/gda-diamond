from collections import OrderedDict
from gda.device.scannable import ScannableMotionBase
from org.slf4j import LoggerFactory
from xml.etree.ElementTree import ElementTree


class GeometryScannable(ScannableMotionBase):
	""" Class for updating a detector geometry from a geometry file
	
	"""
	def __init__(self, name, detectorNameInGeometryFile, geometryFile, # Defaults are for  pilatus3
				origin_offset_units = 'mm',
				origin_offset_vector = [62.58314655, -18.31388151, 621.14621608],
				calibration_date = '0000-01-01 00:00:00',
				calibration_scan_number = -1,
				fast_pixel_direction_value = [0.172],
				fast_pixel_direction_units = 'mm',
				fast_pixel_direction_vector = [ 0.7063757 , 0.00183285, -0.70783474],
				slow_pixel_direction_value = [0.172],
				slow_pixel_direction_units = 'mm',
				slow_pixel_direction_vector = [4.41563000e-04, 9.99995312e-01, 3.03000900e-03]):
		self.name = name
		self.detectorNameInGeometryFile = detectorNameInGeometryFile
		self.geometryFile = geometryFile
		self.defaults = {}
		self.defaults['origin_offset_units'] = 			origin_offset_units
		self.defaults['origin_offset_vector'] = 			origin_offset_vector
		self.defaults['calibration_date'] = 				calibration_date
		self.defaults['calibration_scan_number'] =		calibration_scan_number
		self.defaults['fast_pixel_direction_value'] =		fast_pixel_direction_value
		self.defaults['fast_pixel_direction_units'] =		fast_pixel_direction_units
		self.defaults['fast_pixel_direction_vector'] =	fast_pixel_direction_vector
		self.defaults['slow_pixel_direction_value'] =		slow_pixel_direction_value
		self.defaults['slow_pixel_direction_units'] =		slow_pixel_direction_units
		self.defaults['slow_pixel_direction_vector'] =	slow_pixel_direction_vector

		self.logger = LoggerFactory.getLogger('GeometryScannable:%s' % name)

		self.fields = OrderedDict()
		self.fields['origin_offset_units'] = 			'%s'
		self.fields['origin_offset_vector'] = 			'%f'
		self.fields['calibration_date'] = 				'%f'
		self.fields['calibration_scan_number'] =		'%i'
		self.fields['fast_pixel_direction_value'] =		'%f'
		self.fields['fast_pixel_direction_units'] =		'%s'
		self.fields['fast_pixel_direction_vector'] =	'%f'
		self.fields['slow_pixel_direction_value'] =		'%f'
		self.fields['slow_pixel_direction_units'] =		'%s'
		self.fields['slow_pixel_direction_vector'] =	'%f'

		self.inputNames = []
		self.extraNames = [key for key in self.fields.iterkeys()]
		self.outputFormat = [fmt for fmt in self.fields.itervalues()]
		self.logger.debug('extraNames: {}{}', self.extraNames,'')
		self.logger.debug('outputFormat: {}{}', self.outputFormat,'')

		for field in self.fields.iterkeys():
			self.fields[field] = self.defaults[field]

	# ScannableMotionBase overrides

	def rawGetPosition(self):
		return [value for value in self.fields.itervalues()]

	def atScanStart(self):
		self.updatePosition()

	# Local functions

	def getDetector(self, detectorNameInGeometryFile, geometryXml):
		self.logger.debug('detectorNameInGeometryFile =  {}, geometryXml = {}', detectorNameInGeometryFile, geometryXml)
		for detXml in geometryXml.findall('detector'):
			if detXml.attrib['name'] == detectorNameInGeometryFile:
				self.logger.debug('detectorNameInGeometryFile =  {}, name = {}, detXml = {}', detectorNameInGeometryFile, detXml.attrib['name'], detXml)
				return detXml

	def updateField(self, field, newValue, default):
		oldValue = self.fields[field]

		if newValue == None:
			newValue = default

		if  newValue != oldValue:
			self.fields[field] = newValue
			self.logger.info('Updated {} to {} from {}', field, newValue, oldValue)

	def updatePosition(self):
		geometryXml = ElementTree()
		geometryXml.parse(self.geometryFile)
		detXml  = self.getDetector(self.detectorNameInGeometryFile, geometryXml)
		if detXml == None:
			self.logger.warn("No Gemetry information found in {} with the name {}",
							 geometryXml, self.detectorNameInGeometryFile)
			return
		self.logger.debug('detXml = {}{}', detXml, '')
		# ------------------------------ I16-651 ------------------------------
		positionXml = detXml.find('position')
		position = [ float(element.text) for element in positionXml.findall('vector/element') ]
		self.updateField('origin_offset_units', positionXml.find('units').text, self.origin_offset_units)
		self.updateField('origin_offset_vector', position, self.origin_offset_vector) 
		# ------------------------------ I16-648 ------------------------------
		self.updateField('calibration_date', detXml.find('time').text, self.calibration_date)
		self.updateField('calibration_scan_number', int(detXml.find('scan').text), self.calibration_scan_number)
		# ------------------------------ I16-649 ------------------------------
		axes = detXml.findall('axis')
		for axisXml in axes:
			size = float(axisXml.find('size').text)
			units = axisXml.find('units').text
			vector = [ float(element.text) for element in axisXml.findall('vector/element') ]

			axisName = axisXml.attrib['name']
			if axisName == 'fast':
				self.updateField('fast_pixel_direction_value', [size], self.fast_pixel_direction_value)
				self.updateField('fast_pixel_direction_units', units, self.fast_pixel_direction_units)
				self.updateField('fast_pixel_direction_vector', vector, self.fast_pixel_direction_vector)
			if axisName == 'slow':
				self.updateField('slow_pixel_direction_value', [size], self.slow_pixel_direction_value)
				self.updateField('slow_pixel_direction_units', units, self.slow_pixel_direction_units)
				self.updateField('slow_pixel_direction_vector', vector, self.slow_pixel_direction_vector)

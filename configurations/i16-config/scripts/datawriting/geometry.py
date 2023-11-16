from collections import OrderedDict
from gda.device.scannable import ScannableMotionBase
from org.slf4j import LoggerFactory
from xml.etree.ElementTree import ElementTree

class GeometryScannable(ScannableMotionBase):
	""" Class for updating a detector geometry from a geometry file
	
	"""
	def __init__(self, name, detectorNameInGeometryFile, geometryFile):
		self.name = name
		self.detectorNameInGeometryFile = detectorNameInGeometryFile
		self.geometryFile = geometryFile

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
		self.updatePosition()

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
		self.logger.debug('detXml = {}{}', detXml, '')
		# ------------------------------ I16-651 ------------------------------
		"""
		origin_offset:
		  units@: mm 											# TRANSFORMATION_UNITS, TODO: Use value from geometry file
		  vector@: [62.58314655, -18.31388151, 621.14621608]	# TRANSFORMATION_VECTOR, TODO: Use value from geometry file
		"""
		positionXml = detXml.find('position')
		position = [ float(element.text) for element in positionXml.findall('vector/element') ]

		self.updateField('origin_offset_units', positionXml.find('units').text, 'mm')
		self.updateField('origin_offset_vector', position, [62.58314655, -18.31388151, 621.14621608]) 
		# ------------------------------ I16-648 ------------------------------
		"""
		calibration_date: "0000-01-01 00:00:00"	# CALIBRATION_TIME : CALIBRATION_TIME_DEF, TODO: Use value from geometry file
		calibration_scan_number: -1				# CALIBRATION_SCAN : CALIBRATION_SCAN_DEF, TODO: Use value from geometry file
		"""
		self.updateField('calibration_date', detXml.find('time').text, '0000-01-01 00:00:00')
		self.updateField('calibration_scan_number', int(detXml.find('scan').text), -1)
		# ------------------------------ I16-649 ------------------------------
		"""
		module/:
		  fast_pixel_direction:
		    value: [0.172] 												# FAST_PIXEL_SIZE, TODO: Use value from geometry file
		    units@: mm 													# FAST_PIXEL_UNITS, TODO: Use value from geometry file
		    vector@: [ 0.7063757 , 0.00183285, -0.70783474] 				# FAST_PIXEL_DIRECTION, TODO: Use value from geometry file
		  slow_pixel_direction:
		    value: [0.172] 												# SLOW_PIXEL_SIZE, TODO: Use value from geometry file
		    units@: mm 													# SLOW_PIXEL_UNITS, TODO: Use value from geometry file
		     vector@: [4.41563000e-04, 9.99995312e-01, 3.03000900e-03] 	# SLOW_PIXEL_DIRECTION, TODO: Use value from geometry file
		"""
		axes = detXml.findall('axis')
		for axisXml in axes:
			size = float(axisXml.find('size').text)
			units = axisXml.find('units').text
			vector = [ float(element.text) for element in axisXml.findall('vector/element') ]

			axisName = axisXml.attrib['name']
			if axisName == 'fast':
				self.updateField('fast_pixel_direction_value', [size], [0.172])
				self.updateField('fast_pixel_direction_units', units, 'mm')
				#self.updateField('fast_pixel_direction_vector', vector, [ 0.7063757 , 0.00183285, -0.70783474])
				self.updateField('fast_pixel_direction_vector', vector, [ 0.7 , 0.002, -0.7])
			if axisName == 'slow':
				self.updateField('slow_pixel_direction_value', [size], [0.172])
				self.updateField('slow_pixel_direction_units', units, 'mm')
				#self.updateField('slow_pixel_direction_vector', vector, [4.41563000e-04, 9.99995312e-01, 3.03000900e-03])
				self.updateField('slow_pixel_direction_vector', vector, [4e-04, 10e-01, 3e-03])

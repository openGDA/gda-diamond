"""
GeometryScannable class that defines the detector geometry

Last Updated 29/Oct/2025 by Dan Porter for I16-969
"""

import os
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

		self.inputNames = []
		self.extraNames = ['origin_offset_value', 'origin_offset_units' ,'origin_offset_vector', 'calibration_date', 'calibration_scan_number',
					'fast_pixel_direction_value','fast_pixel_direction_units', 'fast_pixel_direction_vector', 'slow_pixel_direction_value',
					'slow_pixel_direction_units','slow_pixel_direction_vector']
		self.outputFormat = ['%f', '%s', '%f', '%f', '%i', '%f', '%s', '%f', '%f', '%s', '%f']

		self.logger.debug('extraNames: {}{}', self.extraNames,'')
		self.logger.debug('outputFormat: {}{}', self.outputFormat,'')

		for field in self.extraNames:
			setattr(self, field, None)

	def rawGetPosition(self):
		return [getattr(self, val_name) for val_name in self.extraNames]

	def atScanStart(self):
		self.updatePosition()

	def getDetector(self, detectorNameInGeometryFile, geometryXml):
		self.logger.debug('detectorNameInGeometryFile =  {}, geometryXml = {}', detectorNameInGeometryFile, geometryXml)
		for detXml in geometryXml.findall('detector'):
			if detXml.attrib['name'] == detectorNameInGeometryFile:
				self.logger.debug('detectorNameInGeometryFile =  {}, name = {}, detXml = {}', detectorNameInGeometryFile, detXml.attrib['name'], detXml)
				return detXml

	def updatePosition(self):
			geometryXml = ElementTree()
			if not os.path.isfile(self.geometryFile):
				self.logger.warn("Geometry file does not exist: ", self.geometryFile)
				return
			geometryXml.parse(self.geometryFile)
			detXml = self.getDetector(self.detectorNameInGeometryFile, geometryXml)
			if detXml == None:
				self.logger.warn("No Geometry information found in {} with the name {}",
								 geometryXml, self.detectorNameInGeometryFile)
				return
			self.logger.debug('detXml = {}{}', detXml, '')
			# ------------------------------ I16-969 ------------------------------
			# ------------------------------ I16-651 ------------------------------
			positionXml = detXml.find('position')
			position = [float(element.text) for element in positionXml.findall('vector/element')]
			self.origin_offset_value = float(positionXml.find('size').text)
			self.origin_offset_units = positionXml.find('units').text
			self.origin_offset_vector = position
			# ------------------------------ I16-648 ------------------------------
			self.calibration_date = detXml.find('time').text
			self.calibration_scan_number = int(detXml.find('scan').text)
			# ------------------------------ I16-649 ------------------------------
			axes = detXml.findall('axis')
			for axisXml in axes:
				size = float(axisXml.find('size').text)
				units = axisXml.find('units').text
				vector = [float(element.text) for element in axisXml.findall('vector/element')]

				axisName = axisXml.attrib['name']
				if axisName == 'fast':
					self.fast_pixel_direction_value = [size]
					self.fast_pixel_direction_units = units
					self.fast_pixel_direction_vector = vector
				if axisName == 'slow':
					self.slow_pixel_direction_value = [size]
					self.slow_pixel_direction_units = units
					self.slow_pixel_direction_vector = vector

#!/usr/bin/env python

import os
from gda.configuration.properties import LocalProperties
import time
from gda.px.detector import PilatusDetectorCollectionParameters

WRITE_TEMPLATE_PROPERTY = "gda.device.detector.pilatus.writetemplate"
TEMPLATE_TEMPLATE_FILE_PROPERTY = "gda.cbf.template.template.file"

CBF_ROTATION_VECTOR_FORMAT = "%s %.4g %.4g %.4g . . ." # % (depends_on, v[0], v[1], v[2])

def _set(state):
	LocalProperties.set(WRITE_TEMPLATE_PROPERTY, str(state).lower())

def enable():
	_set(True)

def disable():
	_set(False)

def should_write_template():
	return True # LocalProperties.check(WRITE_TEMPLATE_PROPERTY)

def create_template(template_template, parameters):
	'''Return a cbf template configured for the generation of full cbf
	images. Distance and pixel size should be provided in mm.
	Beam centre should be in pixels.'''

	if parameters.has_key("gonio_rotation_vector"):
		vx, vy, vz = parameters["gonio_rotation_vector"]
		cbf_gonio_rotation_axis = CBF_ROTATION_VECTOR_FORMAT % (".       ", vx, vy, vz)
	else:
		cbf_gonio_rotation_axis = parameters["gonio_rotation_axis"] # legacy

	return template_template % {
							"beamline": parameters['beamline'],
							"xtal_id": parameters.get('xtal_id', 'xtal001'),
							"detector_id": parameters['detector_id'],
							"detector_name": parameters['detector_name'],
							"beam_x": parameters['beam_x'] * parameters['pixel_size_x'],
							"beam_y": parameters['beam_y'] * parameters['pixel_size_y'],
							"pixel_x": parameters['pixel_size_x'],
							"pixel_y": parameters['pixel_size_y'],
							"distance": parameters['distance'],
							"gonio_rotation_axis": cbf_gonio_rotation_axis
	}

def write_template(template_file, parameters):
	
	parent_dir = os.path.dirname(template_file)
	if not os.path.isdir(parent_dir):
		os.makedirs(parent_dir)
	
	template_template_file = "/dls_sw/b16/software/var_diffraction/dls-b16.cbftt" # LocalProperties.get(TEMPLATE_TEMPLATE_FILE_PROPERTY)
	tr = open(template_template_file, 'rb')
	template_template = tr.read()
	tr.close()
	
	parameters['beamline'] = "DLS_B16" # % LocalProperties.get("gda.beamline.name.upper")
	template = create_template(template_template, parameters)
	
	tw = open(template_file, 'wb')
	tw.write(template)
	tw.close()

def configure_template(handler, detector, beamPositionPixels, detector_distance, gonio_rotation_vector):
	
	if should_write_template():
		semirandom_filename = "%03d.cif" % int(time.time() * 1000 % 1000)
		template_location = "/dls_sw/b16/software/var_diffraction/cbf-cache/"
		template_file = os.path.join(template_location, semirandom_filename)
		handler.update("writing CBF template to " + template_file)
		write_template(template_file, {
			'detector_id': detector.id,
			'detector_name': detector.shortName,
			'beam_x': beamPositionPixels[0],
			'beam_y': beamPositionPixels[1],
			'pixel_size_x': detector.pixelSize[0],
			'pixel_size_y': detector.pixelSize[1],
			'distance': detector_distance,
			'gonio_rotation_vector': gonio_rotation_vector
		})
	
	else:
		handler.update("not writing CBF template")
		template_file = "0" # need to tell it 0 to unset
	
	params = PilatusDetectorCollectionParameters()
	params.setCbfTemplateFile(template_file)
	detector.sendParameters(params)

#!/usr/bin/env python

import numpy as np
from scipy import linalg
import scipy as sp
from scipy import optimize
import scisoftpy as dnp
import sys
from collections import OrderedDict
import xml.etree.ElementTree as ET
import time

#TODO: Extend configuration to other detectors

def cs(degrees):
    r = np.deg2rad(degrees)
    return np.cos(r), np.sin(r)

def rotate_x(degrees):
    c, s = cs(degrees)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

def rotate_y(degrees):
    c, s = cs(degrees)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

def rotate_z(degrees):
    c, s = cs(degrees)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


# detector is mounted on delta arm which is horizontal at delta=0
# it has orientation given by Euler angles (a,b,c) as O = R_x(a) R_y'(b) R_z''(c) - an
# intrinsic rotation - for z being detector normal (away from sample) and
# detector origin at (p_x, p_y, p_z)


pixel_size = 0.172

def orient_detector(params, delta=0, gamma=0):
    '''Orient the detector with three Euler angles and two diffractometer circles
    Return transformation matrix from detector frame to laboratory frame and
    also diffractometer rotations
    '''
    a,b,c = params[0:3]
    # orientation matrix is inverse of transformation from lab to detector frame
    O = np.dot(rotate_x(a), np.dot(rotate_y(b), rotate_z(c))).T
#     R = np.dot(rotate_x(-delta), rotate_y(gamma))
    R = np.dot(rotate_x(gamma), rotate_y(delta)) # this is for x-dir up
    return np.dot(R, O), R

def direct_beam(params, delta, gamma):
    '''Calculate where direct beam intercepts detector in pixel coordinate
    '''
    O, R = orient_detector(params, delta, gamma)
    p = np.array(params[3:])
    p = np.dot(R, p)
    d = np.dot(p, O[:,2]) # distance from sample to nearest point on detector

    # direct beam is (0, 0, z)
    # thus (0, 0, z) * O[:,2] = d
    # and relative position vector needs to be transformed back to detector frame
    p_b = np.array([0, 0, d/O[2,2]]) - p
    m = np.dot(O.T, p_b)[:2]
    return m/pixel_size

def pixels_diff(params, *args):
    deltas, gammas = args[0], args[1]
    data = np.ravel(np.asarray(args[2]))
    results = [direct_beam(params, d, g) for g, d in zip(gammas, deltas)]
    return np.ravel(np.array(results)) - data

bnds = [(-180, 180), (-180, 180), (-180, 180), (-1000, 1000), (-1000, 1000), (0, 1000)]

def calibrate_detector(data, deltas, gammas, i_params):
    return optimize.leastsq(pixels_diff, i_params, args=(deltas, gammas, data))

def calibrate_detector2(data, deltas, gammas, i_params):
    return optimize.fmin_l_bfgs_b(residuals_sq, i_params, bounds=bnds, args=(deltas, gammas, data), approx_grad=True)
#, factr=10, pgtol=1e-10, epsilon=1e-12)

def residuals_sq(params, *args):
    ps = pixels_diff(params, *args)
    return np.square(ps).sum()

def calibrate_detector_global(data, deltas, gammas):
    return optimize.differential_evolution(residuals_sq, bounds=bnds, args=(deltas, gammas, data))


sample_deltas = [-9.5, -9., -8.5, -8., -7.5, -7., -6.5, -6. ] * 3
sample_gammas = [-1.] * 8 + [0.] * 8 + [1.] * 8

sample_data = [(261, 57), (230, 57), (198, 56), (167, 55), (134, 54), (102, 54), (68, 53), (35, 52),
        (260, 108), (229, 107), (198, 107), (166, 106), (134, 106), (101, 106), (68, 105), (34, 105),
        (259, 158), (228, 158), (197, 158), (165, 158), (133, 158), (100, 158), (67, 158), (33, 157)]

# 0.4663, -44.01, -88.99, 17.96, 50.40, 525.9
#
# [[ 0.01268187, -0.99991112,  0.00411266],
#  [ 0.71913747,  0.01197841,  0.69476458],
#  [-0.69475209, -0.00585335,  0.71922547]]


def extract_axes(datfile):
    deltaoffsets = datfile["delta_axis_offset"]
    deltas = datfile["delta"]
    deltas = deltas - deltaoffsets
    gammas = datfile["gam"]
    return {"delta" : deltas, "gamma" : gammas}

def extract_image_paths(datfile, datadir, detector_path_template):
    template = "%s/" + datfile["metadata"][detector_path_template]
    numbers = datfile["path"]
    return [ template % (datadir, n) for n in numbers ]

def extract_pixel_peaks(image_paths):
    peaks = []
    for image_path in image_paths:
        image = dnp.io.load(image_path, warn=False)
        image = image['image_01']
        fast_axis_length = image.shape[1]
        peaks.append( (image.argmax() % fast_axis_length,
            image.argmax() / fast_axis_length) )
    return peaks

def print_output(parameters, fast, slow, normal, d0, fitted_params, deltas, gammas, data):
    print "\nX is up (gamma axis), Y is toward the ring (delta axis), Z is along the beam."
    print "\nFitted Parameters:"
    for item in parameters.items():
        print item

    print "\nFast Axis:"
    print fast
    print "\nSlow Axis:"
    print slow
    print "\nDetector Plane Normal:"
    print normal
    print "\nDetector Origin Position:"
    print d0

    print "\nPixel Diff"
    print pixels_diff(fitted_params, deltas, gammas, data)

    print "\nData"
    print data

# in-place prettyprint formatter
def indent_tree(elem, level=0):
    indent = "\t"
    i = "\n" + level * indent
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indent
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent_tree(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def generate_xml(fast, slow, d0, pixel_size, timestamp, scannumber, detector):
    format_string = '%.9f'
    root = ET.Element('geometry')
    det_node = ET.SubElement(root, 'detector')
    det_node.attrib['name'] = detector
    fast_node = ET.SubElement(det_node, 'axis')
    fast_node.attrib['name'] = 'fast'
    slow_node = ET.SubElement(det_node, 'axis')
    slow_node.attrib['name'] = 'slow'
    position_node = ET.SubElement(det_node, 'position')
    position_node.attrib['name'] = 'origin'

    date_node = ET.SubElement(det_node, 'time')
    date_node.text = timestamp
    scan_node = ET.SubElement(det_node, 'scan')
    scan_node.text = "%d" % scannumber


    fast_vector_node = ET.SubElement(fast_node, 'vector')
    fast_vector_node.append(ET.Element('element'))
    fast_vector_node.append(ET.Element('element'))
    fast_vector_node.append(ET.Element('element'))
    fast_vector_node.getchildren()[0].text = format_string % fast[0]
    fast_vector_node.getchildren()[1].text = format_string % fast[1]
    fast_vector_node.getchildren()[2].text = format_string % fast[2]
    slow_vector_node = ET.SubElement(slow_node, 'vector')
    slow_vector_node.append(ET.Element('element'))
    slow_vector_node.append(ET.Element('element'))
    slow_vector_node.append(ET.Element('element'))
    slow_vector_node.getchildren()[0].text = format_string % slow[0]
    slow_vector_node.getchildren()[1].text = format_string % slow[1]
    slow_vector_node.getchildren()[2].text = format_string % slow[2]
    position_vector_node = ET.SubElement(position_node, 'vector')
    position_vector_node.append(ET.Element('element'))
    position_vector_node.append(ET.Element('element'))
    position_vector_node.append(ET.Element('element'))
    position_vector_node.getchildren()[0].text = format_string % d0[0]
    position_vector_node.getchildren()[1].text = format_string % d0[1]
    position_vector_node.getchildren()[2].text = format_string % d0[2]

    position_node.append(ET.Element("size"))
    position_node.getchildren()[1].text = "1"
    position_node.append(ET.Element("units"))
    position_node.getchildren()[2].text = "mm"
    fast_node.append(ET.Element("size"))
    fast_node.getchildren()[1].text = str(pixel_size)
    fast_node.append(ET.Element("units"))
    fast_node.getchildren()[2].text = "mm"
    slow_node.append(ET.Element("size"))
    slow_node.getchildren()[1].text = str(pixel_size)
    slow_node.append(ET.Element("units"))
    slow_node.getchildren()[2].text = "mm"

    indent_tree(root)
    return ET.ElementTree(root)

def usage():
    print """
Usage: dpcalib /path/to/dat/file.dat detector"

    where detector is pilatus1 or pilatus3

e.g.
    dpcalib.py /dls/i16/data/2018/cm19668-2/705061.dat pilatus3
"""

def main( argv ):
    if len(argv) < 3:
        usage()
        return
    datfilepath = argv[1]
    detector = argv[2]

    if detector == "pilatus1":
        detector_path_template = "pilatus_100k_path_template"
    elif detector == "pilatus3":
        detector_path_template = "pilatus3_100k_path_template"
    else:
        print "detector must be pilatus1 or pilatus3"
        usage()
        return

    datadir = datfilepath.rsplit('/', 1)[0]
    print "\nProcessing data file " + datfilepath
    print "data file directory " + datadir
    datfile = dnp.io.load(datfilepath, warn=False)
    scannumber = datfile.metadata['SRSRUN']
    timestring = datfile.metadata['date']
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(timestring))
    axes = extract_axes(datfile)
    deltas = axes["delta"]
    gammas = axes["gamma"]
    data = extract_pixel_peaks(extract_image_paths(datfile, datadir, detector_path_template))

    params = OrderedDict([('x_rot', 0.5), ('y_rot', -45), ('z_rot', 0),
                          ('x_pos', 18), ('y_pos', 50), ('z_pos', 500)])
    initial_params = tuple(params.values())

    fitted_params = calibrate_detector2(data, deltas, gammas, initial_params)
    params['x_rot'], params['y_rot'], params['z_rot'],\
        params['x_pos'], params['y_pos'], params['z_pos'] = fitted_params[0]

    orientation_matrix = orient_detector(fitted_params[0])[0]
    fast = orientation_matrix.T[0]
    slow = orientation_matrix.T[1]
    normal = orientation_matrix.T[2]

    detector_origin_position = [params['x_pos'], params['y_pos'], params['z_pos']]
    print_output(params, fast, slow, normal, detector_origin_position, fitted_params[0], deltas, gammas, data)
    # TODO: rework this so that this script doesn't erase the calibration for pilatus1 when pilatus3 is calibrated. 
    xml_tree = generate_xml(fast, slow, detector_origin_position, pixel_size, timestamp, scannumber, detector)
    xml_tree.write('geometry.xml')

if __name__ == "__main__":
    main( sys.argv )

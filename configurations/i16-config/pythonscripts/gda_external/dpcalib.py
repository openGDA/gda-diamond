import numpy as np
from scipy import linalg
import scipy as sp
from scipy import optimize
import scisoftpy as dnp
import sys
from collections import OrderedDict

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


# define y vertical upwards, z along beam, thus x is "away from storage ring"
# => rotate_delta(d) = rotate_x(-d), rotate_gamma = rotate_y

# detector is mounted on delta arm which is horizontal at delta=0
# it has orientation given by Euler angles (a,b,c) as O = R_x(a) R_y'(b) R_z''(c) - an
# intrinsic rotation - for z being detector normal (away from sample) and
# and detector origin at (p_x, p_y, p_z)


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
    R = np.dot(rotate_y(delta), rotate_x(gamma)) # this is for x-dir up
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
    deltas = datfile["delta"]
    gammas = datfile["gam"]
    return {"delta" : deltas, "gamma" : gammas}

def extract_image_paths(datfile, datadir):
    template = "%s/" + datfile["metadata"]["pilatus100k_path_template"]
    numbers = datfile["path"]
    return [ template % (datadir, n) for n in numbers ]

def extract_pixel_peaks(image_paths):
    peaks = []
    for image_path in image_paths:
        image = dnp.io.load(image_path, warn=False)
        image = image['image0']
        fast_axis_length = image.shape[1]
        peaks.append( (image.argmax() % fast_axis_length,
            image.argmax() / fast_axis_length) )
    return peaks

def print_output(parameters, fast, slow, normal, d0):
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

def write_xml(fast, slow, d0):
    pass

def main( argv ):
    if len(argv) < 2:
        print "Require path to data file"
        return
    datfilepath = argv[1]
    datadir = datfilepath.rsplit('/', 1)[0]
    print "\nProcessing data file " + datfilepath
    print "data file directory " + datadir
    datfile = dnp.io.load(datfilepath, warn=False)
    axes = extract_axes(datfile)
    deltas = axes["delta"]
    gammas = axes["gamma"]
    data = extract_pixel_peaks(extract_image_paths(datfile, datadir))


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
    print_output(params, fast, slow, normal, detector_origin_position)

if __name__ == "__main__":
    main( sys.argv )

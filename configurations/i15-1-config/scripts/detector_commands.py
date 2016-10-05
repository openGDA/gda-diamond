"""Jython commands for detectors specific to this beamline.

The commands defined here are intended for use as part of the mscan() syntax.
For instance:
>>> mscan(step(my_scannable, 0, 10, 1), det=mandelbrot(0.1))
"""

from mapping_scan_commands import _fetch_model_for_detector

def _fetch_detector_and_model(detector_name, detector_model_name, exposure_time):
    """Obtain and possibly update an Area Detector model, to be passed to mscan().
    """
    print "_fetch_detector_and_model(%r, %r, %r) called..." % (detector_name, detector_model_name, exposure_time)
    print "calling _fetch_model_for_detector(%r)" % (detector_model_name)
    model = _fetch_model_for_detector(detector_model_name)

    if exposure_time is not None:
        print "calling model.setExposureTime(%r)" % (exposure_time)
        model.setExposureTime(exposure_time)
    else:
        pass  # Keep the value already set.

    print "returning (%r, %r)" % (detector_name, model)
    return detector_name, model

def mandelbrot(exposure_time=None):
    return _fetch_detector_and_model('mandelbrot', 'mandelbrot_detector', exposure_time)

def cam2det(exposure_time=None):
    return _fetch_detector_and_model('cam2det', 'Area Detector', exposure_time)

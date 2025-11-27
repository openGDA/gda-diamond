from org.eclipse.scanning.command.Services import getRunnableDeviceService
from org.eclipse.scanning.api.points.models import StaticModel, AxialStepModel, AxialArrayModel, CompoundModel, ConsecutiveMultiModel, TwoAxisGridPointsModel, TwoAxisGridStepModel, TwoAxisPointSingleModel, AxialPointsModel, OneAxisPointRepeatedModel
from org.eclipse.scanning.sequencer import ScanRequestBuilder
from mapping_scan_commands import submit
from gda.device.scannable import DummyScannable
from gda.device import Scannable
from org.eclipse.scanning.api.points.models import BoundingBox

from scanning.xanes_utils import submit_scan

malcolm_blocks = {"xspress3Excalibur":"BL18I-ML-SCAN-03", "excalibur":"BL18I-ML-SCAN-03", "xspress3":"BL18I-ML-SCAN-06"} 

prefix = "BL18I"
if LocalProperties.isDummyModeEnabled():
    import socket
    prefix = socket.gethostname().split(".")[0]
    malcolm_blocks = {"xspress3":prefix + "-ML-SCAN-03"}

malcolm_axes = ["t1x", "t1y", "t1z", "t1theta"]


def check_malcolm_names_ok(axis_name, block_name):
    if axis_name not in malcolm_axes:
        print("Cannot run scan - axis name needs to be one of {}".format(malcolm_axes))
        return False

    if block_name not in malcolm_blocks.keys():
        print("Cannot run scan - malcolm block_name needs to be one of {}".format(malcolm_blocks.keys()))
        return False

    return True


def run_continuous_scan(axis_name, start_pos, end_pos, step_size, exposure_time,
                        num_repetitions=1, is_alternating=True,
                        continuous_scan=True, malcolm_block_name="xspress3"):
    """
        Run a 1-dimensional continuous Malcolm scan using a single axis (t1x, t1y or t1z) and a detector.
        Parameters
            axis_name = name of axis to scan (t1x, t1y or t1z)
            start_pos - start position
            end_pos - end position
            step_size - step size
            exposure_time - 'time per point'
        Optional parameters :
            num_repetitions - how many times to repeat the scan
            is_alternating - whether to scan back and forth when repeating (default = True)
            continuous_scan - whether to scan continuously (default = True)
            malcolm_block_name - human readable name of malcolm block to use ("xspress3", "excalibur" or "xspress3Excalibur"; default = "xspress3")
        
    """

     # Extract name from Scannable.
    if isinstance(axis_name, Scannable):
        axis_name = axis_name.getName()
    
    if not check_malcolm_names_ok(axis_name, malcolm_block_name):
        return

    detector_name = malcolm_blocks[malcolm_block_name]
    
    print("Running scan using %s with %s detector (exposure time = %.2f sec)" % (axis_name, detector_name, exposure_time))
    print("Scan start, stop, step : %.5f, %.5f, %.5f" % (start_pos, end_pos, step_size))

    # Get detector runnable device
    detector_device = getRunnableDeviceService().getRunnableDevice(detector_name)
    if detector_device is None:
        raise Exception("Could not find runnable device for detector called " + detector_name)
    
    # Set the exposure time on detector model
    detector_model = detector_device.getModel()
    detector_model.setExposureTime(exposure_time)
    detectors = {detector_model.getName(): detector_model}

    if num_repetitions > 1:
        """ 
        Do 2-d map, fast axis is the one selected by user. Malcolm on I18 doesn't like using
        a 'dummy' scannable for slow axis, so do very small range of t1y positions so
        that y stays in same position for each row of the map.
        """
        # We should replace t1y with one of the unused motors rather than always
        # using t1y.
        t1y_position = float(t1y.getPosition()) 
        end_t1y = t1y_position + 0.0001
        t1y_step = 0.0001/(num_repetitions-1)
        
        bounds = BoundingBox([start_pos, t1y_position], [end_pos, end_t1y])

        path_model = TwoAxisGridStepModel(axis_name, "t1y")
        path_model.setxAxisStep(step_size)
        path_model.setyAxisStep(t1y_step)
        path_model.setBoundingBox(bounds)
        path_model.setContinuous(True)
        path_model.setAlternating(is_alternating)
    else:
        # Make step scan style model with single axis
        path_model_fast_axis = AxialStepModel(axis_name, start_pos, end_pos, step_size)
        path_model_fast_axis.setContinuous(continuous_scan)
        path_model_fast_axis.setAlternating(is_alternating)
    
    # Generate ScanRequest using the builder
    request = ScanRequestBuilder().withPathAndRegion(path_model, None).withDetectors(detectors).build()
    name_for_queue = axis_name + " scan"
    submit_scan(request, name=name_for_queue)


def run_step_scan(scannable, start_pos, end_pos, step_size, exposure_time=1.0, malcolm_block_name="xspress3"):
    """
        Run a 1-dimensional Malcolm step scan using a single axis and a detector.
        Parameters :
            scannable - scannable to be moved during scan
            start_pos - start position
            end_pos - end position
            step_size - step size
            exposure_time - 'time per point'
        Optional parameters :
            malcolm_block_name - human readable name of malcolm block to use ("xspress3", "excalibur" or "xspress3Excalibur"; default = "xspress3")
    """

    detector_name = malcolm_blocks[malcolm_block_name]
    
    print("Running scan using %s with %s detector (exposure time = %.2f sec)" % (scannable, detector_name, exposure_time))
    print("Scan start, stop, step : %.5f, %.5f, %.5f" % (start_pos, end_pos, step_size))

    # Get detector runnable device
    detector_device = getRunnableDeviceService().getRunnableDevice(detector_name)
    if detector_device is None:
        raise Exception("Could not find runnable device for detector called " + detector_name)
    
    # Set the exposure time on detector model
    detector_model = detector_device.getModel()
    detector_model.setExposureTime(exposure_time)
    detectors = {detector_model.getName(): detector_model}
    
    # Make step scan style model with single axis
    path_model = AxialStepModel(scannable.getName(), start_pos, end_pos, step_size)
    path_model.setContinuous(True)

    # Generate ScanRequest using the builder
    request = ScanRequestBuilder().withPathAndRegion(path_model, None).withDetectors(detectors).build()
        
    name_for_queue = scannable.getName() + " scan"
    # return request
    submit_scan(request, name=name_for_queue)


from org.eclipse.scanning.command.Services import getRunnableDeviceService
from org.eclipse.scanning.api.points.models import StaticModel, AxialStepModel, AxialArrayModel, CompoundModel, TwoAxisPointSingleModel,  AxialPointsModel, OneAxisPointRepeatedModel
from org.eclipse.scanning.sequencer import ScanRequestBuilder
from mapping_scan_commands import submit

malcolm_blocks = {"xspress3Excalibur":"BL18I-ML-SCAN-03", "excalibur":"BL18I-ML-SCAN-03", "xspress3":"BL18I-ML-SCAN-06"} 
malcolm_axes = ["t1x", "t1y", "t1z", "t1theta"]

def run_scan_request(scan_request, scan_name="QXES") :
    print("Running scan")
    try :
        submit(scan_request, block=True, name=scan_name)
        print("Run complete")
    except Exception as e:
        print("Exception running scan",e)

def check_malcolm_names_ok(axis_name, block_name) :
    if axis_name not in malcolm_axes :
        print("Cannot run scan - axis name needs to be one of "+malcolm_axes)
        return False

    if block_name not in malcolm_blocks.keys():
        print("Cannot run scan - malcolm block_name needs to be one of "+malcolm_blocks.keys())
        return False

    return True


def run_continuous_scan(axis_name, start_pos, end_pos, step_size, exposure_time, malcolm_block_name="xspress3", continuous_scan = True):
    """
        Run a 1-dimensional continuous Malcolm scan using a single axis (t1x, t1y or t1z) and a detector.
        Parameters :
            axis_name = name of axis to scan (t1x, t1y or t1z)
            start_pos - start position
            end_pos - end position
            step_size - step size
            exposure_time - 'time per point'
        Optional parameters :
            malcolm_block_name - human readable name of malcolm block to use ("xspress3", "excalibur" or "xspress3Excalibur"; default = "xspress3")
            continuous_scan - whether to scan continuously (default = True)
        
    """
    if not check_malcolm_names_ok(axis_name, malcolm_block_name) :
        return

    detector_name = malcolm_blocks[malcolm_block_name]
    
    print("Running scan using %s with %s detector (exposure time = %.2f sec)"%(axis_name, detector_name, exposure_time))
    print("Scan start, stop, step : %.5f, %.5f, %.5f"%(start_pos, end_pos, step_size))

    # Get detector runnable device
    detector_device = getRunnableDeviceService().getRunnableDevice(detector_name)
    if detector_device is None :
        raise Exception("Could not find runnable device for detector called "+detector_name)
    
    # Set the exposure time on detector model
    detector_model = detector_device.getModel()
    detector_model.setExposureTime(exposure_time)
    detectors = {detector_model.getName() : detector_model}
    
    # Make step scan style model with single axis
    path_model = AxialStepModel(axis_name, start_pos, end_pos, step_size)
    path_model.setContinuous(continuous_scan)
    
    # Generate ScanRequest using the builder
    request = ScanRequestBuilder().withPathAndRegion(path_model, None).withDetectors(detectors).build()
    name_for_queue = axis_name+" scan"
    run_scan_request(request, scan_name=name_for_queue)
    

from gda.util.osgi import OsgiJythonHelper
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService

def to_json(scan_request) :
    marshaller_service = OsgiJythonHelper.getService(IMarshallerService)
    return marshaller_service.marshal(scan_request)
    
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
    
    print("Running scan using %s with %s detector (exposure time = %.2f sec)"%(scannable, detector_name, exposure_time))
    print("Scan start, stop, step : %.5f, %.5f, %.5f"%(start_pos, end_pos, step_size))

    # Get detector runnable device
    detector_device = getRunnableDeviceService().getRunnableDevice(detector_name)
    if detector_device is None :
        raise Exception("Could not find runnable device for detector called "+detector_name)
    
    # Set the exposure time on detector model
    detector_model = detector_device.getModel()
    detector_model.setExposureTime(exposure_time)
    detectors = {detector_model.getName() : detector_model}
    
    # Make step scan style model with single axis
    path_model = AxialStepModel(scannable.getName(), start_pos, end_pos, step_size)
    path_model.setContinuous(True)

    # Generate ScanRequest using the builder
    request = ScanRequestBuilder().withPathAndRegion(path_model, None).withDetectors(detectors).build()
        
    name_for_queue = scannable.getName()+" scan"
    # return request
    run_scan_request(request, scan_name=name_for_queue)
    


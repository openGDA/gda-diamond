import sys
from mapping_scan_commands import submit
from org.eclipse.scanning.api.points.models import AxialStepModel, AxialMultiStepModel #@Unresolvedimport

def run_xanes_scan_request(scanRequest, xanesEdgeParams):
    try:
        run_scan_request(scanRequest, xanesEdgeParams)
    except (KeyboardInterrupt):
        print("XANES scan interrupted by user")
    except:
        print("XANES scan terminated abnormally: {}".format(sys.exc_info()[0]))

def run_scan_request(scanRequest, xanesEdgeParams):
    print("Running XANES scan")
    print("scanRequest = {}".format(scanRequest))
    print("xanesEdgeParams = {}".format(xanesEdgeParams))

    compound_model = scanRequest.getCompoundModel()
    print("Original compound model: {}".format(compound_model))

    models = compound_model.getModels()

    # Extract step model(s) for dcm_enrg
    dcm_enrg_model = models.get(0)
    if isinstance(dcm_enrg_model, AxialStepModel):
        step_models = [dcm_enrg_model]
    elif isinstance(dcm_enrg_model, AxialMultiStepModel):
        step_models = dcm_enrg_model.getModels()

    # Extract bounding box for map
    map_box = models.get(1).getBoundingBox()
    print("Bounding box for map: {}".format(map_box))

    # Extract processing file name.
    processingRequest = scanRequest.getProcessingRequest()
    if processingRequest is not None:
        request = processingRequest.getRequest()
        if request is not None:
            print("Processing request: {}".format(request))

    # Set ROIs to null, as they will interfere with the bounding box of the map
    compound_model.setRegions(None)

    # Remove dcm_enrg model from ScanRequest, as we are going to control it ourselves
    models.pop(0)
    print("New compound model: {}".format(compound_model))
    print("Step models: {}".format(step_models))

    # Calculate total number of scans
    total_scans = 0;
    for step_model in step_models:
        dcm_start = step_model.getStart()
        dcm_stop = step_model.getStop()
        dcm_step = step_model.getStep()
        total_scans = total_scans +  int(round((dcm_stop - dcm_start) / dcm_step)) + 1
    print("Total scans: {}".format(total_scans))

    # Now loop round for each step model
    scan_number = 0
    for step_model in step_models:
        dcm_start = step_model.getStart()
        dcm_stop = step_model.getStop()
        dcm_step = step_model.getStep()

        print("Step model: dcm_start: {}, dcm_stop: {}, dcm_step: {}".format(dcm_start, dcm_stop, dcm_step))

        # Simulate drift correction by changing start points for each axis
        x_axis_start = map_box.getxAxisStart()
        y_axis_start = map_box.getyAxisStart()

        # Submit scans for this start/step/step combination
        dcm_value = dcm_start
        while dcm_value <= (dcm_stop + 0.00000001): # allow for inaccuracies in floating-point comparisons
            map_box.setxAxisStart(x_axis_start)
            map_box.setyAxisStart(y_axis_start)

            scan_number = scan_number + 1
            scan_name = "XANES scan {} of {}".format(scan_number, total_scans)

            print("{}, dcm_value: {}, x_axis_start: {}, y_axis_start: {}".format(scan_name, dcm_value, x_axis_start, y_axis_start))
            #print("scan request: {}".format(scanRequest))

            dcm_enrg.moveTo(dcm_value)
            submit(scanRequest, block=True, name=scan_name)

            # Set up for next scan
            dcm_value = dcm_value + dcm_step
            x_axis_start = x_axis_start + 0.002
            y_axis_start = y_axis_start + 0.001

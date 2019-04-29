# Scripts for running XANES scanning in dummy mode

def run_xanes_scan_request(scanRequest, xanesEdgeParams):
    print("Running XANES scan")
    print("scanRequest = {0}".format(scanRequest))
    print("xanesEdgeParams = {0}".format(xanesEdgeParams))

    models = scanRequest.getCompoundModel().getModels()
    if not models.size() > 1:
        print("Only one scan model found: have you forgotten to define dcm_enrg as an outer scannable?")
        return;

    dcm_enrg_model = scanRequest.getCompoundModel().getModels().get(0)
    print("Model for dcm_enrg: {0}".format(dcm_enrg_model))
    dcm_start = dcm_enrg_model.getStart()
    dcm_stop = dcm_enrg_model.getStop()
    dcm_step = dcm_enrg_model.getStep()
    num_scans = int(round((dcm_stop - dcm_start) / dcm_step)) + 1

    map_box = scanRequest.getCompoundModel().getModels().get(1).getBoundingBox()
    print("Bounding box for map: {0}".format(map_box))
    fast_axis_start = map_box.getFastAxisStart()
    slow_axis_start = map_box.getSlowAxisStart()

    # Set ROIs to null, as they will interfere with the bounding box of the map
    scanRequest.getCompoundModel().setRegions(None)

    # Submit all scans
    for i in range(1, num_scans + 1):
        map_box = scanRequest.getCompoundModel().getModels().get(1).getBoundingBox()
        map_box.setFastAxisStart(fast_axis_start)
        map_box.setSlowAxisStart(slow_axis_start)

        dcm_enrg_model.setStart(dcm_start)
        dcm_enrg_model.setStop(dcm_start)

        scan_name = "XANES scan {0} of {1}".format(i, num_scans)
        print("{0} = {1}".format(scan_name, scanRequest))
        submit(scanRequest, block=False, name=scan_name)

        # Set up for next scan
        dcm_start = dcm_start + dcm_step
        fast_axis_start = fast_axis_start + 0.002
        slow_axis_start = slow_axis_start + 0.001

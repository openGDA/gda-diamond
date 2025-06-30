import os
import scisoftpy as dnp

from gda.jython import InterfaceProvider #@Unresolvedimport #@Unusedimport

from org.eclipse.scanning.api.points.models import AxialStepModel, AxialArrayModel, AxialMultiStepModel #@Unresolvedimport
from org.eclipse.scanning.api.points.models import TwoAxisGridPointsModel, TwoAxisGridStepModel #@Unresolvedimport
from org.eclipse.scanning.api.scan.models import ScanMetadata #@Unresolvedimport

from uk.ac.diamond.osgi.services import ServiceProvider
from org.eclipse.scanning.api.device import IRunnableDeviceService


def get_energies(energy_model):
    """
    Converts the outer energy scan model to a list of energies
    """
    energies = []
    if isinstance(energy_model,AxialMultiStepModel):
        print("Multistep model")
        energy_models = energy_model.getStepModels()
        for ee in energy_models:
            start = ee.getStart()
            stop  = ee.getStop()
            step  = ee.getStep()
            step_enrgs = dnp.arange(start,stop,step)
            #print("sub_region",start,stop,step)
            energies = dnp.concatenate((energies,step_enrgs))
    elif isinstance(energy_model,AxialStepModel):
        start = energy_model.getStart()
        stop  = energy_model.getStop()
        step  = energy_model.getStep()
        step_enrgs = dnp.arange(start,stop,step)
        energies = dnp.concatenate((energies,step_enrgs))
    elif isinstance(energy_model,AxialArrayModel):
        step_enrgs = energy_model.getPositions()
        energies = dnp.concatenate((energies,step_enrgs))
    return energies

def get_y_dimensions(map_model):
    map_box = map_model.getBoundingBox()

    y_min = map_box.getyAxisStart()
    y_range = map_box.getyAxisLength()
    y_max = y_min + y_range

    if isinstance(map_model, TwoAxisGridPointsModel):
        y_step = y_range/map_model.getyAxisPoints()
    elif isinstance(map_model, TwoAxisGridStepModel):
        y_step = map_model.getyAxisStep()
    else:
        raise Exception('Scan path {} not supported'.format(type(map_model)))

    return y_min, y_max, y_range, y_step

def get_x_dimensions(map_model):
    map_box = map_model.getBoundingBox()

    x_min = map_box.getxAxisStart()
    x_range = map_box.getxAxisLength()
    x_max = x_min + x_range

    if isinstance(map_model, TwoAxisGridPointsModel):
        x_step = x_range/map_model.getxAxisPoints()
    elif isinstance(map_model, TwoAxisGridStepModel):
        x_step = map_model.getxAxisStep()
    else:
        raise Exception('Scan path {} not supported'.format(type(map_model)))

    return x_min, x_max, x_range, x_step

def get_models(scanRequest):
    compound_model = scanRequest.getCompoundModel()

    models = compound_model.getModels()
    if not models.size() > 1:
        print("Only one scan model found: have you forgotten to define energy as an outer scannable?")
        return;

    dcm_enrg_model = models.get(0)
    print(dcm_enrg_model)

    models.pop(0)
    map_model = models.get(0)

    return dcm_enrg_model, map_model

def model_to_step(scan_model):
    """
    Extracts the step size from the stage scan model
    """
    map_box = scan_model.getBoundingBox()
    box_slow_length = map_box.getyAxisLength()
    box_fast_length = map_box.getxAxisLength()
    slow_step=0.0
    fast_step=0.0
    if isinstance(scan_model,TwoAxisGridStepModel):
        slow_step = scan_model.getyAxisStep()
        fast_step = scan_model.getxAxisStep()
    elif isinstance(scan_model,TwoAxisGridPointsModel):
        slow_points = scan_model.getyAxisPoints()
        fast_points = scan_model.getxAxisPoints()
        slow_step   = box_slow_length/slow_points
        fast_step   = box_fast_length/fast_points
    return slow_step,fast_step


def get_detector_model(name, exposure=0.1, **kwargs):
    
    runnableDeviceService = ServiceProvider.getService(IRunnableDeviceService)
    detector = runnableDeviceService.getRunnableDevice(name)
    assert detector is not None, "Detector '" + name + "' not found"

    model = detector.getModel()
    if exposure > 0:
        model.setExposureTime(exposure)

    for key, value in kwargs.iteritems():
        setattr(model, key, value)

    return (name, model)

def get_line_to_track(xanesEdgeParams):
    lineToTrackParam = xanesEdgeParams.getLineToTrack()
    if lineToTrackParam is not None:
        lineToTrack = lineToTrackParam.getElement() + "-" + lineToTrackParam.getLine()
        print("Line to track = {}".format(lineToTrack))
    else:
        lineToTrack = None

    return lineToTrack

def get_edge_to_energy(xanesEdgeParams):
    edgeToEnergyParam = xanesEdgeParams.getEdgeToEnergy()
    if edgeToEnergyParam is not None:
        edgeElement = edgeToEnergyParam.getEdge()
        # append 'a' as only the alpha line is used
        if not edgeElement.endswith('a'):
            edgeElement = edgeElement + 'a'
        print("Edge element = {} ".format(edgeElement))
    else:
        edgeElement = None

    return edgeElement

def get_scan_name(index, num_scans, lineToTrack):
    if lineToTrack:
        scan_name = "XANES_scan_{0}_of_{1}_using_{2}_to_track".format(index+1, num_scans, lineToTrack)
    else:
        scan_name = "XANES_scan_{0}_of_{1}_no_tracking".format(index+1, num_scans)

    return scan_name

def get_visit_path():
    visitPath = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    visitPath, tail = os.path.split(visitPath)
    print("Visit path: {}".format(visitPath))

    return visitPath

def calculate_number_points(scan_model):
    if isinstance(scan_model, TwoAxisGridPointsModel):
        return scan_model.getxAxisPoints() * scan_model.getyAxisPoints();
    elif isinstance(scan_model, TwoAxisGridStepModel):
        bounding_box = scan_model.getBoundingBox()
        x_points = bounding_box.getxAxisLength()/scan_model.getxAxisStep() + 1
        y_points = bounding_box.getyAxisLength()/scan_model.getyAxisStep() + 1;
        return (x_points * y_points + 1)

def create_scan_metadata(sparse_pos_y, sparse_ind_y):
    smetadata = ScanMetadata()
    smetadata.setType(ScanMetadata.MetadataType.ENTRY)
    smetadata.addField("sparse_y_positions", sparse_pos_y)
    smetadata.addField("sparse_y_index", sparse_ind_y)
    return smetadata


def create_scan_metadata_cur(sparse_pos_y, sparse_ind_y,sparse_pos_e, sparse_ind_e):
    smetadata = ScanMetadata()
    smetadata.setType(ScanMetadata.MetadataType.ENTRY)
    smetadata.addField("sparse_y_positions", sparse_pos_y)
    smetadata.addField("sparse_y_index", sparse_ind_y)
    smetadata.addField("sparse_energy_positions", sparse_pos_e)
    smetadata.addField("sparse_energy_index", sparse_ind_e)
    return smetadata


import scisoftpy as dnp
from org.eclipse.scanning.api.points.models import AxialStepModel, AxialArrayModel, AxialMultiStepModel #@Unresolvedimport
    
    
"""
Get energy points to scan
"""
def get_energies(energy_model):
    energies = []
    if isinstance(energy_model,AxialMultiStepModel):
        print("Multistep model")
        energy_models = energy_model.getStepModels()
        for ee in energy_models:
            start = ee.getStart()
            stop  = ee.getStop()
            step  = ee.getStep()
            step_energies = dnp.arange(start,stop,step)
            print("sub_region",start,stop,step)
            energies = dnp.concatenate((energies,step_energies))
    elif isinstance(energy_model,AxialStepModel):
        start = energy_model.getStart()
        stop  = energy_model.getStop()
        step  = energy_model.getStep()
        step_energies = dnp.arange(start,stop,step)
        energies = dnp.concatenate((energies,step_energies))
    elif isinstance(energy_model,AxialArrayModel):
        step_energies = energy_model.getPositions()
        energies = dnp.concatenate((energies,step_energies))
    return energies

"""
Get the y dimensions of the bounding box
"""
def get_y_dimensions(map_model):
    map_box = map_model.getBoundingBox()
    
    y_min = map_box.getyAxisStart()
    y_range = map_box.getyAxisLength()
    y_max = y_min + y_range
    y_step = y_range/map_model.getyAxisPoints()
    
    return y_min, y_max, y_range, y_step

"""
Get the x dimensions of the bounding box
"""
def get_x_dimensions(map_model):
    map_box = map_model.getBoundingBox()
    
    x_min = map_box.getxAxisStart()
    x_range = map_box.getxAxisLength()
    x_max = x_min + x_range
    x_step = x_range/map_model.getxAxisPoints()
    
    return x_min, x_max, x_range, x_step

"""
Get the energy model and the map model
"""
def get_models(scanRequest):
    compound_model = scanRequest.getCompoundModel()
    print("Original compound model: {}".format(compound_model))
    
    models = compound_model.getModels()
    if not models.size() > 1:
        print("Only one scan model found: have you forgotten to define dcm_enrg as an outer scannable?")
        return;
    
    dcm_enrg_model = models.get(0)
    
    models.pop(0)
    map_model = models.get(0)
    
    return dcm_enrg_model, map_model


# TODO
def set_amplifier_gains():
    current_gain1 = int(caget("BL14I-DI-BPM-03:IAMP1:MR").encode("ascii"))
    current_gain2 = int(caget("BL14I-DI-BPM-03:IAMP2:MR").encode("ascii"))
    current_gain1 = range_dict[current_gain1]
    current_gain2 = range_dict[current_gain2]
    current_gain = max(current_gain1,current_gain2)
    print("Amplifier Gains",current_gain1,current_gain2,current_gain)
    sleep(2)
    caput("BL14I-DI-BPM-03:IAMP1:SETRANGE",current_gain)
    caput("BL14I-DI-BPM-03:IAMP2:SETRANGE",current_gain)
    sleep(2)
import java
import traceback
import sys
import scisoftpy as dnp
from mapping_scan_commands import submit
from org.eclipse.scanning.api.points.models import AxialStepModel, AxialArrayModel,AxialMultiStepModel #@Unresolvedimport

from org.slf4j import LoggerFactory

xanes_utils_logger = LoggerFactory.getLogger("xanes_utils")

def submit_scan(scanRequest, block=True, name="", raise_on_failure = False) :
    """
        Submit scan and handle any exceptions :
        * Interrupted exception is raised
        * Other exception types are logged, and raised if raise_on_failure = True,
        
        Function return True if scan ran successfully, False otherwise
    """
    try :
        submit(scanRequest, block=block, name=name)
        return True
    except java.lang.InterruptedException as e :
        raise e
    except Exception as e:
        msg="XANES scan terminated abnormally: {}".format(sys.exc_info()[0])
        xanes_utils_logger.warn("{} {}",msg, traceback.format_exc())

        if raise_on_failure :
            raise e
        
        print(msg)
        print(traceback.format_exc()) 
        return False

def get_models(scanRequest):
    """
        Get the energy model and the map model
    """
    compound_model = scanRequest.getCompoundModel()
    print("Original compound model: {}".format(compound_model))
    
    models = compound_model.getModels()
    if models.size() <= 1:
        print("Only one scan model found: have you forgotten to define dcm_enrg as an outer scannable?")
        return;
    
    dcm_enrg_model = models.get(0)
    
    models.pop(0)
    map_model = models.get(0)
    
    return dcm_enrg_model, map_model

def generate_range(step_model) :
    vals=[]
    vals.extend(dnp.arange(step_model.getStart(), step_model.getStop(), step_model.getStep()))
    return vals;

def get_energies(energy_model):
    """
        Make a list of energy points to be scan scanned
    """
    energies = []
    if isinstance(energy_model,AxialMultiStepModel):
        print("Multistep model")
        energy_models = energy_model.getStepModels()
        for ee in energy_models:
            step_energies = generate_range(ee)
            print("sub_region",ee.getStart(), ee.getStop(), ee.getStep())
            energies.extend(step_energies)
    elif isinstance(energy_model,AxialStepModel):
        step_energies = generate_range(energy_model)
        energies.extend(step_energies)
    elif isinstance(energy_model,AxialArrayModel):
        step_energies = energy_model.getPositions()
        energies.extend(step_energies)
    return energies

def get_y_dimensions(map_model):
    """
        Get the y dimensions of the bounding box
    """
    map_box = map_model.getBoundingBox()
    
    y_min = map_box.getyAxisStart()
    y_range = map_box.getyAxisLength()
    y_max = y_min + y_range
    y_step = y_range/map_model.getyAxisPoints()
    
    return y_min, y_max, y_range, y_step

def get_x_dimensions(map_model):
    """
        Get the x dimensions of the bounding box
    """
    map_box = map_model.getBoundingBox()
    
    x_min = map_box.getxAxisStart()
    x_range = map_box.getxAxisLength()
    x_max = x_min + x_range
    x_step = x_range/map_model.getxAxisPoints()
    
    return x_min, x_max, x_range, x_step

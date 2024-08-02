import sys
import traceback
from mapping_scan_commands import submit
from org.eclipse.scanning.api.points.models import AxialStepModel, AxialMultiStepModel #@Unresolvedimport
import scisoftpy as dnp

def run_xanes_scan_request(scanRequest, xanesEdgeParams):
    try:
        run_scan_request(scanRequest, xanesEdgeParams)
    except (KeyboardInterrupt):
        print("XANES scan interrupted by user")
    except:
        print("XANES scan terminated abnormally: {}".format(sys.exc_info()[0]))
        print(traceback.format_exc())

from gda.jython import JythonServerFacade, ScriptBase
def wait_if_paused() :
    if ScriptBase.isPaused() == True :
        print "Waiting while paused..."
        ScriptBase.checkForPauses()
        print "Continuing"
        
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

    print("Energy model scannable : "+dcm_enrg_model.getName())
    # energy_scannable = Finder.find(dcm_enrg_model.getName())
    energy_scannable = energy_nogap

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

    # Calculate all the energy points for the scan  
    print("Appending energy points : ")
    all_energies = []
    for step_model in step_models:
        params = [step_model.getStart(), step_model.getStop(), step_model.getStep()]
        print("dcm_start: {}, dcm_stop: {}, dcm_step: {}".format(params[0], params[1], params[2]))
        all_energies.extend(dnp.arange(params[0], params[1], params[2]))

    print("Total scans: {}".format(len(all_energies)))

    # Now loop round for each step model
    scan_number = 1

    for energy in all_energies :
        scan_name = "XANES scan {} of {}. Energy = {}".format(scan_number, len(all_energies), energy)
        print(scan_name)
        energy_scannable.moveTo(energy*1000)
        submit(scanRequest, block=True, name=scan_name)
        scan_number += 1


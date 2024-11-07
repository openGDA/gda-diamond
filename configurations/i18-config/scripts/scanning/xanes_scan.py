import sys
import traceback
from mapping_scan_commands import submit
from org.eclipse.scanning.api.points.models import AxialStepModel, AxialMultiStepModel #@Unresolvedimport
from org.eclipse.scanning.api.scan.models import ScanMetadata #@Unresolvedimport
from org.eclipse.scanning.api.points import MapPosition

import scisoftpy as dnp
from org.slf4j import LoggerFactory

xanes_logger = LoggerFactory.getLogger("xanes_scan")

def run_xanes_scan_request(scanRequest, xanesEdgeParams):
    try:
        run_scan_request(scanRequest, xanesEdgeParams)
    except:
        msg="XANES scan script terminated abnormally: {}".format(sys.exc_info()[0])
        xanes_logger.error(msg, traceback.format_exc())
        print(msg)
        print(traceback.format_exc())
        
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
        xanes_logger.warn("{} {}",msg, traceback.format_exc())

        if raise_on_failure :
            raise e
        
        print(msg)
        print(traceback.format_exc()) 
        return False
    
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

    element_edge_string = xanesEdgeParams.getEdgeToEnergy().getEdge()

    models = compound_model.getModels()

    # Extract step model(s) for dcm_enrg
    dcm_enrg_model = models.get(0)
    print("Energy model : %s"%(type(dcm_enrg_model)))
    if isinstance(dcm_enrg_model, AxialStepModel):
        step_models = [dcm_enrg_model]
    elif isinstance(dcm_enrg_model, AxialMultiStepModel):
        step_models = dcm_enrg_model.getModels()

    print("Energy model scannable : "+dcm_enrg_model.getName())
    energy_scannable = Finder.find(dcm_enrg_model.getName())

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

    all_nexus_file_names = []

    # Now loop round for each step model
    scan_number = 1

    for energy in all_energies :
        scan_name = "XANES scan {} of {}. Energy = {}".format(scan_number, len(all_energies), energy)

        # set the scan metadata to include list of all nexus files in the stack of scans run so far
        smetadata = ScanMetadata()
        smetadata.setType(ScanMetadata.MetadataType.ENTRY)
        smetadata.addField("all_nexus_file_names", "\n".join(all_nexus_file_names))
        smetadata.addField("edge_name", element_edge_string)
        scanRequest.setScanMetadata([smetadata])
        
        # Update the beamline configuration to move the mono to the scan energy
        position_map = scanRequest.getStartPosition()
        if position_map is None :
            position_map = MapPosition()
        position_map.put(energy_scannable.getName(), energy*1000)
        scanRequest.setStartPosition(position_map)
        
        # Add processing to scan request to reconstruct the map after final energy has been collected
        if energy == all_energies[-1] :  
            print("Adding processing to reconstruct the map after final energy point")
            scanRequest.getProcessingRequest().getRequest().put("xanes-map-stack", [])
        
        print(scan_name)        
        
        # Run scan and attempt a 2nd time if if goes wrong. Catch exceptions so subsequent scans are run.
        result = submit_scan(scanRequest, block=True, name=scan_name, raise_on_failure=False)
        if result == False :
            submit_scan(scanRequest, block=True, name=scan_name, raise_on_failure=False)
            
        print("current energy : {}".format(energy_scannable.getPosition()))
        
        all_nexus_file_names.append(filename_listener.file_name)
        
        scan_number += 1


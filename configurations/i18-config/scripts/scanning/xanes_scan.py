import sys
import traceback
from org.eclipse.scanning.api.points.models import AxialStepModel, AxialMultiStepModel #@Unresolvedimport
from org.eclipse.scanning.api.scan.models import ScanMetadata #@Unresolvedimport
from org.eclipse.scanning.api.points import MapPosition
from gda.data import NumTracker
import scisoftpy as dnp
from org.slf4j import LoggerFactory

from scanning.xanes_utils import submit_scan

xanes_logger = LoggerFactory.getLogger("xanes_scan")



def run_xanes_scan_request(scanRequest, xanesEdgeParams, *args, **kwargs):
    try:
        run_scan_request(scanRequest, xanesEdgeParams, *args, **kwargs)
    except:
        stacktrace=traceback.format_exc()
        msg="XANES scan script terminated abnormally: {} {}".format(sys.exc_info()[0], stacktrace)
        xanes_logger.error(msg, stacktrace) # , traceback.format_exc())
        print(msg)
    
from gda.jython import JythonServerFacade, ScriptBase, InterfaceProvider

def wait_if_paused() :
    if ScriptBase.isPaused() == True :
        print "Waiting while paused..."
        ScriptBase.checkForPauses()
        print "Continuing"
        
def run_scan_request(scanRequest, xanesEdgeParams, block_on_submit=True, num_retries=0) :
    print("Running XANES scan")
    print("scanRequest = {}".format(scanRequest))
    print("xanesEdgeParams = {}".format(xanesEdgeParams))

    sparse_parameters = xanesEdgeParams.getSparseParameters()
    print("Sparse parameters : {}".format(sparse_parameters))
    
    compound_model = scanRequest.getCompoundModel()
    print("Original compound model: {}".format(compound_model))

    element_edge_string = "unknown" if xanesEdgeParams.getEdgeToEnergy() is None \
        else xanesEdgeParams.getEdgeToEnergy().getEdge()
        
    #element_edge_string = xanesEdgeParams.getEdgeToEnergy().getEdge()

    models = compound_model.getModels()

    # Extract step model(s) for dcm_enrg
    dcm_enrg_model = models.get(0)
    print("Energy model : %s"%(type(dcm_enrg_model)))
    if isinstance(dcm_enrg_model, AxialStepModel):
        step_models = [dcm_enrg_model]
    elif isinstance(dcm_enrg_model, AxialMultiStepModel):
        step_models = dcm_enrg_model.getModels()

    energy_scn_name = dcm_enrg_model.getName()
    if not beam_available() :
        print("Beam not avalable - using energy_nogap for energy scannable")
        energy_scn_name = "energy_nogap"

    print("Energy model scannable : "+energy_scn_name)
    energy_scannable = Finder.find(energy_scn_name)

    #Conversion factor from model energy units to eV needed for the DCM
    energy_units = LocalProperties.get("gda.scan.energy.defaultUnits", "kev")
    energy_multiplier = 1.0 if energy_units.lower() == "ev" else 1000.0
    
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
    
    # Use the NumTracker to get the number of the next Nexus file to be created
    num_tracker = NumTracker()
    nexus_scan_number = num_tracker.getCurrentFileNumber() + 1
    num_tracker.incrementNumber() # increment it
    
    # Setup Nexus file path format 
    beamline_name = LocalProperties.get("gda.beamline.name")
    visit_folder = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    nexus_name_format = visit_folder+"/"+str(beamline_name)+"-%d_%03d.nxs"
    print("Nexus file path format : {}".format(nexus_name_format))
    print("Add all scans to queue : "+str(not block_on_submit))
    
    for index, energy in enumerate(all_energies) :
        scan_name = "XANES scan {} of {}. Energy = {}".format(index+1, len(all_energies), energy)

        # set the scan metadata to include list of all nexus files in the stack of scans run so far
        smetadata = ScanMetadata()
        smetadata.setType(ScanMetadata.MetadataType.ENTRY)
        smetadata.addField("all_nexus_file_names", "\n".join(all_nexus_file_names))
        smetadata.addField("edge_name", element_edge_string)
        scanRequest.setScanMetadata([smetadata])
        
        # Set full path to nexus file on scanRequest object
        file_path = nexus_name_format%(nexus_scan_number, index)
        scanRequest.setFilePath(file_path)
        
        # Update the beamline configuration to move the mono to the scan energy
        position_map = scanRequest.getStartPosition()
        if position_map is None :
            position_map = MapPosition()
        position_map.put(energy_scannable.getName(), energy*energy_multiplier)
        scanRequest.setStartPosition(position_map)
        
        # Add processing to scan request to reconstruct the map after final energy has been collected
        if energy == all_energies[-1] :  
            print("Adding processing to reconstruct the map after final energy point")
            scanRequest.getProcessingRequest().getRequest().put("xanes-map-stack", [])
        
        print(scan_name)        
        print(file_path)
        
        # Run scan and attempt a 2nd time if if goes wrong. Catch exceptions so subsequent scans are run.
        result = submit_scan(scanRequest, block=block_on_submit, name=scan_name, raise_on_failure=False)
        if result == False and num_retries > 0 :
            submit_scan(scanRequest, block=block_on_submit, name=scan_name, raise_on_failure=False)
        
        # Add the scan just run/submitted to the list of all nexus file names
        all_nexus_file_names.append(file_path)

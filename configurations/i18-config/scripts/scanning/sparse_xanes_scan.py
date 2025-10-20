from org.eclipse.scanning.sequencer import ScanRequestBuilder #@Unresolvedimport
from org.eclipse.scanning.api.scan.models import ScanMetadata #@Unresolvedimport
from org.eclipse.scanning.api.points.models import CompoundModel #@Unresolvedimport
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI #@Unresolvedimport
from org.eclipse.scanning.api.points.models import AxialStepModel, AxialArrayModel
from org.eclipse.scanning.api.points import MapPosition
from gda.data import NumTracker

from scanning.xanes_utils import submit_scan, get_models, get_energies, get_x_dimensions, get_y_dimensions

import scisoftpy as dnp

def run_sparse_xanes_scan_request(scanRequest, xanesEdgeParams, block_on_submit=True):

    sparse_parameters = xanesEdgeParams.getSparseParameters()
    rows_percentage = 1.0
    if sparse_parameters is not None:
        rows_percentage = float(sparse_parameters.getPercentage())/100

    energy_model, map_model = get_models(scanRequest)
    energies = get_energies(energy_model)
    num_scans = len(energies)
    
    element_edge_string = xanesEdgeParams.getEdgeToEnergy().getEdge()
    print("Element and edge : {}".format(element_edge_string))
    print("Number of scans: {}".format(num_scans))
    print("Energies: {}".format(energies))

    energy_scn_name = energy_model.getName()
    if not beam_available() :
        print("Beam not avalable - using energy_nogap for energy scannable")
        energy_scn_name = "energy_nogap"
        
    print("Energy axis : %s"%(energy_scn_name))
    energy_scannable = Finder.find(energy_scn_name)

    #Conversion factor from model energy units to eV needed for the DCM
    energy_units = LocalProperties.get("gda.scan.energy.defaultUnits", "kev")
    energy_multiplier = 1.0 if energy_units.lower() == "ev" else 1000.0

    x_axis_name = map_model.getxAxisName()
    y_axis_name = map_model.getyAxisName()
    is_alternating = map_model.isAlternating()

    print("X axis name: %s, Y axis name : %s , alternating : %s"%(x_axis_name, y_axis_name, is_alternating))

    y_min, y_max, y_range, y_step = get_y_dimensions(map_model)
    x_min, x_max, x_range, x_step = get_x_dimensions(map_model)
    print("y_min {}, y_max {}, y_range {}, y_step {}".format(y_min, y_max, y_range, y_step))  
    print("x_min {}, x_max {}, x_range {}, x_step {}".format(x_min, x_max, x_range, x_step))  

    y_positions = dnp.arange(y_min, y_max, y_step)
    num_y_positions = len(y_positions)

    all_nexus_file_names = []
    
    # Use the NumTracker to get the number of the next Nexus file to be created
    num_tracker = NumTracker()
    nexus_scan_number = num_tracker.getCurrentFileNumber() + 1
    num_tracker.incrementNumber() #
    
    # Setup Nexus file path format 
    beamline_name = LocalProperties.get("gda.beamline.name")
    visit_folder = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    nexus_name_format = visit_folder+"/"+str(beamline_name)+"-%d_%03d.nxs"
    
    for idx, energy in enumerate(energies):
        
        scan_name = "Sparse XANES scan {} of {}. Energy = {}".format(idx+1, num_scans, energy)
        
        
        # last scan will be all positions
        if idx < len(energies)-1:
            n_lines = int (rows_percentage*num_y_positions)#
            # print(n_lines, rows_percentage, num_y_positions)
            rand_y_index = []
            while len(rand_y_index) < n_lines:
                r=dnp.random.randint(0, num_y_positions)
                if r not in rand_y_index:
                    rand_y_index.append(r)
            rand_y_index = dnp.sort(rand_y_index)
        else :
            rand_y_index = range(num_y_positions)
        
        # Generate positions from indices
        rand_y_positions = [y_positions[i] for i in rand_y_index]

        # y model    
        y_axis_model = AxialArrayModel(y_axis_name, rand_y_positions) 
        y_axis_model.setContinuous(False)
        
        # x model
        x_axis_model = AxialStepModel(x_axis_name, x_min, x_max, x_step)
        x_axis_model.setContinuous(True)
        x_axis_model.setAlternating(is_alternating)
        # create the model
        cm = CompoundModel([y_axis_model,x_axis_model])
        
        # create the region
        region = RectangularROI(y_min-y_step,x_min-x_step,x_range+x_step,y_range+y_step,0.0)
        
        # add sparse positions to metadata
        sparse_pos_y_str = ''.join(str(x)+" " for x in rand_y_positions)
        sparse_ind_y_str = ''.join(str(x)+" " for x in rand_y_index)
        smetadata = ScanMetadata()
        smetadata.setType(ScanMetadata.MetadataType.ENTRY)
        smetadata.addField("sparse_y_positions", sparse_pos_y_str)
        smetadata.addField("sparse_y_index", sparse_ind_y_str)
        smetadata.addField("all_nexus_file_names", "\n".join(all_nexus_file_names))
        smetadata.addField("edge_name", element_edge_string)
        
        print("%d sparse Y positions"%(len(rand_y_positions)))
        print("Positions : %s"%(sparse_pos_y_str))
        print("Indices   : %s"%(sparse_ind_y_str))
        
        # position of the dcm for this energy
        dcm_energy_position = MapPosition({energy_scannable.getName():energy*energy_multiplier})
        
        # full path to the nexus file
        file_path = nexus_name_format%(nexus_scan_number, idx)        
        
        # create request
        request = ScanRequestBuilder() \
                  .withPathAndRegion(cm, None) \
                  .withDetectors(scanRequest.getDetectors()) \
                  .ignorePreprocess(True) \
                  .withScanMetadata([smetadata]) \
                  .withProcessingRequest(scanRequest.getProcessingRequest()) \
                  .withStartPosition(dcm_energy_position) \
                  .withFilePath(file_path) \
                  .build()
                  
        # Add processing to scan request to reconstruct the map after final energy has been collected
        if energy == energies[-1] :
            print("Adding processing to reconstruct the map after final energy point")
            request.getProcessingRequest().getRequest().put("xanes-map-stack", [])
            
        
        print(scan_name)
        print(file_path)

        result = submit_scan(request, block=block_on_submit, name=scan_name, raise_on_failure = False)
        if result == False :
            submit_scan(request, block=block_on_submit, name=scan_name, raise_on_failure = False)
            
        # Add the scan just run/submitted to the list of all nexus file names
        all_nexus_file_names.append(file_path)


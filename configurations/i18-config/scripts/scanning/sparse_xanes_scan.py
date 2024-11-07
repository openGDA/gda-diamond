from org.eclipse.scanning.sequencer import ScanRequestBuilder #@Unresolvedimport
from org.eclipse.scanning.api.scan.models import ScanMetadata #@Unresolvedimport
from org.eclipse.scanning.api.points.models import CompoundModel #@Unresolvedimport
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI #@Unresolvedimport
from org.eclipse.scanning.api.points.models import AxialStepModel, AxialArrayModel

from scanning.xanes_utils import submit_scan, get_models, get_energies, get_x_dimensions, get_y_dimensions

import scisoftpy as dnp

def run_sparse_xanes_scan_request(scanRequest, xanesEdgeParams):

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

    print("Energy axis : %s"%(energy_model.getName()))
    energy_scannable = Finder.find(energy_model.getName())    

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
    
    for idx, energy in enumerate(energies):
        
        print("\nPreparing Sparse XANES scan %d of %d"%(idx+1, num_scans))
        
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
        
        # create request
        request = ScanRequestBuilder() \
                  .withPathAndRegion(cm, None) \
                  .withDetectors(scanRequest.getDetectors()) \
                  .ignorePreprocess(True) \
                  .withScanMetadata([smetadata]) \
                  .withProcessingRequest(scanRequest.getProcessingRequest()) \
                  .build()
                  
        # Add processing to scan request to reconstruct the map after final energy has been collected
        if energy == energies[-1] :
            print("Adding processing to reconstruct the map after final energy point")
            request.getProcessingRequest().getRequest().put("xanes-map-stack", [])

        # Move the monochromator
        print("Moving %s to %.5f eV"%(energy_scannable.getName(), energy*1000))
        energy_scannable.moveTo(energy*1000)
        sleep(0.5)
        
        scan_name = "Sparse XANES_scan_{0}_of_{1}".format(idx+1, num_scans)
        print("Submitting %s "%(scan_name))

        result = submit_scan(request, block=True, name=scan_name, raise_on_failure = False)
        if result == False :
            submit_scan(request, block=True, name=scan_name, raise_on_failure = False)
            
        all_nexus_file_names.append(filename_listener.file_name)
        print("File path "+filename_listener.file_name)


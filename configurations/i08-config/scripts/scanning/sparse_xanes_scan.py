import os
import json
from time import sleep

import scisoftpy as dnp

# Num tracker imports
from gda.data import NumTracker  #@Unresolvedimport

# Java imports
from java.lang import Exception as JavaException  #@Unresolvedimport
from java.lang import InterruptedException  #@Unresolvedimport
from mapping_scan_commands import submit

# Dawn, Nexus and scanning imports
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI  #@Unresolvedimport
from org.eclipse.dawnsci.nexus import NexusNodeFactory  #@Unresolvedimport
from org.eclipse.scanning.sequencer import ScanRequestBuilder  #@Unresolvedimport
from org.eclipse.scanning.api.device import IScannableDeviceService  #@Unresolvedimport
from org.eclipse.scanning.api.scan.models import ScanMetadata  #@Unresolvedimport
from org.eclipse.scanning.api.points.models import (  #@Unresolvedimport
    AxialArrayModel,
    AxialStepModel,
    CompoundModel,
)
from uk.ac.diamond.daq.scanning import NXObjectScannable  #@Unresolvedimport
from uk.ac.diamond.osgi.services import ServiceProvider  #@Unresolvedimport

# Scripts imports
from scanning.xanes_utils import (
    create_scan_metadata,
    get_edge_to_energy,
    get_energies,
    get_models,
    get_visit_path,
    get_x_dimensions,
    get_y_dimensions,
)

#from gda.epics import CAClient

numtracker = NumTracker('tmp')

print("Setting up sparse xanes scan")

PROCESSING_REQUEST_NAME = "i08-xanes-sparse-stack"
SCANS_FOLDER_NAME = "sparse_xanes"
ENERGY_SCANNABLE = energyFocus

def run_sparse_xanes_scan_request(scanRequest, xanesEdgeParams):
    print(scanRequest)
    print("Xanes parameters: {}\n".format(xanesEdgeParams))

    # Validation for detector used
    valid_malcolm_detector_name = '-ML-SCAN-01'
    malcolm_detector_name = scanRequest.getDetectors().keys()[0]
    if (not malcolm_detector_name.endswith(valid_malcolm_detector_name)):
        print("Selected detector is not valid for this type of scan")
        return;
    
    # Get energy model from the ScanRequest
    energy_model, map_model = get_models(scanRequest)
    energies = get_energies(energy_model)
    min_energy = min(energies)
    max_energy = max(energies)
    print("\nEnergy Range: Min = {:.4f}, Max = {:.4f}".format(min_energy, max_energy))
    print("Energies: {}".format(energies))
    num_scans = len(energies)
    print("Total number of scans: {}\n".format(num_scans))

    # Get the 2D dimensions
    y_min, y_max, y_range, y_step = get_y_dimensions(map_model)
    x_min, x_max, x_range, x_step = get_x_dimensions(map_model)
    print("Region: ")
    print("Y-axis: min = {:.5f}, max = {:.5f}, range = {:.5f}, step = {:.5f}".format(y_min, y_max, y_range, y_step))
    print("X-axis: min = {:.5f}, max = {:.5f}, range = {:.5f}, step = {:.5f}\n".format(x_min, x_max, x_range, x_step))
    
    # Percentage of rows to keep in the model
    sparseParameters = xanesEdgeParams.getSparseParameters()
    fraction_to_keep = float(sparseParameters.getPercentage())/100
    print("Percentage of rows to keep in the model: {}%".format(int(fraction_to_keep * 100)))
    y_positions = dnp.arange(y_min, y_max+0.5*y_step, y_step)
    n_lines = int(fraction_to_keep*len(y_positions))
    print("Number of y positions available: {}".format(len(y_positions)))
    print("Number of lines to scan (n_lines): {}".format(n_lines))

    # Use the NumTracker to get the number of the next Nexus file to be created
    num_tracker = NumTracker()
    nexus_scan_number = num_tracker.getCurrentFileNumber() + 1
    num_tracker.incrementNumber() # increment it

    # Setup Nexus file path format 
    beamline_name = LocalProperties.get("gda.beamline.name")
    visit_folder = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    #nexus_name_format = visit_folder+"/"+str(beamline_name)+"-%d_%03d.nxs"
    nexus_name_format = visit_folder+"/"+ SCANS_FOLDER_NAME +"/"+str(beamline_name)+"-%d_%03d.nxs"
    print("Nexus file path format : {}".format(nexus_name_format))

    # configure NeXus group for file paths
    nxc = NexusNodeFactory.createNXcollection()
    node = NexusNodeFactory.createDataNode()
    node.setDataset(dnp.array([""])._jdataset())
    nxc.addDataNode('paths',node)

    # make NeXus scannable
    nxobs = NXObjectScannable("magic_nexus_scannable", "previous_scan_files", nxc)
    scannableDeviceService = ServiceProvider.getService(IScannableDeviceService)
    scannableDeviceService.register(nxobs)
    # add the created scannable for file paths to the current scan request
    mnps = scanRequest.getMonitorNamesPerScan()
    mnps.add("magic_nexus_scannable")
    scanRequest.setMonitorNamesPerScan(mnps)
    
    
    # TODO
    edgeElement = get_edge_to_energy(xanesEdgeParams) # to be used by processing request

    try:
        print("Moving energy scannable to first energy {}\n".format(dnp.amin(energies)))
        ENERGY_SCANNABLE.moveTo(dnp.amin(energies))
        sleep(5)

        # Create 2d map per energy point
        all_nexus_file_names = []
        for index, energy in enumerate(energies):
            print("Moving energy scannable to energy {}".format(energy))
            pos(ENERGY_SCANNABLE, energy) #@Undefinedvariable
            sleep(2)
            
            # Last scan will be all positions
            if index < len(energies)-1:
                random_y_indices = []
                
                while len(random_y_indices) < n_lines:
                    random_index = dnp.random.randint(0, len(y_positions))
                    if random_index not in random_y_indices:
                        random_y_indices.append(random_index)
                        
                if (len(random_y_indices) < 2):
                    print("Not enough points to run the scan")
                    break
                
                # Sort the random y indices
                random_y_indices = dnp.sort(random_y_indices)
                # Get the random y positions using sorted indices
                random_y_positions = y_positions[random_y_indices]
                print("Selected {} random y positions: {}".format(len(random_y_positions), random_y_positions))
            else:
                # For the last scan, use **all** y positions
                random_y_positions = y_positions
                print("Last scan: using all y positions ({} total)".format(len(random_y_positions)))

            # TODO Processing Request: removed for now
            # for last scan, save the files of this stack
            # if index == len(energies) - 1:
            #    # kick off the processing request when it is the last scan
            #    print('At last sparse XANES scan...')
            #    config = {"edge_element": edgeElement}
            #    print('Kicking off {} with {}'.format(PROCESSING_REQUEST_NAME, config))
            #    scanRequest.getProcessingRequest().getRequest().put(PROCESSING_REQUEST_NAME, [json.dumps(config)])
            #    print("scanRequest = {}".format(scanRequest))

            # Create the Y and X axis model
            y_axis_model = AxialArrayModel("SampleY",random_y_positions)
            y_axis_model.setContinuous(False)
            x_axis_model = AxialStepModel("SampleX", x_min, x_max, x_step)
            x_axis_model.setContinuous(True)
            cm = CompoundModel([y_axis_model,x_axis_model])

            # Create the Rectangular region
            region =  RectangularROI(y_min - y_step, x_min, y_range + 2*y_step, x_range, 0.0)

            # Add sparse positions to metadata
            sparse_pos_y = ''.join(str(x)+" " for x in random_y_positions)
            sparse_ind_y = ''.join(str(x)+" " for x in random_y_indices)
            smetadata = create_scan_metadata(sparse_pos_y, sparse_ind_y)

            # Create full file path
            file_path = nexus_name_format%(nexus_scan_number, index)
            print("NeXus file path is: {}".format(file_path))

            # create request
            request = ScanRequestBuilder() \
                      .withPathAndRegion(cm, region) \
                      .withDetectors(scanRequest.getDetectors()) \
                      .ignorePreprocess(True)\
                      .withScanMetadata([smetadata]) \
                      .withMonitorNamesPerScan(scanRequest.getMonitorNamesPerScan()) \
                      .withFilePath(file_path) \
                      .build()
                      
            # TODO ProcessingRequest: to add later
            #.withProcessingRequest(scanRequest.getProcessingRequest()) \
            
            # Submit the scan
            print("Submitting scan {}/{} at energy: {:.4f}\n".format(index+1, len(energies), energy))
            scan_name = "Sparse XANES_scan_{0}_of_{1}".format(index+1, num_scans)
            
            try:
                submit(request, block=True, name=scan_name)
            except InterruptedException as e:
                print(e)
                print("Stopping script as requested")
                break
            except JavaException as e:
                print(e)
                print("Problem with the scan at :",energy)
            else:
                # Collection filepaths
                all_nexus_file_names.append(file_path)
                node.setDataset(dnp.array(all_nexus_file_names)._jdataset())
    except Exception as e:
        print("XANES scan crashed...")
        print(e)
    except JavaException as e:
        print("XANES scan crashed...")
        print(e)
    finally:
        print("Sequence of XANES scans finished")
        
        
        
        
        
        
        
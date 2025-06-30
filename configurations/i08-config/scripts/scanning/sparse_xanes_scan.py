import os
import json
from time import sleep
import scisoftpy as dnp

# Java imports
from java.lang import Exception as JavaException #@Unresolvedimport
from java.lang import InterruptedException #@Unresolvedimport

# Scanning imports
from org.eclipse.scanning.sequencer import ScanRequestBuilder #@Unresolvedimport
from org.eclipse.scanning.api.scan.models import ScanMetadata #@Unresolvedimport
from org.eclipse.scanning.api.points.models import AxialArrayModel, AxialStepModel, CompoundModel #@Unresolvedimport
from uk.ac.diamond.osgi.services import ServiceProvider #@Unresolvedimport
from org.eclipse.scanning.api.device import IScannableDeviceService #@Unresolvedimport

# Dawn and Nexus imports
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI #@Unresolvedimport
from org.eclipse.dawnsci.nexus import NexusNodeFactory #@Unresolvedimport
from uk.ac.diamond.daq.scanning import NXObjectScannable #@Unresolvedimport

# Scripts imports
from scanning.xanes_utils import get_visit_path, get_edge_to_energy, get_models, get_energies
from scanning.xanes_utils import get_x_dimensions, get_y_dimensions, create_scan_metadata
from mapping_scan_commands import submit
from gda.data import NumTracker #@Unresolvedimport
#from gda.epics import CAClient


# Scannables imports

numtracker = NumTracker('tmp')

print("Setting up sparse xanes scan")

PROCESSING_REQUEST_NAME = "i08-xanes-sparse-stack"
ENERGY_SCANNABLE = energyFocus

def run_sparse_xanes_scan_request(scanRequest, xanesEdgeParams):
    print(scanRequest)
    print("Xanes parameters: {}\n".format(xanesEdgeParams))

    valid_malcolm_detector_name = '-ML-SCAN-01'
    malcolm_detector_name = scanRequest.getDetectors().keys()[0]
    if (not malcolm_detector_name.endswith(valid_malcolm_detector_name)):
        print("Selected detector is not valid for this type of scan")
        return;

    visitPath = get_visit_path()
    edgeElement = get_edge_to_energy(xanesEdgeParams)

    # percentage of rows to keep in the model
    sparseParameters = xanesEdgeParams.getSparseParameters()
    percentage = float(sparseParameters.getPercentage())/100

    energy_model, map_model = get_models(scanRequest)
    energies = get_energies(energy_model)
    min_energy = min(energies)
    max_energy = max(energies)
    print("\nEnergy Range: Min = {:.4f}, Max = {:.4f}".format(min_energy, max_energy))
    print("Energies: {}".format(energies))

    num_scans = len(energies)
    print("Total number of scans: {}\n".format(num_scans))

    y_min, y_max, y_range, y_step = get_y_dimensions(map_model)
    x_min, x_max, x_range, x_step = get_x_dimensions(map_model)
    print("Region: ")
    print("Y-axis: min = {:.5f}, max = {:.5f}, range = {:.5f}, step = {:.5f}".format(y_min, y_max, y_range, y_step))
    print("X-axis: min = {:.5f}, max = {:.5f}, range = {:.5f}, step = {:.5f}\n".format(x_min, x_max, x_range, x_step))

    y_positions = dnp.arange(y_min, y_max+0.5*y_step, y_step)
    n_lines = int (percentage*len(y_positions))

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

    try:
        # move to first energy and disable harmonic switching
        print("Moving energy scannable to first energy {}\n".format(dnp.amin(energies)))
        ENERGY_SCANNABLE.moveTo(dnp.amin(energies))
        # TODO does energyFocus do anything related to disableHarmonicSwitching?
        # energyFocus.disableHarmonicSwitching()
        sleep(10)

        # TODO does the energy scannable have anything related to current gain?
        # disable locum gain switching
        #range_dict = {1:"100pA", 2:"1nA", 4:"10nA", 8:"100nA", 16:"1uA", 32:"10uA",64:"100uA", 128:"1mA"}
        #current_gain1 = int(caget("BL14I-DI-BPM-03:IAMP1:MR").encode("ascii"))
        #current_gain2 = int(caget("BL14I-DI-BPM-03:IAMP2:MR").encode("ascii"))
        #current_gain1 = range_dict[current_gain1]
        #current_gain2 = range_dict[current_gain2]
        #current_gain = max(current_gain1,current_gain2)
        #print("Amplifier Gains",current_gain1,current_gain2,current_gain)
        #sleep(2)
        #caput("BL14I-DI-BPM-03:IAMP1:SETRANGE",current_gain)
        #caput("BL14I-DI-BPM-03:IAMP2:SETRANGE",current_gain)
        #sleep(2)

        # create 2d map per energy point
        files = []
        for idx, energy in enumerate(energies):
            print("Moving energy scannable to energy {}".format(energy))
            pos(ENERGY_SCANNABLE, energy) #@Undefinedvariable
            sleep(2)
            # last scan will be all positions
            if idx < len(energies)-1:
                rand_index = []
                while len(rand_index) < n_lines:
                    r=dnp.random.randint(0, len(y_positions))
                    if r not in rand_index:
                        rand_index.append(r)
                if (len(rand_index) < 2):
                    print("Not enough points to run the scan")
                    break
                rand_index = dnp.sort(rand_index) # sort the indices
                # get the random y positions using sorted indices
                rand_y_positions = y_positions[rand_index]
                print("Selected {} random y positions: {}".format(len(rand_y_positions), rand_y_positions))

            # TODO removed for now
            # for last scan, save the files of this stack
            #if idx == len(energies) - 1:
            #    # kick off the processing request when it is the last scan
            #    print('At last sparse XANES scan...')
            #    config = {"edge_element": edgeElement}
            #    print('Kicking off {} with {}'.format(PROCESSING_REQUEST_NAME, config))
            #    scanRequest.getProcessingRequest().getRequest().put(PROCESSING_REQUEST_NAME, [json.dumps(config)])
            #    print("scanRequest = {}".format(scanRequest))

            # y model
            y_axis_model = AxialArrayModel("SampleY",rand_y_positions)
            y_axis_model.setContinuous(False)

            # x model
            x_axis_model = AxialStepModel("SampleX", x_min, x_max, x_step)
            x_axis_model.setContinuous(True)

            # create the model
            cm = CompoundModel([y_axis_model,x_axis_model])

            # create the region
            region =  RectangularROI(y_min-y_step,x_min,y_range+2*y_step,x_range,0.0)

            # add sparse positions to metadata
            sparse_pos_y = ''.join(str(x)+" " for x in rand_y_positions)
            sparse_ind_y = ''.join(str(x)+" " for x in rand_index)
            smetadata = create_scan_metadata(sparse_pos_y, sparse_ind_y)

            # create request
            request = ScanRequestBuilder() \
                      .withPathAndRegion(cm, region) \
                      .withDetectors(scanRequest.getDetectors()) \
                      .ignorePreprocess(True)\
                      .withScanMetadata([smetadata]) \
                      .withMonitorNamesPerScan(scanRequest.getMonitorNamesPerScan()) \
                      .build()
            # TODO to add later
            #.withProcessingRequest(scanRequest.getProcessingRequest()) \

            # Submit the scan
            print("Submitting scan {}/{} at energy: {:.4f}\n".format(idx+1, len(energies), energy))
            scan_name = "Sparse XANES_scan_{0}_of_{1}".format(idx+1, num_scans)
            try:
                submit(request, block=True, name=scan_name)
            except InterruptedException as e:
                print(e)
                print("Stopping script")
                break
            except JavaException as e:
                print(e)
                print("Problem with the scan at :",energy)
            else:
                # collection filepaths
                # calculate path of last and append
                files.append(os.path.join(visitPath, "scan", "i08-{0}.nxs".format(numtracker.currentFileNumber)))
                node.setDataset(dnp.array(files)._jdataset())
                # TODO
                

    except Exception as e:
        print(e)
        # TODO 
        #dcm_enrg.enableHarmonicSwitching()
        #print("XANES scan crashed...re-enabling harmonic switching")
        print("XANES scan crashed...")
    except JavaException as e:
        print(e)
        print("XANES scan crashed...")
    finally:
        # TODO
        print("Sequence of XANES scans finished")
        #print("Locum-4 amplifer gains to auto")
        #caput("BL14I-DI-BPM-03:IAMP1:SETRANGE","Auto")
        #caput("BL14I-DI-BPM-03:IAMP2:SETRANGE","Auto")
        #print("At end, re-enabling harmonic switching")
        #dcm_enrg.enableHarmonicSwitching()
        
        
        
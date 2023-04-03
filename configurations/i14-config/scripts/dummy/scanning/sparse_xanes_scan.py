from java.lang import Exception as JavaException #@Unresolvedimport
from org.eclipse.scanning.sequencer import ScanRequestBuilder #@Unresolvedimport
from org.eclipse.scanning.api.scan.models import ScanMetadata #@Unresolvedimport
from org.eclipse.scanning.api.points.models import CompoundModel #@Unresolvedimport
from org.eclipse.scanning.api.points.models import AxialStepModel, AxialArrayModel #@Unresolvedimport
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI #@Unresolvedimport

import scisoftpy as dnp
from mapping_scan_commands import submit
from dummy.scanning.utils import get_energies, get_models, get_x_dimensions, get_y_dimensions


def run_sparse_xanes_scan_request(scanRequest, xanesEdgeParams):
    
    valid_malcolm_detector_name = '-ML-SCAN-01'
    malcolm_detector_name = scanRequest.getDetectors().keys()[0]
    if (not malcolm_detector_name.endswith(valid_malcolm_detector_name)):
        print("Selected detector is not valid for this type of scan")
        return;
    
    sparse_parameters = xanesEdgeParams.getSparseParameters()
    if sparse_parameters is not None:
        rows_percentage = float(sparse_parameters.getPercentage())/100

    energy_model, map_model = get_models(scanRequest)
    energies = get_energies(energy_model)
    num_scans = len(energies)
    print("Number of scans: {}".format(num_scans))
    print("Energies: {}".format(energies))

    y_min, y_max, y_range, y_step = get_y_dimensions(map_model)
    x_min, x_max, x_range, x_step = get_x_dimensions(map_model)
    print("y_min {}, y_max {}, y_range {}, y_step {}".format(y_min, y_max, y_range, y_step))  
    print("x_min {}, x_max {}, x_range {}, x_step {}".format(x_min, x_max, x_range, x_step))  
    
    try:
        # move to first energy and disable harmonic switching
        #dcm_enrg.moveTo(dnp.amin(energies))
        #dcm_enrg.disableHarmonicSwitching()
        #sleep(10)
        
        # disable locum gain switching
        
        for idx, energy in enumerate(energies):
            y_positions = dnp.arange(y_min, y_max, y_step)
            # last scan will be all positions
            if idx < len(energies)-1:
                n_lines = int (rows_percentage*len(y_positions))
                rand_index = []
                while len(rand_index) < n_lines:
                    r=dnp.random.randint(0, len(y_positions))
                    if r not in rand_index:
                        rand_index.append(r)
                rand_index = dnp.sort(rand_index)
                rand_y_positions = y_positions[rand_index]
                print("rand_y_positions", len(rand_y_positions), rand_index)
                
            # y model    
            y_axis_model = AxialArrayModel("SampleY",rand_y_positions) 
            y_axis_model.setContinuous(False)
            
            # x model
            x_axis_model = AxialStepModel("SampleX", x_min, x_max, x_step)
            x_axis_model.setContinuous(True)
            
            # create the model
            cm = CompoundModel([y_axis_model,x_axis_model])
            
            # create the region
            region = RectangularROI(y_min-y_step,x_min-x_step,x_range+x_step,y_range+y_step,0.0)
            
            # add sparse positions to metadata
            sparse_pos_y = ''.join(str(x)+" " for x in rand_y_positions)
            sparse_ind_y = ''.join(str(x)+" " for x in rand_index)
            smetadata = ScanMetadata()
            smetadata.setType(ScanMetadata.MetadataType.ENTRY)
            smetadata.addField("sparse_y_positions", sparse_pos_y)
            smetadata.addField("sparse_y_index", sparse_ind_y)
            
            # create request
            request = ScanRequestBuilder() \
                      .withPathAndRegion(cm, region) \
                      .withDetectors(scanRequest.getDetectors()) \
                      .ignorePreprocess(True) \
                      .withScanMetadata([smetadata]) \
                      .withProcessingRequest(scanRequest.getProcessingRequest()) \
                      .build()
                      
            # pos(dcm_enrg, energy)
            #sleep(2)

            print('Submitting scan ',idx+1,'.')
            scan_name = "Sparse XANES_scan_{0}_of_{1}".format(idx+1, num_scans)
            try:
                submit(request, block=True, name=scan_name)
            except JavaException as e:
                print(e)
                print("Problem with the scan at :",energy)
    except Exception as e:
        print(e)
        # dcm_enrg.enableHarmonicSwitching()
        print("XANES scan crashed...re-enabling harmonic switching")
    finally:
        print("Locum-4 amplifer gains to auto")
                #caput("BL14I-DI-BPM-03:IAMP1:SETRANGE","Auto")
                #caput("BL14I-DI-BPM-03:IAMP2:SETRANGE","Auto")    
        print("At end, re-enabling harmonic switching")
                #dcm_enrg.enableHarmonicSwitching()







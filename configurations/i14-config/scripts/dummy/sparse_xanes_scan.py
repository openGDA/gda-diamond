from java.net import URI
from java.lang import System
from java.lang import Exception as JavaException
import scisoftpy as dnp

from org.eclipse.scanning.sequencer import ScanRequestBuilder
from org.eclipse.scanning.api.scan.models import ScanMetadata
from org.eclipse.scanning.api.points.models import BoundingBox, CompoundModel
from org.eclipse.scanning.api.points.models import AxialStepModel, AxialArrayModel, AxialMultiStepModel
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI
from org.eclipse.scanning.command.Services import getEventService, getRunnableDeviceService
from org.eclipse.scanning.api.event.scan import ScanBean
from org.eclipse.scanning.api.event.EventConstants import SUBMISSION_QUEUE

from dummy.sparse_xanes_scan_utilities import *
from mapping_scan_commands import submit

def run_sparse_xanes_scan_request(scanRequest, xanesEdgeParams):
    # Initialise the scan submitter
    #submitter = getEventService().createSubmitter(URI(System.getProperty("GDA/gda.activemq.broker.uri")), SUBMISSION_QUEUE)

    # percentage of rows to keep in the model
    percentage = float(xanesEdgeParams.getPercentage())/100

    validMalcolmDetectorName = '-ML-SCAN-01'
    malcolmDetectorName = scanRequest.getDetectors().keys()[0]
    if (not malcolmDetectorName.endswith(validMalcolmDetectorName)):
        print("Selected detector is not valid for this type of scan")
        return;

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
        #1. Move to first energy and disable harmonic switching
        #dcm_enrg.moveTo(dnp.amin(energies))
        #dcm_enrg.disableHarmonicSwitching()
        #sleep(10)
        
        #2. disable locum gain switching
        #set_amplifier_gains()
        
        # 3. create 2d map per energy point
        for idx, energy in enumerate(energies):
            y_positions = dnp.arange(y_min, y_max, y_step)
            # last scan will be all positions
            if idx < len(energies)-1:
                n_lines = int (percentage*len(y_positions))
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
                      
            #pos(dcm_enrg, energy)
            #sleep(2)
            # Submit the scan
            print('Submitting scan ',idx+1,'.')
            scan_name = "Sparse XANES_scan_{0}_of_{1}".format(idx+1, num_scans)
            try:
                #submitter.blockingSubmit(ScanBean(request))
                submit(scanRequest, block=True, name=scan_name)
            except JavaException as e:
                # scan failed?
                print(e)
                print("Problem with the scan at :",energy)
    except Exception as e:
                #print(e)
                #dcm_enrg.enableHarmonicSwitching()
        print("XANES scan crashed...re-enabling harmonic switching")
    finally:
        print("Locum-4 amplifer gains to auto")
                #caput("BL14I-DI-BPM-03:IAMP1:SETRANGE","Auto")
                #caput("BL14I-DI-BPM-03:IAMP2:SETRANGE","Auto")    
        print("At end, re-enabling harmonic switching")
                #dcm_enrg.enableHarmonicSwitching()







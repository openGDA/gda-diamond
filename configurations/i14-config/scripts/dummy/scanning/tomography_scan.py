from math import sin #, pi, sqrt
from time import sleep
import scisoftpy as dnp #@Undefinedvariable #@Unresolvedimport

from java.lang import Exception as JavaException #@Undefinedvariable #@Unresolvedimport
from java.lang import InterruptedException #@Unresolvedimport
from org.eclipse.scanning.api.points.models import TwoAxisGridStepModel  #@Undefinedvariable #@Unresolvedimport

from gdaserver import stage1_rotation, SampleX, SampleY, SampleZ #@Undefinedvariable #@Unresolvedimport
from mapping_scan_commands import mscan, grid, rect, detector #@Undefinedvariable #@Unresolvedimport

print("Setting up tomography scan")

def run_tomo_scan(scanRequest, x_calibration, z_calibration,
                  start_angle, stop_angle, step_angle, angle_measured, z_centre):
    
    models = scanRequest.getCompoundModel().getModels()
    if len(models) > 1:
        print("3D scans are not supported. Please unselect third axis")
        return
    
    grid_step_model = models.get(0)
    if not isinstance(grid_step_model, TwoAxisGridStepModel):
        print("Not a valid model. Please select Raster Scan Path")
        return
    
    if len(scanRequest.getDetectors().keys()) <1:
        print("A detector has not been selected")
        return
    
    detector_name = scanRequest.getDetectors().keys()[0]
    detector_value = scanRequest.getDetectors().values()[0]
    print("Detector name: %s" % (detector_name))
    exposure_time = detector_value.getExposureTime()
    print("Exposure time: %f" % (exposure_time))
        
    # region
    x_step = grid_step_model.getxAxisStep()
    y_step = grid_step_model.getyAxisStep()

    bounding_box = grid_step_model.getBoundingBox()
    x_centre = bounding_box.getxAxisStart()
    y_centre = bounding_box.getyAxisStart()
    
    x_range = bounding_box.getxAxisLength()
    y_range = bounding_box.getyAxisLength()
    
    # calibration results
    x_mean = x_calibration.getMean()
    x_amp = x_calibration.getAmplitude()
    x_freq = x_calibration.getFrequency()
    x_phase = x_calibration.getPhase()
    
    z_mean = z_calibration.getMean()
    z_amp = z_calibration.getAmplitude()
    z_freq = z_calibration.getFrequency()
    z_phase = z_calibration.getPhase()

    x_position = x_mean + x_amp*sin(x_freq*angle_measured + x_phase)
    z_position = z_mean + z_amp*sin(z_freq*angle_measured + z_phase)
    
    offset_x = x_centre - x_position
    offset_z = z_centre - z_position
    
    rotations = dnp.arange(start_angle, stop_angle, step_angle)
    print("Rotations: ", rotations)
    
    for rot in rotations:
        stage1_rotation.moveTo(rot) #@Undefinedvariable
        
        x_position = x_mean + x_amp*sin(x_freq*rot + x_phase) + offset_x
        z_position = z_mean + z_amp*sin(z_freq*rot + z_phase) + offset_z    
        
        SampleX.moveTo(x_position) #@Undefinedvariable
        SampleZ.moveTo(z_position) #@Undefinedvariable
        sleep(2)
        print(x_position, z_position)
        
        x_start = x_position - 0.5*x_range
        x_end   = x_position + 0.5*x_range     
        y_start = y_centre - 0.5*y_range
        y_end   = y_centre + 0.5*y_range
        
        # processing request
        processingRequest = scanRequest.getProcessingRequest()
        request = processingRequest.getRequest()
        if request.keys(): 
            print ("It contains post processing request")
            requestKey = request.keys()[0]
            requestValue = request.values()[0]
            try:
                mscan(path=[grid(axes=('SampleX', 'SampleY'), start=(x_start, y_start), stop=(x_end, y_end), step=(x_step, y_step), alternating=False, continuous=True, verticalOrientation=False, roi=[rect(origin=(x_start, y_start), size=(x_range, y_range))])], monitorsPerScan=['beam'], det=[detector(detector_name, exposure_time)],proc=[(requestKey,requestValue)])
            except InterruptedException as e:
                print(e)
                print("Stopping script")
                break
            except JavaException as e:
                print(e)
                print("Scan failed but will try to continue rest of angles")    
        else:
            print("It does not contain post processing request")
            try:
                mscan(path=[grid(axes=('SampleX', 'SampleY'), start=(x_start, y_start), stop=(x_end, y_end), step=(x_step, y_step), alternating=False, continuous=True, verticalOrientation=False, roi=[rect(origin=(x_start, y_start), size=(x_range, y_range))])], monitorsPerScan=['beam'], det=[detector(detector_name, exposure_time)],proc=[])
            except InterruptedException as e:
                    print(e)
                    print("Stopping script")
                    break
            except JavaException as e:
                print(e)
                print("Scan failed but will try to continue rest of angles")
                
            sleep(5)
        
        
        
        
        
        
        
        
        
    
        
        
        
        
        
        
        
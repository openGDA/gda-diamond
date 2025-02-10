from math import sin #, pi, sqrt
from time import sleep

from java.lang import Exception as JavaException #@Undefinedvariable #@Unresolvedimport
from java.lang import InterruptedException #@Unresolvedimport
from org.eclipse.scanning.api.points.models import TwoAxisGridStepModel  #@Undefinedvariable #@Unresolvedimport

from gdaserver import stage1_rotation, SampleX, SampleZ #@Undefinedvariable #@Unresolvedimport
from mapping_scan_commands import submit

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

    bounding_box = grid_step_model.getBoundingBox()
    x_start = bounding_box.getxAxisStart()
    y_start = bounding_box.getyAxisStart()
    print("x start: %f" % (x_start))
    print("y start: %f" % (y_start))
    
    x_range = bounding_box.getxAxisLength()
    y_range = bounding_box.getyAxisLength()
    
    x_end = x_start + x_range
    y_end = y_start + y_range
    print("x end: %f" % (x_end))
    print("y end: %f" % (y_end))
    
    x_centre = (x_start + x_end) / 2
    y_centre = (y_start + y_end) / 2
    print("x centre: %f" % (x_centre))
    print("y centre: %f" % (y_centre))
    
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
    
    rotations = []
    current = start_angle
    while current <= stop_angle:
        rotations.append(current)
        current += step_angle
    print("Rotations: ", rotations)
    
    for index, rot in enumerate(rotations):
        stage1_rotation.moveTo(rot) #@Undefinedvariable
        
        x_position = x_mean + x_amp*sin(x_freq*rot + x_phase) + offset_x
        z_position = z_mean + z_amp*sin(z_freq*rot + z_phase) + offset_z    
        
        SampleX.moveTo(x_position) #@Undefinedvariable
        SampleZ.moveTo(z_position) #@Undefinedvariable
        sleep(2)
        
        scan_name = "Tomography_scan_{0}_of_{1}".format(index+1, len(rotations))
        print("{0} = {1}".format(scan_name, scanRequest))
        
        try:
            submit(scanRequest, block=True, name=scan_name)
        except InterruptedException as e:
            print(e)
            print("Stopping script")
            break
        except JavaException as e:
            print(e)
            print("Problem with the scan?")
            #if "Error from Malcolm" in e.toString():
            #    print("Error in Malcolm")
            #    print("Waiting")
            #    sleep(15)
        sleep(5)
        
        
        
        
        
        
        
        
    
        
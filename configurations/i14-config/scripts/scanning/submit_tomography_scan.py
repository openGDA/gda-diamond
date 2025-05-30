from gda.util.osgi import OsgiJythonHelper #@Unresolvedimport
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService #@Unresolvedimport
from org.eclipse.scanning.api.event.scan import ScanRequest #@Unresolvedimport
from uk.ac.diamond.daq.mapping.api import TomographyCalibrationData #@Unresolvedimport

import math
from java.lang import System
from java.util import Date
from java.text import SimpleDateFormat

marshaller_service = OsgiJythonHelper.getService(IMarshallerService)


def format_time(total_estimated_time):
    hours = math.floor(total_estimated_time / 3600.0)
    minutes = math.floor((total_estimated_time % 3600.0) / 60.0)
    seconds = total_estimated_time % 60.0
    return "Mapping scan duration: {:02.0f}h {:02.0f}m {:02.0f}s".format(hours, minutes, seconds)

def format_total_time(total_estimated_time):
    hours = math.floor(total_estimated_time / 3600.0)
    minutes = math.floor((total_estimated_time % 3600.0) / 60.0)
    seconds = total_estimated_time % 60.0
    return "Total tomography scans duration: {:02.0f}h {:02.0f}m {:02.0f}s".format(hours, minutes, seconds)

def get_current_time():
    now = Date()
    formatter = SimpleDateFormat("h:mm a")
    return "Current time: " + formatter.format(now).upper()

def get_end_time(total_estimated_time):
    current_time_ms = System.currentTimeMillis()
    end_time_ms = current_time_ms + (total_estimated_time * 1000)
    end_date = Date(long(end_time_ms))
    formatter = SimpleDateFormat("h:mm a")
    return "Scans complete by: " + formatter.format(end_date).upper()

formatted_mapping_time = format_time(scanEstimatedTime)
print(formatted_mapping_time)
formatted_total_time = format_total_time(totalEstimatedTime)
print(formatted_total_time)
print("")
print(get_current_time())
end_time = get_end_time(totalEstimatedTime)
print(end_time)
print("")

scanRequest = marshaller_service.unmarshal(scanRequestJson, ScanRequest) #@Undefinedvariable

x_calibration = marshaller_service.unmarshal(xCalibration, TomographyCalibrationData) #@Undefinedvariable
y_calibration = marshaller_service.unmarshal(yCalibration, TomographyCalibrationData) #@Undefinedvariable
z_calibration = marshaller_service.unmarshal(zCalibration, TomographyCalibrationData) #@Undefinedvariable

start_angle = startAngle #@Undefinedvariable
stop_angle = stopAngle #@Undefinedvariable
step_angle = stepAngle #@Undefinedvariable
angle_measured = angleMeasured #@Undefinedvariable
z_centre = zCentre #@Undefinedvariable
include_y = includeY #@Undefinedvariable

print("Start angle: %f" % (start_angle))
print("Stop angle: %f" % (stop_angle))
print("Step angle: %f" % (step_angle))
print("Angle measured: %f" % (angle_measured))
print("SampleZ centre: %f" % (angle_measured))

def print_fit_calibration(axis, calibration_axis):
    print("-------- %s FIT -------" % (axis))
    mean = calibration_axis.getMean()
    freq = calibration_axis.getFrequency()
    phase = calibration_axis.getPhase()
    amp = calibration_axis.getAmplitude()
    
    print("%s_mean  = %f" % (axis,mean))
    print("%s_freq  = %f" % (axis,freq))
    print("%s_phase = %f" % (axis,phase))
    print("%s_amp   = %f" % (axis,amp))
    

if include_y:
    print("Including y axis")
    print_fit_calibration("x", x_calibration)
    print_fit_calibration("y", y_calibration)
    print_fit_calibration("z", z_calibration)
    
    run_tomo_scan_with_y(scanRequest,
                         x_calibration,
                         y_calibration,
                         z_calibration,
                         start_angle,
                         stop_angle,
                         step_angle,
                         angle_measured,
                         z_centre)

else:
    print("Not including y axis")
    print_fit_calibration("x", x_calibration)
    print_fit_calibration("z", z_calibration)
    
    run_tomo_scan(scanRequest,
                  x_calibration,
                  z_calibration,
                  start_angle,
                  stop_angle,
                  step_angle,
                  angle_measured,
                  z_centre)

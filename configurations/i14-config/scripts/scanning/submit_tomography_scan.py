from gda.util.osgi import OsgiJythonHelper #@Unresolvedimport
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService #@Unresolvedimport
from org.eclipse.scanning.api.event.scan import ScanRequest #@Unresolvedimport
from uk.ac.diamond.daq.mapping.api import TomographyCalibrationData #@Unresolvedimport
    
marshaller_service = OsgiJythonHelper.getService(IMarshallerService)

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

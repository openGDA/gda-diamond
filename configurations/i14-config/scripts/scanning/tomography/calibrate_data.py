from gda.util.osgi import OsgiJythonHelper
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from uk.ac.diamond.daq.mapping.api import TomographyCalibrationData
from math import sin #, pi, sqrt
import scisoftpy as dnp
from gdaserver import SampleX, SampleY, SampleZ
from java.lang import Exception as JavaException



def print_results(name, est_mean, est_freq, est_phase, est_amp):
    print("%s_mean  = %f" % (name,est_mean))
    print("%s_freq  = %f" % (name,est_freq))
    print("%s_phase = %f" % (name,est_phase))
    print("%s_amp   = %f" % (name,est_amp))

marshaller_service = OsgiJythonHelper.getService(IMarshallerService)
x_calibration = marshaller_service.unmarshal(xCalibration, TomographyCalibrationData)
y_calibration = marshaller_service.unmarshal(yCalibration, TomographyCalibrationData)
z_calibration = marshaller_service.unmarshal(zCalibration, TomographyCalibrationData)

print(x_calibration)
print(y_calibration)
print(z_calibration)

# X FIT
x_mean = x_calibration.getMean()
x_freq = x_calibration.getFrequency()
x_phase = x_calibration.getPhase()
x_amp = x_calibration.getAmplitude()

print("### X FIT ###")
print_results("x", x_mean, x_freq, x_phase, x_amp)

# Y FIT
y_mean = y_calibration.getMean()
y_freq = y_calibration.getFrequency()
y_phase = y_calibration.getPhase()
y_amp = y_calibration.getAmplitude()

print("### Y FIT ###")
print_results("y", y_mean, y_freq, y_phase, y_amp)

# Z FIT
z_mean = z_calibration.getMean()
z_freq = z_calibration.getFrequency()
z_phase = z_calibration.getPhase()
z_amp = z_calibration.getAmplitude()

print("### Z FIT ###")
print_results("z", z_mean, z_freq, z_phase, z_amp)

# positions
#x_position = x_mean + x_amp*sin(x_freq*angle_measured + x_phase)
#z_position = z_mean + z_amp*sin(z_freq*angle_measured + z_phase)
#y_position = y_mean + y_amp*sin(y_freq*angle_measured + y_phase)

#pos(SampleX, x_position)
#pos(SampleY, y_position)
#pos(SampleZ, z_position)



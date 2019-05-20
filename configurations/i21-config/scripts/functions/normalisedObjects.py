from functions.device_function_class import DeviceFunctionClass
from gdascripts.configuration.properties.localProperties import LocalProperties

def normalisation(x1, x2):
	y=x1/x2;
	return y;

#LocalProperties.set("gda.plot.ScanPlotSettings.separateYAxes", True)
#Example: this object return value of draincurrent_i/m4c1 when used in a scan which acquire both smpcdrain and m4c1
normalised_drain_current = DeviceFunctionClass("normalised_drain_current", "draincurrent_i","m4c1", "normalisation");

#Usage: scan x 1 10 1 draincurrent_i 1.0 m4c1 1.0 normalised_drain_current
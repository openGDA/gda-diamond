from gda.util.osgi import OsgiJythonHelper
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from org.eclipse.scanning.api.event.scan import ScanRequest

print("Running submit_laminography_scan.py")

marshaller_service = OsgiJythonHelper.getService(IMarshallerService)

scanRequest = marshaller_service.unmarshal(scanRequestJson, ScanRequest) #@Undefinedvariable

start_angle = startAngle #@Undefinedvariable
stop_angle = stopAngle #@Undefinedvariable
step_angle = stepAngle #@Undefinedvariable

print("Start angle: %f" % (start_angle))
print("Stop angle: %f" % (stop_angle))
print("Step angle: %f" % (step_angle))

run_laminography_scan(scanRequest, start_angle, stop_angle, step_angle)

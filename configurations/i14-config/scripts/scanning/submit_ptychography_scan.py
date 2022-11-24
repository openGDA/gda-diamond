# Script to be called by the ptychography scan GUI
# It relies on the fact that the GUI has called the GDAJythonScriptService to put a JSON form of
# the ScanRequest into the Jython namespace as scanRequestJson and the ptychography parameters as ptychoParamsJson

from gda.util.osgi import OsgiJythonHelper
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from org.eclipse.scanning.api.event.scan import ScanRequest

print("Running submit_ptychography_scan.py")

marshaller_service = OsgiJythonHelper.getService(IMarshallerService)

scanRequest = marshaller_service.unmarshal(scanRequestJson, ScanRequest)

run_ptychography_scan_request(scanRequest)

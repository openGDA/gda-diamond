# Script to be called by the XANES scan GUI
# It converts to JSON data to objects and calls the user script run_xanes_scan_request()
from gda.factory import Finder
from gda.util.osgi import OsgiJythonHelper
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from org.eclipse.scanning.api.event.scan import ScanRequest
from uk.ac.diamond.daq.mapping.api import XanesEdgeParameters

print("Running submit_xanes_scan.py")

marshaller_service = OsgiJythonHelper.getService(IMarshallerService)

scanRequest = marshaller_service.unmarshal(scanRequestJson, ScanRequest)
xanesEdgeParams = marshaller_service.unmarshal(customParams, XanesEdgeParameters)

run("scanning/sparse_xanes_scan.py")

run_sparse_xanes_scan_request(scanRequest, xanesEdgeParams, block_on_submit=False)

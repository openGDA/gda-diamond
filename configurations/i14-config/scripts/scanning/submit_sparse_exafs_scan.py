# Script to be called by the XANES scan GUI
# It converts to JSON data to objects and calls the user script run_xanes_scan_request()
from gda.factory import Finder
from gda.util.osgi import OsgiJythonHelper
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from org.eclipse.scanning.api.event.scan import ScanRequest
from uk.ac.diamond.daq.mapping.api import XanesEdgeParameters

print("Running submit_sparse_exafs_scan.py")

marshaller_service = OsgiJythonHelper.getService(IMarshallerService)

scanRequest = marshaller_service.unmarshal(scanRequestJson, ScanRequest)

run_sparse_exafs_scan_request(scanRequest)




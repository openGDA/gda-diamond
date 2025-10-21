from gda.factory import Finder
from gda.util.osgi import OsgiJythonHelper
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from org.eclipse.scanning.api.event.scan import ScanRequest
from uk.ac.diamond.daq.mapping.api import XanesEdgeParameters

print("Running data_driven/submit_initial_scan.py")

marshaller_service = OsgiJythonHelper.getService(IMarshallerService)

scanRequest = marshaller_service.unmarshal(scanRequestJson, ScanRequest)
xanesEdgeParams = marshaller_service.unmarshal(customParams, XanesEdgeParameters)

run_initial_data_driven_scan(scanRequest, xanesEdgeParams)
# Take a mapping scan request and submit with left and right polarisations
# This script requires the appropriate ScanRequest and PolarisationScanParameters to be
# present (in JSON format) in the Jython namespace, named "scanRequestJson"
# and "polarisationScanParamsJson" respectively.

from polarisation.polarisation_functions import run_polarisation_scan
from gda.util.osgi import OsgiJythonHelper
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from org.eclipse.scanning.api.event.scan import ScanRequest
from uk.ac.diamond.daq.mapping.api import PolarisationScanParameters

print("Running submit_polarisation_scan.py")

marshaller_service = OsgiJythonHelper.getService(IMarshallerService)

scanRequest = marshaller_service.unmarshal(scanRequestJson, ScanRequest)
polarisationScanParams = marshaller_service.unmarshal(polarisationScanParamsJson, PolarisationScanParameters)

# Most of the work is delegated to this function
run_polarisation_scan(scanRequest, polarisationScanParams)

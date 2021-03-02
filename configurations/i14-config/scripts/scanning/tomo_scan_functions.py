# Define a function to submit tomography scane ("normal" and dry run")
# This function in turn calls functions that must be defined by the beamline
# It relies on the fact that the GUI has called the GDAJythonScriptService to put a JSON form of
# the ScanRequest into the Jython namespace as scanRequestJson and the tomography parameters as tomoParamsJson

from gda.util.osgi import OsgiJythonHelper
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from org.eclipse.scanning.api.event.scan import ScanRequest
from uk.ac.diamond.daq.mapping.api import TomographyParams

print('Defining submit_tomo_scan()')

def submit_tomo_scan(dry_run = False):
    marshaller_service = OsgiJythonHelper.getService(IMarshallerService)
    scanRequest = marshaller_service.unmarshal(scanRequestJson, ScanRequest)
    tomoParams = marshaller_service.unmarshal(tomoParamsJson, TomographyParams)
    if dry_run:
        run_tomo_dry_run(scanRequest, tomoParams)
    else:
        run_tomo_scan(scanRequest, tomoParams)

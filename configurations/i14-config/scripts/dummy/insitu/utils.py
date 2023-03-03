import json
from java.net import URI
from mapping_scan_commands import submit
from gda.util.osgi import OsgiJythonHelper
from java.lang import Exception as JavaException
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from org.eclipse.scanning.api.scan import IFilePathService
from org.eclipse.scanning.api.event.scan import (ScanRequest, ScanBean)
from org.eclipse.scanning.command.Services import getEventService
from gda.configuration.properties.LocalProperties import getBrokerURI

def get_scan_request(filename):
    
    marshaller_service = OsgiJythonHelper.getService(IMarshallerService)
    visit_config_dir = OsgiJythonHelper.getService(IFilePathService).getVisitConfigDir()
    
    filepath = visit_config_dir + "/" + filename
    
    with open(filepath, 'r') as f:
        scan_request_json = f.read()
        scan_request = marshaller_service.unmarshal(scan_request_json, ScanRequest)
        
    return scan_request


def pprint_scan_request(filename):
    
    visit_config_dir = OsgiJythonHelper.getService(IFilePathService).getVisitConfigDir()
    filepath = visit_config_dir + "/" + filename
    
    with open(filepath, 'r') as f:
        parsed = json.load(f)
        print(json.dumps(parsed, indent=3))
        
        
def run_scan(scan_request, name="scan", num_repetitions=1):
    print("Running scan")
    for _ in range(num_repetitions):
        try:
            submit(scan_request, name=name)
        except JavaException as e:
            print(e)
            print("Scan failed but will try to continue")
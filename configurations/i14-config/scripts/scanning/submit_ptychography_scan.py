# Script to be called by the ptychography scan GUI
# It relies on the fact that the GUI has called the GDAJythonScriptService to put a JSON form of
# the ScanRequest into the Jython namespace as scanRequestJson
import json

print("Running submit_ptychography_scan.py")

scan_request = json.loads(scanRequestJson)
run_ptychography_scan_request(scan_request)
# Script to be called by the tomography scan GUI
# It converts to JSON data to a dict and calls
import json

print("Running submit_tomography_scan.py")

scan_request = json.loads(scanRequestJson)
tomo_params = json.loads(tomoParamsJson)
run_tomo_scan(scan_request, tomo_params)

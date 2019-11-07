# Script to be called by the tomography scan GUI
# It converts to JSON data to a dict and calls
import json

print("Running submit_tomography_scan.py")

tomo_params = json.loads(tomoParamsJson)
scan_request = json.loads(scanRequestJson)
run_tomo_scan(tomo_params, scan_request)

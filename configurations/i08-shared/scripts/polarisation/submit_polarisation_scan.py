# Take a mapping scan request and submit with left and right polarisations

from polarisation.polarisation_functions import submit_scan

print("Running submit_polarisation_scan.py")

# Submit the same ScanRequest with left & right polarisation 
submit_scan(scanRequestJson, "set_left_polarisation.py", "left")
submit_scan(scanRequestJson, "set_right_polarisation.py", "right")

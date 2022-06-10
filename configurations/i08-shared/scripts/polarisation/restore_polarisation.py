from polarisation.polarisation_functions import restore_polarisation

# Restore the previous positions of the ID gap & phase motors
# This script is intended to be used as an "after script" in a ScanRequest
print("Running restore_polarisation.py")
restore_polarisation()
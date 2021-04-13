from polarisation.polarisation_functions import set_polarisation

# Set the ID gap & phase motors for left polarisation
# This script is intended to be used as a "before script" in a ScanRequest
print("Running set_left_polarisation.py")
set_polarisation(False)
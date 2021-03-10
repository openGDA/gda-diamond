from polarisation.polarisation_functions import set_polarisation

# Set the ID gap & phase motors for left polarisation
# This script is intended to be used as a "before script" in a ScanRequest
set_polarisation(200, -0.02, 0.02)
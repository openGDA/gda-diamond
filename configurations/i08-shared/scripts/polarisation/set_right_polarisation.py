from polarisation.polarisation_functions import set_polarisation

# Set the ID gap & phase motors for right polarisation
# This script is intended to be used as a "before script" in a ScanRequest
set_polarisation(100, 0.01, -0.01)
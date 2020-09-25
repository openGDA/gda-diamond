# Script to be called by the Standards scan GUI
# It splits up the arguments in the energy text box and calls standards_scan()
# The GUI sets the contents of the energy text box as a named value in the script service as "scanPath"
# and the exposure time as "exposureTime".

import re

# An energy range specifies <start> <stop> <step> as a string such as: "5 20 0.001"
# Split the string and convert to floating point numbers
def split_and_convert_energy_range(energy_range):
    split_range = energy_range.split(' ')
    return [float(i) for i in split_range]

print("Running submit_standards_scan.py")

energy_ranges = scanPath.split(';')
path = [split_and_convert_energy_range(i) for i in energy_ranges]
standards_scan(path, float(exposureTime))

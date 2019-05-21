# Script to be called by the Standards scan GUI
# It splits up the arguments in the energy text box and calls standards_scan()
# The contents of the energy text box must be set as a named value in the script service as "scanPath"

import re

# An energy range specifies <start> <stop> <step> as a string such as: "5 20 0.001"
# Split the string and convert to floating point numbers
def split_and_convert_energy_range(energy_range):
    split_range = re.findall(r'[\w.]+', energy_range)
    return [float(i) for i in split_range]

print("Running submit_standards_scan.py")

energy_ranges = scanPath.split(';')
path = [split_and_convert_energy_range(i) for i in energy_ranges]
standards_scan(path)

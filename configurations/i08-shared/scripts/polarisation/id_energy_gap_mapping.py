# Functions to change the mappings between ID energy & gap
import csv
from gdascripts.utils import caput
from i08_shared_utilities import is_live


def get_coefficients(file_path):
    filename = open(file_path, 'r')
    csv_file = csv.DictReader(filename)
    
    energy_to_gap = []
    gap_to_energy = []
    for row in csv_file:
        energy_to_gap.append(float(row["EnergyToGap"]))
        gap_to_energy.append(float(row["GapToEnergy"]))
        
    return energy_to_gap, gap_to_energy  

def set_mappings_for_polarisation(file_name):
    energy_to_gap, gap_to_energy = get_coefficients(file_name)
    set_mappings(energy_to_gap, gap_to_energy)

def set_mappings(energy_to_gap, gap_to_energy):
    for x in range(len(energy_to_gap)):
        pv = "BL08I-OP-ID-01:VT:C{}".format(x + 1)
        set_mapping(pv, energy_to_gap[x])
    for x in range(len(gap_to_energy)):
        pv = "BL08I-OP-ID-01:BVT:C{}".format(x + 1)
        set_mapping(pv, gap_to_energy[x])
    print("Polarisation setting complete")

def set_mapping(pv, value):
    if is_live():
        caput(pv, value)
    else:
        print("caput({}, {:e})".format(pv, value))
        
        
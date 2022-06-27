# Functions to change the mappings between ID energy & gap
import sys
import csv
from gdascripts.utils import caput
from i08_shared_utilities import is_live
from gda.configuration.properties import LocalProperties

print("Running id_energy_gap_mapping.py")

gda_var_dir = LocalProperties.get("gda.var")
circular_coefficients_filename = gda_var_dir + "/circular.csv"
linear_coefficients_filename = gda_var_dir + "/linear.csv"
energy_to_gap_col_name= "eV to mm"
gap_to_energy_col_name = "mm to eV"

def get_coefficients(file_path):
    polarisation_type = file_path.split("/")[-1].split(".")[0]
          
    filename = open(file_path, 'r')
    file = csv.DictReader(filename)
    
    energy_to_gap = []
    gap_to_energy = []
    
    for col in file:
        energy_to_gap.append(float(col[energy_to_gap_col_name]))
        gap_to_energy.append(float(col[gap_to_energy_col_name]))
        
    print("Energy to gap for {} polarisation coefficients: {}".format(polarisation_type, energy_to_gap))
    print("Gap to energy for {} polarisation coefficients: {}".format(polarisation_type, gap_to_energy))
    
    return energy_to_gap, gap_to_energy

def set_mappings_for_linear_polarisation():
    print("Setting mappings for linear polarisation")
    energy_to_gap, gap_to_energy = get_coefficients(linear_coefficients_filename)
    set_mappings(energy_to_gap, gap_to_energy)

def set_mappings_for_circular_polarisation():
    print("Setting mappings for circular polarisation")
    energy_to_gap, gap_to_energy = get_coefficients(circular_coefficients_filename)
    set_mappings(energy_to_gap, gap_to_energy)

def set_mappings(energy_to_gap, gap_to_energy):
    for x in range(len(energy_to_gap)):
        pv = "BL08I-OP-ID-01:VT:C{}".format(x + 1)
        set_mapping(pv, energy_to_gap[x])
    for x in range(len(gap_to_energy)):
        pv = "BL08I-OP-ID-01:BVT:C{}".format(x + 1)
        set_mapping(pv, gap_to_energy[x])

def set_mapping(pv, value):
    if is_live():
        caput(pv, value)
    else:
        print("caput({}, {:e})".format(pv, value))
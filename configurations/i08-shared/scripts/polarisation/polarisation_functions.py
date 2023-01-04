from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from id_energy_gap_mapping import set_mappings_for_polarisation

# Name of the files that contain the mappings coefficients 

coefficients_directory = LocalProperties.get("gda.var") + "/polarisationCoefficients"
circular_left_filename = coefficients_directory + "/circular_left.csv"
circular_right_filename = coefficients_directory + "/circular_right.csv"
linear_horizontal_filename = coefficients_directory + "/linear_horizontal.csv"
linear_vertical_filename = coefficients_directory + "/linear_vertical.csv"

# The scannables we need to set a polarisation mode
id_gap_scannable = Finder.find("idgap")
phase_scannable  = Finder.find("phase")

# Module-level variables to store the original phase motor positions
polarisation_idgap_position = 50
original_phase_position = None
polarisation_phase_position = None

def set_circular_left_polarisation(edge):
    polarisation_phase_position = get_phase_position_from_edge(edge)
    
    id_gap_scannable.moveTo(polarisation_idgap_position)
    phase_scannable.moveTo(0);
    phase_scannable.moveTo(polarisation_phase_position)
    
    set_mappings_for_polarisation(circular_left_filename)
    
    
def set_circular_right_polarisation(edge):
    polarisation_phase_position = get_phase_position_from_edge(edge)
    
    id_gap_scannable.moveTo(polarisation_idgap_position)
    phase_scannable.moveTo(0);
    phase_scannable.moveTo(-polarisation_phase_position);
    
    set_mappings_for_polarisation(circular_right_filename)
    
    
def set_linear_horizontal_polarisation():
    set_mappings_for_polarisation(linear_horizontal_filename)
    
def set_linear_vertical_polarisation():
    set_mappings_for_polarisation(linear_vertical_filename)
    
def get_phase_position_from_edge(edge):
    if edge == 'O-K':
        return 17.8
    elif edge == 'Fe-L':
        return 18.2
    elif edge == 'Co-L':
        return 18.4
    elif edge == 'Ni-L':
        return 18.6
    elif edge == 'Cu-L':
        return 18.8
    else:
        raise ValueError("Edge not valid")
    
    
    
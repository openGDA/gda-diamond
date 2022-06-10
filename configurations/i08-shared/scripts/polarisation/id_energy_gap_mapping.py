# Functions to change the mappings between ID energy & gap
from gdascripts.utils import caput
from i08_shared_utilities import is_live

print("Running id_energy_gap_mapping.py")

# Energy to gap for linear polarisation
linear_ev_to_mm = [3.4358, 1.1055e-1]

# Gap to energy for linear polarisation
linear_mm_to_ev = [1.5212e3, -3.8e2]

# Energy to gap for circular polarisation
circular_ev_to_mm = [1.2175e1, 1.83e-2]

# Gap to energy for circular polarisation
circular_mm_to_ev = [-6.6613e2, 5.4725e1]

def set_mappings_for_linear_polarisation():
    print("Setting mappings for linear polarisation")
    set_mappings(linear_ev_to_mm, linear_mm_to_ev)

def set_mappings_for_circular_polarisation():
    print("Setting mappings for circular polarisation")
    set_mappings(circular_ev_to_mm, circular_mm_to_ev)

def set_mappings(ev_to_mm, mm_to_ev):
    for x in range(2):
        pv = "BL08I-OP-ID-01:VT:C{}".format(x + 1)
        set_mapping(pv, ev_to_mm[x])
    for x in range(2):
        pv = "BL08I-OP-ID-01:BVT:C{}".format(x + 1)
        set_mapping(pv, mm_to_ev[x])

def set_mapping(pv, value):
    if is_live():
        caput(pv, value)
    else:
        print("caput({}, {:e})".format(pv, value))
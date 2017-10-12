import math

def calculate_hv_scan_values(hv_start, hv_end, hv_step, start_centre_energy, centre_energy_hv_function_name):
    """Inputs: [hv_start, hv_end, hv_ step, start_centre_energy, centre_energy_hv_function_name].
     Return a tuple of (photon energy, centre energy) tuples calculated according
     to the function defined by centre_energy_hv_function_name. """

    def insert_into_namespace(name, value, name_space=globals()):
       """Takes variable name (name) and assigns a value (value) to it in a namespace (name_space)"""

       name_space[name] = value
       print "Values inserted into namespace as {0}".format(name)

    tuple_list = []

    if float(hv_step) == 0.0:
        raise ValueError("Step size should not be 0!")
    if hv_start == hv_end:
        raise ValueError("Values for hv_start and hv_end should be different!")

    constant = start_centre_energy - centre_energy_hv_function_name(float(hv_start))
    hv_step = abs(hv_step)
    number_of_steps = abs(int(math.floor(abs(hv_end - hv_start) / hv_step))) + 1
    print "Steps: {0}".format(number_of_steps)

    hv = float(hv_start)
    for i in range(number_of_steps):
        tuple_list.append((hv, centre_energy_hv_function_name(hv)
        + constant))
        if hv_end > hv_start:
            hv += hv_step
        else:
            hv -= hv_step

    tuples = tuple(tuple_list)
    insert_into_namespace("energy_points", tuples)

    return tuples
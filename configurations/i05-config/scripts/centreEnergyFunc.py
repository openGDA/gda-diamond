# Detector work function to use in conjunction with calculate_hv_scan_values()
# in order to generate a list of tuples for photon energy dependence measurements

# 4th order polynomial fit to the detector work function
# phi(E) = p0 + p1*E^1 + p2*E^2 + p3*E^3 + p4*E^4 


def centre_energy_func(E):
    """Input: hv energy. Returns: energy adjusted according to detector work function"""

    coeff = {'p0': 4.3084,
             'p1': 0.0023989,
             'p2': 4.2168e-05,
             'p3': -1.2475e-07,
             'p4': 2.3462e-10}

    return  coeff['p0'] + coeff['p1'] * E + coeff['p2'] * E**2 + coeff['p3'] * E**3 + coeff['p4'] * E**4
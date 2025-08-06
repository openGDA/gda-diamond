# Lookup tables

def get_idgap_energy_phase_for_mn(degree):
    # Fixed energy value for Mn (Manganese)
    energy_value_mn = 641.2
    
    # Print the selected angle in degrees
    print "Selected degree:", degree
    
    # Determine ID gap and phase values based on the input degree
    if degree == 0:
        igdap_value_mn = 30.68
        phase_value_mn = 0
    if degree == 10:
        igdap_value_mn = 26.0
        phase_value_mn = 8.99
    elif degree == 20:
        igdap_value_mn = 24.6
        phase_value_mn = 10.3
    elif degree == 30:
        igdap_value_mn = 21.6
        phase_value_mn = 13.26
    elif degree == 40:
        igdap_value_mn = 20.4
        phase_value_mn = 14.8
    elif degree == 50:
        igdap_value_mn = 19.9
        phase_value_mn = 15.445
    elif degree == 60:
        igdap_value_mn = 19.55
        phase_value_mn = 17.55
    elif degree == 70:
        igdap_value_mn = 19.75
        phase_value_mn = 19.20
    elif degree == 80:
        igdap_value_mn = 20.05
        phase_value_mn = 20.23
    else:
        print "Unsupported degree:", degree
        raise ValueError("Unsupported degree: " + str(degree))
    
    # Print the calculated values for Mn
    print "Energy value (Mn):", energy_value_mn
    print "ID gap value (Mn):", igdap_value_mn
    print "Phase value (Mn):", phase_value_mn
        
    return energy_value_mn, igdap_value_mn, phase_value_mn

def get_idgap_energy_phase_for_fe(degree):
    # Fixed energy value for Fe (Iron)
    energy_value_fe = 704.6
    
    # Print the selected angle in degrees
    print "Selected degree:", degree
    
    # Determine ID gap and phase values based on the input degree
    if degree == 0: # LH
        igdap_value_fe = 32.02
        phase_value_fe = 0
    elif degree == 10:
        igdap_value_fe = 27.31
        phase_value_fe = 9
    elif degree == 20:
        igdap_value_fe = 24.4
        phase_value_fe = 11.7
    elif degree == 30:
        igdap_value_fe = 22.65
        phase_value_fe = 13.4
    elif degree == 40:
        igdap_value_fe = 21.47
        phase_value_fe = 14.9
    elif degree == 50:
        igdap_value_fe = 20.82
        phase_value_fe = 16.3
    elif degree == 60:
        igdap_value_fe = 20.62
        phase_value_fe = 17.6
    elif degree == 70:
        igdap_value_fe = 20.8
        phase_value_fe = 19.2
    elif degree == 80:
        igdap_value_fe = 21.4
        phase_value_fe = 21.3
    elif degree == 90: # LV
        igdap_value_fe = 22.4
        phase_value_fe = 26.5
    else:
        print "Unsupported degree:", degree
        raise ValueError("Unsupported degree: " + str(degree))
    
    # Print the calculated values for Fe
    print "Energy value (Fe):", energy_value_fe
    print "ID gap value (Fe):", igdap_value_fe
    print "Phase value (Fe):", phase_value_fe
        
    return energy_value_fe, igdap_value_fe, phase_value_fe

def get_idgap_energy_phase_for_co(degree):
    # Fixed energy value for Co (Cobalt)
    energy_value_co = 774.1
        
    # Print the selected angle in degrees
    print "Selected degree:", degree
    
    # Determine ID gap and phase values based on the input degree
    if degree == 0: # LH
        igdap_value_co = 33.458
        phase_value_co = 0
    elif degree == 10:
        igdap_value_co = 28.68
        phase_value_co = 9
    elif degree == 20:
        igdap_value_co = 25.73
        phase_value_co = 11.7
    elif degree == 30:
        igdap_value_co = 23.93
        phase_value_co = 13.4
    elif degree == 40:
        igdap_value_co = 22.69
        phase_value_co = 14.9
    elif degree == 50:
        igdap_value_co = 21.98
        phase_value_co = 16.3
    elif degree == 60:
        igdap_value_co = 21.75
        phase_value_co = 17.7
    elif degree == 70:
        igdap_value_co = 21.91
        phase_value_co = 19.3
    elif degree == 80:
        igdap_value_co = 22.46
        phase_value_co = 21.3
    elif degree == 90: # LV
        igdap_value_co = 23.45
        phase_value_co = 26.5
    else:
        print "Unsupported degree:", degree
        raise ValueError("Unsupported degree: " + str(degree))
    
    # Print the calculated values for Co
    print "Energy value (Co):", energy_value_co
    print "ID gap value (Co):", igdap_value_co
    print "Phase value (Co):", phase_value_co
        
    return energy_value_co, igdap_value_co, phase_value_co





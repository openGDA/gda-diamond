# ===================================================================================
# Configuration of servers after restart/reset
# ===================================================================================

# Uncomment (and edit) if non-standard motors are required for use with ncdgridscan
gridscan_stage = [base_x, base_y]

# Uncomment to change which channels and gain settings are used for It and I0 values in nexus files
# NB Commenting this out again after a reset will not return the settings to default until the servers
#    are restarted
scaler_channels = {'It': NcdChannel(channel=3, scaling=bs2diodegain),
                   'I0': NcdChannel(channel=1, scaling=d4d2gain)}

# ===================================================================================
# Add any commands that needs to be run after each restart/reset below this line
# ===================================================================================
#diode_y = SingleEpicsPositionerClass('diode_y', 'BL22I-MO-TABLE-05:Y', 'BL22I-MO-TABLE-05:Y.RBV' , 'BL22I-MO-TABLE-05:Y.DMOV' , 'BL22I-MO-TABLE-05:Y.STOP','mm', '%.4f')
#diode_x = SingleEpicsPositionerClass('diode_x', 'BL22I-MO-TABLE-05:X', 'BL22I-MO-TABLE-05:X.RBV' , 'BL22I-MO-TABLE-05:X.DMOV' , 'BL22I-MO-TABLE-05:X.STOP','mm', '%.4f')

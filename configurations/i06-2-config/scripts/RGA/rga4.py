from Diamond.PseudoDevices.EpicsDevices import EpicsMonitorClass

print "-"*100
print "Enable RGA4 objects: rga4tot, rga4O2, rga4H2O, rga4CO, rga4H2, rga4CO2, rga4CH4, rga4Ar, rgaPeem"

exec("[rga4tot, rga4O2, rga4CO, rga4CO2, rga4CH4, rga4H2O, rga4Ar, rga4H2] = [None, None, None, None, None, None, None, None]")
rga4tot = EpicsMonitorClass('rga4tot', 'BL06I-VA-RGA-04:TOTP', 'mbar', '%.2e')
rga4O2 = EpicsMonitorClass('rga4O2', 'BL06I-VA-RGA-04:BAR:M32', 'mbar', '%.2e')
rga4H2O = EpicsMonitorClass('rga4H2O', 'BL06I-VA-RGA-04:BAR:M18', 'mbar', '%.2e')
rga4CO = EpicsMonitorClass('rga4CO', 'BL06I-VA-RGA-04:BAR:M28', 'mbar', '%.2e')
rga4H2 = EpicsMonitorClass('rga4H2', 'BL06I-VA-RGA-04:BAR:M2', 'mbar', '%.2e')

rga4CO2 = EpicsMonitorClass('rga4CO2', 'BL06I-VA-RGA-04:BAR:M44', 'mbar', '%.2e')
rga4CH4 = EpicsMonitorClass('rga4CH4', 'BL06I-VA-RGA-04:BAR:M16', 'mbar', '%.2e')
rga4Ar = EpicsMonitorClass('rga4Ar', 'BL06I-VA-RGA-04:BAR:M40', 'mbar', '%.2e')

rgaPeem=[rga4tot, rga4O2, rga4CO, rga4CO2, rga4CH4, rga4H2O, rga4Ar, rga4H2]
 
#scan timer 0 10000 10 rga4tot rga4O2 rga4H2O rga4CO rga4CO2 rga4CH4 rga4Ar rga4H2
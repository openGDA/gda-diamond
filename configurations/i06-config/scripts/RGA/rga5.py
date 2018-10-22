from Diamond.PseudoDevices.EpicsDevices import EpicsMonitorClass

print "-"*100
print "Enable RGA5 objects: rga5tot, rga5O2, rga5CO, rga5CO2, rga5CH4, rga5H2O, rga5Ar, rga5H2, rgaPreparation"

exec("[rga5tot, rga5O2, rga5CO, rga5CO2, rga5CH4, rga5H2O, rga5Ar, rga5H2] = [None, None, None, None, None, None, None, None]")
rga5tot = EpicsMonitorClass('rga5tot', 'BL06I-VA-RGA-05:TOTP', 'mbar', '%.2e')
rga5O2 = EpicsMonitorClass('rga5O2', 'BL06I-VA-RGA-05:BAR:M32', 'mbar', '%.2e')
rga5H2O = EpicsMonitorClass('rga5H2O', 'BL06I-VA-RGA-05:BAR:M18', 'mbar', '%.2e')
rga5CO = EpicsMonitorClass('rga5CO', 'BL06I-VA-RGA-05:BAR:M28', 'mbar', '%.2e')
rga5H2 = EpicsMonitorClass('rga5H2', 'BL06I-VA-RGA-05:BAR:M2', 'mbar', '%.2e')
rga5CO2 = EpicsMonitorClass('rga5CO2', 'BL06I-VA-RGA-05:BAR:M44', 'mbar', '%.2e')
rga5CH4 = EpicsMonitorClass('rga5CH4', 'BL06I-VA-RGA-05:BAR:M16', 'mbar', '%.2e')
rga5Ar = EpicsMonitorClass('rga5Ar', 'BL06I-VA-RGA-05:BAR:M40', 'mbar', '%.2e')

rgaPreparation= [rga5tot, rga5O2, rga5CO, rga5CO2, rga5CH4, rga5H2O, rga5Ar, rga5H2]

#scan timer 0 10000 10 rga5tot rga5O2 rga5H2O rga5CO rga5CO2 rga5CH4 rga5Ar rga5H2
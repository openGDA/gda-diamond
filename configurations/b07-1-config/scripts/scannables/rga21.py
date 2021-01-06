from epics.EpicsDevices import EpicsMonitorClass

print "-"*100
print "Enable MKS RGA21 objects: rga21tot, rga21sumofpeaks, rga21H2, rga21HE, rga21CH2, rga21CH3, rga21CH4, rga21H2O,rga21CO, rga21O2, rga21AR, rga21CO2, rga21CF3, rga21"

exec("[rga21tot, rga21sumofpeaks, rga21H2, rga21HE, rga21CH2, rga21CH3, rga21CH4, rga21H2O,rga21CO, rga21O2, rga21AR, rga21CO2, rga21CF3] = [None, None, None, None, None, None, None, None, None, None, None, None, None]")
rga21tot = EpicsMonitorClass('rga21tot', 'BL07C-VA-RGA-21:TOTP', 'mbar', '%.2e')
rga21sumofpeaks = EpicsMonitorClass('rga21sumofpeaks', 'BL07C-VA-RGA-21:SUMP', 'mbar', '%.2e')
rga21H2 = EpicsMonitorClass('rga21H2', 'BL07C-VA-RGA-21:BAR:M2', 'mbar', '%.2e')
rga21HE = EpicsMonitorClass('rga21HE', 'BL07C-VA-RGA-21:BAR:M4', 'mbar', '%.2e')
rga21CH2 = EpicsMonitorClass('rga21CH2', 'BL07C-VA-RGA-21:BAR:M14', 'mbar', '%.2e')
rga21CH3 = EpicsMonitorClass('rga21CH3', 'BL07C-VA-RGA-21:BAR:M15', 'mbar', '%.2e')
rga21CH4 = EpicsMonitorClass('rga21CH4', 'BL07C-VA-RGA-21:BAR:M16', 'mbar', '%.2e')
rga21H2O = EpicsMonitorClass('rga21H2O', 'BL06I-VA-RGA-21:BAR:M18', 'mbar', '%.2e')
rga21CO = EpicsMonitorClass('rga21CO', 'BL06I-VA-RGA-21:BAR:M28', 'mbar', '%.2e')
rga21O2 = EpicsMonitorClass('rga21O2', 'BL06I-VA-RGA-21:BAR:M32', 'mbar', '%.2e')
rga21AR = EpicsMonitorClass('rga21AR', 'BL06I-VA-RGA-21:BAR:M40', 'mbar', '%.2e')
rga21CO2 = EpicsMonitorClass('rga21CO2', 'BL06I-VA-RGA-21:BAR:M44', 'mbar', '%.2e')
rga21CF3 = EpicsMonitorClass('rga21CF3', 'BL06I-VA-RGA-21:BAR:M69', 'mbar', '%.2e')

rga21= [rga21tot, rga21sumofpeaks, rga21H2, rga21HE, rga21CH2, rga21CH3, rga21CH4, rga21H2O,rga21CO, rga21O2, rga21AR, rga21CO2, rga21CF3]

#scan timer 0 10000 10 rga5tot rga5O2 rga5H2O rga5CO rga5CO2 rga5CH4 rga5Ar rga5H2
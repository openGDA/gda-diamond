from epics.EpicsDevices import EpicsMonitorClass

print "-"*100
print "Enable MKS RGA24 objects: rga24tot, rga24sumofpeaks, rga24H2, rga24HE, rga24CH2, rga24CH3, rga24CH4, rga24H2O,rga24CO, rga24O2, rga24AR, rga24CO2, rga24CF3, rga24"

exec("[rga24tot, rga24sumofpeaks, rga24H2, rga24HE, rga24CH2, rga24CH3, rga24CH4, rga24H2O,rga24CO, rga24O2, rga24AR, rga24CO2, rga24CF3] = [None, None, None, None, None, None, None, None, None, None, None, None, None]")
rga24tot = EpicsMonitorClass('rga24tot', 'BL07C-VA-RGA-24:TOTP', 'mbar', '%.2e')
rga24sumofpeaks = EpicsMonitorClass('rga24sumofpeaks', 'BL07C-VA-RGA-24:SUMP', 'mbar', '%.2e')
rga24H2 = EpicsMonitorClass('rga24H2', 'BL07C-VA-RGA-24:BAR:M2', 'mbar', '%.2e')
rga24HE = EpicsMonitorClass('rga24HE', 'BL07C-VA-RGA-24:BAR:M4', 'mbar', '%.2e')
rga24CH2 = EpicsMonitorClass('rga24CH2', 'BL07C-VA-RGA-24:BAR:M14', 'mbar', '%.2e')
rga24CH3 = EpicsMonitorClass('rga24CH3', 'BL07C-VA-RGA-24:BAR:M15', 'mbar', '%.2e')
rga24CH4 = EpicsMonitorClass('rga24CH4', 'BL07C-VA-RGA-24:BAR:M16', 'mbar', '%.2e')
rga24H2O = EpicsMonitorClass('rga24H2O', 'BL07C-VA-RGA-24:BAR:M18', 'mbar', '%.2e')
rga24CO = EpicsMonitorClass('rga24CO', 'BL07C-VA-RGA-24:BAR:M28', 'mbar', '%.2e')
rga24O2 = EpicsMonitorClass('rga24O2', 'BL07C-VA-RGA-24:BAR:M32', 'mbar', '%.2e')
rga24AR = EpicsMonitorClass('rga24AR', 'BL07C-VA-RGA-24:BAR:M40', 'mbar', '%.2e')
rga24CO2 = EpicsMonitorClass('rga24CO2', 'BL07C-VA-RGA-24:BAR:M44', 'mbar', '%.2e')
rga24CF3 = EpicsMonitorClass('rga24CF3', 'BL07C-VA-RGA-24:BAR:M69', 'mbar', '%.2e')

rga24= [rga24tot, rga24sumofpeaks, rga24H2, rga24HE, rga24CH2, rga24CH3, rga24CH4, rga24H2O,rga24CO, rga24O2, rga24AR, rga24CO2, rga24CF3]

#scan timer 0 10000 10 rga5tot rga5O2 rga5H2O rga5CO rga5CO2 rga5CH4 rga5Ar rga5H2
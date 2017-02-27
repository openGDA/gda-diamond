from Diamond.PseudoDevices.EpicsDevices import EpicsMonitorClass, EpicsLazyMonitorClass

exec("[ptot, pO2, pCO, pCO2, pCH4, pH2O, pAr, prepI0, pH2] = [None, None, None, None, None, None, None, None,None]")
ptot = EpicsMonitorClass('ptot', 'BL06I-VA-RGA-05:TOTP', 'mbar', '%.2e')
pO2 = EpicsMonitorClass('pO2', 'BL06I-VA-RGA-05:BAR:M32', 'mbar', '%.2e')
pH2O = EpicsMonitorClass('pH2O', 'BL06I-VA-RGA-05:BAR:M18', 'mbar', '%.2e')
pCO = EpicsMonitorClass('pCO', 'BL06I-VA-RGA-05:BAR:M28', 'mbar', '%.2e')
pH2 = EpicsMonitorClass('pH2', 'BL06I-VA-RGA-05:BAR:M2', 'mbar', '%.2e')

pCO2 = EpicsMonitorClass('pCO2', 'BL06I-VA-RGA-05:BAR:M44', 'mbar', '%.2e')
pCH4 = EpicsMonitorClass('pCH4', 'BL06I-VA-RGA-05:BAR:M16', 'mbar', '%.2e')
pAr = EpicsMonitorClass('pAr', 'BL06I-VA-RGA-05:BAR:M40', 'mbar', '%.2e')
#prepI0 = EpicsMonitorClass('prepI0', 'BL06I-EA-USER-01:AI1', 'Volt', '%.4e')
 
#scan timer 0 10000 10 ptot pO2 pH2O pCO pCO2 pCH4 pAr pH2
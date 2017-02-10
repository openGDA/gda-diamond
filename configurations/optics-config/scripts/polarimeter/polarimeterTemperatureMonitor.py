'''
create 2 scannables that monitor Retardation motor temperature and Analyser motor temperature in a polarimeter.

Created on 08 Feb 2017

@author: fy65
'''
from epics.pvmonitor.threadedMonitor import EpicsPVWithMonitorListener

print "-"*100
print "Creating Temperature monitors: anatemp, rettemp"

rettemp = EpicsPVWithMonitorListener('rettemp', 'ME02P-MO-RET-01:ROT:TEMP', 'degree', '%.4.1f')
anatemp = EpicsPVWithMonitorListener('anatemp', 'ME02P-MO-ANA-01:ROT:TEMP', 'degree', '%.4.1f')
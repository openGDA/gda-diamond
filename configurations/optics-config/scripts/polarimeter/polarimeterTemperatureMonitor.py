'''
create 2 scannables that monitor Retardation motor temperature and Analyser motor temperature in a polarimeter.

Created on 08 Feb 2017

@author: fy65
'''
from utils import installation

print "-"*100
print "Create Temperature monitors: anatemp, rettemp"

if installation.isLive():
    from epics.pvmonitor.threadedMonitor import EpicsPVWithMonitorListener
    rettemp = EpicsPVWithMonitorListener('rettemp', 'ME02P-MO-RET-01:ROT:TEMP', 'degree', '%.4.1f')
    anatemp = EpicsPVWithMonitorListener('anatemp', 'ME02P-MO-ANA-01:ROT:TEMP', 'degree', '%.4.1f')
else:
    from gda.device.monitor import DummyEpicsMonitorDouble
    from scannables.DummyThreadedMonitor import DummyEpicsPVWithDummyEpicsMonitorDouble
    ret_temp_value = DummyEpicsMonitorDouble()
    ret_temp_value.setLowerLimit(40)
    ret_temp_value.setUpperLimit(120)
    ret_temp_value.setIncrement(5)
    ana_temp_value = DummyEpicsMonitorDouble()
    ana_temp_value.setLowerLimit(40)
    ana_temp_value.setUpperLimit(120)
    ana_temp_value.setIncrement(5)
    rettemp = DummyEpicsPVWithDummyEpicsMonitorDouble('rettemp', ret_temp_value, 'degree', '%.4.1f')
    anatemp = DummyEpicsPVWithDummyEpicsMonitorDouble('anatemp', ana_temp_value, 'degree', '%.4.1f')
        
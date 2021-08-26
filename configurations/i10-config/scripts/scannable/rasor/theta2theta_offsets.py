'''
Created on Aug 19, 2021

@author: fy65
'''
import installation
from gdascripts.pd.epics_pds import EpicsReadWritePVClass
from gdascripts.pd.dummy_pds import DummyEpicsReadWritePVClass
from utils.ExceptionLogs import localStation_exception
import sys

if installation.isLive():
    try:
        th_off = EpicsReadWritePVClass('th_off', 'ME01D-MO-DIFF-01:THETA.OFF', 'deg', '%.6f')
        tth_off = EpicsReadWritePVClass('tth_off', 'ME01D-MO-DIFF-01:TWOTHETA.OFF', 'deg', '%.6f')
    except:
        localStation_exception(sys.exc_info(), "creating th & tth offset and encoder offset scannables")
else:
    th_off = DummyEpicsReadWritePVClass('th_off', 0.0, 90.0, 'deg', '%.6f')
    tth_off = DummyEpicsReadWritePVClass('tth_off', 0.0, 90.0, 'deg', '%.6f')
        
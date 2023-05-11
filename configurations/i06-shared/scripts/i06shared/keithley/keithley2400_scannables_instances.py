'''
create current and voltage scannbales for Keithley 2400

Created on May 11, 2023

@author: fy65
'''
print("create Keithley 2400 scannables for Current (keiCur1) and Voltage (keiVol1)")

from i06shared.keithley.epics_keithley_2400_class import EpicsKeithley2400
from i06shared.keithley.keithley2400_scannables_class import Keithley2400Current, Keithley2400Voltage

keithley2400 = EpicsKeithley2400("keithley2400", "BL06J-EA-SRCM-01:")
keithley2400.configure()

keiCur1 = Keithley2400Current('keiCur1', keithley2400)

keiVol1 = Keithley2400Voltage('keiVol1', keithley2400)

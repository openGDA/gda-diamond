'''
create current and voltage scannbales for Keithley 2400

Created on May 11, 2023

@author: fy65
'''
from i06shared.keithley.epics_keithley_2461_class import EpicsKeithley2461
from i06shared.keithley.keithley2461_scannables_class import Keithley2461Current,\
    Keithley2461Voltage
print("create Keithley 2400 scannables for Current (keiCur1) and Voltage (keiVol1)")


keithley2400 = EpicsKeithley2461("keithley2400", "BL06J-EA-SRCM-01:")
keithley2400.configure()

keiCur1 = Keithley2461Current('keiCur1', keithley2400)

keiVol1 = Keithley2461Voltage('keiVol1', keithley2400)

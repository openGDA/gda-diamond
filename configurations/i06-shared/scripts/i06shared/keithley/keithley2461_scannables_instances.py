'''
Created on Aug 3, 2022

@author: fy65
'''
print("create Keithley 2461 scannables for Current (keiCur) and Voltage (keiVol)")

from i06shared.keithley.epics_keithley_2461_class import EpicsKeithley2461
from i06shared.keithley.keithley2461_scannables_class import Keithley2461Current, Keithley2461Voltage

keithley = EpicsKeithley2461("keithley", "BL06I-EA-SRCM-01:")
keithley.configure()

keiCur = Keithley2461Current('keiCur', keithley)

keiVol = Keithley2461Voltage('keiVol', keithley)

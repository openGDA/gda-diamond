'''
Created on Aug 3, 2022

@author: fy65
'''
print("create Keithley 2461 scannables for Current (keiCur), Voltage (keiVol), and Resistance (keiRes)")

from i06shared.keithley.epics_keithley_class import EpicsKeithley2461
from i06shared.keithley.keithley2461_scannables_class import Keitlhey2461Resistance, Keitlhey2461Current, Keitlhey2461Voltage

keithley = EpicsKeithley2461("keithley", "BL06I-EA-SRCM-01:")
keithley.configure()

keiRes = Keitlhey2461Resistance('keiRes', keithley)

keiCur = Keitlhey2461Current('keiCur', keithley)

keiVol = Keitlhey2461Voltage('keiVol', keithley)

'''
create current and voltage scannbales for Keithley 2461

Created on Aug 3, 2022

@author: fy65
'''
print("create Keithley 2461 scannables for Current (keiCur) and Voltage (keiVol)")

from i06shared.keithley.epics_keithley_source_meter_class import EpicsKeithleySourceMeter
from i06shared.keithley.keithley2461_scannables_class import Keithley2461Current, Keithley2461Voltage

keithley2461 = EpicsKeithleySourceMeter("keithley2461", "BL06I-EA-SRCM-01:", model=2461)
keithley2461.configure()

keiCur = Keithley2461Current('keiCur', keithley2461)

keiVolt = Keithley2461Voltage('keiVolt', keithley2461)

'''
create current and voltage scannbales for Keithley 2400

Created on May 11, 2023
copied from i06share on 10 Dec 2024

@author: fy65
'''
print("create Keithley 2400 scannables for Current (keiCur1) and Voltage (keiVol1)")

from keithley.epics_keithley_source_meter_class import EpicsKeithleySourceMeter
from keithley.keithley2400_scannables_class import Keithley2400Current, Keithley2400Voltage

keithley2400 = EpicsKeithleySourceMeter("keithley2400", "BL10I-EA-K2400-01:", model=2400)
keithley2400.configure()

keiCur1 = Keithley2400Current('keiCur1', keithley2400)

keiVol1 = Keithley2400Voltage('keiVol1', keithley2400)

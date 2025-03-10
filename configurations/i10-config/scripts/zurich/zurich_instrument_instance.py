'''
Created on 19 Jul 2019

@author: fy65
'''
from zurich.ZurichInstrumentScannable import ZurichScannable
from zurich.ZurichInstrumentDetector import ZurichDetector

ZURICH_INSTRUMENT_PC_ADDRESS = "172.23.110.68"
ZURICH_INSTRUMENT_PC_PORT = 51423
ZURICH_INSTRUMENT_MESSAGER_TERMINATOR = '\r\n'
ZURICH_INSTRUMENT_MESSAGER_SEPARATOR = ' '

dev4260 = ZurichScannable("dev4260", ZURICH_INSTRUMENT_PC_ADDRESS, ZURICH_INSTRUMENT_PC_PORT, ZURICH_INSTRUMENT_MESSAGER_TERMINATOR, ZURICH_INSTRUMENT_MESSAGER_SEPARATOR)
det4260 = ZurichDetector("det4260", ZURICH_INSTRUMENT_PC_ADDRESS, ZURICH_INSTRUMENT_PC_PORT, ZURICH_INSTRUMENT_MESSAGER_TERMINATOR, ZURICH_INSTRUMENT_MESSAGER_SEPARATOR, dataPath='/dev4206/demods/0/sample', staticsPath='/dev4206/scopes/0/wave')

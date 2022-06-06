'''
create M4 and M5 fine pitch control to be shared by BeamStablisation_class.py and rasteringUseKeysight.py
Created on Jun 6, 2022

@author: fy65
'''
from gda.device.scannable import PVScannable

m4fpitch=PVScannable("m4fpitch","BL06I-EA-SGEN-01:CH1:OFF"); m4fpitch.configure()
m5fpitch=PVScannable("m5fpitch","BL06I-EA-SGEN-01:CH2:OFF"); m5fpitch.configure()

'''
create M4 and M5 fine pitch control to be shared by BeamStablisation_class.py and rasteringUseKeysight.py
Created on Jun 6, 2022

@author: fy65
'''
from gda.device.scannable import PVScannable, DummyScannable
from i06shared import installation

if installation.isLive():
    m4fpitch=PVScannable("m4fpitch","BL06I-EA-SGEN-01:CH1:OFF"); m4fpitch.configure()
    m5fpitch=PVScannable("m5fpitch","BL06I-EA-SGEN-01:CH2:OFF"); m5fpitch.configure()
else:
    m4fpitch=DummyScannable("m4fpitch",0.014); m4fpitch.configure()
    m5fpitch=DummyScannable("m5fpitch",0.345); m5fpitch.configure()

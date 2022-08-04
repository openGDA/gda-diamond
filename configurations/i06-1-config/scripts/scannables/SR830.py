'''
defines scannables for Lock-in Amplifier SR830

Created on Aug 4, 2022

@author: fy65
'''
from gda.device.scannable import PVScannable

srs830_x = PVScannable("srs830_x","BL06J-EA-LKAMP-01:SR830:A:Disp1")
srs830_x.configure()
srs830_x.setCanMove(False)
srs830_y = PVScannable("srs830_y","BL06J-EA-LKAMP-01:SR830:A:Disp2")
srs830_y.configure()
srs830_y.setCanMove(False)
srs830_v = PVScannable("srs830_v","BL06J-EA-LKAMP-01:SR830:A:Ampl")
srs830_v.configure()
srs830_v.setCanMove(False)


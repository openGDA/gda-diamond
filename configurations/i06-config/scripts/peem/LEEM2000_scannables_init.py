'''
script provided by Francesco Maccherozzi
'''
from peem.LEEEM_MODULE_CLASS import LEEM_Scannable_Class
from peem.LEEM_FOV_Rotation_CLASS import LEEM_FOV_Rotation_Class
from i06shared import installation
from gda.device.scannable import DummyUnitsScannable
degree_sign = u"\N{DEGREE SIGN}"
exec("[objAlignX, objAlignY, leem_temp, leem_rot]= [None, None, None, None]")
if installation.isLive():
    from peem.LEEM2000_tcp import leem2000
    objAlignX = LEEM_Scannable_Class('objAlignX',"mAmp", 36, leem2000)
    objAlignY = LEEM_Scannable_Class('objAlignY',"mAmp", 37, leem2000)
    leem_temp = LEEM_Scannable_Class('leem_temp',"deg", 39, leem2000)
    leem_rot = LEEM_FOV_Rotation_Class('leem_rot', "deg", leem2000)
else:
    objAlignX = DummyUnitsScannable('objAlignX', 1.0, "mA", "mA"); objAlignX.setOutputFormat(['%3.2f'])
    objAlignY = DummyUnitsScannable('objAlignY', 2.0, "mA", "mA"); objAlignY.setOutputFormat(['%3.2f'])
    leem_temp = DummyUnitsScannable('leem_temp', 18.0, "centigrade", "centigrade"); leem_temp.setOutputFormat(['%3.2f'])
    leem_rot = DummyUnitsScannable('leem_rot', 0.0, "deg", "deg"); leem_rot.setOutputFormat(['%.3f'])
    
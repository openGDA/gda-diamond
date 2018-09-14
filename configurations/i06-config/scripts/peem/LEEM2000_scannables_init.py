'''
script provided by Francesco Maccherozzi
'''
from peem.LEEEM_MODULE_CLASS import LEEM_Scannable_Class
from peem.LEEM_FOV_Rotation_CLASS import LEEM_FOV_Rotation_Class
from __main__ import leem2000  # @UnresolvedImport

exec("[objAlignX, objAlignY, leem_temp, leem_rot]= [None, None, None, None]")
objAlignX = LEEM_Scannable_Class('objAlignX',"mAmp", 36, leem2000)
objAlignY = LEEM_Scannable_Class('objAlignY',"mAmp", 37, leem2000)
leem_temp = LEEM_Scannable_Class('leem_temp',"deg", 39, leem2000)
leem_rot = LEEM_FOV_Rotation_Class('leem_rot', leem2000)
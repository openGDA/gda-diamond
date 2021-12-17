'''
Created on Jan 5, 2021

@author: fy65
'''
from scannable.positions.positionCompare import PositionCompareClass
magnetField = PositionCompareClass("magnetField", "BL10J-EA-MAGC-01:FIELD", "BL10J-EA-MAGC-01:FIELD:RBV", 0.1, "T", "%3.3f")
magnetCurrent = PositionCompareClass("magnetCurrent", "BL10J-EA-MAGC-01:DMD", "BL10J-EA-MAGC-01:DMD", 1, "A", "%3.3f")
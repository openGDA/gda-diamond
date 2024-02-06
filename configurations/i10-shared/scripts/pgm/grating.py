from i10shared import installation
from scannables.dummyListScannable import DummyListScannable
from PGM_Grating import PGM_GratingClass

print("-"*100)
print("Enable the Grating Control on PGM: 'grating'")

gratingGetPV = 'BL10I-OP-PGM-01:NLINES.VAL';
gratingSetPV = 'BL10I-OP-PGM-01:NLINES2.VAL';
gratingMoveStatusPV = "BL10I-OP-PGM-01:STATUS:MOVING";
if installation.isLive():
    grating = PGM_GratingClass('grating', gratingGetPV, gratingSetPV, gratingMoveStatusPV, unit = "lines/mm");
else:
    grating = DummyListScannable('grating', list_values = ["400 lines/mm Au", "400 lines/mm Si", "1200 lines/mm Au"], format_string = "%s")


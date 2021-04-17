from Diamond.PseudoDevices.PGM_Grating import PGM_GratingClass
from i06shared import installation
from i06shared.scannables.dummyListScannable import DummyListScannable

print "-"*100
print "Enable the Grating Control on PGM: 'grating'";

gratingGetPV = 'BL06I-OP-PGM-01:NLINES.VAL';
gratingSetPV = 'BL06I-OP-PGM-01:NLINES2.VAL';
gratingMoveStatusPV="BL06I-OP-PGM-01:STATUS:MOVING";
if installation.isLive():
    grating = PGM_GratingClass('grating', gratingGetPV, gratingSetPV,gratingMoveStatusPV);
else:
    grating = DummyListScannable('grating',list_values=[150, 400, 1200], unit="lines/mm", format_string="%d")


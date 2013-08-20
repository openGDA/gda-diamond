
from Diamond.PseudoDevices.PGM_Grating import PGM_GratingClass

print "Enable the Grating Control on PGM";

gratingGetPV = 'BL06I-OP-PGM-01:NLINES.VAL';
gratingSetPV = 'BL06I-OP-PGM-01:NLINES2.VAL';
grating = PGM_GratingClass('grating', gratingGetPV, gratingSetPV);



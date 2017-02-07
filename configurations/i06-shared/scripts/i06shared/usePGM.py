from Diamond.PseudoDevices.PGM_Grating import PGM_GratingClass

print "-"*100
print "Enable the Grating Control on PGM";

gratingGetPV = 'BL06I-OP-PGM-01:NLINES.VAL';
gratingSetPV = 'BL06I-OP-PGM-01:NLINES2.VAL';
gratingMoveStatusPV="BL06I-OP-PGM-01:STATUS:MOVING";
grating = PGM_GratingClass('grating', gratingGetPV, gratingSetPV,gratingMoveStatusPV);



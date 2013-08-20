
from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataHeaderDeviceClass

fileHeader = MetadataHeaderDeviceClass("fileHeader");

blList = [beamenergy, ringcurrent]; fileHeader.add(blList);

#bpmList= [xbpm1x, xbpm1y, xbpm2x, xbpm2y, xbpm1anglex, xbpm1angley]; fileHeader.add(bpmList);

idList = [iddgap, iddtrp, iddbrp, idugap, idutrp, idubrp, pugap]; fileHeader.add(idList);

pgmList = [pgmpitch, pgmgratpitch, cff, grating, pgmenergy]; fileHeader.add(pgmList);

energyList = [denergy, uenergy]; fileHeader.add(energyList);

slitList = [s1xgap, s1ygap]; fileHeader.add(slitList);

commonMirrorList = [m1x, m1pitch, m1qg, m6x, m6yaw, m6pitch, m6qg]; fileHeader.add(commonMirrorList);

#exitSlitList = [s6y, s6ygap]; fileHeader.add(exitSlitList);

#fileHeader.remove([testMotor2]);
add_default([fileHeader]);

#To eLog the scan
fileHeader.setScanLogger(i06);

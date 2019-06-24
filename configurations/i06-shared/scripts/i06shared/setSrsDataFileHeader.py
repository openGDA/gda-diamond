
from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataHeaderDeviceClass
from i06shared import installation
from gda.configuration.properties import LocalProperties
# from i06shared.devices.useID import denergy, uenergy
# from i06shared.devices.usePGM import grating
print "-"*100
print "SRS scan data file header setup"

fileHeader = MetadataHeaderDeviceClass("fileHeader");

import __main__  # @UnresolvedImport


blList = [__main__.beamenergy, __main__.ringcurrent]; fileHeader.add(blList);

#bpmList= [xbpm1x, xbpm1y, xbpm2x, xbpm2y, xbpm1anglex, xbpm1angley]; fileHeader.add(bpmList);

idList = [__main__.iddgap, __main__.iddtrp, __main__.iddbrp, __main__.idugap, __main__.idutrp, __main__.idubrp,__main__.pugap]; fileHeader.add(idList);

beamline = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME)

if installation.isLive() and beamline !="lab44":
    pgmList = [__main__.pgmpitch, __main__.pgmgratpitch, __main__.cff, __main__.grating, __main__.pgmenergy]
else:
    #grating requires EPICS access
    pgmList = [__main__.pgmpitch, __main__.pgmgratpitch, __main__.cff, __main__.pgmenergy]

fileHeader.add(pgmList);

if installation.isLive() and beamline !="lab44":
    energyList = [__main__.denergy, __main__.uenergy]; fileHeader.add(energyList);

slitList = [__main__.s1xgap, __main__.s1ygap]; fileHeader.add(slitList);

commonMirrorList = [__main__.m1x, __main__.m1pitch, __main__.m1qg, __main__.m6x, __main__.m6yaw, __main__.m6pitch, __main__.m6qg]; fileHeader.add(commonMirrorList);

#exitSlitList = [s6y, s6ygap]; fileHeader.add(exitSlitList);

#fileHeader.remove([testMotor2]);
#add_default([fileHeader]);

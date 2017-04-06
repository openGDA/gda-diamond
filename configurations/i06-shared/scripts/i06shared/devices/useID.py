
from Diamond.PseudoDevices.ID_Polarisation import ID_PolarisationClass;
#from Diamond.PseudoDevices.ID_Polarisation import ID_PolarisationWithMonitorClass
from Diamond.PseudoDevices.ID_Polarisation import EnergyConsolidationClass;
#from Diamond.PseudoDevices.ID_Polarisation import NewEnergyConsolidationClass;

from Diamond.PseudoDevices.ID_Polarisation import CombinedIDEnergyClass;

from Diamond.PseudoDevices.ID_Harmonic import ID_HarmonicClass

import __main__  # @UnresolvedImport
# global Energy, pgmenergy
# global denergy0, denergy1, iddpgmenergy, iddrpenergy0, iddrpenergy1
# global uenergy0, uenergy1, idupgmenergy, idurpenergy0, idurpenergy1

### Polarisation Control on ID;
print "-"*100
print "Enable the Polarisation Control on ID, creating objects:"
print "    'iddpol'      - downstream ID polarisation";
print "    'denergy'     - downstream ID energy for the current 'iddpol' polarisation with Row Phase & PGM"
print "    'hdenergy'    - downstream ID energy for the current 'iddpol' polarisation without Row Phase, with PGM "
print "    'iddrpenergy' - downstream ID energy for the current 'iddpol' polarisation with Row Phase "
print "    'idupol'      - upstream ID polarisation";
print "    'uenergy'     - upstream ID energy for the current 'iddpol' polarisation with Row Phase & PGM"
print "    'huenergy'    - upstream ID energy for the current 'iddpol' polarisation without Row Phase, with PGM "
print "    'idurpenergy' - upstream ID energy for the current 'iddpol' polarisation with Row Phase "
print "    'duenergy'    - combined energy - moves 'denergy', 'uenergy', and 'pgmenergy' concurrently"
#IDD
iddpolSetPV = 'BL06I-OP-IDD-01:SETPOL';
iddpolGetPV = 'BL06I-OP-IDD-01:POL';
iddpolStatusPV = 'BL06I-OP-IDD-01:POL:STATUS';

iddEnablePV = "SR06I-MO-SERVC-01:IDBLENA";

#IDU
idupolSetPV = 'BL06I-OP-IDU-01:SETPOL';
idupolGetPV = 'BL06I-OP-IDU-01:POL';
idupolStatusPV = 'BL06I-OP-IDU-01:POL:STATUS';

iduEnablePV = "SR06I-MO-SERVC-21:IDBLENA";

__main__.iddpol = ID_PolarisationClass('iddpol', iddpolSetPV, iddpolGetPV, iddpolStatusPV, iddEnablePV);
__main__.denergy = EnergyConsolidationClass('denergy', __main__.iddpol, __main__.denergy0, __main__.denergy1, inPositionTolerance = 0.001);
__main__.hdenergy = EnergyConsolidationClass('hdenergy', __main__.iddpol, __main__.iddpgmenergy,__main__. denergy1, inPositionTolerance = 0.001);
#newdenergy = NewEnergyConsolidationClass('denergy', iddpol, denergy0, denergy1);
__main__.iddrpenergy = EnergyConsolidationClass('iddrpenergy', __main__.iddpol, __main__.iddrpenergy0, __main__.iddrpenergy1, inPositionTolerance = 0.001);
__main__.Energy.addGroupMember(__main__.denergy);
__main__.Energy.addGroupMember(__main__.hdenergy);
__main__.Energy.addGroupMember(__main__.iddrpenergy);

__main__.idupol = ID_PolarisationClass('idupol', idupolSetPV, idupolGetPV, idupolStatusPV, iduEnablePV);
__main__.uenergy = EnergyConsolidationClass('uenergy', __main__.idupol, __main__.uenergy0, __main__.uenergy1, inPositionTolerance = 0.001);
__main__.huenergy = EnergyConsolidationClass('huenergy', __main__.idupol, __main__.idupgmenergy, __main__.uenergy1, inPositionTolerance = 0.001);
__main__.idurpenergy = EnergyConsolidationClass('idurpenergy', __main__.idupol, __main__.idurpenergy0, __main__.idurpenergy1, inPositionTolerance = 0.001);
__main__.Energy.addGroupMember(__main__.uenergy);
__main__.Energy.addGroupMember(__main__.huenergy);
__main__.Energy.addGroupMember(__main__.idurpenergy);

__main__.duenergy = CombinedIDEnergyClass("duenergy", __main__.denergy, __main__.uenergy, __main__.pgmenergy);
__main__.Energy.addGroupMember(__main__.duenergy);

### Enable the Harmonic Control on ID";
print "-"*100
print "Enable the Harmonic Control on ID, creating objects:"
print "    'iddhar' - downstrean ID harmonic"
print "    'iduhar' - upstream ID harmonic"

pvHarmonicIDD = "BL06I-OP-IDD-01:HARMONIC";
__main__.iddhar = ID_HarmonicClass("iddhar", pvHarmonicIDD);

pvHarmonicIDU = "BL06I-OP-IDU-01:HARMONIC";
__main__.iduhar = ID_HarmonicClass("iduhar", pvHarmonicIDU);



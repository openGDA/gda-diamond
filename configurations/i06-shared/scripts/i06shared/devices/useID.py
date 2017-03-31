
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

iddpol = ID_PolarisationClass('iddpol', iddpolSetPV, iddpolGetPV, iddpolStatusPV, iddEnablePV);
denergy = EnergyConsolidationClass('denergy', iddpol, __main__.denergy0, __main__.denergy1, inPositionTolerance = 0.001);
hdenergy = EnergyConsolidationClass('hdenergy', iddpol, __main__.iddpgmenergy,__main__. denergy1, inPositionTolerance = 0.001);
#newdenergy = NewEnergyConsolidationClass('denergy', iddpol, denergy0, denergy1);
iddrpenergy = EnergyConsolidationClass('iddrpenergy', iddpol, __main__.iddrpenergy0, __main__.iddrpenergy1, inPositionTolerance = 0.001);
__main__.Energy.addGroupMember(denergy);
__main__.Energy.addGroupMember(hdenergy);
__main__.Energy.addGroupMember(iddrpenergy);

idupol = ID_PolarisationClass('idupol', idupolSetPV, idupolGetPV, idupolStatusPV, iduEnablePV);
uenergy = EnergyConsolidationClass('uenergy', idupol, __main__.uenergy0, __main__.uenergy1, inPositionTolerance = 0.001);
huenergy = EnergyConsolidationClass('huenergy', idupol, __main__.idupgmenergy, __main__.uenergy1, inPositionTolerance = 0.001);
idurpenergy = EnergyConsolidationClass('idurpenergy', idupol, __main__.idurpenergy0, __main__.idurpenergy1, inPositionTolerance = 0.001);
__main__.Energy.addGroupMember(uenergy);
__main__.Energy.addGroupMember(huenergy);
__main__.Energy.addGroupMember(idurpenergy);

duenergy = CombinedIDEnergyClass("duenergy", denergy, uenergy, __main__.pgmenergy);
__main__.Energy.addGroupMember(duenergy);

### Enable the Harmonic Control on ID";
print "-"*100
print "Enable the Harmonic Control on ID, creating objects:"
print "    'iddhar' - downstrean ID harmonic"
print "    'iduhar' - upstream ID harmonic"

pvHarmonicIDD = "BL06I-OP-IDD-01:HARMONIC";
iddhar = ID_HarmonicClass("iddhar", pvHarmonicIDD);

pvHarmonicIDU = "BL06I-OP-IDU-01:HARMONIC";
iduhar = ID_HarmonicClass("iduhar", pvHarmonicIDU);



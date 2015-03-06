
from Diamond.PseudoDevices.ID_Polarisation import ID_PolarisationClass;
#from Diamond.PseudoDevices.ID_Polarisation import ID_PolarisationWithMonitorClass
from Diamond.PseudoDevices.ID_Polarisation import EnergyConsolidationClass;
#from Diamond.PseudoDevices.ID_Polarisation import NewEnergyConsolidationClass;

from Diamond.PseudoDevices.ID_Polarisation import CombinedIDEnergyClass;

from Diamond.PseudoDevices.ID_Harmonic import ID_HarmonicClass

global Energy, pgmenergy
global denergy0, denergy1, iddpgmenergy, iddrpenergy0, iddrpenergy1
global uenergy0, uenergy1, idupgmenergy, idurpenergy0, idurpenergy1

### Polarisation Control on ID;
print "Enable the Polarisation Control on ID";

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
denergy = EnergyConsolidationClass('denergy', iddpol, denergy0, denergy1, inPositionTolerance = 0.05);
hdenergy = EnergyConsolidationClass('hdenergy', iddpol, iddpgmenergy, denergy1, inPositionTolerance = 0.05);
#newdenergy = NewEnergyConsolidationClass('denergy', iddpol, denergy0, denergy1);
iddrpenergy = EnergyConsolidationClass('iddrpenergy', iddpol, iddrpenergy0, iddrpenergy1, inPositionTolerance = 0.05);
Energy.addGroupMember(denergy);
Energy.addGroupMember(hdenergy);
Energy.addGroupMember(iddrpenergy);

idupol = ID_PolarisationClass('idupol', idupolSetPV, idupolGetPV, idupolStatusPV, iduEnablePV);
uenergy = EnergyConsolidationClass('uenergy', idupol, uenergy0, uenergy1, inPositionTolerance = 0.05);
huenergy = EnergyConsolidationClass('uenergy', idupol, idupgmenergy, uenergy1, inPositionTolerance = 0.05);
idurpenergy = EnergyConsolidationClass('idurpenergy', idupol, idurpenergy0, idurpenergy1, inPositionTolerance = 0.05);
Energy.addGroupMember(uenergy);
Energy.addGroupMember(huenergy);
Energy.addGroupMember(idurpenergy);


duenergy = CombinedIDEnergyClass("duenergy", denergy, uenergy, pgmenergy);
Energy.addGroupMember(duenergy);

### Enable the Harmonic Control on ID";
print "Enable the Harmonic Control on ID";

pvHarmonicIDD = "BL06I-OP-IDD-01:HARMONIC";
iddhar = ID_HarmonicClass("iddhar", pvHarmonicIDD);

pvHarmonicIDU = "BL06I-OP-IDU-01:HARMONIC";
iduhar = ID_HarmonicClass("iduhar", pvHarmonicIDU);



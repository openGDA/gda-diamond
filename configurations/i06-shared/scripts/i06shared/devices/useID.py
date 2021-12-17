
from Diamond.PseudoDevices.ID_Polarisation import ID_PolarisationClass;
from Diamond.PseudoDevices.ID_Polarisation import EnergyConsolidationClass;
from Diamond.PseudoDevices.ID_Polarisation import CombinedIDEnergyClass;
from Diamond.PseudoDevices.ID_Harmonic import ID_HarmonicClass

### Polarisation Control on ID;
print("-"*100)
print("Enable the Polarisation Control on ID, creating objects:")
print("    'iddpol'      - downstream ID polarisation")
print("    'denergy'     - downstream ID energy for the current 'iddpol' polarisation with Row Phase & PGM")
print("    'hdenergy'    - downstream ID energy for the current 'iddpol' polarisation without Row Phase, with PGM ")
print("    'iddrpenergy' - downstream ID energy for the current 'iddpol' polarisation with Row Phase ")
print("    'idupol'      - upstream ID polarisation")
print("    'uenergy'     - upstream ID energy for the current 'iddpol' polarisation with Row Phase & PGM")
print("    'huenergy'    - upstream ID energy for the current 'iddpol' polarisation without Row Phase, with PGM ")
print("    'idurpenergy' - upstream ID energy for the current 'iddpol' polarisation with Row Phase ")
print("    'duenergy'    - combined energy - moves 'denergy', 'uenergy', and 'pgmenergy' concurrently")
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
denergy = EnergyConsolidationClass('denergy', iddpol, denergy0, denergy1, inPositionTolerance = 0.001);  # @UndefinedVariable
hdenergy = EnergyConsolidationClass('hdenergy', iddpol, iddpgmenergy, denergy1, inPositionTolerance = 0.001);  # @UndefinedVariable
iddrpenergy = EnergyConsolidationClass('iddrpenergy', iddpol, iddrpenergy0, iddrpenergy1, inPositionTolerance = 0.001);  # @UndefinedVariable
Energy.addGroupMember(denergy);  # @UndefinedVariable
Energy.addGroupMember(hdenergy);  # @UndefinedVariable
Energy.addGroupMember(iddrpenergy);  # @UndefinedVariable

idupol = ID_PolarisationClass('idupol', idupolSetPV, idupolGetPV, idupolStatusPV, iduEnablePV);
uenergy = EnergyConsolidationClass('uenergy', idupol, uenergy0, uenergy1, inPositionTolerance = 0.001);  # @UndefinedVariable
huenergy = EnergyConsolidationClass('huenergy', idupol, idupgmenergy, uenergy1, inPositionTolerance = 0.001);  # @UndefinedVariable
idurpenergy = EnergyConsolidationClass('idurpenergy', idupol, idurpenergy0, idurpenergy1, inPositionTolerance = 0.001);  # @UndefinedVariable
Energy.addGroupMember(uenergy);  # @UndefinedVariable
Energy.addGroupMember(huenergy);  # @UndefinedVariable
Energy.addGroupMember(idurpenergy);  # @UndefinedVariable

duenergy = CombinedIDEnergyClass("duenergy", denergy, uenergy, pgmenergy);  # @UndefinedVariable
Energy.addGroupMember(duenergy);  # @UndefinedVariable

### Enable the Harmonic Control on ID";
print("-"*100)
print("Enable the Harmonic Control on ID, creating objects:")
print("    'iddhar' - downstrean ID harmonic")
print("    'iduhar' - upstream ID harmonic")

pvHarmonicIDD = "BL06I-OP-IDD-01:HARMONIC";
iddhar = ID_HarmonicClass("iddhar", pvHarmonicIDD);

pvHarmonicIDU = "BL06I-OP-IDU-01:HARMONIC";
iduhar = ID_HarmonicClass("iduhar", pvHarmonicIDU);



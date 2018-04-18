from Diamond.energyScannableSwitchable import EnergyScannableSwitchable
from Diamond.energyScannableSwitcher import EnergyScannableSwitcher
from scannable.id_energys.idu_energy_gap import idu_circ_neg_energy,\
    idu_circ_pos_energy, idu_lin_hor_energy, idu_lin_ver_energy

print "-"*100
print "Creating Switchable energy scannables and the corresponding Swticher scannables:"
print "    1. 'idu_pos_neg_switchable' and 'idu_pos_neg_switcher' - Switch between 'idu_circ_pos_energy' and 'idu_circ_neg_energy'"
print "    2. 'idu_hor_ver_switchable' and 'idu_hor_ver_switcher' - Switch between 'idu_lin_hor_energy' and 'idu_lin_ver_energy'"
# Switchable scannable
idu_pos_neg_switchable = EnergyScannableSwitchable('idu_pos_neg_switchable', [idu_circ_pos_energy, idu_circ_neg_energy])
idu_pos_neg_switchable.setLevel(6)

# Switcher scannable
idu_pos_neg_switcher = EnergyScannableSwitcher('idu_pos_neg_switcher', idu_pos_neg_switchable)
idu_pos_neg_switcher.setLevel(6)

idu_hor_ver_switchable = EnergyScannableSwitchable('idu_hor_ver_switchable', [idu_lin_hor_energy, idu_lin_ver_energy])
idu_hor_ver_switchable.setLevel(6)

# Switcher scannable
idu_hor_ver_switcher = EnergyScannableSwitcher('idu_hor_ver_switcher', idu_hor_ver_switchable)
idu_hor_ver_switcher.setLevel(6)

print
print "==== idu Switchable energy scannables and Switcher scannables done.==== "

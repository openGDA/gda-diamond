from Diamond.energyScannableSwitchable import EnergyScannableSwitchable
from Diamond.energyScannableSwitcher import EnergyScannableSwitcher
from scannables.id_energys.idd_energy_gap import idd_circ_neg_energy, \
    idd_circ_pos_energy, idd_lin_hor_energy, idd_lin_ver_energy

print("-"*100)
print("Creating Switchable energy scannables and the corresponding Swticher scannables:")
print("    1. 'idd_pos_neg_switchable' and 'idd_pos_neg_switcher' - Switch between 'idd_circ_pos_energy' and 'idd_circ_neg_energy'")
print("    2. 'idd_hor_ver_switchable' and 'idd_hor_ver_switcher' - Switch between 'idd_lin_hor_energy' and 'idd_lin_ver_energy'")
# Switchable scannable
idd_pos_neg_switchable = EnergyScannableSwitchable('idd_pos_neg_switchable', [idd_circ_pos_energy, idd_circ_neg_energy])
idd_pos_neg_switchable.setLevel(6)

# Switcher scannable
idd_pos_neg_switcher = EnergyScannableSwitcher('idd_pos_neg_switcher', idd_pos_neg_switchable)
idd_pos_neg_switcher.setLevel(6)

idd_hor_ver_switchable = EnergyScannableSwitchable('idd_hor_ver_switchable', [idd_lin_hor_energy, idd_lin_ver_energy])
idd_hor_ver_switchable.setLevel(6)

# Switcher scannable
idd_hor_ver_switcher = EnergyScannableSwitcher('idd_hor_ver_switcher', idd_hor_ver_switchable)
idd_hor_ver_switcher.setLevel(6)

print('\n')
print("==== idd Switchable energy scannables and Switcher scannables done.==== ")

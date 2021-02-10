from gda.epics.CAClient import put as caput

# set the pilatus threshold accordingto energy
def pilatus_set_energy_threshold(energy):
    energy_threshold = max([energy/2.0+0.1,9.1])
    caput('BL11K-EA-PILAT-01:CAM:ThresholdEnergy',energy_threshold)
    return energy_threshold

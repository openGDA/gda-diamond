'''
The template script for users to set experiment input parameters for a q-scan.
These parameters are organised into 4 dictionary variables as each of them will be changed for different situations.
These 4 dictionary are merged before passing to the qscan method in module dataCollection.qScan2 to perform the data collection.

Important Notes:
1. If and when you need to change any key name in these dictionary, you must update the qscan method in module dataCollection.qScan2 accordingly!
2. If you add more key names to these dictionaries, you must access their value in the qscan method in module dataCollection.qScan2 by its key-name.
3. The ID gap is calculated using idgap_fn(Ep, polarisation) function in module calibration.Energy2Gap4ID, which extracted from Energy_class.py,
   so when you update Energy calibration in Energy_class.py, you must update Energy2Gap4ID.py

Created on 12 Jan 2018
Tested in dummy mode on 12 Jan 2018

@author: fy65
'''
from dataCollection.qScan2 import qscan

###########################################################
# input of the lattice parameter
latticeparameters={
    'a' : 3.9,
    'c' : 13.2
    }

###########################################################
# definition of the sample and ctape position along (pi,0)
motorpositions={
    'sax_sample' : -0.076,
    'say_sample' : -1.65,
    'saz_sample' : 0.74,
    
    'sax_ctape' : 0.93,
    'say_ctape' : -1.65,
    'saz_ctape' : -1.26,
    
    'saazimuth_val' : 3,
    'satilt_val' : -1.9,
    'sapolar_offset' : +1.0
    }

#####################################################################################################
# definition of the q range and the steps along (pi,0)
qrange={
    'qStart' : 0.26,
    'qEnd' : 0.5,
    'qStep' : 0.02,
    }
n_points = int((qrange['qEnd']-qrange['qStart'])/qrange['qStep'] + 1) 
qrange['n_points']=n_points

#####################################################################################################
# q scan over the entire q range using the M5lq mirror, s5v1gap = 10, LV, energy = 935.8 eV, (pi,0)
print('scan over the entire q range using the M5lq mirror, s5v1gap = 10, LV, energy = 935.8 eV, (pi,0)')
# Switch to LV
experimentparameters={
    'beam_energy' : 935.8,
    'beam_polarisation' : 'LV',
    's5v1gap_val' : 10,
    'energy_sample' : 932.5,
    'thts_val' : 146.0,
    'vec' : 1,   #(pi,0)
    'n_frames_per_point_sample' : 20,
    'sample_exposure_time' : 30,     # in seconds
    'n_frames_per_point_elastic' : 6,
    'elastic_exposure_time' : 10    #in seconds
    }

parameters=dict(experimentparameters.items()+qrange.items()+motorpositions.items()+latticeparameters.items())

qscan(**parameters)

###################################################################
# definition of the q range and the steps along (pi,0)
qrange={
    'qStart' : -0.5,
    'qEnd' : 0.5,
    'qStep' : 0.02,
    }
n_points = int((qrange['qEnd']-qrange['qStart'])/qrange['qStep'] + 1) 
qrange['n_points']=n_points

#####################################################################################################
# q scan over the entire q range using the M5lq mirror, s5v1gap = 10, LH, energy = 935.8 eV, (pi,0)
print('scan over the entire q range using the M5lq mirror, s5v1gap = 10, LH, energy = 935.8 eV, (pi,0)')
# Switch to LH
experimentparameters={
    'beam_energy' : 935.8,
    'beam_polarisation' : 'LH',
    's5v1gap_val' : 10,
    'energy_sample' : 932.5,
    'thts_val' : 146.0,
    'vec' : 1,   #(pi,0)
    'n_frames_per_point_sample' : 20,
    'sample_exposure_time' : 30,     # in seconds
    'n_frames_per_point_elastic' : 6,
    'elastic_exposure_time' : 10    #in seconds
    }
parameters=dict(experimentparameters.items()+qrange.items()+motorpositions.items()+latticeparameters.items())

qscan(**parameters)

###################################################################


###########################################################
# definition of the sample and ctape position along (pi,pi)

motorpositions={
    'sax_sample' : -0.126,
    'say_sample' : -1.65,
    'saz_sample' : 1.9,
    
    'sax_ctape' : 1.007,
    'say_ctape' : -1.65,
    'saz_ctape' : -1.0,
    
    'saazimuth_val' : -42,
    'satilt_val' : -3.7,
    'sapolar_offset' : -3.0
    }

#####################################################################################################
# definition of the q range and the steps along (pi,pi)
qrange={
    'qStart' : -0.07,
    'qEnd' : 0.35,
    'qStep' : 0.02,
    }
n_points = int((qrange['qEnd']-qrange['qStart'])/qrange['qStep'] + 1) 
qrange['n_points']=n_points

#####################################################################################################
# q scan over the entire q range using the M5lq mirror, s5v1gap = 10, LV, energy = 935.8 eV, (pi,pi)
print('scan over the entire q range using the M5lq mirror, s5v1gap = 10, LV, energy = 935.8 eV, (pi,pi)')
# Switch to LV
experimentparameters={
    'beam_energy' : 935.8,
    'beam_polarisation' : 'LV',
    's5v1gap_val' : 10,
    'energy_sample' : 932.5,
    'thts_val' : 146.0,
    'vec' : 2,   #(pi,pi)
    'n_frames_per_point_sample' : 20,
    'sample_exposure_time' : 30,     # in seconds
    'n_frames_per_point_elastic' : 6,
    'elastic_exposure_time' : 10    #in seconds
    }
parameters=dict(experimentparameters.items()+qrange.items()+motorpositions.items()+latticeparameters.items())

qscan(**parameters)

#####################################################################################################
# definition of the q range and the steps along (pi,pi)
qrange={
    'qStart' : -0.35,
    'qEnd' : 0.35,
    'qStep' : 0.02,
    }
n_points = int((qrange['qEnd']-qrange['qStart'])/qrange['qStep'] + 1) 
qrange['n_points']=n_points

#####################################################################################################
# q scan over the entire q range using the M5lq mirror, s5v1gap = 10, LH, energy = 935.8 eV, (pi,pi)
print('scan over the entire q range using the M5lq mirror, s5v1gap = 10, LH, energy = 935.8 eV, (pi,pi)')

# Switch to LH
experimentparameters={
    'beam_energy' : 935.8,
    'beam_polarisation' : 'LH',
    's5v1gap_val' : 10,
    'energy_sample' : 932.5,
    'thts_val' : 146.0,
    'vec' : 2,   #(pi,pi)
    'n_frames_per_point_sample' : 20,
    'sample_exposure_time' : 30,     # in seconds
    'n_frames_per_point_elastic' : 6,
    'elastic_exposure_time' : 10    #in seconds
    }
parameters=dict(experimentparameters.items()+qrange.items()+motorpositions.items()+latticeparameters.items())

qscan(**parameters)


###################################################################

print('Macro is completed !!!')
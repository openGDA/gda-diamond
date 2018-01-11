'''
Created on 16th Dec 2017

@author: i21user
'''
from dataCollection.qScan import qscan

###########################################################
# input of the lattice parameter
a = 3.9
c = 13.2

###########################################################
# definition of the sample and ctape position along (pi,0)

sax_LCO_pi0 = -0.076
say_LCO_pi0 = -1.65
saz_LCO_pi0 = 0.74

sax_ctape_pi0 = 0.93
say_ctape_pi0 = -1.65
saz_ctape_pi0 = -1.26

saazimuth_LCO_pi0 = 3
satilt_LCO_pi0 = -1.9
sapolaroffset_pi0 = +1.0

#####################################################################################################
# definition of the q range and the steps along (pi,0)

qStart_pi0 = 0.26
qEnd_pi0 = 0.5
qStep_pi0 = 0.02
n_points_pi0 = int((qEnd_pi0-qStart_pi0)/qStep_pi0 + 1) 

#####################################################################################################
# q scan over the entire q range using the M5lq mirror, s5v1gap = 10, LV, energy = 935.8 eV, (pi,0)
print('scan over the entire q range using the M5lq mirror, s5v1gap = 10, LV, energy = 935.8 eV, (pi,0)')
# Switch to LV
beam_energy=935.8
beam_polarisation='LV'
s5v1gap_val=10
energy_sample=932.5
thts_val=146.0
vec=1 #(pi,0)
n_frames_per_point_sample=20
sample_exposure_time=30     # in seconds
n_frames_per_point_elastic=6
elastic_exposure_time=10    #in seconds

qscan(beam_energy,beam_polarisation,s5v1gap_val,saazimuth_LCO_pi0,satilt_LCO_pi0,say_LCO_pi0,\
            qStart_pi0,qStep_pi0,n_points_pi0,energy_sample,sapolaroffset_pi0,thts_val,vec,a,\
            sax_LCO_pi0,saz_LCO_pi0,n_frames_per_point_sample,sample_exposure_time,\
            sax_ctape_pi0,saz_ctape_pi0,n_frames_per_point_elastic,elastic_exposure_time)

###################################################################
# definition of the q range and the steps along (pi,0)

qStart_pi0 = -0.5
qEnd_pi0 = 0.5
qStep_pi0 = 0.02
n_points_pi0 = int((qEnd_pi0-qStart_pi0)/qStep_pi0 + 1) 

#####################################################################################################
# q scan over the entire q range using the M5lq mirror, s5v1gap = 10, LH, energy = 935.8 eV, (pi,0)
print('scan over the entire q range using the M5lq mirror, s5v1gap = 10, LH, energy = 935.8 eV, (pi,0)')
# Switch to LH
beam_energy=935.8
beam_polarisation='LH'
s5v1gap_val=10
energy_sample=932.5
thts_val=146.0
vec=1 #(pi,0)
n_frames_per_point_sample=20
sample_exposure_time=30     # in seconds
n_frames_per_point_elastic=6
elastic_exposure_time=10    #in seconds

qscan(beam_energy,beam_polarisation,s5v1gap_val,saazimuth_LCO_pi0,satilt_LCO_pi0,say_LCO_pi0,\
            qStart_pi0,qStep_pi0,n_points_pi0,energy_sample,sapolaroffset_pi0,thts_val,vec,a,\
            sax_LCO_pi0,saz_LCO_pi0,n_frames_per_point_sample,sample_exposure_time,\
            sax_ctape_pi0,saz_ctape_pi0,n_frames_per_point_elastic,elastic_exposure_time)

###################################################################


###########################################################
# definition of the sample and ctape position along (pi,pi)

sax_LCO_pipi = -0.126
say_LCO_pipi = -1.65
saz_LCO_pipi = 1.9

sax_ctape_pipi = 1.007
say_ctape_pipi = -1.65
saz_ctape_pipi = -1.0

saazimuth_LCO_pipi = -42
satilt_LCO_pipi = -3.7
sapolaroffset_pipi = -3.0

#####################################################################################################
# definition of the q range and the steps along (pi,pi)

qStart_pipi = -0.07
qEnd_pipi = 0.35
qStep_pipi = 0.02
n_points_pipi = int((qEnd_pipi-qStart_pipi)/qStep_pipi + 1)

#####################################################################################################
# q scan over the entire q range using the M5lq mirror, s5v1gap = 10, LV, energy = 935.8 eV, (pi,pi)
print('scan over the entire q range using the M5lq mirror, s5v1gap = 10, LV, energy = 935.8 eV, (pi,pi)')
# Switch to LV
beam_energy=935.8
beam_polarisation='LV'
s5v1gap_val=10
energy_sample=932.5
thts_val=146.0
vec=2 #(pi,pi)
n_frames_per_point_sample=20
sample_exposure_time=30     # in seconds
n_frames_per_point_elastic=6
elastic_exposure_time=10    #in seconds

qscan(beam_energy,beam_polarisation,s5v1gap_val,saazimuth_LCO_pipi,satilt_LCO_pipi,say_LCO_pipi,\
            qStart_pipi,qStep_pipi,n_points_pipi,energy_sample,sapolaroffset_pipi,thts_val,vec,a,\
            sax_LCO_pipi,saz_LCO_pipi,n_frames_per_point_sample,sample_exposure_time,\
            sax_ctape_pipi,saz_ctape_pipi,n_frames_per_point_elastic,elastic_exposure_time)


#####################################################################################################
# definition of the q range and the steps along (pi,pi)

qStart_pipi = -0.35
qEnd_pipi = 0.35
qStep_pipi = 0.02
n_points_pipi = int((qEnd_pipi-qStart_pipi)/qStep_pipi + 1)

#####################################################################################################
# q scan over the entire q range using the M5lq mirror, s5v1gap = 10, LH, energy = 935.8 eV, (pi,pi)
print('scan over the entire q range using the M5lq mirror, s5v1gap = 10, LH, energy = 935.8 eV, (pi,pi)')

# Switch to LH
beam_energy=935.8
beam_polarisation='LH'
s5v1gap_val=10
energy_sample=932.5
thts_val=146.0
vec=2 #(pi,pi)
n_frames_per_point_sample=20
sample_exposure_time=30     # in seconds
n_frames_per_point_elastic=6
elastic_exposure_time=10    #in seconds

qscan(beam_energy,beam_polarisation,s5v1gap_val,saazimuth_LCO_pipi,satilt_LCO_pipi,say_LCO_pipi,\
            qStart_pipi,qStep_pipi,n_points_pipi,energy_sample,sapolaroffset_pipi,thts_val,vec,a,\
            sax_LCO_pipi,saz_LCO_pipi,n_frames_per_point_sample,sample_exposure_time,\
            sax_ctape_pipi,saz_ctape_pipi,n_frames_per_point_elastic,elastic_exposure_time)


###################################################################

print('Macro is completed !!!')
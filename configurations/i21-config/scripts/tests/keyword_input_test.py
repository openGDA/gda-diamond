'''
Created on 11 Jan 2018

@author: fy65
'''
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
print parameters
def show_input_values(**kwargs):
    print 'beam_energy       = %f' % (kwargs['beam_energy'])
    print 'beam_polarisation = %s' % (kwargs['beam_polarisation'])
    print 's5v1gap_val       = %f' % (kwargs['s5v1gap_val'])
    print 'energy_sample     = %f' % (kwargs['energy_sample'])
    print 'thts_val          = %f' % (kwargs['thts_val'])
    print 'vec               = %d' % (kwargs['vec'])    #(pi,0)
    print 'n_frames_per_point_sample  = %d' % (kwargs['n_frames_per_point_sample'])
    print 'sample_exposure_time       = %f' % (kwargs['sample_exposure_time'])     # in seconds
    print 'n_frames_per_point_elastic = %d' % (kwargs['n_frames_per_point_elastic'])
    print 'elastic_exposure_time      = %f' % (kwargs['elastic_exposure_time'])    #in seconds

    
show_input_values(**parameters)
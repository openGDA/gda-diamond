'''
Created on 26th Mar 2019

@author: i21user

modified MGF 17/IX/19
modified on 12/10/21 by SA 
'''

import math as mh
from acquisition.darkImageAcqusition import acquire_dark_image
from gdaserver import th, sample_stage, s5v1gap, energy, andor, difftth, fastshutter, spech, m4c1, checkbeam  # @UnresolvedImport
from gdascripts.utils import frange
from shutters.detectorShutterControl import primary
from functions.go_founctions import go
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
from acquisition.acquireImages import acquireRIXS
from acquisition.acquireCarbonTapeImages import acquire_ctape_image

LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]
   
#########################################################################


#########################################################################
# definition of the sample and ctape position along (pi,0)
#########################################################################

x_sample_pi0 = -1.357
y_sample_pi0 = -1.5
z_sample_pi0 = -0.9
th_sample_pi0 = 138.16
phi_sample_pi0 = -50.7
chi_sample_pi0 = 3.3


x_ctape_pi0 = +0.39
y_ctape_pi0 = -1.5
z_ctape_pi0 = -3.5
th_ctape_pi0 = 138.16
phi_ctape_pi0 = -50.7
chi_ctape_pi0 = 3.3

sample_pi0_values = [x_sample_pi0,y_sample_pi0,z_sample_pi0,th_sample_pi0,phi_sample_pi0,chi_sample_pi0]
ctape_pi0_values = [x_ctape_pi0,y_ctape_pi0,z_ctape_pi0,th_ctape_pi0,phi_ctape_pi0,chi_ctape_pi0]

def samplestage(positions):
    '''move to sample stage to given positions concurrently and wait until all moves complete
    '''
    sample_stage.moveTo(positions)
    
def sample_pi0():
    '''move to sample_pi0 position concurrently and wait until all moves complete
    '''
    samplestage(sample_pi0_values)

def ctape_pi0():
    '''move to ctape_pi0 position concurrently and wait until all moves complete
    '''
    samplestage(ctape_pi0_values)


#################################################################
# definition of the sample and ctape position along (pi,pi)
#################################################################

x_sample_pipi=-1.373
y_sample_pipi=-2.0
z_sample_pipi=+0.9
th_sample_pipi = 138.16
phi_sample_pipi = -50.7
chi_sample_pipi = 3.3


x_ctape_pipi=+0.18
y_ctape_pipi=-2.0
z_ctape_pipi=-2.8
th_ctape_pipi = 138.16
phi_ctape_pipi = -50.7
chi_ctape_pipi = 3.3

sample_pipi_values = [x_sample_pipi,y_sample_pipi,z_sample_pipi,th_sample_pipi,phi_sample_pipi,chi_sample_pipi]
ctape_pipi_values = [x_ctape_pipi,y_ctape_pipi,z_ctape_pipi,th_ctape_pipi,phi_ctape_pipi,chi_ctape_pipi]

def sample_pipi():
    '''move to sample_pipi position concurrently and wait until all moves complete
    '''
    samplestage(sample_pipi_values)

def ctape_pipi():
    '''move to ctape_pipi position concurrently and wait until all moves complete
    '''
    samplestage(ctape_pipi_values)
    

#####################################
# defining exit slit opening
#####################################
s5v1gap.moveTo(20)

#####################################
# Information for spech calculation
#####################################
specgammaval = 12 #Needs to be updated if gamma is changed.
Detector_pxsz = 0.01358
E_dispersion = 0.00675  #needs to be updated to the current experimental value
energy_val_fix = 931.4  #Resonant energy
spech_val_fix = 1365.554  #Spech corresponding to the resonant energy

#####################################
#Defining CCD parameters
#####################################

sample_no_images = 4
ctape_no_images = 1

sample_exposure_time = 300
ctape_exposure_time = 120

##################################################################
#We acquire some dark images before the E scan:
##################################################################
#Dark Image
energy.moveTo(810)
acquire_dark_image(1, andor, sample_exposure_time)


######################################
# moving diode to 0
######################################
difftth.moveTo(0)

#################################################################
# Define Energies and Theta values at which we want to measure
#################################################################

th_list = frange(20,140.01,10)
energy_list = frange(925,935.01,0.4)

#################################################################
#Defining E_initial
#################################################################

E_initial = 931

#################################################################
###################### ACQUIRING DATA ###########################
#################################################################
primary()
fastshutter('Open')

###define experimental logics to collecting data from carbon tape and sample
def collect_data(ctape,sample):
    '''collect experiment data from ctape and sample
    @param ctape: function that moves beam to ctape position
    @param sample: function that moves beam to sample position  
    '''
    for th_val in th_list:
        th.moveTo(th_val)
        for energy_val in energy_list:
            print ("move energy to %f " % energy_val)
            energy.moveTo(energy_val)
            spech_val = spech_val_fix+(energy_val_fix-energy_val)*Detector_pxsz*mh.sin(specgammaval*mh.pi/180)/E_dispersion
            spech.moveTo(spech_val)
            
            ctape()
            print('cTape at th = %.3f and Energy = %.3f'%(th_val,energy_val))
            acquire_ctape_image(ctape_no_images, andor, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
            print('******************************************************************')
    
            sample()
            print('RIXS at th = %.3f and Energy = %.3f'%(th_val,energy_val))
            acquireRIXS(sample_no_images, andor, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
            print('******************************************************************')

#############################################################
###################### SAMPLE (PI,0)########################
#############################################################

#####################################################
# energy scan with LH along (pi, 0)
go(E_initial, LH)
collect_data(ctape_pi0, sample_pi0)
    

#####################################################
#energy scan with LV along (pi, 0)
go(E_initial, LV)
collect_data(ctape_pi0, sample_pi0)


#################################################


#############################################################
###################### SAMPLE (PI,PI)########################
#############################################################

##########################################################
# energy scan with LH along (pi, pi)
go(E_initial, LH)
collect_data(ctape_pipi, sample_pipi)
    
#################################################


#####################################################
#energy scan with LV along (pi, pi)
go(E_initial, LV)
collect_data(ctape_pipi, sample_pipi)

        
#################################################
#################################################


# move spech to the optimised position for qscan (resonance)
energy.moveTo(energy_val_fix)
spech.moveTo(spech_val_fix)


#####################################################################
print('Macro is completed !!!')
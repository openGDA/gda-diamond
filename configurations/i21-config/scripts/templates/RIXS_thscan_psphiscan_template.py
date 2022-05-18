'''
Created on 12th Oct 2021

@author: Stefano Agrestini
'''

import math as mh
from gdaserver import x,y,z,th,phi,chi, s5v1gap, energy, andor, difftth, fastshutter, spech, m4c1, checkbeam  # @UnresolvedImport
from acquisition.darkImageAcqusition import acquire_dark_image
from gdascripts.utils import frange
from shutters.detectorShutterControl import primary
from functions.go_founctions import go
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
from acquisition.acquireImages import acquireRIXS

LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]

#########################################################################


#########################################################################
# definition of the sample and ctape position along (pi,0)
#########################################################################

x_sample_pi0=-1.357
y_sample_pi0=-1.5
z_sample_pi0=-0.9
th_sample_pi0 = 138.16
phi_sample_pi0 = -50.7
chi_sample_pi0 = 3.3

x_ctape_pi0=+0.39
y_ctape_pi0=-1.5
z_ctape_pi0=-3.5
th_ctape_pi0 = 138.16
phi_ctape_pi0 = -50.7
chi_ctape_pi0 = 3.3

def sample_pi0():
    '''move to sample_pi0 position concurrently and wait until all moves complete
    '''
    x.asynchronousMovTo(x_sample_pi0)
    y.asynchronousMovTo(y_sample_pi0)
    z.asynchronousMovTo(z_sample_pi0)
    th.asynchronousMovTo(th_sample_pi0)
    phi.asynchronousMovTo(phi_sample_pi0)
    chi.asynchronousMovTo(chi_sample_pi0)
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    th.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
   

def ctape_pi0():
    '''move to ctape_pi0 position concurrently and wait until all moves complete
    '''
    x.asynchronousMovTo(x_ctape_pi0)
    y.asynchronousMovTo(y_ctape_pi0)
    z.asynchronousMovTo(z_ctape_pi0)
    th.asynchronousMovTo(th_ctape_pi0)
    phi.asynchronousMovTo(phi_ctape_pi0)
    chi.asynchronousMovTo(chi_ctape_pi0)
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    th.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()



#####################################
# defining exit slit opening
#####################################
exit_slit = 20
s5v1gap.moveTo(exit_slit)
#####################################


######################################
# moving diode to 0
######################################
difftth.moveTo(0)

####################################################################################################
#Defining CCD parameters
####################################################################################################

sample_no_images = 1
ctape_no_images = 1

sample_exposure_time = 60
ctape_exposure_time = 30

##################################################################
#We acquire some dark images before the E scan:
##################################################################
#Dark Image
energy.moveTo(810)
acquire_dark_image(1, andor, sample_exposure_time)

###########################################


#####################################
# Information for spech calculation
#####################################
specgammaval = 12 #Needs to be updated if gamma is changed.
Detector_pxsz = 0.01358
E_dispersion = 0.00599  #needs to be updated to the current experimental value
energy_val_fix = 879.4  #Resonant energy
spech_val_fix = 1411.620  #Spech corresponding to the resonant energy

#################################################################
# Define Energies, Theta, and Phi values at which we want to measure
#################################################################

imageno_list = [6,6,12] # it allows to collect a different number of images for different th 
th_list =   [15,45,75]  #frange(15,75.01,30)
phi_list = frange(-60,60.01,10)
energy_list = [879.4] #frange(925,935,0.4)

E_initial = 879.4


############################################################
################# ACQUIRING DATA ###########################
############################################################

primary()
fastshutter('Open')

energy.moveTo(E_initial)

sample_pi0()
 
for n in [0,1]:
    sample_no_images = imageno_list[n]
    th_val = th_list[n]
    th.moveTo(th_val)
    for energy_val in energy_list:
        print(energy_val)
        energy.moveTo(energy_val)
        spech_val = spech_val_fix+(energy_val_fix-energy_val)*Detector_pxsz*mh.sin(specgammaval*mh.pi/180)/E_dispersion
        spech.moveTo(spech_val)
        for phi_val in phi_list:
            phi.moveTo(phi_val)
             
            go(E_initial, LH)
            print('LH RIXS at th = %.3f and phi = %.3f and Energy = %.3f'%(th_val,phi_val,energy_val))
            acquireRIXS(sample_no_images, andor, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
            print('******************************************************************')
            
            go(E_initial, LV)
            print('LV RIXS at th = %.3f and phi = %.3f and Energy = %.3f'%(th_val,phi_val,energy_val))
            acquireRIXS(sample_no_images, andor, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
            print('******************************************************************')


      
##########################################

sample_pi0()

# move spech to the optimised position for qscan (resonance)
energy.moveTo(energy_val_fix)
spech.moveTo(spech_val_fix) 


#############################################################################################################
print('Macro is completed !!!')
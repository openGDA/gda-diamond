'''
Created on 26th Mar 2019

@author: i21user

modified MGF 17/IX/19
modified on 12/10/21 by SA 
'''

import math as mh
from acquisition.darkImageAcqusition import acquire_dark_image
from gdaserver import x,y,z,th,phi,chi, s5v1gap, energy, andor, difftth, fastshutter, spech, m4c1, checkbeam  # @UnresolvedImport
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

def sample_pipi():
    '''move to sample_pipi position concurrently and wait until all moves complete
    '''
    x.asynchronousMovTo(x_sample_pipi)
    y.asynchronousMovTo(y_sample_pipi)
    z.asynchronousMovTo(z_sample_pipi)
    th.asynchronousMovTo(th_sample_pipi)
    phi.asynchronousMovTo(phi_sample_pipi)
    chi.asynchronousMovTo(chi_sample_pipi)
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    th.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()

def ctape_pipi():
    '''move to ctape_pipi position concurrently and wait until all moves complete
    '''
    x.asynchronousMovTo(x_ctape_pipi)
    y.asynchronousMovTo(y_ctape_pipi)
    z.asynchronousMovTo(z_ctape_pipi)
    th.asynchronousMovTo(th_ctape_pipi)
    phi.asynchronousMovTo(phi_ctape_pipi)
    chi.asynchronousMovTo(chi_ctape_pipi)
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    th.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
    

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

#############################################################
###################### SAMPLE (PI,0)########################
#############################################################
def collect_pi0_data():
    for th_val in th_list:
        th.moveTo(th_val)
        for energy_val in energy_list:
            print ("move energy to %f " % energy_val)
            energy.moveTo(energy_val)
            spech_val = spech_val_fix+(energy_val_fix-energy_val)*Detector_pxsz*mh.sin(specgammaval*mh.pi/180)/E_dispersion
            spech.moveTo(spech_val)
            
            ctape_pi0()
            print('cTape at th = %.3f and Energy = %.3f'%(th_val,energy_val))
            acquire_ctape_image(ctape_no_images, andor, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
            print('******************************************************************')
    
            sample_pi0()
            print('RIXS at th = %.3f and Energy = %.3f'%(th_val,energy_val))
            acquireRIXS(sample_no_images, andor, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
            print('******************************************************************')

############################################################
# energy scan with LH along (pi, 0)

go(E_initial, LH)
collect_pi0_data()
    
        
#################################################


#####################################################
#energy scan with LV along (pi, 0)

go(E_initial, LV)
collect_pi0_data()


#################################################



#############################################################
###################### SAMPLE (PI,PI)########################
#############################################################
def collect_pipi_data():
    for th_val in th_list:
        th.moveTo(th_val)
        for energy_val in energy_list:
            print ("move energy to %f " % energy_val)
            energy.moveTo(energy_val)
            spech_val = spech_val_fix+(energy_val_fix-energy_val)*Detector_pxsz*mh.sin(specgammaval*mh.pi/180)/E_dispersion
            spech.moveTo(spech_val)
            
            ctape_pipi()
            print('cTape at th = %.3f and Energy = %.3f'%(th_val,energy_val))
            acquire_ctape_image(ctape_no_images, andor, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
            print('******************************************************************')
    
            sample_pipi()
            print('RIXS at th = %.3f and Energy = %.3f'%(th_val,energy_val))
            acquireRIXS(sample_no_images, andor, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
            print('******************************************************************')


##########################################################
# energy scan with LH along (pi, pi)

go(E_initial, LH)
collect_pipi_data()
    
#################################################


#####################################################
#energy scan with LV along (pi, pi)

go(E_initial, LV)
collect_pipi_data()

        
#################################################
#################################################


# move spech to the optimised position for qscan (resonance)

energy.moveTo(energy_val_fix)
spech.moveTo(spech_val_fix)


#####################################################################
print('Macro is completed !!!')
'''
Created on 12th Oct 2021

@author: Stefano Agrestini
'''

import math as mh
from gdaserver import andor, andor2, xcam # @UnresolvedImport
from gdascripts.utils import frange
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS

LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]

#########################################################################


#########################################################################
# definition of the sample and ctape position along (pi,0)
#########################################################################

x_sample_pi0=-1.357
y_sample_pi0=-1.5
z_sample_pi0=-0.9

phi_sample_pi0 = 0.0

x_ctape_pi0=+0.39
y_ctape_pi0=-1.5
z_ctape_pi0=-3.5

#####################################
# defining exit slit opening
#####################################
exit_slit = 20

#######################################################################
# User Section - defining energy at which dark image to be collected
#######################################################################
dark_image_energy = 810

####################################################################################################
#Defining CCD parameters
####################################################################################################

detector_to_use = andor

sample_no_images = 1
ctape_no_images = 1

sample_exposure_time = 60
ctape_exposure_time = 30


#####################################
# Information for spech calculation
#####################################
specgammaval = 12 #Needs to be updated if gamma is changed.
Detector_pxsz = 0.01358
E_dispersion = 0.00599  #needs to be updated to the current experimental value
energy_val_fix = 879.4  #Resonant energy
spech_val_fix = 1411.620  #Spech corresponding to the resonant energy

#####################################################################################
# Define Energies, Polarisation, Theta, and Phi values at which we want to measure
#####################################################################################

imageno_list = [6, 6, 12] # it allows to collect a different number of images for different th 
th_list =      [15,45,75]  #[round(x, 0) for x in frange(15,75.01,30)]
phi_list = [round(x, 0) for x in frange(-60,60.01,10)]
energy_list = [879.4] #[round(x, 1) for x in frange(925,935,0.4)]
polarisation_list = [LH, LV]

#####################################
spech_list = []
for energy_val in energy_list:
    spech_val = spech_val_fix+(energy_val_fix-energy_val)*Detector_pxsz*mh.sin(specgammaval*mh.pi/180)/E_dispersion
    spech_list.append(spech_val)

energy_spech_pairs = zip(energy_list, spech_list)
theta_imageno_pairs = zip(th_list, imageno_list)

########################################################################
### Users don't change lines below this line.
########################################################################
from gdaserver import s5v1gap, difftth, fastshutter # @UnresolvedImport

s5v1gap.moveTo(exit_slit)

######################################
# moving diode to 0
######################################
difftth.moveTo(0)

##################################################################
#We acquire some dark images before the E scan:
##################################################################
from acquisition.darkImageAcqusition import acquire_dark_image
from scannable.continuous.continuous_energy_scannables import energy

energy.moveTo(dark_image_energy)
acquire_dark_image(1, detector_to_use, sample_exposure_time)

###########################################
# shutter control
###########################################
from shutters.detectorShutterControl import primary, polarimeter

if detector_to_use in [andor, xcam]:
    primary()
if detector_to_use is andor2:
    polarimeter()
fastshutter('Open')    

energy.moveTo(energy_list[0]) ###do this really required???

############################################################
################# ACQUIRING DATA ###########################
############################################################

from gdaserver import xyz_stage, m4c1, th, phi, spech  # @UnresolvedImport
from scannabledevices.checkbeanscannables import checkbeam
from functions.go_founctions import go
from acquisition.acquire_images import acquireRIXS

xyz_stage([x_sample_pi0, y_sample_pi0, z_sample_pi0])
 
for th_val,image_no in theta_imageno_pairs:
    th.asynchronousMoveTo(th_val)
    for energy_val, spech_val in energy_spech_pairs:
        print("move energy to %f ..." % energy_val)
        energy.asynchronousMoveTo(energy_val)
        spech.asynchronousMoveTo(spech_val)        
        for phi_val in phi_list:
            phi.asynchronousMoveTo(phi_val)
            for pol in polarisation_list: 
                go(energy_val, pol)
                th.waitWhileBusy()
                energy.waitWhileBusy()
                spech.waitWhileBusy()
                phi.waitWhileBusy()
                
                print('%s RIXS at th = %.3f, phi = %.3f, Energy = %.3f and spech = %.3f'%(pol, th_val, phi_val, energy_val, spech_val))
                acquireRIXS(image_no, detector_to_use, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
                print('******************************************************************')
            
      
##########################################

xyz_stage([x_sample_pi0, y_sample_pi0, z_sample_pi0]) ### why this line required?

# move spech to the optimised position for qscan (resonance)
energy.asynchronousMoveTo(energy_val_fix)
spech.asynchronousMoveTo(spech_val_fix) 
energy.waitWhileBusy()
spech.waitWhileBusy()

#############################################################################################################
print('Macro is completed !!!')
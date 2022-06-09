
'''
Created on 12th Oct 2021

@author: SA
'''

from gdascripts.utils import frange
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
from gdaserver import andor, andor2, xcam  # @UnresolvedImport

LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]


#########################################################################
# definition of the sample and ctape position along (pi,0)
#########################################################################

x_sample_pi0 = -1.357
y_sample_pi0 = -1.5
z_sample_pi0 = -0.9

phi_sample_pi0 = -50.7 ###???this is not used here???

x_ctape_pi0=+0.39
y_ctape_pi0=-1.5
z_ctape_pi0=-3.5

#########################################################################
# definition of the sample step for scans
#########################################################################
z_sample_step = 0.01
y_sample_step = 0.05

#####################################
# defining exit slit opening
#####################################
exit_slit = 40

#######################################################################
# User Section - defining energy at which dark image to be collected
#######################################################################
dark_image_energy = 500

#####################################
# Information for spech calculation
#####################################
specgammaval = 30 #Needs to be updated if gamma is changed.
Detector_pxsz = 0.01358
E_dispersion = 0.00801  #needs to be updated to the current experimental value
energy_val_fix = 529.5  #Resonant energy
spech_val_fix = 1386.53  #Spech corresponding to the resonant energy

#####################################
#Defining CCD parameters
#####################################

detector_to_use = andor

sample_no_images = 1
ctape_no_images = 1

sample_exposure_time = 20
ctape_exposure_time = 5

############################################
# Defining energy parameter for Survey scan
############################################
polarisation_val = LV

############################################
# Defining Survey scan parameters
############################################
en_val = 529.75
number_of_iterations_survey = 15

############################################
# Defining eenergy mapping parameters
############################################
en_list = [round(x, 2) for x in frange(526, 536.01, 0.25)]
number_of_iterations_map = 10

#####################################
# Defining theta angle parameter
#####################################
th_val = 45

##################################################################
## User should not change lines below this line
##################################################################

from gdaserver import th, s5v1gap, difftth, fastshutter, spech  # @UnresolvedImport
from acquisition.darkImageAcqusition import acquire_dark_image
from shutters.detectorShutterControl import primary, polarimeter
from functions.go_founctions import go
from scannable.continuous.continuous_energy_scannables import energy

s5v1gap.moveTo(exit_slit)

##################################################################
#We acquire some dark images before the E scan:
##################################################################
#Dark Image
energy.moveTo(dark_image_energy)
acquire_dark_image(1, detector_to_use, sample_exposure_time)

######################################
# moving diode to 0
######################################
difftth.asynchronousMoveTo(0)

if detector_to_use in [andor, xcam]:
    primary()
if detector_to_use is andor2:
    polarimeter()
fastshutter('Open')    

th.asynchronousMoveTo(th_val)

# change polarization
go(en_val, polarisation_val)

difftth.waitWhileBusy()
th.waitWhileBusy()

#################################################################
###################### ACQUIRING DATA ###########################
#################################################################
from acquisition.acquireCarbonTapeImages import acquire_ctape_image, remove_ctape_image
from acquisition.acquire_images import acquireRIXS

def move_energy_to(en_val):
    import math as mh
    energy.asynchronousMoveTo(en_val)
    spech_val = spech_val_fix + (energy_val_fix - en_val) * Detector_pxsz * mh.sin(specgammaval * mh.pi / 180) / E_dispersion
    spech.asynchronousMoveTo(spech_val)
    energy.waitWhileBusy()
    spech.waitWhileBusy()
    print('RIXS at Energy = %.2f, and spech=%.2f' % (en_val, spech_val))
    
#############################################################
###################### Survey Scans #########################
#############################################################

from gdaserver import xyz_stage, m4c1  # @UnresolvedImport
from scannabledevices.checkbeanscannables import checkbeam

total_number_of_data_files_to_be_collected = (number_of_iterations_survey * 2)
print("Starts survey scans: \ntotal number of files to collect %r" % total_number_of_data_files_to_be_collected)
total_number_of_images_to_be_collected = number_of_iterations_survey * (sample_no_images + ctape_no_images)
print("Total number of images to be collected: %r" %  (total_number_of_images_to_be_collected))
import datetime
print("Total exposure time requested to detector excluding all motion times: %r" % str(datetime.timedelta(seconds = number_of_iterations_survey * (sample_exposure_time * sample_no_images + ctape_exposure_time * ctape_no_images))))
# progress logs
number_of_data_files_collected_so_far = 0
number_of_images_collected_so_far = 0
number_of_data_files_to_be_collected = total_number_of_data_files_to_be_collected
number_of_images_to_be_collected = total_number_of_images_to_be_collected

for j in range(number_of_iterations_survey):
    move_energy_to(en_val)
       
    xyz_stage.moveTo([x_ctape_pi0, y_ctape_pi0, z_ctape_pi0])
    acquire_ctape_image(ctape_no_images, detector_to_use, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
    number_of_data_files_collected_so_far += 1
    number_of_images_collected_so_far += ctape_no_images
    number_of_data_files_to_be_collected -= 1
    number_of_images_to_be_collected -= ctape_no_images
    print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
    print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
    print("Number of images collected so far: %r" % number_of_images_collected_so_far)
    print("Number of images to go: %r" % number_of_images_to_be_collected)
    print('******************************************************************')
    
    xyz_stage.moveTo([x_sample_pi0, y_sample_pi0, z_sample_pi0 + z_sample_step * j])
    acquireRIXS(sample_no_images, detector_to_use, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
    number_of_data_files_collected_so_far += 1
    number_of_images_collected_so_far += sample_no_images
    number_of_data_files_to_be_collected -= 1
    number_of_images_to_be_collected -= sample_no_images
    print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
    print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
    print("Number of images collected so far: %r" % number_of_images_collected_so_far)
    print("Number of images to go: %r" % number_of_images_to_be_collected)
    print('******************************************************************')
        
    remove_ctape_image(detector_to_use)


#############################################################
######################## Energy map #########################
#############################################################
total_number_of_data_files_to_be_collected = (len(en_list) * number_of_iterations_map * 2)
print("Starts energy map scans: \ntotal number of files to collect %r" % total_number_of_data_files_to_be_collected)
total_number_of_images_to_be_collected = len(en_list) * number_of_iterations_map * (sample_no_images + ctape_no_images)
print("Total number of images to be collected: %r" %  (total_number_of_images_to_be_collected))

print("Total exposure time requested to detector excluding all motion times: %r" % str(datetime.timedelta(seconds = len(en_list) * number_of_iterations_map * (sample_exposure_time * sample_no_images + ctape_exposure_time * ctape_no_images))))
# progress logs
number_of_data_files_collected_so_far = 0
number_of_images_collected_so_far = 0
number_of_data_files_to_be_collected = total_number_of_data_files_to_be_collected
number_of_images_to_be_collected = total_number_of_images_to_be_collected

for j, en_val in enumerate(en_list):
    move_energy_to(en_val)
    
    for i in range(number_of_iterations_map):
        
        xyz_stage.moveTo([x_ctape_pi0, y_ctape_pi0, z_ctape_pi0])
        acquire_ctape_image(ctape_no_images, detector_to_use, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
        number_of_data_files_collected_so_far += 1
        number_of_images_collected_so_far += sample_no_images
        number_of_data_files_to_be_collected -= 1
        number_of_images_to_be_collected -= sample_no_images
        print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
        print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
        print("Number of images collected so far: %r" % number_of_images_collected_so_far)
        print("Number of images to go: %r" % number_of_images_to_be_collected)
        print('******************************************************************')
        
        xyz_stage.moveTo([x_sample_pi0, y_sample_pi0 + y_sample_step * i, z_sample_pi0 + z_sample_step * j])
        acquireRIXS(sample_no_images, detector_to_use, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
        number_of_data_files_collected_so_far += 1
        number_of_images_collected_so_far += sample_no_images
        number_of_data_files_to_be_collected -= 1
        number_of_images_to_be_collected -= sample_no_images
        print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
        print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
        print("Number of images collected so far: %r" % number_of_images_collected_so_far)
        print("Number of images to go: %r" % number_of_images_to_be_collected)
        print('******************************************************************')
        
        remove_ctape_image(detector_to_use)
        

#################################################
#################################################

# move spech to the optimised position for qscan (resonance)

energy.asynchronousMoveTo(energy_val_fix)
spech.asynchronousMoveTo(spech_val_fix) 
energy.waitWhileBusy()
spech.waitWhileBusy()

# feabsorber('Close')

#####################################################################
print('Macro is completed !!!')

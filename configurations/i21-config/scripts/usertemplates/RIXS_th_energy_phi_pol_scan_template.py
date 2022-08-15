'''
This module supports data collections from user defined carbon tape position, sample position, or both positions
 at each (theta, energy, phi, pol) position defined in a list of points.
 It implements raster scan algorithm for inner loops.

 dark image is also collected before ctape and sample data collection.

@since: 16 June 2022
@contact: Fajin Yuan
@group: Diamond I21 Team
@status: tested in dummy mode  

Testing parameters: (as currently recorded in this script)

Data collection points: [(15, 6, 879.4, 1411.62, -60.0, 'LH'), (15, 6, 879.4, 1411.62, -60.0, 'LV'), (15, 6, 879.4, 1411.62, -50.0, 'LV'), (15, 6, 879.4, 1411.62, -50.0, 'LH'), (15, 6, 879.4, 1411.62, -40.0, 'LH'), (15, 6, 879.4, 1411.62, -40.0, 'LV'), (15, 6, 879.4, 1411.62, -30.0, 'LV'), (15, 6, 879.4, 1411.62, -30.0, 'LH'), (15, 6, 879.4, 1411.62, -20.0, 'LH'), (15, 6, 879.4, 1411.62, -20.0, 'LV'), (15, 6, 879.4, 1411.62, -10.0, 'LV'), (15, 6, 879.4, 1411.62, -10.0, 'LH'), (15, 6, 879.4, 1411.62, 0.0, 'LH'), (15, 6, 879.4, 1411.62, 0.0, 'LV'), (15, 6, 879.4, 1411.62, 10.0, 'LV'), (15, 6, 879.4, 1411.62, 10.0, 'LH'), (15, 6, 879.4, 1411.62, 20.0, 'LH'), (15, 6, 879.4, 1411.62, 20.0, 'LV'), (15, 6, 879.4, 1411.62, 30.0, 'LV'), (15, 6, 879.4, 1411.62, 30.0, 'LH'), (15, 6, 879.4, 1411.62, 40.0, 'LH'), (15, 6, 879.4, 1411.62, 40.0, 'LV'), (15, 6, 879.4, 1411.62, 50.0, 'LV'), (15, 6, 879.4, 1411.62, 50.0, 'LH'), (15, 6, 879.4, 1411.62, 60.0, 'LH'), (15, 6, 879.4, 1411.62, 60.0, 'LV'), (45, 6, 879.4, 1411.62, -60.0, 'LH'), (45, 6, 879.4, 1411.62, -60.0, 'LV'), (45, 6, 879.4, 1411.62, -50.0, 'LV'), (45, 6, 879.4, 1411.62, -50.0, 'LH'), (45, 6, 879.4, 1411.62, -40.0, 'LH'), (45, 6, 879.4, 1411.62, -40.0, 'LV'), (45, 6, 879.4, 1411.62, -30.0, 'LV'), (45, 6, 879.4, 1411.62, -30.0, 'LH'), (45, 6, 879.4, 1411.62, -20.0, 'LH'), (45, 6, 879.4, 1411.62, -20.0, 'LV'), (45, 6, 879.4, 1411.62, -10.0, 'LV'), (45, 6, 879.4, 1411.62, -10.0, 'LH'), (45, 6, 879.4, 1411.62, 0.0, 'LH'), (45, 6, 879.4, 1411.62, 0.0, 'LV'), (45, 6, 879.4, 1411.62, 10.0, 'LV'), (45, 6, 879.4, 1411.62, 10.0, 'LH'), (45, 6, 879.4, 1411.62, 20.0, 'LH'), (45, 6, 879.4, 1411.62, 20.0, 'LV'), (45, 6, 879.4, 1411.62, 30.0, 'LV'), (45, 6, 879.4, 1411.62, 30.0, 'LH'), (45, 6, 879.4, 1411.62, 40.0, 'LH'), (45, 6, 879.4, 1411.62, 40.0, 'LV'), (45, 6, 879.4, 1411.62, 50.0, 'LV'), (45, 6, 879.4, 1411.62, 50.0, 'LH'), (45, 6, 879.4, 1411.62, 60.0, 'LH'), (45, 6, 879.4, 1411.62, 60.0, 'LV'), (75, 12, 879.4, 1411.62, -60.0, 'LH'), (75, 12, 879.4, 1411.62, -60.0, 'LV'), (75, 12, 879.4, 1411.62, -50.0, 'LV'), (75, 12, 879.4, 1411.62, -50.0, 'LH'), (75, 12, 879.4, 1411.62, -40.0, 'LH'), (75, 12, 879.4, 1411.62, -40.0, 'LV'), (75, 12, 879.4, 1411.62, -30.0, 'LV'), (75, 12, 879.4, 1411.62, -30.0, 'LH'), (75, 12, 879.4, 1411.62, -20.0, 'LH'), (75, 12, 879.4, 1411.62, -20.0, 'LV'), (75, 12, 879.4, 1411.62, -10.0, 'LV'), (75, 12, 879.4, 1411.62, -10.0, 'LH'), (75, 12, 879.4, 1411.62, 0.0, 'LH'), (75, 12, 879.4, 1411.62, 0.0, 'LV'), (75, 12, 879.4, 1411.62, 10.0, 'LV'), (75, 12, 879.4, 1411.62, 10.0, 'LH'), (75, 12, 879.4, 1411.62, 20.0, 'LH'), (75, 12, 879.4, 1411.62, 20.0, 'LV'), (75, 12, 879.4, 1411.62, 30.0, 'LV'), (75, 12, 879.4, 1411.62, 30.0, 'LH'), (75, 12, 879.4, 1411.62, 40.0, 'LH'), (75, 12, 879.4, 1411.62, 40.0, 'LV'), (75, 12, 879.4, 1411.62, 50.0, 'LV'), (75, 12, 879.4, 1411.62, 50.0, 'LH'), (75, 12, 879.4, 1411.62, 60.0, 'LH'), (75, 12, 879.4, 1411.62, 60.0, 'LV')]
Total number of points to collection data: 78
Total number of data files to be collected: 156
Total number of images to be collected: 702
Total exposure time requested to detector excluding all motion times: '11:03:00'

Tests start at 2022-06-16 14:49:01.975 when dark image was taken, finish at 2022-06-17 03:06:17.048, total time taken is 12:17:16 (for the same sample and ctape position for pi0 and pipi)

This script provides data collection progress information as below:

Number of data files collected so far: 154
Number of data files to go: 2
Number of images collected so far: 689
Number of images to go: 13

The data collection process also monitors beam status: i.e. pause beam drops or during topup, and resume afterwards

=== Scan started at 2022-06-17 00:41:10.146 ===
=== Beam checking enabled: ringcurrent must exceed 190, currently True
=== Beam checking enabled: feBeamPermit must be in state: Open, currently True
=== Beam checking enabled: topup_time must exceed 5, currently True
*** checktopup_time: Beam down at: 00:42:10 . Pausing scan...
*** checktopup_time: Beam back up at: 00:42:11 . Resuming scan in 5s...
*** checktopup_time:  Resuming scan now at 00:42:16
Writing data to file: /scratch/gda_versions/gda-master-20220324/gda_data_non_live/i21-12872.nxs
    ds    checkrc_beamok    checktopup_time_beamok    count_time    m4c1
1.0000                 1                         0         60.00    1.35
2.0000                 1                         1         60.00    2.007
3.0000                 1                         1         60.00    2.565
4.0000                 1                         1         60.00    3.872
5.0000                 1                         1         60.00    4.65
6.0000                 1                         1         60.00    6.481
7.0000                 1                         1         60.00    6.789
8.0000                 1                         1         60.00    8.697
9.0000                 1                         1         60.00    8.368
10.000                 1                         1         60.00    10.088
11.000                 1                         1         60.00    9.175
12.000                 1                         1         60.00    9.266
Scan complete.
=== Scan ended at 2022-06-17 00:53:17.049 ===

Created on 12th Oct 2021

@author: Stefano Agrestini
'''

import math as mh
from gdaserver import andor, andor2, xcam # @UnresolvedImport
from gdascripts.utils import frange
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS

LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]

#########################################################################
# definition of the sample and ctape position along (pi,0)
#########################################################################

x_sample_pi0 = -1.357
y_sample_pi0 = -1.5
z_sample_pi0 = -0.9

phi_sample_pi0 = 0.0 #this is not used as phi is changing in the data collection
chi_sample_pi0 = 0.0

x_ctape_pi0 = +0.39
y_ctape_pi0 = -1.5
z_ctape_pi0 = -3.5

chi_ctape_pi0 = 0.0

enable_ctape_collection = True
enable_sample_collection = True

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

#the following line override sample_no_images
imageno_list = [6, 6, 12] # it allows to collect a different number of images for different th 
th_list =      [15,45,75]  #[round(x, 3) for x in frange(15,75.01,30)]
phi_list = [round(x, 0) for x in frange(-60,60.01,10)]
energy_list = [879.4] #[round(x, 3) for x in frange(925,935,0.4)]
polarisation_list = [LH, LV]

####################################################################
## User should not need to change anything below this line
####################################################################
spech_list = []
for energy_val in energy_list:
    spech_val = spech_val_fix + (energy_val_fix - energy_val) * Detector_pxsz * mh.sin(specgammaval * mh.pi / 180) / E_dispersion
    spech_list.append(spech_val)

theta_imageno_pairs = zip(th_list, imageno_list)
energy_spech_pairs = zip(energy_list, spech_list)

def generate_points(level1_list_of_tuples, level2_list_of_tuples, level3_list, level4_list):
    '''
    generate a list of tuples of positions at which image data will be collected from detector.
    It implements raster motion algorithm for inner motors to save time taken for the data collection.
     
    @param leve1_list_of_tuples: list of tuples containing 2 elements in outer-most loop
    @param level2_list_of_tuples:  list of tuples containing 2 elements in the 1st inner loop
    @param level3_list:  list of positions in the 2nd inner loop
    @param level4_list:  list of positions in the inner-most loop     
   '''
    total_points = []
    for index1, th_imageno in enumerate(level1_list_of_tuples):
        if index1 % 2 == 0:
            for index2, energy_spech in enumerate(level2_list_of_tuples):
                if index2 % 2 == 0:
                    for index3, phi_val in enumerate(level3_list):
                        if index3 % 2 == 0:
                            for pol_val in level4_list:
                                total_points.append(th_imageno + energy_spech + (phi_val,) + (pol_val,))
                        if index3 % 2 == 1:
                            for pol_val in reversed(level4_list):
                                total_points.append(th_imageno + energy_spech + (phi_val,) + (pol_val,))
                if index2 % 2 == 1:
                    for index3, phi_val in enumerate(reversed(level3_list)):
                        if index3 % 2 == 0:
                            for pol_val in level4_list:
                                total_points.append(th_imageno + energy_spech + (phi_val,) + (pol_val,))
                        if index3 % 2 == 1:
                            for pol_val in reversed(level4_list):
                                total_points.append(th_imageno + energy_spech + (phi_val,) + (pol_val,))
                       
        if index1 % 2 == 1:
            for index2, energy_spech in enumerate(reversed(level2_list_of_tuples)):
                if index2 % 2 == 0:
                    for index3, phi_val in enumerate(level3_list):
                        if index3 % 2 == 0:
                            for pol_val in level4_list:
                                total_points.append(th_imageno + energy_spech + (phi_val,) + (pol_val,))
                        if index3 % 2 == 1:
                            for pol_val in reversed(level4_list):
                                total_points.append(th_imageno + energy_spech + (phi_val,) + (pol_val,))
                if index2 % 2 == 1:
                    for index3, phi_val in enumerate(reversed(level3_list)):
                        if index3 % 2 == 0:
                            for pol_val in level4_list:
                                total_points.append(th_imageno + energy_spech + (phi_val,) + (pol_val,))
                        if index3 % 2 == 1:
                            for pol_val in reversed(level4_list):
                                total_points.append(th_imageno + energy_spech + (phi_val,) + (pol_val,))
                                
    return total_points

point_list = generate_points(theta_imageno_pairs, energy_spech_pairs, phi_list, polarisation_list)
print("\nData collection points: %r" % point_list)
print("Total number of points to collection data: %r" % len(point_list))

## generate some stats data
total_number_of_images_to_be_collected = 0
total_number_of_data_files_to_be_collected = 0
total_exposure_times = 0

if enable_ctape_collection:
    total_number_of_data_files_to_be_collected += len(theta_imageno_pairs) * len(energy_spech_pairs) * len(phi_list) * len(polarisation_list)
    total_number_of_images_to_be_collected += len(energy_spech_pairs) * len(phi_list) * len(polarisation_list) * len(theta_imageno_pairs) * ctape_no_images
    total_exposure_times += len(theta_imageno_pairs) * len(energy_spech_pairs) * len(phi_list) * len(polarisation_list) * ctape_exposure_time * ctape_no_images
if enable_sample_collection:
    total_number_of_data_files_to_be_collected += len(theta_imageno_pairs) * len(energy_spech_pairs) * len(phi_list) * len(polarisation_list)
    total_number_of_images_to_be_collected += len(energy_spech_pairs) * len(phi_list) * len(polarisation_list) * sum(imageno_list)
    total_exposure_times += len(energy_spech_pairs) * len(phi_list) * len(polarisation_list) * sample_exposure_time * sum(imageno_list)
    
print("Total number of data files to be collected: %r" % (total_number_of_data_files_to_be_collected))
print("Total number of images to be collected: %r" %  (total_number_of_images_to_be_collected))
import datetime
print("Total exposure time requested to detector excluding all motion times: %r" % str(datetime.timedelta(seconds = total_exposure_times)))

# progress trackers
number_of_data_files_collected_so_far = 0
number_of_images_collected_so_far = 0
number_of_data_files_to_be_collected = total_number_of_data_files_to_be_collected
number_of_images_to_be_collected = total_number_of_images_to_be_collected

answer = "y"

# you can comment out the following line to remove user input required when running this script without user present to respond to this question!
answer = raw_input("\nAre these collection parameters correct to continue [y/n]?")

##########################################################################
## define data collection functions
##########################################################################
def collect_ctape_data(x_ctape, y_ctape, z_ctape, det, no_images, exposure_time):
    from gdaserver import xyz_stage, m4c1  # @UnresolvedImport
    from scannabledevices.checkbeanscannables import checkbeam
    from acquisition.acquireCarbonTapeImages import acquire_ctape_image   
    global number_of_data_files_collected_so_far, number_of_images_collected_so_far, number_of_data_files_to_be_collected, number_of_images_to_be_collected
    
    print("move to ctape position %r" % [x_ctape, y_ctape, z_ctape])
    xyz_stage.moveTo([x_ctape, y_ctape, z_ctape])
    acquire_ctape_image(no_images, det, exposure_time, m4c1, exposure_time, checkbeam)
    number_of_data_files_collected_so_far += 1
    number_of_images_collected_so_far += no_images
    number_of_data_files_to_be_collected -= 1
    number_of_images_to_be_collected -= no_images
    print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
    print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
    print("Number of images collected so far: %r" % number_of_images_collected_so_far)
    print("Number of images to go: %r" % number_of_images_to_be_collected)
    print('******************************************************************')

def collect_sample_data(x_sample, y_sample, z_sample, det, no_images, exposure_time, dark_image_filename):
    from gdaserver import xyz_stage, m4c1  # @UnresolvedImport
    from scannabledevices.checkbeanscannables import checkbeam
    from acquisition.acquire_images import acquireRIXS
    from acquisition.darkImageAcqusition import remove_dark_image_link, add_dark_image_link
    global number_of_data_files_collected_so_far, number_of_images_collected_so_far, number_of_data_files_to_be_collected, number_of_images_to_be_collected
    
    add_dark_image_link(det, dark_image_filename)
    print("move to sample position %r" % [x_sample, y_sample, z_sample])
    xyz_stage.moveTo([x_sample, y_sample, z_sample])
    acquireRIXS(no_images, det, exposure_time, m4c1, exposure_time, checkbeam)
    number_of_data_files_collected_so_far += 1
    number_of_images_collected_so_far += no_images
    number_of_data_files_to_be_collected -= 1
    number_of_images_to_be_collected -= no_images
    print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
    print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
    print("Number of images collected so far: %r" % number_of_images_collected_so_far)
    print("Number of images to go: %r" % number_of_images_to_be_collected)
    print('******************************************************************')
    remove_dark_image_link(det)

def collect_data(x_sample, y_sample, z_sample, chi_sample, x_ctape, y_ctape, z_ctape, chi_ctape, det, ctape_no_images, ctape_exposure_time, sample_no_images, sample_exposure_time, dark_image_filename):
    from acquisition.acquireCarbonTapeImages import remove_ctape_image
    from gdaserver import chi  # @UnresolvedImport
    if enable_ctape_collection:
        chi.moveTo(chi_ctape)
        collect_ctape_data(x_ctape, y_ctape, z_ctape, det, ctape_no_images, ctape_exposure_time)
    if enable_sample_collection:
        chi.moveTo(chi_sample)
        collect_sample_data(x_sample, y_sample, z_sample, det, sample_no_images, sample_exposure_time, dark_image_filename)
    if enable_ctape_collection:
        remove_ctape_image(det)

if answer == "y":
    
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
    from acquisition.darkImageAcqusition import acquire_dark_image, remove_dark_image_link
    from scannable.continuous.continuous_energy_scannables import energy
    from acquisition.acquireCarbonTapeImages import remove_ctape_image
    
    energy.moveTo(dark_image_energy)
    remove_dark_image_link(detector_to_use) # ensure any previous dark image file link is removed
    remove_ctape_image(detector_to_use) # ensure any previous elastic image file link is removed
    dark_image_filename = acquire_dark_image(1, detector_to_use, sample_exposure_time)
    
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
    
    from gdaserver import th, phi, spech  # @UnresolvedImport
    from functions.go_founctions import go
    
    for th_val,no_images,energy_val,spech_val,phi_val,pol_val in point_list:
        print("move th to %f ..." % th_val)
        th.asynchronousMoveTo(th_val)
        print("move energy to %f ..." % energy_val)
        energy.asynchronousMoveTo(energy_val)
        print("move spech to %f ..." % spech_val)
        spech.asynchronousMoveTo(spech_val)
        print("move phi to %f ..." % phi_val)
        phi.asynchronousMoveTo(phi_val)
        print("move polarisation to %s ..." % pol_val)
        go(energy_val, pol_val)
        th.waitWhileBusy()
        energy.waitWhileBusy()
        spech.waitWhileBusy()
        phi.waitWhileBusy()
        print("all motions are completed!")
        
        print('\n%s RIXS at th = %.3f, phi = %.3f, Energy = %.3f and spech = %.3f' % (pol_val, th_val, phi_val, energy_val, spech_val))
        collect_data(x_sample_pi0, y_sample_pi0, z_sample_pi0, chi_sample_pi0, x_ctape_pi0, y_ctape_pi0, z_ctape_pi0, chi_ctape_pi0, detector_to_use, ctape_no_images, ctape_exposure_time, no_images, sample_exposure_time, dark_image_filename)
        
    ##########################################
    
    # move spech to the optimised position for qscan (resonance)
    energy.asynchronousMoveTo(energy_val_fix)
    spech.asynchronousMoveTo(spech_val_fix) 
    energy.waitWhileBusy()
    spech.waitWhileBusy()

#############################################################################################################
print('Macro is completed !!!')

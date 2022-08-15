'''
This module supports data collections from user defined poistions for carbon tape sample. It consists a survey scan of sample z followed by 
energy scan with raster map of sample y and z.
If enabled, the survey scan collects data at each specified z sample poistion at fixed energy position; 
if enable, the energy mapping scan collects data at each y sample position defined in a list at each (energy, z) position given.

This script first takes a dark image, followed by taking ctape image and sample images alternatively at each motors positions.

@since: 14 June 2022
@contact: Fajin Yuan
@group: Diamond I21 Team
@status: tested in dummy mode

Testing parameters: (as currently recorded in this script)

collect data at (energy, spech) positions in survey scan: (529.75, 1386.318)
collect data at sample z positions in survey scan: [-0.9, -0.89, -0.88, -0.87, -0.86, -0.85, -0.84, -0.83, -0.82, -0.81, -0.8, -0.79, -0.78, -0.77, -0.76]
collect data at sample positions in survey scan: [(-1.357, -1.5, -0.9), (-1.357, -1.5, -0.89), (-1.357, -1.5, -0.88), (-1.357, -1.5, -0.87), (-1.357, -1.5, -0.86), (-1.357, -1.5, -0.85), (-1.357, -1.5, -0.84), (-1.357, -1.5, -0.83), (-1.357, -1.5, -0.82), (-1.357, -1.5, -0.81), (-1.357, -1.5, -0.8), (-1.357, -1.5, -0.79), (-1.357, -1.5, -0.78), (-1.357, -1.5, -0.77), (-1.357, -1.5, -0.76)]

collect data at sample z positions in mapping scan: [-0.9, -0.89, -0.88, -0.87, -0.86, -0.85, -0.84, -0.83, -0.82, -0.81, -0.8, -0.79, -0.78, -0.77, -0.76, -0.75, -0.74, -0.73, -0.72, -0.71, -0.7, -0.69, -0.68, -0.67, -0.66, -0.65, -0.64, -0.63, -0.62, -0.61, -0.6, -0.59, -0.58, -0.57, -0.56, -0.55, -0.54, -0.53, -0.52, -0.51, -0.5]
collect data at (energy, spech, z) positions in mapping scan: [(526.0, 1389.497, -0.9), (526.25, 1389.285, -0.89), (526.5, 1389.073, -0.88), (526.75, 1388.861, -0.87), (527.0, 1388.649, -0.86), (527.25, 1388.437, -0.85), (527.5, 1388.225, -0.84), (527.75, 1388.013, -0.83), (528.0, 1387.802, -0.82), (528.25, 1387.59, -0.81), (528.5, 1387.378, -0.8), (528.75, 1387.166, -0.79), (529.0, 1386.954, -0.78), (529.25, 1386.742, -0.77), (529.5, 1386.53, -0.76), (529.75, 1386.318, -0.75), (530.0, 1386.106, -0.74), (530.25, 1385.894, -0.73), (530.5, 1385.682, -0.72), (530.75, 1385.47, -0.71), (531.0, 1385.258, -0.7), (531.25, 1385.047, -0.69), (531.5, 1384.835, -0.68), (531.75, 1384.623, -0.67), (532.0, 1384.411, -0.66), (532.25, 1384.199, -0.65), (532.5, 1383.987, -0.64), (532.75, 1383.775, -0.63), (533.0, 1383.563, -0.62), (533.25, 1383.351, -0.61), (533.5, 1383.139, -0.6), (533.75, 1382.927, -0.59), (534.0, 1382.715, -0.58), (534.25, 1382.503, -0.57), (534.5, 1382.292, -0.56), (534.75, 1382.08, -0.55), (535.0, 1381.868, -0.54), (535.25, 1381.656, -0.53), (535.5, 1381.444, -0.52), (535.75, 1381.232, -0.51), (536.0, 1381.02, -0.5)]
collect data at sample y positions in mapping scan: [-1.5, -1.45, -1.4, -1.35, -1.3, -1.25, -1.2, -1.15, -1.1, -1.05]

total number of files to collect 850
Total number of images to be collected: 850
Total exposure time requested to detector excluding all motion times: '2:57:05'

Test started at 2022-06-17 18:45:23.411, and finished at 2022-06-18 01:33:06.975, total time taken is 06:47:42 (for the same sample and ctape position for pi0 and pipi)

This script provides data collection progress information as below:

Number of data files collected so far: 22
Number of data files to go: 828
Number of images collected so far: 22
Number of images to go: 828

The data collection process also monitors beam status: i.e. pause beam drops or during topup, and resume afterwards

=== Scan started at 2022-06-17 18:55:34.156 ===
=== Beam checking enabled: ringcurrent must exceed 190, currently True
=== Beam checking enabled: feBeamPermit must be in state: Open, currently True
=== Beam checking enabled: topup_time must exceed 5, currently True
*** checktopup_time: Beam down at: 18:55:54 . Pausing scan...
*** checktopup_time: Beam back up at: 18:55:55 . Resuming scan in 5s...
*** checktopup_time:  Resuming scan now at 18:56:00
Writing data to file: /scratch/gda_versions/gda-master-20220324/gda_data_non_live/i21-13512.nxs
    ds    checkrc_beamok    checktopup_time_beamok    count_time    m4c1
1.0000                 1                         0         20.00    1.42
Scan complete.
=== Scan ended at 2022-06-17 18:56:10.437 ===
<No dataset processors are configured>

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
phi_sample_pi0 = -50.7 
chi_sample_pi0 = 0.0 

enable_sample_collection = True

x_ctape_pi0 = +0.39
y_ctape_pi0 = -1.5
z_ctape_pi0 = -3.5
phi_ctape_pi0 = -50.7 
chi_ctape_pi0 = 0.0 

enable_ctape_collection = True

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
do_survey_collection = True

############################################
# Defining energy mapping parameters
############################################
energy_start = 526
energy_stop = 536.01
energy_step = 0.25

number_of_iterations_map = 10
do_energy_map_collection = True

#####################################
# Defining theta angle parameter
#####################################
th_val = 45

##################################################################
## User should not change lines below this line
##################################################################
def calculate_spech_from_energy(energy_val, specgammaval, detector_pxsz, e_dispersion, energy_val_fix, spech_val_fix):
    import math as mh
    return spech_val_fix + (energy_val_fix - energy_val) * detector_pxsz * mh.sin(specgammaval * mh.pi / 180) / e_dispersion

total_number_of_data_files_to_be_collected = 0
total_number_of_images_to_be_collected = 0
total_exposure_time_requested = 0

if do_survey_collection:
    # survey scan parameters
    spech_val = round(calculate_spech_from_energy(en_val, specgammaval, Detector_pxsz, E_dispersion, energy_val_fix, spech_val_fix), 3)
    energy_spech_pair = (en_val, spech_val)
    print("\ncollect data at (energy, spech) positions in survey scan: %r" % (energy_spech_pair,))
    z_sample_pi0_list_survey = [round(z_sample_pi0 + z_sample_step * i, 3) for i in range(number_of_iterations_survey)]
    print("collect data at sample z positions in survey scan: %r" % z_sample_pi0_list_survey)
    sample_pi0_positions_survey = [(x_sample_pi0, y_sample_pi0, z) for z in z_sample_pi0_list_survey]
    print("collect data at sample positions in survey scan: %r" % sample_pi0_positions_survey)
    
    if enable_ctape_collection:
        total_number_of_data_files_to_be_collected += number_of_iterations_survey
        total_number_of_images_to_be_collected += number_of_iterations_survey * ctape_no_images
        total_exposure_time_requested += number_of_iterations_survey * ctape_exposure_time * ctape_no_images
    if enable_sample_collection:
        total_number_of_data_files_to_be_collected += number_of_iterations_survey
        total_number_of_images_to_be_collected += number_of_iterations_survey * sample_no_images
        total_exposure_time_requested += number_of_iterations_survey * sample_exposure_time * sample_no_images

if do_energy_map_collection:
    #energy mapping scan parameters
    en_list = [round(x, 3) for x in frange(energy_start, energy_stop, energy_step)]
    spech_list = [round(calculate_spech_from_energy(energy_val, specgammaval, Detector_pxsz, E_dispersion, energy_val_fix, spech_val_fix), 3) for energy_val in en_list]
    z_sample_pi0_list_map = [round(z_sample_pi0 + z_sample_step * i,3) for i in range(len(en_list))]
    print("\ncollect data at sample z positions in mapping scan: %r" % z_sample_pi0_list_map)
    energy_spech_z_tuples =zip(en_list, spech_list, z_sample_pi0_list_map)
    print("collect data at (energy, spech, z) positions in mapping scan: %r" % energy_spech_z_tuples)
    y_sample_pi0_list_map = [round(y_sample_pi0 + y_sample_step * i, 3) for i in range(number_of_iterations_map)]
    print("collect data at sample y positions in mapping scan: %r" % y_sample_pi0_list_map)

    if enable_ctape_collection:
        total_number_of_data_files_to_be_collected += len(en_list) * number_of_iterations_map
        total_number_of_images_to_be_collected += len(en_list) * number_of_iterations_map * ctape_no_images
        total_exposure_time_requested += len(en_list) * number_of_iterations_map * ctape_exposure_time * ctape_no_images
    if enable_sample_collection:
        total_number_of_data_files_to_be_collected += len(en_list) * number_of_iterations_map
        total_number_of_images_to_be_collected += len(en_list) * number_of_iterations_map * sample_no_images
        total_exposure_time_requested += len(en_list) * number_of_iterations_map * sample_exposure_time * sample_no_images
        
print("\ntotal number of files to collect %r" % total_number_of_data_files_to_be_collected)
print("Total number of images to be collected: %r" %  (total_number_of_images_to_be_collected))
import datetime
print("Total exposure time requested to detector excluding all motion times: %r" % str(datetime.timedelta(seconds = total_exposure_time_requested)))

answer = "y"

# you can comment out the following line to remove user input required when running this script
answer = raw_input("\nAre these collection parameters correct to continue [y/n]?")

##################################################################
## Define energy move function
##################################################################
def move_energy_to(energy_val, spech_val):
    from scannable.continuous.continuous_energy_scannables import energy
    from gdaserver import spech  # @UnresolvedImport
    print("move energy to %f ..." % energy_val)
    energy.asynchronousMoveTo(energy_val)
    print("move spech to %f ..." % spech_val)
    spech.asynchronousMoveTo(spech_val)
    energy.waitWhileBusy()
    spech.waitWhileBusy()
    print('RIXS at Energy = %.2f, and spech=%.2f' % (energy_val, spech_val))
    
##################################################################
## Define survey scan function
##################################################################
def survey_scan_at_fixed_energy(sample_positions, energy_spech_pair, phi_sample, chi_sample, phi_ctape, chi_ctape, det):
    from gdaserver import m4c1,xyz_stage, phi, chi  # @UnresolvedImport
    from acquisition.acquireCarbonTapeImages import acquire_ctape_image, remove_ctape_image
    from acquisition.acquire_images import acquireRIXS
    from scannabledevices.checkbeanscannables import checkbeam
    global number_of_data_files_collected_so_far,number_of_images_collected_so_far,number_of_data_files_to_be_collected,number_of_images_to_be_collected
    
    points_done =[]
    print("\nStart Survey scan data collection ...")
    for sample_pos in sample_positions:
        try:
            move_energy_to(*energy_spech_pair)
            if enable_ctape_collection:
                print("move to ctape position %r ..." % ([x_ctape_pi0, y_ctape_pi0, z_ctape_pi0]))
                phi.asynchronousMoveTo(phi_ctape)
                chi.asynchronousMoveTo(chi_ctape)
                xyz_stage.moveTo([x_ctape_pi0, y_ctape_pi0, z_ctape_pi0])
                phi.waitWhileBusy()
                chi.waitWhileBusy()
                ctape_data_collected = False
                acquire_ctape_image(ctape_no_images, det, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
                number_of_data_files_collected_so_far += 1
                number_of_images_collected_so_far += ctape_no_images
                number_of_data_files_to_be_collected -= 1
                number_of_images_to_be_collected -= ctape_no_images
                print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
                print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
                print("Number of images collected so far: %r" % number_of_images_collected_so_far)
                print("Number of images to go: %r" % number_of_images_to_be_collected)
                print('******************************************************************')
                ctape_data_collected = True

            if enable_sample_collection:
                print("move to sample position %r ..." % (list(sample_pos)))
                phi.asynchronousMoveTo(phi_sample)
                chi.asynchronousMoveTo(chi_sample)
                xyz_stage.moveTo(list(sample_pos))
                phi.waitWhileBusy()
                chi.waitWhileBusy()
                acquireRIXS(sample_no_images, det, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
                number_of_data_files_collected_so_far += 1
                number_of_images_collected_so_far += sample_no_images
                number_of_data_files_to_be_collected -= 1
                number_of_images_to_be_collected -= sample_no_images
                print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
                print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
                print("Number of images collected so far: %r" % number_of_images_collected_so_far)
                print("Number of images to go: %r" % number_of_images_to_be_collected)
                print('******************************************************************')
            
            points_done.append(sample_pos)
        
        except Exception, e:
            print("Survey scan data collection interrupted. Points not collected yet are: %r" % ([x for x in sample_positions if x not in points_done]))
            raise e
        finally:
            if enable_ctape_collection and ctape_data_collected:
                remove_ctape_image(det)
            
#################################################################################################
## Define energy and sample mapping scan function - energy changes with z position changes
##################################################################################################
def energy_sample_raster_scan(energy_spech_z_tuples, y_sample_pi0_list_map, phi_sample, chi_sample, phi_ctape, chi_ctape, det):
    from gdaserver import m4c1,xyz_stage, phi, chi  # @UnresolvedImport
    from acquisition.acquireCarbonTapeImages import acquire_ctape_image, remove_ctape_image
    from acquisition.acquire_images import acquireRIXS
    from scannabledevices.checkbeanscannables import checkbeam
    global number_of_data_files_collected_so_far,number_of_images_collected_so_far,number_of_data_files_to_be_collected,number_of_images_to_be_collected

    out_points_done =[]
    print("\nStart Energy Sample mapping scan data collection ...")
    for en_val, spech_val, z_val in energy_spech_z_tuples:
        try:
            move_energy_to(en_val, spech_val)
            inner_points_done = []
            for y_val in y_sample_pi0_list_map:
                if enable_ctape_collection:
                    print("move to ctape position %r ..." % ([x_ctape_pi0, y_ctape_pi0, z_ctape_pi0]))
                    phi.asynchronousMoveTo(phi_ctape)
                    chi.asynchronousMoveTo(chi_ctape)
                    xyz_stage.moveTo([x_ctape_pi0, y_ctape_pi0, z_ctape_pi0])
                    phi.waitWhileBusy()
                    chi.waitWhileBusy()
                    ctape_data_collected = False
                    acquire_ctape_image(ctape_no_images, det, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
                    number_of_data_files_collected_so_far += 1
                    number_of_images_collected_so_far += sample_no_images
                    number_of_data_files_to_be_collected -= 1
                    number_of_images_to_be_collected -= sample_no_images
                    print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
                    print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
                    print("Number of images collected so far: %r" % number_of_images_collected_so_far)
                    print("Number of images to go: %r" % number_of_images_to_be_collected)
                    print('******************************************************************')
                    ctape_data_collected = True
                
                if enable_sample_collection: 
                    print("move to sample position %r ..." % ([x_sample_pi0, y_val, z_val]))
                    phi.asynchronousMoveTo(phi_sample)
                    chi.asynchronousMoveTo(chi_sample)
                    xyz_stage.moveTo([x_sample_pi0, y_val, z_val])
                    phi.waitWhileBusy()
                    chi.waitWhileBusy()
                    acquireRIXS(sample_no_images, det, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
                    number_of_data_files_collected_so_far += 1
                    number_of_images_collected_so_far += sample_no_images
                    number_of_data_files_to_be_collected -= 1
                    number_of_images_to_be_collected -= sample_no_images
                    print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
                    print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
                    print("Number of images collected so far: %r" % number_of_images_collected_so_far)
                    print("Number of images to go: %r" % number_of_images_to_be_collected)
                    print('******************************************************************')
                    
                inner_points_done.append(y_val)
            out_points_done.append((en_val, spech_val, z_val))
        except Exception, e:
            print("Energy sample mapping scan data collection interrupted.")
            print("Points not collected in outer loop (energy, spech, z) are: %r" % ([x for x in energy_spech_z_tuples if x not in out_points_done]))
            print("Points not collected in inner loop y are: %r" % ([x for x in y_sample_pi0_list_map if x not in inner_points_done]))
            raise e
        finally:  
            if enable_ctape_collection and ctape_data_collected:
                remove_ctape_image(det)

if answer == "y":

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
    # progress logs
    number_of_data_files_collected_so_far = 0
    number_of_images_collected_so_far = 0
    number_of_data_files_to_be_collected = total_number_of_data_files_to_be_collected
    number_of_images_to_be_collected = total_number_of_images_to_be_collected
    
    #############################################################
    ###################### Survey Scans #########################
    #############################################################    
    if do_survey_collection:        
        survey_scan_at_fixed_energy(sample_pi0_positions_survey, energy_spech_pair, phi_sample_pi0, chi_sample_pi0, phi_ctape_pi0, chi_ctape_pi0, detector_to_use)
    
    #############################################################
    ######################## Energy map #########################
    #############################################################
    if do_energy_map_collection:
        energy_sample_raster_scan(energy_spech_z_tuples, y_sample_pi0_list_map, phi_sample_pi0, chi_sample_pi0, phi_ctape_pi0, chi_ctape_pi0, detector_to_use)

    #################################################

    # move spech to the optimised position for qscan (resonance)    
    energy.asynchronousMoveTo(energy_val_fix)
    spech.asynchronousMoveTo(spech_val_fix) 
    energy.waitWhileBusy()
    spech.waitWhileBusy()

# feabsorber('Close')

#####################################################################
print('Macro is completed !!!')

'''
This module support data collections from user defined carbon tape position and sample position in (x,y,z)
 at each (theta, energy) position defined in a list of theta positions and a list of energy positions.
 It implements raster scan algorithm.

@since: 27 May 2022
@contact: Fajin Yuan
@group: Diamond I21 Team
@status:   

Based on /dls_sw/i21/scripts/Users/RIXS_Escan_template_new.py
Created on 26th Mar 2019

@author: i21user

modified MGF 17/IX/19
modified on 12/10/21 by SA 
'''

import math as mh
from gdascripts.utils import frange
from gdaserver import andor, andor2, xcam  # @UnresolvedImport
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS

LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]


##########################################################################
# User Section - definition of the sample and ctape position along (pi,0)#
##########################################################################

x_sample_pi0 = -1.357
y_sample_pi0 = -1.5
z_sample_pi0 = -0.9

x_ctape_pi0=+0.39
y_ctape_pi0=-1.5
z_ctape_pi0=-3.5

phi_pi0 = 0.0

############################################################################
# User Section - definition of the sample and ctape position along (pi,pi)
############################################################################

x_sample_pipi = -1.373
y_sample_pipi = -2.0
z_sample_pipi = +0.9

x_ctape_pipi = +0.18
y_ctape_pipi = -2.0
z_ctape_pipi = -2.8

phi_pipi = 45

#############################################
# User Section - defining exit slit opening
#############################################
exit_slit = 20

#######################################################################
# User Section - defining energy at which dark image to be collected
#######################################################################
dark_image_energy = 810

########################################
#User Section - Defining CCD parameters
########################################

detector_to_use = andor

sample_no_images = 4
ctape_no_images = 1

sample_exposure_time = 300
ctape_exposure_time = 120

#####################################
# Information for spech calculation -- is this user section??
#####################################
specgammaval = 12  # Needs to be updated if gamma is changed.
Detector_pxsz = 0.01358
E_dispersion = 0.00675  # needs to be updated to the current experimental value
energy_val_fix = 931.4  # Resonant energy
spech_val_fix = 1365.554  # Spech corresponding to the resonant energy

###############################################################################
# User Section - Define Energies and Theta values at which we want to measure
###############################################################################
th_start = 20
th_staop = 140.01
th_step = 10

energy_start = 925
energy_stop = 935.01
energy_step = 0.4

##############################################################
###### User should NOT edit this section
##############################################################
#group sample and ctape positions together for each data collection  
sample_pi0 = [x_sample_pi0,y_sample_pi0,z_sample_pi0]
ctape_pi0 = [x_ctape_pi0,y_ctape_pi0,z_ctape_pi0]

sample_pipi = [x_sample_pipi,y_sample_pipi,z_sample_pipi]
ctape_pipi= [x_ctape_pipi,y_ctape_pipi,z_ctape_pipi]

#################################################################
# User Section - Define order of data collection
#################################################################

polarisation_collect_order = [LH, LV, LH, LV]
sample_collect_order = [sample_pi0, sample_pi0, sample_pipi, sample_pipi]
ctape_collect_order = [ctape_pi0, ctape_pi0, ctape_pipi, ctape_pipi]
phi_positions = [phi_pi0, phi_pi0, phi_pipi, phi_pipi]

##################################################################
###### User don't need to edit the sections below this line ######
##################################################################

collection_positions = zip(polarisation_collect_order, phi_positions, ctape_collect_order, sample_collect_order)
print("Data Collections are ordered in list (polarisation, phi_position, ctape_positions, sample_positions): %r" % collection_positions)

######################################################################
### Calculate raster points for data collection
######################################################################
th_list = [round(x,3) for x in frange(th_start, th_staop, th_step)]
print("theta positions: %r" % th_list)
energy_list = [round(x,3) for x in frange(energy_start, energy_stop, energy_step)]
print("energy positions: %r" % energy_list)

def generate_points(outer_list, inner_list):
    total_points = []
    for index, outer_val in enumerate(outer_list):
        if index % 2 == 0:
            for inner_val in inner_list:
                total_points.append((outer_val, inner_val))
        if index % 2 == 1:
            for inner_val in reversed(inner_list):
                total_points.append((outer_val, inner_val))
    print("Raster positions (th, energy): %r" % total_points)
    print("Total number of points: %r" % len(total_points))
    return total_points

point_list = generate_points(th_list, energy_list)

total_number_of_data_files_to_be_collected = (len(point_list) * len(collection_positions) * 2)
print("Total number of data files to be collected: %r" % (total_number_of_data_files_to_be_collected))
total_number_of_images_to_be_collected = (len(point_list) * len(collection_positions) * (sample_no_images + ctape_no_images))
print("Total number of images to be collected: %r" %  (total_number_of_images_to_be_collected))
import datetime
print("Total exposure time requested to detector excluding all motion times: %r" % str(datetime.timedelta(seconds = len(point_list) * len(collection_positions) * (sample_exposure_time * sample_no_images + ctape_exposure_time * ctape_no_images))))

# progress logs
number_of_data_files_collected_so_far = 0
number_of_images_collected_so_far = 0
number_of_data_files_to_be_collected = total_number_of_data_files_to_be_collected
number_of_images_to_be_collected = total_number_of_images_to_be_collected

###define experimental logics to collecting data from carbon tape and sample
def collect_data(ctape, sample, point_list, det):
    '''collect experiment data from ctape and sample positions at the given points with the given detector
    @param ctape: ctape position
    @param sample: sample position
    @param point_list: list of (th, energy) tuple positions 
    @param det: the detector used to collect images
    '''
    from acquisition.acquire_images import acquireRIXS
    from acquisition.acquireCarbonTapeImages import acquire_ctape_image, remove_ctape_image
    from scannabledevices.checkbeanscannables import checkbeam
    from utils.ScriptLogger import SinglePrint
    from time import sleep
    from gdaserver import th, m4c1, xyz_stage, pgmEnergy, spech  # @UnresolvedImport
    from scannable.continuous.continuous_energy_scannables import energy

    global number_of_data_files_collected_so_far,number_of_images_collected_so_far,number_of_data_files_to_be_collected,number_of_images_to_be_collected

    th_last = float(th.getPosition())
    for th_val, energy_val in point_list:
        if th_val != th_last:
            print("move th to %f ..." % th_val)
            th.asynchronousMoveTo(th_val)
            th_last = th_val
        while pgmEnergy.isBusy():
            SinglePrint.sprint("pgmEnergy is busy at the moment, wait for it to stop before move energy ...")
            sleep(1.0)
        print("move energy to %f ..." % energy_val)
        energy.asynchronousMoveTo(energy_val)
        spech_val = spech_val_fix+(energy_val_fix-energy_val)*Detector_pxsz*mh.sin(specgammaval*mh.pi/180)/E_dispersion
        print("move spech to %f ..." % spech_val)
        spech.asynchronousMoveTo(spech_val)
        th.waitWhileBusy()
        energy.waitWhileBusy()
        spech.waitWhileBusy()
        
        print("move to ctape position %r" % ctape)
        xyz_stage.moveTo(ctape)
        print('cTape at th = %.3f and Energy = %.3f'%(th_val,energy_val))
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
        
        print("move to sample position %r" % sample)
        xyz_stage.moveTo(sample)
        print('RIXS at th = %.3f and Energy = %.3f'%(th_val,energy_val))
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
        
        remove_ctape_image(det)

answer = "y"

# you can comment out the following line to remove user input required when running this script
answer = raw_input("\nAre these collection parameters correct to continue [y/n]?")

if answer == "y":
    from acquisition.darkImageAcqusition import acquire_dark_image
    from gdaserver import s5v1gap, difftth, fastshutter, spech  # @UnresolvedImport
    from shutters.detectorShutterControl import primary, polarimeter
    from functions.go_founctions import go
    from scannable.continuous.continuous_energy_scannables import energy

    #####################################
    # defining exit slit opening
    #####################################
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
    difftth.moveTo(0)    
    
    #################################################################
    #Defining E_initial
    #################################################################
    
    E_initial = energy_list[0] ## was 'E_initial = 931'
    E_end = energy_list[-1]
    
    #################################################################
    ###################### ACQUIRING DATA ###########################
    #################################################################
    if detector_to_use in [andor, xcam]:
        primary()
    if detector_to_use is andor2:
        polarimeter()
    fastshutter('Open')    

    # collecting data with given parameters
    from gdaserver import phi  # @UnresolvedImport
    i = 0
    for pol, phi_val, ctape, sample in collection_positions:
        phi.asynchronousMoveTo((phi_val))
        if i % 2 == 0:
            go(E_initial, pol) # for forward energy change
        if i % 2 == 1:
            go(E_end, pol) # for reverse energy change
        phi.waitWhileBusy()
        collect_data(ctape, sample, point_list, detector_to_use)
        i += 1
    
            
    #################################################
    #################################################
    
    # move spech to the optimised position for qscan (resonance)    
    energy.asynchronousMoveTo(energy_val_fix)
    spech.asynchronousMoveTo(spech_val_fix)
    energy.waitWhileBusy()
    spech.waitWhileBusy()

#####################################################################
print('Macro is completed !!!')

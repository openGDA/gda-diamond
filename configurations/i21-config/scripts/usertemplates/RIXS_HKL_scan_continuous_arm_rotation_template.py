'''
This module supports data collections from user defined carbon tape position and sample position in (x,y,z)
 at each of L, H or both positions in user-defined list for pi0, pipi or both directions at fixed energy position.
  
 This script converts the H,L positions to actual motor positions.
 
 This script first takes a dark image, followed by taking ctape image and sample images alternatively at each motors positions.

@since: 14 June 2022
@contact: Fajin Yuan
@group: Diamond I21 Team
@status: tested in dummy run off beamline I21

Testing parameters: (as currently recorded in this script)

Collection points for L Scan with fixed H at pi0: [(-37.15389, 17.519906, 13.519906, -0.05, 0.15), (-32.005315, 19.002562, 15.002562, -0.05, 0.175), (-27.458346, 20.585563, 16.585563, -0.05, 0.2), (-23.414161, 22.249341, 18.249341, -0.05, 0.225), (-19.786675, 23.979052, 19.979052, -0.05, 0.25), (-16.503751, 25.763492, 21.763492, -0.05, 0.275), (-13.506099, 27.594226, 23.594226, -0.05, 0.3), (-10.745398, 29.464903, 25.464903, -0.05, 0.325), (-8.182349, 31.370754, 27.370754, -0.05, 0.35), (-5.784932, 33.308214, 29.308214, -0.05, 0.375), (-3.526943, 35.274647, 31.274647, -0.05, 0.4)]
Collection points for L Scan with fixed H at pipi: [(-37.15389, 17.519906, 13.519906, -0.05, 0.15), (-32.005315, 19.002562, 15.002562, -0.05, 0.175), (-27.458346, 20.585563, 16.585563, -0.05, 0.2), (-23.414161, 22.249341, 18.249341, -0.05, 0.225), (-19.786675, 23.979052, 19.979052, -0.05, 0.25), (-16.503751, 25.763492, 21.763492, -0.05, 0.275), (-13.506099, 27.594226, 23.594226, -0.05, 0.3), (-10.745398, 29.464903, 25.464903, -0.05, 0.325), (-8.182349, 31.370754, 27.370754, -0.05, 0.35), (-5.784932, 33.308214, 29.308214, -0.05, 0.375), (-3.526943, 35.274647, 31.274647, -0.05, 0.4)]
Collection points for H Scan with fixed L at pi0: [(12.293779, 24.469251, 20.469251, 0.0001, 0.3), (41.100325, 27.594226, 23.594226, 0.05, 0.3), (-13.506099, 27.594226, 23.594226, -0.05, 0.3), (63.647351, 35.467015, 31.467015, 0.1, 0.3), (-28.180335, 35.467015, 31.467015, -0.1, 0.3), (80.143421, 45.990147, 41.990147, 0.15, 0.3), (-34.153274, 45.990147, 41.990147, -0.15, 0.3), (93.249286, 58.18034, 54.18034, 0.2, 0.3), (-35.068945, 58.18034, 54.18034, -0.2, 0.3), (104.736412, 71.829506, 67.829506, 0.25, 0.3), (-32.906906, 71.829506, 67.829506, -0.25, 0.3), (115.714305, 87.215654, 83.215654, 0.3, 0.3), (-28.498651, 87.215654, 83.215654, -0.3, 0.3)]
Collection points for H Scan with fixed L at pipi: [(12.293779, 24.469251, 20.469251, 0.0001, 0.3), (41.100325, 27.594226, 23.594226, 0.05, 0.3), (-13.506099, 27.594226, 23.594226, -0.05, 0.3), (63.647351, 35.467015, 31.467015, 0.1, 0.3), (-28.180335, 35.467015, 31.467015, -0.1, 0.3), (80.143421, 45.990147, 41.990147, 0.15, 0.3), (-34.153274, 45.990147, 41.990147, -0.15, 0.3), (93.249286, 58.18034, 54.18034, 0.2, 0.3), (-35.068945, 58.18034, 54.18034, -0.2, 0.3), (104.736412, 71.829506, 67.829506, 0.25, 0.3), (-32.906906, 71.829506, 67.829506, -0.25, 0.3), (115.714305, 87.215654, 83.215654, 0.3, 0.3), (-28.498651, 87.215654, 83.215654, -0.3, 0.3)]
Total number of data files to be collected: 96
Total number of images to be collected: 288
Total exposure time requested to detector excluding all motion times: '12:24:00'

Tests start at 2022-06-13 17:07:00.075 when dark image was taken, finish at 2022-06-14 09:03:50.269, total time taken is 15:56:50 (for the same sample and ctape position for pi0 and pipi)

This script provides data collection progress information as below:

Number of data files collected so far: 94
Number of data files to go: 2
Number of images collected so far: 282
Number of images to go: 6

The data collection process also monitors beam status: i.e. pause beam drops or during topup, and resume afterwards

=== Beam checking enabled: ringcurrent must exceed 190, currently True
=== Beam checking enabled: feBeamPermit must be in state: Open, currently True
=== Beam checking enabled: topup_time must exceed 5, currently True
*** checktopup_time: Beam down at: 08:48:33 . Pausing scan...
*** checktopup_time: Beam back up at: 08:48:34 . Resuming scan in 5s...
*** checktopup_time:  Resuming scan now at 08:48:39

This script is originally written by i21user.
Created on 27th Mar 2019

@author: i21user
'''

from gdascripts.utils import frange
from templates.momentumTransferFunctions import thLscan, tthLscan
from gdaserver import andor, andor2, xcam  # @UnresolvedImport

###########################################################################################
######################## SAMPLE PARAMETERS ################################################
###########################################################################################
# input of the lattice parameter
a = 4.01
b = a
c = 12.42

###########################################################
# definition of the sample and ctape position along (H,0)
###########################################################
phi_offset_pi0 = 0.0
chi_offset_pi0 = 0.0
th_offset_sample_pi0 = 0.0

#### Sample positions for (H, 0)
x_sample_pi0 = 0.0
y_sample_pi0 = 0.0
z_sample_pi0 = 0.0

#### ctape positions for (H, 0)
x_ctape_pi0 = 0.0
y_ctape_pi0 = 0.0
z_ctape_pi0 = 0.0

# enable collection at pi0
enable_pi0_collection = True

###########################################################
# definition of the sample and ctape position along (H,pi)
###########################################################
phi_offset_pipi = 0.0
chi_offset_pipi = 0.0
th_offset_sample_pipi = 0.0

#### Sample positions for (H, 0)
x_sample_pipi = 0.0
y_sample_pipi = 0.0
z_sample_pipi = 0.0

#### ctape positions for (H, 0)
x_ctape_pipi = 0.0
y_ctape_pipi = 0.0
z_ctape_pipi = 0.0

# enable collection at pipi
enable_pipi_collection = True

##############################################################################################
#####################################
# defining exit slit opening
#####################################
exit_slit = 20

#######################################################################
# User Section - defining energy at which dark image to be collected
#######################################################################
dark_image_energy = 760

####################################################################################################
#Defining CCD parameters
####################################################################################################
detector_to_use = andor

sample_no_images = 5
ctape_no_images = 1

sample_exposure_time = 180
ctape_exposure_time = 30

###################################################################################################
# defining the spectrometer position and energy
###################################################################################################

energy_val_fix = 706.6
energy_val_instrument = 706.6
spech_val_fix = 1626.316

specl_val_fix = 13013.143
sgmr1_val_fix = 2028.6832

############################################################################
#                  L scan with fixed H  (not valid for hexagonal symmetry) #
############################################################################
# a zero value of h_val or l_list would give a zero division error
h_val= -0.05

l_start = 0.15
l_stop = 0.41
l_step = 0.025

# enable L scan collection
enable_l_scan_at_fixed_h = True

############################################################################
#                 H scan with fixed L   (not valid for hexagonal symmetry) #
############################################################################
# a zero value of l_val or h_list would give a zero division error
l_val = 0.3

h_start = 0.05
h_stop = 0.31
h_step = 0.05

# enable H scan collection
enable_h_scan_at_fixed_l = True

# enable alternative positive and negative values of h to reduce number of tth motions
collect_both_positive_and_negative_h = True

#######################################################################
### Users don't modify this section
#######################################################################
# calculate l values for data collection
l_list = [round(x,3) for x in frange(l_start, l_stop, l_step)]
#l_list = [round(x,2) for x in frange(0, -0.16, 0.02)] + [round(x,2) for x in frange(-0.17, -0.3, 0.01)] + [-0.305]

def calculate_th_tth_from_h_l(hval, lval, th_offset):
    th_val = round(thLscan(energy_val_fix, hval, lval, th_offset, 1.0, 0, a, b, c), 6)
    true_tth_val = round(tthLscan(energy_val_fix, hval, lval, 1.0, 0, a, b, c), 6)
    armtth_val = round(true_tth_val - 4, 6)
    return th_val, true_tth_val, armtth_val
    
total_number_of_points_to_be_collected = 0

# calculate L scan collection points
if enable_pi0_collection:
    l_points_pi0 = []
    for lval in l_list:
        th_val, true_tth_val, armtth_val = calculate_th_tth_from_h_l(h_val, lval, th_offset_sample_pi0)
        l_points_pi0.append((th_val, true_tth_val, armtth_val, h_val, lval))
    print("Collection points for L Scan with fixed H at pi0: %r" % l_points_pi0)
    total_number_of_points_to_be_collected += len(l_points_pi0)

if enable_pipi_collection:
    l_points_pipi = []
    for lval in l_list:
        th_val, true_tth_val, armtth_val = calculate_th_tth_from_h_l(h_val, lval, th_offset_sample_pipi)
        l_points_pipi.append((th_val, true_tth_val, armtth_val, h_val, lval))
    print("Collection points for L Scan with fixed H at pipi: %r" % l_points_pipi)
    total_number_of_points_to_be_collected += len(l_points_pipi)

####################################################################
# calculate h values for data collection
hlist = [round(x,4) for x in frange(h_start, h_stop, h_step)]

if collect_both_positive_and_negative_h:
    # to reduce number of tth rotations, we make a list of positive and negative values sorted in increasing order of absolute value 
    h_list = [0.0001]
    
    for h_val in hlist:
        h_list.append(h_val)
        h_list.append(-h_val)
    # to reduce both tth rotations and th rotations, positive and negative values of h should alternate as below
    #h_list = [ 0.0001, 0.05, -0.05, -0.1, 0.1, 0.15, -0.15, -0.2, 0.2, 0.25, -0.25 -0.3, 0.3 ]
else:
    # for only positive or negative values please uncomment the line below
    h_list = hlist

# calculate H scan collection points
if enable_pi0_collection:
    h_points_pi0 = []
    for hval in h_list:
        th_val, true_tth_val, armtth_val = calculate_th_tth_from_h_l(hval, l_val, th_offset_sample_pi0)
        h_points_pi0.append((th_val, true_tth_val, armtth_val, hval, l_val))
    print("Collection points for H Scan with fixed L at pi0: %r" % h_points_pi0)  
    total_number_of_points_to_be_collected += len(h_points_pi0)
    
if enable_pipi_collection:
    h_points_pipi = []
    for hval in h_list:
        th_val, true_tth_val, armtth_val = calculate_th_tth_from_h_l(hval, l_val, th_offset_sample_pipi)
        h_points_pipi.append((th_val, true_tth_val, armtth_val, hval, l_val))
    print("Collection points for H Scan with fixed L at pipi: %r" % h_points_pipi)  
    total_number_of_points_to_be_collected += len(h_points_pipi)

################################################################################

total_number_of_data_files_to_be_collected = (total_number_of_points_to_be_collected * 2)
print("Total number of data files to be collected: %r" % (total_number_of_data_files_to_be_collected))
total_number_of_images_to_be_collected = (total_number_of_points_to_be_collected * (sample_no_images + ctape_no_images))
print("Total number of images to be collected: %r" %  (total_number_of_images_to_be_collected))
import datetime
print("Total exposure time requested to detector excluding all motion times: %r" % str(datetime.timedelta(seconds = total_number_of_points_to_be_collected * (sample_exposure_time * sample_no_images + ctape_exposure_time * ctape_no_images))))

##############################################################
###### User should NOT edit this section
##############################################################
#group sample and ctape positions together for each data collection  
sample_pi0 = [x_sample_pi0,y_sample_pi0,z_sample_pi0]
ctape_pi0 = [x_ctape_pi0,y_ctape_pi0,z_ctape_pi0]

sample_pipi = [x_sample_pipi, y_sample_pipi, z_sample_pipi]
ctape_pipi = [x_ctape_pipi, y_ctape_pipi, z_ctape_pipi]
 
###########################################################
# calculate m5hqx and sgmpitch position for a given tth
###########################################################
def calc_m5hqx(tth):
    return 5.45073852e-03 *tth**2 -2.76585727e+00*tth -4.99989695e+02

def calc_sgmpitch(tth):
    return -5.30033926e-09 * tth**3 + 8.63019222e-07 * tth**2 -4.12472878e-05*tth +  2.33059388e+00

# progress logs
number_of_data_files_collected_so_far = 0
number_of_images_collected_so_far = 0
number_of_data_files_to_be_collected = total_number_of_data_files_to_be_collected
number_of_images_to_be_collected = total_number_of_images_to_be_collected

###define experimental logics to collecting data from carbon tape and sample
def collect_data(point_list, det, ctape, sample, phi_offset, chi_offset):
    '''collect experiment data from ctape and sample positions at the given points with the given detector
    @param point_list: list of (th_val, true_tth_val, armtth_val, h_val, l_val) tuple positions 
    @param det: the detector used to collect images
    '''
    from gdaserver import gv17,m5hqx,sgmpitch,th,m5tth,armtth,m4c1,xyz_stage  # @UnresolvedImport
    from acquisition.acquireCarbonTapeImages import acquire_ctape_image, remove_ctape_image
    from i21commands.checkedMotion import move
    from gdascripts.metadata.nexus_metadata_class import meta
    from acquisition.acquire_images import acquireRIXS
    from scannabledevices.checkbeanscannables import checkbeam
    global number_of_data_files_collected_so_far,number_of_images_collected_so_far,number_of_data_files_to_be_collected,number_of_images_to_be_collected

    phi.asynchronousMoveTo(phi_offset)
    chi.asynchronousMoveTo(chi_offset)
    phi.waitWhileBusy()
    chi.waitWhileBusy()
    
    for th_val, true_tth_val, armtth_val, h_val, l_val in point_list:
    
        energy.asynchronousMoveTo(energy_val_instrument)
    
        print ('th=%.3f, m5tth=%.3f and true_tth=%.3f for h0=%.3f and l=%.3f\n'%(th_val,armtth_val,true_tth_val,h_val,l_val))
        gv17('Close')
        
        #Motor position correction for arm tth :
        print ('move m5hqx to %f ...' % calc_m5hqx(armtth_val))
        m5hqx.asynchronousMoveTo(calc_m5hqx(armtth_val))
        print ('move sgmpitch to %f ...' % calc_sgmpitch(armtth_val))
        sgmpitch.asynchronousMoveTo(calc_sgmpitch(armtth_val))
        
        #move rest of the motors:    
        print ('rotating theta to %f ...' % th_val)
        th.asynchronousMoveTo(th_val)
        print ('rotating collecting mirror to %f ...' % armtth_val)
        m5tth.asynchronousMoveTo(armtth_val)
        
        #Rotate the arm:
        print ('rotating arm with detector to %f ...' % armtth_val) 
        move(armtth,armtth_val,sgmr1_val=sgmr1_val_fix,specl_val=specl_val_fix)
        print ('arm rotation completed')
        
        #make sure all motor motions complete
        energy.waitWhileBusy()
        m5hqx.waitWhileBusy()
        sgmpitch.waitWhileBusy()
        th.waitWhileBusy()
        m5tth.waitWhileBusy()
        print("all motions are completed\n")
    
        # configure metadata to capture
        meta.addScalar("Q", "H", h_val) 
        meta.addScalar("Q", "K", 0) 
        meta.addScalar("Q", "L", l_val) 
    
        #Open Gate valve between sample vessel and detector
        gv17('Reset')
        gv17('Open')
    
        ###Collect data
        print("move to ctape position %r" % ctape_pi0)
        #### Note 'acquire_ctape_image' will create 'elastic_image' node link metadata item to the detector used.
        xyz_stage.moveTo(ctape)
        acquire_ctape_image(ctape_no_images, det, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
        number_of_data_files_collected_so_far += 1
        number_of_images_collected_so_far += ctape_no_images
        number_of_data_files_to_be_collected -= 1
        number_of_images_to_be_collected -= ctape_no_images
        print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
        print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
        print("Number of images collected so far: %r" % number_of_images_collected_so_far)
        print("Number of images to go: %r" % number_of_images_to_be_collected)
        print('******************************************************************\n')
        
        print("move to sample position %r" % sample_pi0)
        xyz_stage.moveTo(sample)
        acquireRIXS(sample_no_images, det, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
        number_of_data_files_collected_so_far += 1
        number_of_images_collected_so_far += sample_no_images
        number_of_data_files_to_be_collected -= 1
        number_of_images_to_be_collected -= sample_no_images
        print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
        print("Number of data files to go: %r" % number_of_data_files_to_be_collected)
        print("Number of images collected so far: %r" % number_of_images_collected_so_far)
        print("Number of images to go: %r" % number_of_images_to_be_collected)
        print('******************************************************************\n')
        
        # able next line if you want to explicitly remove the node link to ctape data collected above from any subsequent scan.
        remove_ctape_image(det)
    
        ### !!!remove dynamic metadata items if you don't want any side effect for future data collection into data files.
        meta.rm("Q", "H")
        meta.rm("Q", "K")
        meta.rm("Q", "L")  

answer = "y"

# you can comment out the following line to remove user input required when running this script
answer = raw_input("\nAre these collection parameters correct to continue [y/n]?")

if answer == "y":
    from gdaserver import phi, chi, s5v1gap, spech, fastshutter  # @UnresolvedImport
    from shutters.detectorShutterControl import primary, polarimeter
    from scannable.continuous.continuous_energy_scannables import energy
    from acquisition.darkImageAcqusition import acquire_dark_image
    
    s5v1gap.asynchronousMoveTo(exit_slit)
    energy.asynchronousMoveTo(energy_val_instrument)
    spech.asynchronousMoveTo(spech_val_fix)
    
    s5v1gap.waitWhileBusy()
    spech.waitWhileBusy()
    energy.waitWhileBusy()
    
    ###########################################
    # Dark Image                                                                #
    #############################################################################
    energy.moveTo(dark_image_energy)
    acquire_dark_image(1, andor, sample_exposure_time)
    energy.moveTo(energy_val_fix)
    
    # shutter control based on detector to use for data collection
    if detector_to_use in [andor, xcam]:
        primary()
    if detector_to_use is andor2:
        polarimeter()
    fastshutter('Open')   

    if enable_pi0_collection:
        ############################################################################
        #                  L scan with fixed H  (not valid for hexagonal symmetry) #
        ############################################################################
        if enable_l_scan_at_fixed_h:
            collect_data(l_points_pi0, detector_to_use, ctape_pi0, sample_pi0, phi_offset_pi0, chi_offset_pi0)  
            
        ############################################################################
        #                 H scan with fixed L   (not valid for hexagonal symmetry) #
        ############################################################################
        if enable_h_scan_at_fixed_l:
            collect_data(h_points_pi0, detector_to_use, ctape_pi0, sample_pi0, phi_offset_pi0, chi_offset_pi0)

    if enable_pipi_collection:
        ############################################################################
        #                  L scan with fixed H  (not valid for hexagonal symmetry) #
        ############################################################################
        if enable_l_scan_at_fixed_h:
            collect_data(l_points_pipi, detector_to_use, ctape_pipi, sample_pipi, phi_offset_pipi, chi_offset_pipi)  
            
        ############################################################################
        #                 H scan with fixed L   (not valid for hexagonal symmetry) #
        ############################################################################
        if enable_h_scan_at_fixed_l:
            collect_data(h_points_pipi, detector_to_use, ctape_pipi, sample_pipi, phi_offset_pipi, chi_offset_pipi)  
        
print ('macro is finished')

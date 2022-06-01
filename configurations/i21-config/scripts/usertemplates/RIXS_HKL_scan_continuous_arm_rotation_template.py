'''
This module support data collections from user defined carbon tape position and sample position in (x,y,z)
 at each of L positions and H positions. This script converts the H,L positions to actual motor positions.

@since: 30 May 2022
@contact: Fajin Yuan
@group: Diamond I21 Team
@status:   

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
l_list = [round(x,3) for x in frange(0.15, 0.41, 0.025)]
#l_list = [round(x,2) for x in frange(0, -0.16, 0.02)] + [round(x,2) for x in frange(-0.17, -0.3, 0.01)] + [-0.305]

# calculate L scan collection points
l_points = []
for l_val in l_list:
    th_val = round(thLscan(energy_val_fix, h_val, l_val, th_offset_sample_pi0, 1.0, 0, a, b, c), 6)
    true_tth_val = round(tthLscan(energy_val_fix, h_val, l_val, 1.0, 0, a, b, c), 6)
    armtth_val = round(true_tth_val - 4, 6)
    l_points.append((th_val, true_tth_val, armtth_val, h_val, l_val))
    
print("Collection points for L Scan with fixed H: %r" % l_points)  
############################################################################
#                 H scan with fixed L   (not valid for hexagonal symmetry) #
############################################################################
# a zero value of l_val or h_list would give a zero division error
l_val = 0.3
hlist = [round(x,2) for x in frange(0.05, 0.31, 0.05)]
# to reduce number of tth rotations, we make a list of positive and negative values sorted in increasing order of absolute value 
h_list = [0.0001]

for h_val in hlist:
    h_list.append(h_val)
    h_list.append(-h_val)
# to reduce both tth rotations and th rotations, positive and negative values of h should alternate as below
#h_list = [ 0.0001, 0.05, -0.05, -0.1, 0.1, 0.15, -0.15, -0.2, 0.2, 0.25, -0.25 -0.3, 0.3 ]

# calculate H scan collection points
h_points = []
for h_val in h_list:
    th_val = round(thLscan(energy_val_fix, h_val, l_val, th_offset_sample_pi0, 1.0, 0, a, b, c), 6)
    true_tth_val = round(tthLscan(energy_val_fix, h_val, l_val, 1.0, 0, a, b, c), 6)
    armtth_val = round(true_tth_val - 4, 6)
    h_points.append((th_val, true_tth_val, armtth_val, h_val, l_val))
 
print("Collection points for H Scan with fixed L: %r" % h_points)  

total_number_of_data_files_to_be_collected = ((len(l_points) + len(h_points)) * 2)
print("Total number of data files to be collected: %r" % (total_number_of_data_files_to_be_collected))
total_number_of_images_to_be_collected = ((len(l_points) + len(h_points)) * (sample_no_images + ctape_no_images))
print("Total number of images to be collected: %r" %  (total_number_of_images_to_be_collected))
import datetime
print("Total exposure time requested to detector excluding all motion times: %r" % str(datetime.timedelta(seconds = (len(l_points) + len(h_points)) * (sample_exposure_time * sample_no_images + ctape_exposure_time * ctape_no_images))))

##############################################################
###### User should NOT edit this section
##############################################################
#group sample and ctape positions together for each data collection  
sample_pi0 = [x_sample_pi0,y_sample_pi0,z_sample_pi0]
ctape_pi0 = [x_ctape_pi0,y_ctape_pi0,z_ctape_pi0]

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
def collect_data(point_list, det):
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
        xyz_stage.moveTo(ctape_pi0)
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
        xyz_stage.moveTo(sample_pi0)
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
    
    phi.asynchronousMoveTo(phi_offset_pi0)
    chi.asynchronousMoveTo(chi_offset_pi0)
    s5v1gap.asynchronousMoveTo(exit_slit)
    # energy.asynchronousMoveTo(energy_val_instrument) #????
    spech.asynchronousMoveTo(spech_val_fix)
    
    phi.waitWhileBusy()
    chi.waitWhileBusy()
    s5v1gap.waitWhileBusy()
    spech.waitWhileBusy()
    
    ##################################
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

    ############################################################################
    #                  L scan with fixed H  (not valid for hexagonal symmetry) #
    ############################################################################
        
    spech.moveTo(spech_val_fix)        
    collect_data(l_points, detector_to_use)  
        
    ############################################################################
    #                 H scan with fixed L   (not valid for hexagonal symmetry) #
    ############################################################################
    
    spech.moveTo(spech_val_fix)
    collect_data(h_points, detector_to_use)  


print ('macro is finished')

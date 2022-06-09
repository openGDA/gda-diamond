'''
This module support data collections from user defined carbon tape position and sample position in (x,y,z)
 at each of q positions. This script converts the q position to actual motor positions.
 
 @since 6 June 2022
 @contact: Fajin Yuan
 @status: tested in dummy

Created on 27th Mar 2019

@author: i21user

modified on 17/IX/19 by MGF
modified on 18/iX/19 by KJZ 
modified on 10/09/21 by JC 

'''
from gdaserver import  andor, andor2, xcam  # @UnresolvedImport
from gdascripts.utils import frange
from functions.go_founctions import go
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]


################################################################
# User Section - Defining the spectrometer tth scattering angle
################################################################

tth = 150.0
tth_m5hq = tth + 4.0
tth_m5lq = tth - 4.0 ###where this used???

########################################################################
##################### SAMPLE PARAMETERS ################################
########################################################################

###########################################################
# User Section - Lattice parameters
###########################################################

a = 3.88
b = 3.82
c = 11.68

##########################################################################
# User Section - definition of the sample and ctape position along (pi,0)#
##########################################################################

x_sample_pi0= +0.4429
y_sample_pi0= +0.7
z_sample_pi0= +1.6
phi_sample_pi0= 0
 
x_ctape_pi0=+0.39
y_ctape_pi0=-1.5
z_ctape_pi0=-3.5
phi_ctape_pi0= 0
 
chi_offset_pi0 = 0.0
th_offset_pi0 = +2.8+2.393
 
############################################################################
# User Section - definition of the sample and ctape position along (pi,pi)
############################################################################

x_sample_pipi=-1.373
y_sample_pipi=-2.0
z_sample_pipi=+0.9
phi_sample_pipi= 45
 
x_ctape_pipi=+0.18
y_ctape_pipi=-2.0
z_ctape_pipi=-2.8
phi_ctape_pipi= 45
 
chi_offset_pipi = 0.0
th_offset_pipi = +2.8+2.393
 
#############################################
# User Section - defining exit slit opening
#############################################
exit_slit = 20

#######################################################################
# User Section - defining energy at which dark image to be collected
#######################################################################
dark_image_energy = 931.5

##############################################################
#Defining Energy
##############################################################
E_initial = 931.5


########################################
#User Section - Defining CCD parameters
########################################

detector_to_use = andor

sample_no_images = 2
ctape_no_images = 1

sample_exposure_time = 3 #30
ctape_exposure_time = 1 #30


#####################################################################
################# Q range and steps #################################
#####################################################################

#### (PI, 0)

qStart_pi0 = 0.3
qEnd_pi0 = 0.5
qStep_pi0 = 0.05

#### (PI, PI)

qStart_pipi = 0.3
qEnd_pipi = 0.6 ###see I21-976 ValueError: math domain error
qStep_pipi = 0.05

######################################################################
### Calculate Q points for data collection
######################################################################

n_points_pi0 = int((qEnd_pi0-qStart_pi0)/qStep_pi0 + 1)
qlist_pi0 = [round(x,3) for x in frange(qStart_pi0, qEnd_pi0, qStep_pi0)]

n_points_pipi = int((qEnd_pipi-qStart_pipi)/qStep_pipi + 1)
qlist_pipi = [round(x,3) for x in frange(qStart_pipi, qEnd_pipi, qStep_pipi)]

##############################################################
###### User should NOT edit this section
##############################################################
#group sample and ctape positions together for each data collection  
sample_pi0 = [x_sample_pi0,y_sample_pi0,z_sample_pi0]
ctape_pi0 = [x_ctape_pi0,y_ctape_pi0,z_ctape_pi0]

sample_pipi = [x_sample_pipi,y_sample_pipi,z_sample_pipi]
ctape_pipi= [x_ctape_pipi,y_ctape_pipi,z_ctape_pipi]

##################################################################
# determine th value for each q
##################################################################
# this is to make theta position calculation from q early so if there is any math domain error it catched before scan or data collection starts
def calculate_theta_value_for_q(th_offset, qlist):
    from templates.momentumTransferFunctions import qtransinplane2th
    th_list = []
    for qval in qlist:
        try:
            thval = qtransinplane2th(E_initial, qval, th_offset, tth_m5hq, 1., 0., 0., a, b, c)
        except ValueError, e:
            print("\nCalculate theta value from q failed at qval = %.4f, th_offset = %.4f, tth_m5hq = %.4f, energy = %.4f" % (qval, th_offset, tth_m5hq, E_initial))
            raise e
        th_list.append(thval)    
    return th_list

thlist_pi0 = calculate_theta_value_for_q(th_offset_pi0, qlist_pi0)
thlist_pipi = calculate_theta_value_for_q(th_offset_pipi, qlist_pipi)

q_th_pair_list_pi0 = zip(qlist_pi0, thlist_pi0)
q_th_pair_list_pipi = zip(qlist_pipi, thlist_pipi)

#################################################################
# User Section - Define order of data collection
#################################################################

polarisation_collect_order = [LH,                 LV,                 LH,                  LV]
sample_collect_order =       [sample_pi0,         sample_pi0,         sample_pipi,         sample_pipi    ]
ctape_collect_order =        [ctape_pi0,          ctape_pi0,          ctape_pipi,          ctape_pipi     ]
phi_sample_positions =       [phi_sample_pi0,     phi_sample_pi0,     phi_sample_pipi,     phi_sample_pipi]
phi_ctape_positions =        [phi_ctape_pi0,      phi_ctape_pi0,      phi_ctape_pipi,      phi_ctape_pipi ]
q_th_pair_positions_list =   [q_th_pair_list_pi0, q_th_pair_list_pi0, q_th_pair_list_pipi, q_th_pair_list_pipi]


##################################################################
###### User don't need to edit the sections below this line ######
##################################################################

collection_positions = zip(polarisation_collect_order, phi_ctape_positions, phi_sample_positions, ctape_collect_order, sample_collect_order, q_th_pair_positions_list)
print("Data Collections are ordered in list (polarisation, phi_ctape_position, phi_sample_position, ctape_positions, sample_positions, q_positions): %r" % collection_positions)

total_number_of_data_files_to_be_collected = ((len(qlist_pi0) + len(qlist_pipi))* len(collection_positions) * 2)
print("Total number of data files to be collected: %r" % (total_number_of_data_files_to_be_collected))
total_number_of_images_to_be_collected = ((len(qlist_pi0) + len(qlist_pipi)) * len(collection_positions) * (sample_no_images + ctape_no_images))
print("Total number of images to be collected: %r" %  (total_number_of_images_to_be_collected))
import datetime
print("Total exposure time requested to detector excluding all motion times: %r" % str(datetime.timedelta(seconds = (len(qlist_pi0) + len(qlist_pipi)) * len(collection_positions) * (sample_exposure_time * sample_no_images + ctape_exposure_time * ctape_no_images))))

# progress logs
number_of_data_files_collected_so_far = 0
number_of_images_collected_so_far = 0
number_of_data_files__to_be_collected = total_number_of_data_files_to_be_collected
number_of_images_to_be_collected = total_number_of_images_to_be_collected

def collect_data(q_th_pair_list, ctape, sample, phi_ctape, phi_sample, pol, det):
    from acquisition.acquire_images import acquireRIXS
    from acquisition.acquireCarbonTapeImages import acquire_ctape_image, remove_ctape_image
    from scannabledevices.checkbeanscannables import checkbeam
    from gdascripts.metadata.nexus_metadata_class import meta
    from gdaserver import xyz_stage, th, m4c1, phi  # @UnresolvedImport
    
    global number_of_data_files_collected_so_far,number_of_images_collected_so_far,number_of_data_files__to_be_collected,number_of_images_to_be_collected

    print('\nscan between q= %.4f and q= %.4f using the M5hq mirror, s5v1gap = %d, %s, energy = %.2f'%(q_th_pair_list[0][0], q_th_pair_list[len(q_th_pair_list)-1][0], exit_slit, pol, E_initial))
    for qval, thval in q_th_pair_list:
        th.asynchronousMoveTo(thval)
        meta.addScalar("Q", "H", qval) 
        
        print('Total number of points is %d. Point number %d is at qtrans_inplane=%.4f, th=%.3f for ctape at %r' % (len(q_th_pair_list), number_of_data_files_collected_so_far + 1.0, qval, thval, ctape))
        phi.asynchronousMoveTo((phi_ctape))
        xyz_stage.moveTo(ctape)
        th.waitWhileBusy()
        phi.waitWhileBusy()
        acquire_ctape_image(ctape_no_images, det, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
        number_of_data_files_collected_so_far += 1
        number_of_images_collected_so_far += ctape_no_images
        number_of_data_files__to_be_collected -= 1
        number_of_images_to_be_collected -= ctape_no_images
        print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
        print("Number of data files to go: %r" % number_of_data_files__to_be_collected)
        print("Number of images collected so far: %r" % number_of_images_collected_so_far)
        print("Number of images to go: %r" % number_of_images_to_be_collected)
        print('******************************************************************')
    
        print('Total number of points is %d. Point number %d is at qtrans_inplane=%.4f, th=%.3f for sample at %r)' % (len(q_th_pair_list), number_of_data_files_collected_so_far + 1.0, qval, thval, sample))
        phi.asynchronousMoveTo((phi_sample))
        xyz_stage.moveTo(sample)
        phi.waitWhileBusy()
        acquireRIXS(sample_no_images, det, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)    
        number_of_data_files_collected_so_far += 1
        number_of_images_collected_so_far += sample_no_images
        number_of_data_files__to_be_collected -= 1
        number_of_images_to_be_collected -= sample_no_images
        print("Number of data files collected so far: %r" % number_of_data_files_collected_so_far)
        print("Number of data files to go: %r" % number_of_data_files__to_be_collected)
        print("Number of images collected so far: %r" % number_of_images_collected_so_far)
        print("Number of images to go: %r" % number_of_images_to_be_collected)
        print('*******************************************************************')
        
        # comment out next line if comment out acquire_ctape_image above
        remove_ctape_image(det)
        meta.rm("Q", "H")

answer = "y"

# you can comment out the following line to remove user input required when running this script
answer = raw_input("\nAre these collection parameters correct to continue [y/n]?")

if answer == "y":

    ############################################################
    ################# ACQUIRING DATA ###########################
    from gdaserver import  s5v1gap, difftth, fastshutter  # @UnresolvedImport
    from shutters.detectorShutterControl import primary, polarimeter    
    from scannable.continuous.continuous_energy_scannables import energy
    from acquisition.darkImageAcqusition import acquire_dark_image
    
    s5v1gap.moveTo(exit_slit)
    
    ######################################
    # moving diode to 0
    ######################################
    difftth.moveTo(0)
    
    ##################################################################
    #We acquire some dark images before the scan:
    ##################################################################
    #Dark Image
    energy.moveTo(dark_image_energy)
    acquire_dark_image(1, detector_to_use, sample_exposure_time)
    
    ###########################################
    
    #################### HQ MIRROR ###########################
    if detector_to_use in [andor, xcam]:
        primary()
    if detector_to_use is andor2:
        polarimeter()
    fastshutter('Open')
    
    for pol, phi_ctape, phi_sample, ctape, sample, q_th_pair_list in collection_positions:
        go(E_initial, pol)
        collect_data(q_th_pair_list, ctape, sample, phi_ctape, phi_sample, pol, detector_to_use)
    
#####################################################################
print('Macro is completed !!!')

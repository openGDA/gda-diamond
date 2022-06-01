'''
Created on 27th Mar 2019

@author: i21user
'''

from shutters.detectorShutterControl import primary
from scannable.continuous.continuous_energy_scannables import energy
from gdaserver import x, y, z, phi, chi, s5v1gap, spech, gv17, armtth, th, m5tth, xcam, m4c1  # @UnresolvedImport
from i21commands.checkedMotion import move
from gdascripts.metadata.nexus_metadata_class import meta
from acquisition.acquireCarbonTapeImages import acquire_ctape_image,\
    remove_ctape_image
from acquisition.acquire_images import acquireRIXS
from scannabledevices.checkbeanscannables import checkbeam
from templates.momentumTransferFunctions import thLscan, tthLscan


###########################################################################################
######################## SAMPLE PARAMETERS ################################################
###########################################################################################
###########################################################
# input of the lattice parameter

a = 4.01
b = a
c = 12.42


###########################################################
# definition of the sample and ctape position along (H,0)

phi_offset_H0 = 0.0
phi.moveTo(phi_offset_H0)

chi_offset_H0 = 0.0
chi.moveTo(chi_offset_H0)

th_offset_H0 = 0.0

#### Sample positions for (H, 0)
x_sample_H0 = 0.0
y_sample_H0 = 0.0
z_sample_H0 = 0.0

#### ctape positions for (H, 0)
x_ctape_H0 = 0.0
y_ctape_H0 = 0.0
z_ctape_H0 = 0.0


def sample_H0():
    x.asynchronousMovTo(x_sample_H0)
    y.asynchronousMovTo(y_sample_H0)
    z.asynchronousMovTo(z_sample_H0)
    x.waitWhileMoving()
    y.waitWhileMoving()
    z.waitWhileMoving()

def ctape_H0():
    x.asynchronousMovTo(x_ctape_H0)
    y.asynchronousMovTo(y_ctape_H0)
    z.asynchronousMovTo(z_ctape_H0)
    x.waitWhileMoving()
    y.waitWhileMoving()
    z.waitWhileMoving()    


##############################################################################################
#####################################
# defining exit slit opening
#####################################
exit_slit = 50
s5v1gap.moveTo(exit_slit)
primary()
#####################################

####################################################################################################
#Defining CCD parameters
####################################################################################################

sample_no_images = 1
ctape_no_images = 1

sample_exposure_time = 120
ctape_exposure_time = 30


##############################################################################################
#####################################
# defining the spectrometer position and energy
#####################################
energy_val_fix=930
spech_val_fix=1400

energy.moveTo(energy_val_fix)
spech.moveTo(spech_val_fix)
#############################################################################


############################################################################
# Defining the H,L values to be measured for a H scan:

l_val=1.0
h_list=[0.01,0.02,0.03,0.04]

for h_val in h_list:
    th_val = thLscan(energy_val_fix,h_val,l_val,th_offset_H0,1.0,0,a,b,c)
    true_tth_val = tthLscan(energy_val_fix,h_val,l_val,1.0,0,a,b,c)
    armtth_val = true_tth_val-4
    print ('th=%.3f, m5tth=%.3f and true_tth=%.3f for h0=%.3f and l=%.3f\n'%(th_val,armtth_val,true_tth_val,h_val,l_val))
    gv17('Close')

    #Rotate the arm:
    ########################################################################
    print ('rotating arm with detector') 
    move(armtth,armtth_val,sgmr1_val=2161.39,specl_val=12701.49)
    print ('arm rotation completed') 
    ########################################################################
    #move rest of the motors:
    ########################################################################
    print ('rotating theta')
    th.moveTo(th_val)
    print ('theta rotation completed')
    print ('rotating collecting mirror')
    m5tth.moveTo(armtth_val)
    print ('m5 rotation completed')
    ########################################################################
    meta.addScalar("Q", "H", h_val) 
    meta.addScalar("Q", "L", l_val) 
    #Open Gate valve between sample vessel and detector
    gv17('Reset')
    gv17('Open')
    
    #########################################################################
    ### Collect data
    #### Note 'acquire_ctape_image' will create 'elastic_image' node link metadata item to the detector used.
    ctape_H0()
    acquire_ctape_image(ctape_no_images, xcam, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
    sample_H0()
    acquireRIXS(sample_no_images, xcam, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
        
    # able next line if you want to explicitly remove the node link to ctape data collected above from any subsequent scan.
    remove_ctape_image(xcam)
    meta.rm("Q", "H")
    meta.rm("Q", "L")  


print ('macro is finished')
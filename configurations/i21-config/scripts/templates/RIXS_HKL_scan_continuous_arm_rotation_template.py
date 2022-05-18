'''
Created on 27th Mar 2019

@author: i21user
'''

from gdaserver import x, y, z, phi, chi, s5v1gap, spech, gv17, armtth, th, m5tth, m5hqx, m4c1, sgmpitch, andor, checkbeam# @UnresolvedImport
from shutters.detectorShutterControl import primary
from scannable.continuous.continuous_energy_scannables import energy
from acquisition.darkImageAcqusition import acquire_dark_image
from gdascripts.utils import frange
from templates.momentumTransferFunctions import thLscan, tthLscan
from i21commands.checkedMotion import move
from gdascripts.metadata.nexus_metadata_class import meta
from acquisition.acquireCarbonTapeImages import acquire_ctape_image, remove_ctape_image
from acquisition.acquireImages import acquireRIXS

###########################################################
###########################################################

def calc_m5hqx(tth):
    return 5.45073852e-03 *tth**2 -2.76585727e+00*tth -4.99989695e+02

def calc_sgmpitch(tth):
    return -5.30033926e-09 * tth**3 + 8.63019222e-07 * tth**2 -4.12472878e-05*tth +  2.33059388e+00

def tth_correction(tth):
    m5hqx.moveTo(calc_m5hqx(tth))
    sgmpitch.moveTo(calc_sgmpitch(tth))


# sleep(120)
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
phi_offset_pi0 = 0.0
phi.moveTo(phi_offset_pi0)

chi_offset_pi0 = 0.0
chi.moveTo(chi_offset_pi0)

th_offset_sample_pi0 = 0.0

#### Sample positions for (H, 0)
x_sample_pi0 = 0.0
y_sample_pi0 = 0.0
z_sample_pi0 = 0.0

#### ctape positions for (H, 0)
x_ctape_pi0 = 0.0
y_ctape_pi0 = 0.0
z_ctape_pi0 = 0.0


def sample_pi0():
    x.asynchronousMovTo(x_sample_pi0)
    y.asynchronousMovTo(y_sample_pi0)
    z.asynchronousMovTo(z_sample_pi0)
    x.waitWhileMoving()
    y.waitWhileMoving()
    z.waitWhileMoving()

def ctape_pi0():
    x.asynchronousMovTo(x_ctape_pi0)
    y.asynchronousMovTo(y_ctape_pi0)
    z.asynchronousMovTo(z_ctape_pi0)
    x.waitWhileMoving()
    y.waitWhileMoving()
    z.waitWhileMoving()    
   


##############################################################################################
#####################################
# defining exit slit opening
#####################################
exit_slit = 20
s5v1gap.moveTo(exit_slit)
primary()
#####################################


####################################################################################################
#Defining CCD parameters
####################################################################################################

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

energy.moveTo(energy_val_instrument)
spech.moveTo(spech_val_fix)

#############################################################################
# Dark Image                                                                #
#############################################################################
energy.moveTo(760)
acquire_dark_image(1, andor, sample_exposure_time)
energy.moveTo(energy_val_fix)

############################################################################
#                  L scan with fixed H  (not valid for hexagonal symmetry) #
############################################################################

spech.moveTo(spech_val_fix)

# a zero value of h_val or l_list would give a zero division error
h_val= -0.05
l_list = frange(0.15, 0.41, 0.025)
#l_list = frange(0, -0.16, 0.02) + frange(-0.17, -0.3, 0.01) + [-0.305]


for l_val in l_list:

    energy.moveTo(energy_val_instrument)

    th_val = thLscan(energy_val_fix, h_val, l_val, th_offset_sample_pi0, 1.0, 0, a, b, c)
    true_tth_val = tthLscan(energy_val_fix, h_val, l_val, 1.0, 0, a, b, c)
    armtth_val = true_tth_val - 4
    print ('th=%.3f, m5tth=%.3f and true_tth=%.3f for h0=%.3f and l=%.3f\n'%(th_val,armtth_val,true_tth_val,h_val,l_val))
    gv17('Close')
    
    #Calculate the rotation parameters:
    tth_correction(armtth_val)
    #Rotate the arm:
    print ('rotating arm with detector') 
    move(armtth,armtth_val,sgmr1_val=sgmr1_val_fix,specl_val=specl_val_fix)
    print ('arm rotation completed') 
    
    #move rest of the motors:    
    print ('rotating theta')
    th.moveTo(th_val)
    print ('theta rotation completed')
    print ('rotating collecting mirror')
    m5tth.moveTo(armtth_val)
    print ('m5 rotation completed')
    
    meta.addScalar("Q", "H", h_val) 
    meta.addScalar("Q", "K", 0) 
    meta.addScalar("Q", "L", l_val) 

    #Open Gate valve between sample vessel and detector
    gv17('Reset')
    gv17('Open')

    ###Collect data
    #### Note 'acquire_ctape_image' will create 'elastic_image' node link metadata item to the detector used.
    # ctape_pi0()
    # acquire_ctape_image(ctape_no_images, andor, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
    sample_pi0()
    acquireRIXS(sample_no_images, andor, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
    
    ### !!!remove dynamic metadata items if you don't want any side effect for future data collection into data files.
    # able next line if you want to explicitly remove the node link to ctape data collected above from any subsequent scan.
    # remove_ctape_image(andor)
    meta.rm("Q", "H")
    meta.rm("Q", "K")
    meta.rm("Q", "L")  
    
    
    
############################################################################
#                 H scan with fixed L   (not valid for hexagonal symmetry) #
############################################################################

spech.moveTo(spech_val_fix)

# a zero value of l_val or h_list would give a zero division error
l_val = 0.3
# to reduce number of tth rotations, we make a list of positive and negative values sorted in increasing order of absolute value 
hlist = frange(0.05, 0.31, 0.05)
h_list = [0.0001]
for h_val in hlist:
    h_list = h_list.append(h_val)
    h_list = h_list.append(-h_val)
# to reduce both tth rotations and th rotations, positive and negative values of h should alternate as below
#h_list = [ 0.0001, 0.05, -0.05, -0.1, 0.1, 0.15, -0.15, -0.2, 0.2, 0.25, -0.25 -0.3, 0.3 ] 


for h_val in h_list:

    energy.moveTo(energy_val_instrument)
    
    th_val = thLscan(energy_val_fix, h_val, l_val, th_offset_sample_pi0, 1.0, 0)
    true_tth_val = tthLscan(energy_val_fix, h_val, l_val, 1.0, 0)
    armtth_val = true_tth_val - 4
    print ('th=%.3f, m5tth=%.3f and true_tth=%.3f for h0=%.3f and l=%.3f\n'%(th_val,armtth_val,true_tth_val,h_val,l_val))
    gv17('Close')
    
    #Calculate the rotation parameters:
    tth_correction(armtth_val)

    #Rotate the arm:
    print ('rotating arm with detector') 
    move(armtth,armtth_val,sgmr1_val=sgmr1_val_fix,specl_val=specl_val_fix)
    print ('arm rotation completed') 
    
    #move rest of the motors:    
    print ('rotating theta')
    th.moveTo(th_val)
    print ('theta rotation completed')
    print ('rotating collecting mirror')
    m5tth.moveTo(armtth_val)
    print ('m5 rotation completed')
    
    meta.addScalar("Q", "H", h_val) 
    meta.addScalar("Q", "K", 0) 
    meta.addScalar("Q", "L", l_val) 

    #Open Gate valve between sample vessel and detector
    gv17('Reset')
    gv17('Open')

    #Collect data
    #### Note 'acquire_ctape_image' will create 'elastic_image' node link metadata item to the detector used.
    # ctape_pi0()
    # acquire_ctape_image(ctape_no_images, andor, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
    sample_pi0()
    acquireRIXS(sample_no_images, andor, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
    
    ### !!!remove dynamic metadata items if you don't want any side effect for future data collection into data files.
    # able next line if you want to explicitly remove the node link to ctape data collected above from any subsequent scan.
    # remove_ctape_image(andor)
    meta.rm("Q", "H")
    meta.rm("Q", "K")
    meta.rm("Q", "L")


print ('macro is finished')

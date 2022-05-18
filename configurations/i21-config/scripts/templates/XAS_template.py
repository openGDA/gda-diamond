'''
Created on 12th Oct 2021

@author: i21user
'''

from gdaserver import x,y,z,th,phi,chi, s5v1gap, energy, gv17, difftth, fastshutter, checkbeam, m5tth, draincurrent_i, diff1_i,fy2_i,m4c1 # @UnresolvedImport
from shutters.detectorShutterControl import erio, primary
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
from scan.cvscan import cvscan
from scannable.continuous.continuous_energy_scannables import draincurrent_c,\
    diff1_c, fy2_c, m4c1_c
from functions.go_founctions import go
from gdascripts.scan.installStandardScansWithProcessing import scan
LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]

#### Sample positions for (pi, 0)
# x_sample_pi0 = -1.815
# y_sample_pi0 = -0.27
# z_sample_pi0 = +2.297
# phi_sample_pi0 = -8.0
# chi_sample_pi0 = +10.85
#
#
# def sample_pi0():
#     '''move to sample_pi0 position concurrently and wait until all moves complete
#     '''
#     x.asynchronousMovTo(x_sample_pi0)
#     y.asynchronousMovTo(y_sample_pi0)
#     z.asynchronousMovTo(z_sample_pi0)
#     phi.asynchronousMovTo(phi_sample_pi0)
#     chi.asynchronousMovTo(chi_sample_pi0)
#     x.waitWhileBusy()
#     y.waitWhileBusy()
#     z.waitWhileBusy()
#     phi.waitWhileBusy()
#     chi.waitWhileBusy()
    
    
#####################################
# defining exit slit opening
#####################################
s5v1gap.moveTo(30)

# Position photo diode to so that we measure XAS through M5 optics
difftth.moveTo(float(m5tth.getPosition())+1.5)

#########################################################
#########################################################
#########  fast XAS scan  (on the fly) ##################
#########################################################
#########################################################

## Define energy range and step in eV, counting time in secs

E_initial = 520.0
E_final = 550.0
E_step = 0.05
counting_time = 0.1  #

# to change Femto Gain if the diode signal or drain current is too small or is saturating
# value must be one of (1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9) for "Low Noise" mode,  
draincurrent_i.setGain(1e8)
diff1_i.setGain(1e9)
fy2_i.setGain(1e9)
# please do NOT change m4c1 gain !!!

def fast_energy_scan_collection():
    # Keep Fast Shutter open throughout XAS measurements
    erio();fastshutter('Open');gv17('Close')
    
    # # Change polarisation to LH
    go(E_initial, LH)
    cvscan(energy, E_initial, E_final, E_step,  draincurrent_c, counting_time,  diff1_c, counting_time,  fy2_c, counting_time,  m4c1_c, counting_time, checkbeam)
    
    # # Change polarisation to LV
    go(E_initial, LV)
    cvscan(energy, E_initial, E_final, E_step,  draincurrent_c, counting_time,  diff1_c, counting_time,  fy2_c, counting_time,  m4c1_c, counting_time, checkbeam)

#########################################################
#########  NORMAL INCIDENCE , THETA = 90 ################
#########################################################

# Move to sample and correct theta
# sample_pi0()
# th.moveTo(90)
# fast_energy_scan_collection()


########################################################
#########  GRAZING IN , THETA = 20 #####################
########################################################

# Move to sample and correct theta
# sample_pi0()
# th.moveTo(20)
fast_energy_scan_collection()


#########################################################
#########################################################
#########  slow XAS scan  (step mode)  ##################
#########################################################
#########################################################
# 
# ## Define energy range and step in eV, counting time in secs
# 
# E_initial = 925.0
# E_final = 965.0
# E_step = 0.1
# counting_time = 1  #

def slow_energy_scan_collection():
    # # Keep Fast Shutter open throughout XAS measurements
    erio();fastshutter('Open');gv17('Close')
    
    # # # Change polarisation to LH
    go(E_initial, LH)
    energy.moveTo(E_initial-2)
    scan(energy, E_initial, E_final, E_step, draincurrent_i, counting_time,  diff1_i, counting_time, fy2_i, counting_time,  m4c1, counting_time, checkbeam)
     
    # # # Change polarisation to LV
    go(E_initial, LV)
    energy.moveTo(E_initial-2)
    scan(energy, E_initial, E_final, E_step, draincurrent_i, counting_time,  diff1_i, counting_time, fy2_i, counting_time,  m4c1, counting_time, checkbeam)
# 
# #########################################################
# #########  NORMAL INCIDENCE , THETA = 90 ################
# #########################################################
# 
# # Move to sample and correct theta
# sample_pi0()
# th.moveTo(90)
# slow_energy_scan_collection()
# 
# # 
# ########################################################
# #########  GRAZING IN , THETA = 20 #####################
# ########################################################
# 
# # Move to sample and correct theta
# sample_pi0()
# th.moveTo(20)
# slow_energy_scan_collection()
# 

# ###################################################################
# ###################################################################
# # Revert fast shutter to normal RIXS operation
primary();fastshutter('Open');gv17('Open')
  
# # Position diff1 so that it is out of the way of the outgoing x-ray beam
difftth.moveTo(0)
  
print('All of the macro is completed !!!')



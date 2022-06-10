'''
Created on 12th Oct 2021

@author: SA
'''

from gdaserver import xyz_stage, th, s5v1gap, gv17, difftth, fastshutter, m5tth, draincurrent_i, diff1_i,fy2_i # @UnresolvedImport
from shutters.detectorShutterControl import erio, primary
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
from scan.cvscan import cvscan
from functions.go_founctions import go
import installation
LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]


#########################################################################
# definition of the sample and ctape position along (pi,0)
#########################################################################

x_sample_pi0 = -1.
y_sample_pi0 = 0.0
z_sample_pi0 = 0.0

y_sample_increment = 0.05
Y_Sample_iteration_number = 5

z_sample_increment = 0.01
z_sample_iteration_number = 5

#########################################################################
## Define energy range and step in eV, counting time in secs
#########################################################################
E_initial = 925.0
E_final = 965.0
E_step = 0.05
counting_time = 0.1

#########################################################################
## Define Polarisation value - one of (LH,LV,CR,CL,LH3,LV3,LH5,LV5)
#########################################################################
pol_val = LH

#############################################
# User Section - defining exit slit opening
#############################################
exit_slit = 30

#########################################################################
## Define amplifier's gain
#########################################################################
# to change Femto Gain if the diode signal or drain current is too small or is saturating
# value must be one of (1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9) for "Low Noise" mode,  
if installation.isLive():
    draincurrent_i.setGain(1e9)
    diff1_i.setGain(1e8)
    fy2_i.setGain(1e8)
# please do NOT change m4c1 gain !!!

#####################################
# defining exit slit opening
#####################################
s5v1gap.asynchronousMoveTo(exit_slit)

# Position photo diode to so that we measure XAS through M5 optics
difftth.asynchronousMoveTo(float(m5tth.getPosition())+1.5)

#########################################################
#########  NORMAL INCIDENCE , THETA = 90 ################
#########################################################

# Move to sample and correct theta
xyz_stage.asynchronousMoveTo([x_sample_pi0, y_sample_pi0, z_sample_pi0])
th.asynchronousMoveTo(90)

s5v1gap.waitWhileBusy()
difftth.waitWhileBusy()
xyz_stage.waitWhileBusy()
th.waitWhileBusy()

# Keep Fast Shutter open throughout XAS measurements
erio();fastshutter('Open');gv17('Close')

# # Change polarisation to LH
go(E_initial, pol_val)

#########################################################
#########  fast XAS scan  (on the fly) ##################
#########################################################
#########################################################
from scannable.continuous.continuous_energy_scannables import draincurrent_c, diff1_c, fy2_c, m4c1_c, energy
from scannabledevices.checkbeanscannables import checkbeamcv
for j in range(z_sample_iteration_number):
    for i in range(Y_Sample_iteration_number):
        xyz_stage.moveTo([x_sample_pi0, y_sample_pi0 + y_sample_increment * i, z_sample_pi0 + z_sample_increment * j])
        cvscan(energy, E_initial, E_final, E_step, draincurrent_c, counting_time,  diff1_c, counting_time,  fy2_c, counting_time, m4c1_c, counting_time, checkbeamcv)
        print("sample y increment number: %r" % (i+1))
    print("sample z increment number: %r" % (j+1))


###################################################################
###################################################################
# Revert fast shutter to normal RIXS operation
primary();fastshutter('Open');gv17('Open')
 
# # Position diff1 so that it is out of the way of the outgoing x-ray beam
difftth.moveTo(0)
 
print('All of the macro is completed !!!')


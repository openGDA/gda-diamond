'''
XAS - fast energy scan with raster of sample position y and z

@since: 20 June 2022
@contact: Fajin Yuan
@group: Diamond I21 Team
@status: tested in dummy mode  

Created on 12th Oct 2021

@author: SA
'''

from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
import installation
LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]


#########################################################################
# definition of the sample and ctape position along (pi,0)
#########################################################################

x_sample_pi0 = -1.
y_sample_pi0 = 0.0
z_sample_pi0 = 0.0

phi_sample_pi0 = 0.0
chi_sample_pi0 = 0.0

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

#############################################
# User Section - defining th value
#############################################
th_val = 90

#########################################################################
## Define amplifier's gain
#########################################################################
# to change Femto Gain if the diode signal or drain current is too small or is saturating
# value must be one of (1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9) for "Low Noise" mode,  
if installation.isLive(): #only live mode requires this - i.e running in i21 GDA.
    from gdaserver import draincurrent_i, diff1_i,fy2_i # @UnresolvedImport
    draincurrent_i.setGain(1e9)
    diff1_i.setGain(1e8)
    fy2_i.setGain(1e8)
# please do NOT change m4c1 gain !!!

#####################################
# data collection
#####################################
from gdaserver import xyz_stage, th, s5v1gap, gv17, difftth, fastshutter, m5tth, phi, chi # @UnresolvedImport
from shutters.detectorShutterControl import erio, primary
from functions.go_founctions import go

# defining exit slit opening
print("move s5v1gap to %f ..." % exit_slit)
s5v1gap.asynchronousMoveTo(exit_slit)

# Position photo diode to so that we measure XAS through M5 optics
difftth_val = float(m5tth.getPosition())+1.5
print("move difftth to %f ..." % difftth_val)
difftth.asynchronousMoveTo(difftth_val)

# Move to sample and correct theta
print("move sampel stage to %r ..." % [x_sample_pi0, y_sample_pi0, z_sample_pi0])
xyz_stage.asynchronousMoveTo([x_sample_pi0, y_sample_pi0, z_sample_pi0])

print("move th to %f ..." % th_val)
th.asynchronousMoveTo(th_val)
print("move phi to %f ..." % phi_sample_pi0)
phi.asynchronousMoveTo(phi_sample_pi0)
print("move chi to %f ..." % chi_sample_pi0)
chi.asynchronousMoveTo(chi_sample_pi0)

s5v1gap.waitWhileBusy()
difftth.waitWhileBusy()
xyz_stage.waitWhileBusy()
th.waitWhileBusy()
phi.waitWhileBusy()
chi.waitWhileBusy()
print("All motions are now completed")

# Keep Fast Shutter open throughout XAS measurements
erio();fastshutter('Open');gv17('Close')

# # Change polarisation to LH
go(E_initial, pol_val)

#########################################################
#########  fast XAS scan  (on the fly) ##################
#########################################################

from scannable.continuous.continuous_energy_scannables import draincurrent_c, diff1_c, fy2_c, m4c1_c, energy
from scannabledevices.checkbeanscannables import checkbeamcv
from scan.cvscan import cvscan

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


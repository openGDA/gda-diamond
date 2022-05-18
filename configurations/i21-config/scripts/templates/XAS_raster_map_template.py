'''
Created on 12th Oct 2021

@author: SA
'''

from gda.jython.commands.ScannableCommands import inc
from gdaserver import x,y,z,th,phi,chi, s5v1gap, energy, gv17, difftth, fastshutter, checkbeam, m5tth, draincurrent_i, diff1_i,fy2_i # @UnresolvedImport
from shutters.detectorShutterControl import erio, primary
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
from scan.cvscan import cvscan
from scannable.continuous.continuous_energy_scannables import draincurrent_c,\
    diff1_c, fy2_c, m4c1_c
from functions.go_founctions import go
LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]

#########################################################################


#########################################################################
# definition of the sample and ctape position along (pi,0)
#########################################################################

x_sample_pi0 = -1.
y_sample_pi0 = 0.0
z_sample_pi0 = 0.0
th_sample_pi0 =0.0
phi_sample_pi0 = 0.0
chi_sample_pi0 = 0.0

def sample_pi0():
    '''move to sample_pi0 position concurrently and wait until all moves complete
    '''
    x.asynchronousMovTo(x_sample_pi0)
    y.asynchronousMovTo(y_sample_pi0)
    z.asynchronousMovTo(z_sample_pi0)
    th.asynchronousMovTo(th_sample_pi0)
    phi.asynchronousMovTo(phi_sample_pi0)
    chi.asynchronousMovTo(chi_sample_pi0)
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    th.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
    

#####################################
# defining exit slit opening
#####################################
s5v1gap.moveTo(30)

# Position photodiode to so that we measure XAS through M5 optics
difftth.moveTo(float(m5tth.getPosition())+1.5)

#########################################################
#########################################################
#########  fast XAS scan  (on the fly) ##################
#########################################################
#########################################################

## Define energy range and step in eV, counting time in secs

E_initial = 925.0
E_final = 965.0
E_step = 0.05
counting_time = 0.1  #

# to change Femto Gain if the diode signal or drain current is too small or is saturating
# value must be one of (1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9) for "Low Noise" mode,  
draincurrent_i.setGain(1e9)
diff1_i.setGain(1e8)
fy2_i.setGain(1e8)
# please do NOT change m4c1 gain !!!

#########################################################
#########  NORMAL INCIDENCE , THETA = 90 ################
#########################################################

# Move to sample and correct theta
sample_pi0()
th.moveTo(90)

# Keep Fast Shutter open throughout XAS measurements
erio();fastshutter('Open');gv17('Close')

# # Change polarisation to LH
go(E_initial,LH)
for j in range(5):
    for i in range(5):
        sample_pi0()   #why it needs to go back to here every iteration in the loop?
        inc(z, 0.01*j)
        inc(y, 0.05*i)
        cvscan(energy, E_initial, E_final, E_step, draincurrent_c, counting_time,  diff1_c, counting_time,  fy2_c, counting_time, m4c1_c, counting_time, checkbeam)
        print(i+1)
    print(j+1)


###################################################################
###################################################################
# Revert fast shutter to normal RIXS operation
primary();fastshutter('Open');gv17('Open')
 
# # Position diff1 so that it is out of the way of the outgoing x-ray beam
difftth.moveTo(0)
 
print('All of the macro is completed !!!')


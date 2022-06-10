'''
Created on 12th Oct 2021

@author: SA
'''

from gdaserver import andor, andor2, xcam  # @UnresolvedImport
from gdaserver import fy2_i, s5v1gap,th,fastshutter,gv17,difftth,m5tth,draincurrent_i,diff1_i,z  # @UnresolvedImport
from gdascripts.scan.installStandardScansWithProcessing import rscan
from shutters.detectorShutterControl import erio, primary, polarimeter

#########################################################################


#########################################################################
# definition of the sample position 
#########################################################################

# sample position to start with
x_sample = -1.
y_sample = 0.0
z_sample = 0.0

#relative z scan parameters
z_start_relative = -0.8
z_stop_relative = 0.9
z_step_relative = 0.05
 

    
########################################
#User Section - Defining CCD parameters
########################################
detector_to_use = andor

########################################
#User Section - Defining resonant energy
########################################
# resonant_energy = 530

#####################################
# defining exit slit opening
#####################################
s5v1gap.moveTo(30)

#########################################################
### Instructions to scan sample position along z  #######
#########################################################

# go to sample position, for example
# sample_pi0()

#move sample to normal incidence
th.moveTo(90)

# move the fast shutter to the erio mode:
erio()

# If the fast shutter is closed, we can open it with the following command
fastshutter('Open')

# Whenever using the erio mode, the beam will be continuously on the sample, then the best
# is to close the valve between the SGM and the arm to protect the CCD detector :
gv17('Close')

# Move the diode (diff1) in position to measure TFY
difftth.moveTo(float(m5tth.getPosition())+1.5)

# measure z scans with diff1 and draincurrent on resonant energy (for example 530) to improve the alignment.
# energy.moveTo(resonant_energy)

# Do a relative z-scan with steps of 0.05 mm for 1 sec
rscan(z, -0.8, 0.9, 0.05, draincurrent_i, 1, diff1_i, 1, fy2_i, 1)
# take note of the scan number for future plotting for comparison 
# if the sample has moved please change to the new z position, for example 1.56
# z.moveTo(1.56)

# Once we have found the optimal positions z, first we change the mode of the fastshutter to camera mode.
if detector_to_use in [andor, xcam]:
    primary()
if detector_to_use is andor2:
    polarimeter()

# Then we open the valve between the SGM and the detector:
gv17('Open')

# Position diff1 so that it is out of the way of the outgoing x-ray beam
difftth.moveTo(0)

print('please correct the sample position in the script and save the script')
# remember to go to the original th, for example 27 degrees
# th.moveTo(27)

# Please note that x could change too. So please check that the sample signal is centred in the detector camera
s5v1gap.moveTo(20)

 
print('All of the macro is completed !!!')


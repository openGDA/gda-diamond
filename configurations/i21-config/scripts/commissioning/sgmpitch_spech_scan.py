'''
This script will ensure SGM pitch and detector height move together so that the elastic peak always appears at a fixed position. 
# The step of detector height movement sgmpitch will depend on each gamma angle

# Moving sgmpitch by 0.002 deg changes the beam position on the detector surface by 120 pixels - for specgamma of 20.0 degree - VPG2 & SVLS1 for pgmEnergy = 350 eV
# Moving sgmpitch by 0.002 deg changes the beam position on the detector surface by 115 pixels - for specgamma of 20.0 degree - VPG2 & SVLS1 for pgmEnergy = 532 eV
# Moving sgmpitch by 0.002 deg changes the beam position on the detector surface by 103 pixels - for specgamma of 20.0 degree - VPG3 & SVLS1 for pgmEnergy = 778 eV
# Moving sgmpitch by 0.002 deg changes the beam position on the detector surface by 110 pixels - for specgamma of 20.0 degree - VPG3 & SVLS1 for pgmEnergy = 852 eV
# Moving sgmpitch by     0.002 deg changes the beam position on the detector surface by 100 pixels - for specgamma of 20.0 degree - VPG3 & SVLS1 for pgmEnergy = 925 eV


# Moving sgmpitch by 0.002 deg changes the beam position on the detector surface by 117 pixels - for specgamma of 20.0 degree - VPG3 & SVLS2 for pgmEnergy = 530 eV
# Moving sgmpitch by 0.002 deg changes the beam position on the detector surface by 108 pixels - for specgamma of 20.0 degree - VPG3 & SVLS2 for pgmEnergy = 712 eV
# Moving sgmpitch by 0.002 deg changes the beam position on the detector surface by 109 pixels - for specgamma of 20.0 degree - VPG3 & SVLS2 for pgmEnergy = 778 eV
# Moving sgmpitch by 0.002 deg changes the beam position on the detector surface by 110 pixels - for specgamma of 20.0 degree - VPG2 & SVLS2 for pgmEnergy = 956 eV
# Moving sgmpitch by 0.002 deg changes the beam position on the detector surface by 105 pixels - for specgamma of 20.0 degree - SVLS2 for pgmEnergy = 1189 eV
# Moving sgmpitch by 0.002 deg changes the beam position on the detector surface by 199 pixels - for specgamma of 12.0 degree - VPG2 & SVLS2 for pgmEnergy = 646 eV

Modified on Sep 15, 2022

@author: fy65

'''

import math as mh
from gdascripts.utils import frange
from gdaserver import andor, Polandor_H, xcam # @UnresolvedImport

# INSERT CURRENT SGMPITCH and SPECH HERE!
sgmpitch_original = 2.325
spech_original = 1415.87

# INSERT SHIFT FOR CURRENT ENERGY AND SPECTROMETER GRATING AT SPECGAMMA DEFINED BY SPECGAMMAVAL
shift = 115 # shift of beam in the vertical direction by moving sgmpitch by 0.002 deg at specgamma=specgammaval
specgammaval = 20 # Please do not change!! the nominal angle for the vertical shift defined above

step_number = 6

sgmpitch_step_original = 0.002

sgmpitch_step  = 0.001

detector_to_use = andor
exposure_time = 20.0

s5v1gap_val = 20.0

################ user parameter section above #############

deltapix = shift*mh.sin(specgammaval*mh.pi/180)

sgmpitch_start = sgmpitch_original - (int(step_number))*sgmpitch_step
sgmpitch_end   = sgmpitch_original + (int(step_number))*sgmpitch_step
sgmpitch_positions = [round(x,3) for x in frange(sgmpitch_start, sgmpitch_end, sgmpitch_step)]

spech_step  = deltapix*(sgmpitch_step/sgmpitch_step_original)*13.5*0.001
spech_start = spech_original - spech_step*(int(step_number))
spech_end   = spech_original + spech_step*(int(step_number))
spech_positions = [round(x,3) for x in frange(spech_start, spech_end, spech_step)]

#create tuple of lists for sgmpitch and spech pair
sgmpicth_spech_pair_positions = tuple(map(list, zip(sgmpitch_positions, spech_positions)))

# create scannable group to move (sgmpitch, spech) in pair
from gda.device.scannable.scannablegroup import ScannableGroup
from gdaserver import sgmpitch, s5v1gap, spech, fastshutter  # @UnresolvedImport

sgmpitch_spech_scannable_group = ScannableGroup()
from commissioning.Scannable_Wrapper import spech_wraper
sgmpitch_spech_scannable_group.addGroupMember(sgmpitch, spech_wraper)

s5v1gap.moveTo(s5v1gap_val)

from shutters.detectorShutterControl import primary, polpi
if detector_to_use in [andor, xcam]:
    primary()
elif detector_to_use is Polandor_H:
    polpi()
fastshutter('Open')

#collec data using nested scan
from gda.jython.commands.ScannableCommands import scan
scan(sgmpitch_spech_scannable_group, sgmpicth_spech_pair_positions, detector_to_use, exposure_time)

print('All scans are done!!!')

from i21commands.checkedMotion import move
move(spech, spech_original)
sgmpitch.moveTo(sgmpitch_original)

'''
This script will collect images of the elastic peaks as function of PGM cff value. 

all images are collected into the same .nxs file.
this script can be extended to include elatic peak data process at the end of this script.

Created on Sep 15, 2022

@author: fy65
'''

from gdaserver import  fastshutter, s5v1gap, d7gascell, d8stick  # @UnresolvedImport
from shutters.detectorShutterControl import primary, polarimeter
from gdaserver import andor, andor2, xcam # @UnresolvedImport

######### user-defined parameter section ###########################################
### Only one of VPG should be True ###
VPG1 = False
VPG2 = True
VPG3 = False

## set detector parameter here
detector_to_use = andor
exposure_time = 30.0

## set motor position here
s5v1gap_val = 20.0
d7gascell_val = 40.0
d8stick_val = 40.0

################################################################################
# The optimised cff of VPG2 for LV is ~ 3.16 at 930 eV for s1vize of 1.5mm, s3vsize of 2.4mm. Oct 8, 2017
# The optimised cff of VPG3 for LV is ~ 5.60 at 930 eV for s1vize of 1.5mm, s3vsize of 2.4mm. Oct 8, 2017
# The optimised cff of VPG2 for LH is ~ 3.12 at 530 eV for s1vize of 1.5mm, s3vsize of 2.5mm. Oct 12, 2017
#### set CFF parameter for each VPG to use here
if VPG1:
    cff_start = 2.04
    cff_end = 2.15
    cff_step = 0.01
    cff_original = 2.1

if VPG2:
    cff_start = 3.25
    cff_end = 3.37
    cff_step = 0.01
    cff_original = 3.31

if VPG3:
    cff_start = 5.0
    cff_end = 6.0
    cff_step = 0.05
    cff_original = 5.5

######### end of user parameter settings ######

s5v1gap.moveTo(s5v1gap_val)
d7gascell.moveTo(d7gascell_val)
d8stick.moveTo(d8stick_val)

if detector_to_use in [andor, xcam]:
    primary()
elif detector_to_use is andor2:
    polarimeter()
fastshutter('Open')

from commissioning.cff_b2_scannable import cff_b2
from gdascripts.scan.installStandardScansWithProcessing import scan

scan(cff_b2, cff_start, cff_end, cff_step, detector_to_use, exposure_time)
    
print('\n')

# Move cff back to the starting value
cff_b2.moveTo(cff_original)


print('All scans are done !!!')

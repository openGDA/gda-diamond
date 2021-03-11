Notes 20210301
Assumed structure/folders

/dls_sw/b16/software/var_diffraction
  |__cbf-cache

contents of var_diffraction
- cbf template
- beamline.parameters file referenced by property

Script module structure at 202102

config/scripts
  |__component
  |__datacollection
  |__det_wrapper
  |__framework
  |__procedure

Activated by: 
from datacollection.diffraction import *
mx_dc.setup(...)
mx_dc.collect()

Finer control over parameters via the diffraction module


Objects:
[DetectorControl]
  |__[detector]
  |__[scan_control]  --> zebra
  |__[shutter_control]  --> zebra

Data Structures:
Primary collection parameters container: ExtendedCollectRequests
Facades for access:
- RunMetadata for single scan parameters
- DatasetMetadata for file location metadata



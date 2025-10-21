#!/dls_sw/apps/python/miniforge/4.10.0-0/envs/python3.10/bin/python
#python environment set by : module load python
# Determine which Spring profiles to use based on which PVs are present 

import epics
from time import sleep

# key = name of spring profile, value = name of PV to check
profile_pv_list = { "spectrometer":"BL18I-MO-XTL-01:PX.RBV",
"vortex":"BL18I-EA-DET-07:CollectMode",
"andor":"BL18I-EA-DET-10:CAM:PortName_RBV",
"medipix":"BL18I-EA-DET-04:DET:PortName_RBV",
"xspress3mini":"BL18I-EA-XSP-03:PortName_RBV"}

# make PV object for each PV to be checked (in parallel, to save time - as recommended in pyepics documentation)
pvs = {prof:epics.PV(pv_name) for prof, pv_name in profile_pv_list.items()}

# sleep to ensure PV objects have been fully initialised (8/4/2025 : 0.2 sec is not always enough for vortex?)
sleep(0.5)

# Make list of profiles to be used, based on PV connection state
profiles = ["-P"]
profile_list = ["-p " + profile_name for profile_name, pv in pvs.items() if pv.connected]

# Print comma separated list of profiles (this is captured by bash script and used in gda startuo parameters)
print(" ".join(profiles+profile_list))

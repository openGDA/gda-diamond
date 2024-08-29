#!/dls_sw/apps/python/miniforge/4.10.0-0/envs/python3.10/bin/python
#python environment set by : module load python


import epics
from time import sleep

# Check whether PV of given name exists
def pv_exists(pv_name) :
    pv = epics.PV(pv_name)
    sleep(0.2) # sleep to ensure pv object has been fully initialised
    return pv.connected


# key = name of spring profile, value = name of PV to check
profile_pv_list = { "spectrometer":"BL18I-MO-DET-01:X.RBV", "vortex":"BL18I-EA-DET-07:CollectMode",
"andor":"BL18I-EA-DET-10:CAM:PortName_RBV", "medipix": "BL18I-EA-DET-04:DET:PortName_RBV" }

# Determine which spring profiles to use based on which PVs are present :
profiles=[]
for profile_name, pv in profile_pv_list.items() :
    if pv_exists(pv) :
        profiles.append("-p "+profile_name)

# Print comma separated list of profiles
print(" ".join(profiles))
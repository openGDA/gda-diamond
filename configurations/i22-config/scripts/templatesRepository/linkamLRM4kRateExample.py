
from linkamrampmaster4000 import LinkamRampMaster4000
lrm4k = LinkamRampMaster4000("lrm4k", linkam)

#the next line sets the time interval for data collection in seconds.
#NB ncddetector time has to be less than this
lrm4k.setCollectionInterval(6)

#Before running this script you need to set the start temperature with e.g. linkam(20)

#the next line establishes the ramps you want to run
lrm4k.setRateRamps([[30,20],[20, 40],[10,30],[30,30],[20,20]])

# The Example above has the following ramps
# 30 C/min to 20C
# 20 C/min to 40C
# 10 C/min to 30C
# 30s at 30C
# 20 C/min to 20C

#below are examples of the way the lrm3k can be used
#scan lrm4k lrm4k ncddetectors ringcurrent sbsdiode ...
scan lrm4k lrm4k 

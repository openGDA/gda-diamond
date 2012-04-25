#!/dls_sw/prod/tools/RHEL5/bin/dls-python2.6
#
#this is a stand-alone python/epics script-- run without GDA
#
# written by Robert Atwood 
# $Id:$
### required libraries and modules
import sys
import os
import commands
import time
import math
from pkg_resources import require
require("numpy")
require("cothread")
import cothread
from cothread.catools import *
####end of module section 

exposure=0.01

for i in range (0,1000):
      caput("BL12I-EA-DIO-01:OUT:02",1,wait=True)
      caput("BL12I-EA-DIO-01:OUT:02",0,wait=True)
      cothread.Sleep(exposure)

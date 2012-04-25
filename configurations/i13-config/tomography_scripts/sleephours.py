#!/dls_sw/prod/tools/RHEL5/bin/dls-python2.6
#
#this is a stand-alone python/epics script-- run without GDA
#
# written by Robert Atwood 
# $Id: tomo_scan_tmp.py 225 2012-02-29 13:31:49Z kny48981 $
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

print "sleeping for 14000 seconds"
cothread.Sleep(14000)
#close the shutter
print "Closing the shutter"
caput("BL12I-PS-SHTR-02:CON",1,wait=True)

#print("calling doflat for dark field")
#camera.setup(flat_exp)
#doflat(fpath,10,flat_exp,"df%s"%scanname)

#oen the shutter
#print "Opening the shutter"
#caput("BL12I-PS-SHTR-02:CON",0,wait=True)




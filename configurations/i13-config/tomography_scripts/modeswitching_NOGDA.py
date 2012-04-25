#!/dls_sw/tools/bin/python2.4
#
#this is a stand-alone python/epics script-- run without GDA
#
# written by Robert Atwood 
# $Id: modeswitching_NOGDA.py 233 2012-04-11 13:31:34Z kny48981 $
### required libraries and modules
import sys
import os
import commands
import time
import math
from pkg_resources import require
require("numpy")
require("cothread")
from cothread.catools import *
####end of module section 
if (len(sys.argv) < 2):
   print("Usage: %s <modulenumber>" % sys.argv[0])
   print("Switch the optical module of the imaging camera to the new module number [1,2,3, or 4]" )
   sys.exit(0)

#store the safe excange position
cameraSafeZ = -10.0

#the correct tomography sample tilt alignment
sampleTiltX = 0.054157
sampleTiltZ = 0.0

#table of positions for each module for each motor

cam1x=(52.0,137.05,215.0,290.815) 
#cam1roll=(-0.4213,-0.298,-0.04037,-0.4055)
cam1roll=(-0.777,-0.298,-0.088,-0.459)
#cam1z=(-91.3,-70.9,-43.7,-59.5)
cam1z=(-91.55,-70.9,-52.4,-59.5)
table3x=(1351.55,1348.75,1350.54,1350.29)
table3y=(37.25,38.61,39.01,39.01)


cam1xpv="BL12I-EA-CAM-01:ZOOM.VAL"
cam1xval="BL12I-EA-CAM-01:ZOOM.RBV"

cam1zpv="BL12I-EA-CAM-01:FOCUS.VAL"
cam1rollpv="BL12I-EA-CAM-01:TILT.VAL"
sampleTiltXpv="BL12I-MO-TAB-02:ST1:RX.VAL"
sampleTiltZpv="BL12I-MO-TAB-02:ST1:RZ.VAL"
table3xpv="BL12I-MO-TAB-03:X.VAL"
table3ypv="BL12I-MO-TAB-03:MOD1:Y.VAL"




def cameraMag(module):	
        

        global sampleTiltX
        global sampleTiltZ
        global cameraSafeZ
        global cam1x
        global cam1roll
        global cam1z
        global cam1xpv
        global cam1xval
        global cam1zpv
        global cam1rollpv
        global sampleTiltXpv
        global table3x
        global table3xpv
        global table3y
        global table3ypv

        print "camera optical module switching\n"

        #create a zero-based array index
        modnum=module-1;

        
        #ensure the sample stage is in the tomography alignment
        caput(sampleTiltXpv,sampleTiltX,wait=False)
        caput(sampleTiltZpv,sampleTiltZ,wait=False)

        #check whether the camera is ALREADY in the required module
        thisx = caget(cam1xval)
        offset= (math.fabs(thisx - cam1x[modnum]) )
        print (thisx,cam1x[modnum])
        print ("offset is", offset)
        if (offset < 0.1):
           print ("already in module ",module)

        if (offset >= 0.1):
           #put camera in the safe position
           caput(cam1zpv,cameraSafeZ,wait=True,timeout=350)
           #put lens translation in the position  for this module
           caput(cam1xpv,cam1x[modnum],wait=True,timeout=350)
           #put camera in the focussed position
           caput(cam1zpv,cam1z[modnum],wait=True,timeout=350)

        #set the camera roll for this module
        #even if we're already in this module
        print("adjusting the tilt")
        caput(cam1rollpv,cam1roll[modnum],wait=True,timeout=10)
        print("adjusting the camera position")
        caput(table3xpv,table3x[modnum],wait=True,timeout=10)
        caput(table3ypv,table3y[modnum],wait=True,timeout=10)

        print "camera optical module switching finished\n"


module=int(sys.argv[1])
print ("Switching to module",module)
cameraMag(module)
print ("Camera now in module",module)
### end

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

tomopos=0    # tomography position centre of rotation (corrected from 1002.358)
flatpos=-100        # ss1.x position for flatfields
exp=.05             # exposure time
anglestep=.25     #angle(360/1440) 
trigpv="BL12I-EA-DIO-01:OUT:02"
hightime=0.15


def doflat(nflat=5,exposure=1):
   global flatpos
   global tomopos
   global trigpv

   #print("moving to flat position")
   #caput ("BL12I-MO-TAB-02:X.VAL", flatpos, wait=True,timeout=300);

   print ("Setting CAM:NumImages")
   caput("BL12I-EA-DET-02:CAM:NumImages",1,wait=False)
   caput("BL12I-EA-DET-02:CAM:ImageMode",0,wait=True)
   caput("BL12I-EA-DET-02:CAM:TriggerMode",2,wait=True)

   print ("Setting TIF:NumCapture")
   caput("BL12I-EA-DET-02:TIF:NumCapture",nflat)
   print ("Setting capture on TIF:Capture=1")
   caput ("BL12I-EA-DET-02:TIF:Capture",1,wait=False)
   print ("TIF:Capture: set to 1 ")
   cothread.Sleep(2)
   print("Arming the camera")
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",1,wait=True,timeout=300)

   for idx in range(0,nflat,1):
      print ("Acquiring CAM:Acquire")
      caput("BL12I-EA-DET-02:CAM:Acquire",1,wait=True, timeout=300)

   print ("TIF:Capture: 0 ")
   caput ("BL12I-EA-DET-02:TIF:Capture",0)
   caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True,timeout=60)

   #print("moving to tomography position")
   #caput ("BL12I-MO-TAB-02:X.VAL", tomopos, wait=True,timeout=300);

def doscan(nsteps=1800,exposure=0.3,readout=0.4):
   global trigpv
   global hightime
   print "Entering doscan routine"
   nplus=nsteps + 1
   print ("Setting CAM:NumImages")
   caput("BL12I-EA-DET-02:CAM:NumImages",1,wait=False)
   caput("BL12I-EA-DET-02:CAM:ImageMode",0,wait=True)
   caput("BL12I-EA-DET-02:CAM:TriggerMode",2,wait=True)

   print ("Setting TIF:NumCapture",nplus)
   caput("BL12I-EA-DET-02:TIF:NumCapture",nplus)
   print ("setting TIF:Capture: 1 ")
   caput ("BL12I-EA-DET-02:TIF:EnableCallbacks",1,wait=True,timeout=10)
   caput ("BL12I-EA-DET-02:TIF:FileNumber",0,wait=False)
   caput ("BL12I-EA-DET-02:TIF:Capture",1,wait=False)

   cothread.Sleep(2)

   caput("BL12I-EA-DET-02:CAM:ArrayCounter",0)

   print("Arming the camera")
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",1,wait=True,timeout=300)


   for ang in range(0,nplus,1):
      startang=0.0
      myang = startang + ang *  (180.0 / nsteps)
      #print ("moving theta = ", myang)
      #caput("BL12I-MO-TAB-02:ST1:THETA.VAL",myang,wait=True,timeout=300)
      #print ("Acquiring CAM:Acquire, theta = ", myang)
      #
      # # software trigger method -- takes 1/2 second longer
      #caput("BL12I-EA-DET-02:CAM:Acquire",1,wait=True,timeout=60)
      #

      #TRIGGER the camera with a hardware method
      print "step= ",ang
      oldframe = caget("BL12I-EA-DET-02:CAM:ArrayCounter_RBV")
      print "oldframe=",oldframe
      print "triggering..."
      caput(trigpv,1,wait=True)
      cothread.Sleep(hightime)
      caput(trigpv,0,wait=True)
      cothread.Sleep(exposure + readout + hightime)
      print "done.."

      newframe = caget("BL12I-EA-DET-02:CAM:ArrayCounter_RBV")
      print newframe
      while (oldframe == newframe):
         print "waiting for frame number update...",newframe
         newframe = caget("BL12I-EA-DET-02:CAM:ArrayCounter_RBV")
         cothread.Sleep(hightime)
      print "finished step",ang




   print ("TIF:Capture: 0 ")
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",0,wait=True,timeout=60)
   caput ("BL12I-EA-DET-02:TIF:Capture",0)
   caput ("BL12I-EA-DET-02:TIF:EnableCallbacks",0,wait=True,timeout=10)

#MAIN part

#caput("BL12I-EA-DET-02:CAM:ADC_MODE", 1,wait=True,timeout=60)
if (len(sys.argv) < 4):
   print " Usage: %s <scan-name> <num-projections> <exposure-time-s> " % sys.argv[0]
   print "CAUTION: bad scan name can crash the server"
   sys.exit(0)

scanname=sys.argv[1]
nproj=int(sys.argv[2])
exposure=float(sys.argv[3])

folderstr="/data/2011/ee7399-1/processing/rawdata/"

linfolder="/dls/i12/%s" % folderstr
winfolder="Z:/%s" % folderstr

linbasefolder = "%s/%s" % (linfolder,scanname)
linprojfolder = "%s/projections" % linbasefolder

winbasefolder = "%s/%s" % (winfolder,scanname)
winprojfolder = "%s/projections" % winbasefolder



if not (os.access (linbasefolder, os.F_OK)):
   os.mkdir(linbasefolder)
else:
   print("Directory %s already exists!" % linbasefolder)
   print("Please use a different folder or move the folder away")
   sys.exit(0)

if not (os.access (linbasefolder, os.F_OK)):
   print ("COULD NOT CREATE %s",linbasefolder)
   sys.exit(0)

if not (os.access (linprojfolder, os.F_OK)):
   os.mkdir(linprojfolder)

if not (os.access (linprojfolder, os.F_OK)):
   print ("COULD NOT CREATE %s",linprojfolder)
   sys.exit(0)


#stop the camera
caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True)

# save the state of callback tabs
procstate=caget("BL12I-EA-DET-02:PROC:EnableCallbacks")
statstate=caget("BL12I-EA-DET-02:STAT:EnableCallbacks")
roistate=caget("BL12I-EA-DET-02:ROI1:EnableCallbacks")
modestate=caget("BL12I-EA-DET-02:CAM:ImageMode")
expstate=caget("BL12I-EA-DET-02:CAM:AcquireTime_RBV")

#disable the callbacks
#caput("BL12I-EA-DET-02:PROC:EnableCallbacks",0,wait=True)
caput("BL12I-EA-DET-02:STAT:EnableCallbacks",0,wait=True)
caput("BL12I-EA-DET-02:ROI1:EnableCallbacks",0,wait=True)


caput("BL12I-EA-DET-02:TIF:FilePath",winprojfolder,datatype=DBR_CHAR_STR)
caput("BL12I-EA-DET-02:TIF:FileName","p_",datatype=DBR_CHAR_STR)
caput("BL12I-EA-DET-02:TIF:FileTemplate","%s%s%05d.tif",datatype=DBR_CHAR_STR)



print ("Setting CAM:NumImages")
caput("BL12I-EA-DET-02:TIF:EnableCallbacks",1,wait=True,timeout=60)
caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True,timeout=60)
caput("BL12I-EA-DET-02:CAM:NumImages",1,wait=False)
caput("BL12I-EA-DET-02:CAM:ImageMode",0,wait=True)
caput("BL12I-EA-DET-02:CAM:TriggerMode",2,wait=True)
caput("BL12I-EA-DET-02:TIF:FileNumber",0,wait=True)
caput("BL12I-EA-DET-02:CAM:AcquireTime",exposure,wait=True)
caput("BL12I-EA-DET-02:CAM:ArrayCounter",0,wait=True)

testexp = caget("BL12I-EA-DET-02:CAM:AcquireTime_RBV")

if not (testexp == exposure):
   print("Exposure time didn't get set properly! requested %f got %f " % (exposure,testexp) )
   sys.exit(0)




print("calling doflat")
doflat(nproj,exposure)
#restore the callbacks



print "restoring the image mode"
caput("BL12I-EA-DET-02:CAM:ImageMode",modestate,wait=True)
print "restoring the exposure"
caput("BL12I-EA-DET-02:CAM:AcquireTime",expstate,wait=True)
print "restoring the tab callbacks"
caput("BL12I-EA-DET-02:PROC:EnableCallbacks",procstate,wait=True)
caput("BL12I-EA-DET-02:STAT:EnableCallbacks",statstate,wait=True)
caput("BL12I-EA-DET-02:ROI1:EnableCallbacks",roistate,wait=True)


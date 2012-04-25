#!/dls_sw/prod/tools/RHEL5/bin/dls-python2.6
#
#this is a stand-alone python/epics script-- run without GDA
#
# written by Robert Atwood 
# $Id: pos_tif_areadetector.py 225 2012-02-29 13:31:49Z kny48981 $
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

def doposcompscan(start=0,stop=5.0,step=0.1,exptime=0.5,fastspeed=100,slowspeed=0.1,leadin=0.1):
   print("Entering doposcompscan")

   origspeed=caget("BL12I-MO-TAB-02:ST1:THETA.VELO.RBV")
   caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True,timeout=10)
   caput("BL12I-EA-DET-02:CAM:AcquireTime",exptime,wait=True,timeout=10)
   caput("BL12I-EA-DET-02:PRO1:EnableCallbacks",0,wait=True)
   caput("BL12I-EA-DET-02:STAT:EnableCallbacks",0,wait=True)
   caput("BL12I-EA-DET-02:TIF:FileNumber",0,wait=True)



   print("Setting up position compare",start,stop,step)

   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:START",start,wait=True)
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:STOP",stop,wait=True)
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:STEP",step,wait=True)

   print("setting control off")
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",0,wait=True,timeout=300)
   print("setting control auto")
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",2,wait=True,timeout=300)


   #calculate expected number of steps
   nsteps=(float(stop)-float(start))/float(step)
   insteps=int(nsteps)+1
   print "calculated number of steps:",insteps
   maxspeed=float(step)/(float(exptime) + 0.35)

   if(maxspeed < slowspeed):
      slowspeed=maxspeed
      print("Adjusting the continuous rotation speed to",slowspeed)
   else:
      print ("Using requested speed ",slowspeed)


   #spin back to the start
   before=start-leadin
   thetapos=before

   print ("moving theta quickly to = ", thetapos)
   caput("BL12I-MO-TAB-02:ST1:THETA.VELO",fastspeed,wait=True,timeout=300)
   caput("BL12I-MO-TAB-02:ST1:THETA.VAL",thetapos,wait=True,timeout=300)



   print "setting TIF  number of steps:",insteps
   print ("Setting TIF:NumCapture")
   caput("BL12I-EA-DET-02:TIF:NumCapture",insteps)
   print ("Activating: Setting TIF:Capture: 1 ")
   caput ("BL12I-EA-DET-02:TIF:Capture",1,wait=False)

   print ("Setting CAM:TriggerMode 2")
   caput("BL12I-EA-DET-02:CAM:TriggerMode", 2, wait=True,timeout=60)

   print ("Setting CAM:NumImages 1")
   caput("BL12I-EA-DET-02:CAM:NumImages",1,wait=False)

   print ("Setting CAM:ImageMode")
   caput("BL12I-EA-DET-02:CAM:ImageMode",1,wait=True,timeout=60)

   print ("Arming the camera")
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",1,wait=True,timeout=60)
   cothread.Sleep(2)


   thetapos=stop+leadin
   movetime=(float(stop)-float(start))/slowspeed 
   exptime=float(insteps) * (float(exptime)+0.35)
   alltime=movetime+exptime
   outtime=alltime * 2.0
   print "Estimated time", alltime, " seconds ... ", alltime/3600.0, "hours"
   print "Setting timeout",outtime

   print ("moving theta for continuous rotation = ", thetapos)
   caput("BL12I-MO-TAB-02:ST1:THETA.VELO",slowspeed,wait=True,timeout=300)
   sfiles=caget("BL12I-EA-DET-02:TIF:FileNumber")
   stime=time.time()
   caput("BL12I-MO-TAB-02:ST1:THETA.VAL",thetapos,wait=True,timeout=outtime)
   etime=time.time()
   efiles=caget("BL12I-EA-DET-02:TIF:FileNumber")

   totaltime=etime-stime
   totalfiles=efiles-sfiles

   msgstring="slowspeed %f: Elapsed time %f for %i images: %f seconds per image" %(slowspeed,totaltime,totalfiles,totaltime/totalfiles)
   print msgstring

   print "Images captured: %i" % totalfiles
   if not (totalfiles == insteps-1):
      print"Missed some Images! %i %i" % (totalfiles,insteps - 1)

   print ("Disarming the camera")
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",0,wait=True,timeout=60)

   print ("setting TIF:Capture: 0 ")
   caput ("BL12I-EA-DET-02:TIF:Capture",0)
   #caput("BL12I-MO-TAB-02:ST1:THETA.VELO",10,wait=True,timeout=300)
   print("Restoring theta speed",origspeed)
   caput("BL12I-MO-TAB-02:ST1:THETA.VELO",origspeed,wait=True,timeout=300)


def doscan(nsteps=1800,exposure=0.3):
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
   caput ("BL12I-EA-DET-02:TIF:Capture",1,wait=False)

   cothread.Sleep(2)

   print("Arming the camera")
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",1,wait=True,timeout=300)


   for ang in range(0,nplus + 1,1):
      #caput("BL12I-EA-DET-02:CAM:Acquire",1,wait=True,timeout=60)
      caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",1,wait=True)
      caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",0,wait=True)
      cothread.Sleep(exposure)


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

folderstr="/data/2012/cm5706-1/tmp/"

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
procstate=caget("BL12I-EA-DET-02:PRO1:EnableCallbacks")
statstate=caget("BL12I-EA-DET-02:STAT:EnableCallbacks")
roistate=caget("BL12I-EA-DET-02:ROI1:EnableCallbacks")
modestate=caget("BL12I-EA-DET-02:CAM:ImageMode")
expstate=caget("BL12I-EA-DET-02:CAM:AcquireTime_RBV")

#disable the callbacks
caput("BL12I-EA-DET-02:PRO1:EnableCallbacks",0,wait=True)
caput("BL12I-EA-DET-02:PRO2:EnableCallbacks",0,wait=True)
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
caput("BL12I-EA-DET-02:CAM:TriggerMode",1,wait=True)
caput("BL12I-EA-DET-02:TIF:FileNumber",0,wait=True)
caput("BL12I-EA-DET-02:CAM:AcquireTime",exposure,wait=True)

testexp = caget("BL12I-EA-DET-02:CAM:AcquireTime_RBV")

if not (testexp == exposure):
   print("Exposure time didn't get set properly! requested %f got %f " % (exposure,testexp) )
   sys.exit(0)


print("calling doscan")
#doscan(nproj,exposure)
print("setting control off")
caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",0,wait=True,timeout=300)
print("setting control auto")
caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",2,wait=True,timeout=300)
caput("BL12I-EA-DET-02:TIF:Capture",0,wait=True,timeout=10)
tspeed=0.08
stepsize=180.0/nproj

doposcompscan(0,180.0,step=stepsize,exptime=exposure,slowspeed=tspeed)

print "restoring the image mode"
caput("BL12I-EA-DET-02:CAM:ImageMode",modestate,wait=True)
print "restoring the exposure"
caput("BL12I-EA-DET-02:CAM:AcquireTime",expstate,wait=True)
print "restoring the tab callbacks"
caput("BL12I-EA-DET-02:PRO1:EnableCallbacks",procstate,wait=True)
caput("BL12I-EA-DET-02:STAT:EnableCallbacks",statstate,wait=True)
caput("BL12I-EA-DET-02:ROI1:EnableCallbacks",roistate,wait=True)


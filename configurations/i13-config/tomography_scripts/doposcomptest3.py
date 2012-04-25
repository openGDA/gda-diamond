#!/dls_sw/prod/tools/RHEL5/bin/dls-python2.6
#
#this is a stand-alone python/epics script-- run without GDA
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

tomopos=-2.2    # tomography position centre of rotation (corrected from 1002.358)
flatpos=-100        # ss1.x position for flatfields
exp=.05             # exposure time
anglestep=.25     #angle(360/1440) 

def doflat():
   global flatpos
   global tomopos
   nflat=20
   print("moving to flat position")
   caput ("BL12I-MO-TAB-02:X.VAL", flatpos, wait=True,timeout=300);
   print ("Setting TIF:NumCapture")
   caput("BL12I-EA-DET-02:TIF:NumCapture",nflat)

   print ("Setting CAM:TriggerMode")
   caput("BL12I-EA-DET-02:CAM:TriggerMode", 0, wait=True,timeout=60)

   print ("Setting CAM:ImageMode")
   caput("BL12I-EA-DET-02:CAM:ImageMode",0,wait=True,timeout=60)
   print ("Setting CAM:NumImages")
   caput("BL12I-EA-DET-02:CAM:NumImages",nflat,wait=True,timeout=60)
   print ("Setting capture on TIF:Capture=1")
   caput ("BL12I-EA-DET-02:TIF:Capture",1,wait=False)
   print ("TIF:Capture: 1 ")
   cothread.Sleep(2)

   for idx in range(0,nflat,1):
      print ("Acquiring CAM:Acquire")
      caput("BL12I-EA-DET-02:CAM:Acquire",1,wait=True, timeout=300)

   print ("TIF:Capture: 0 ")
   caput ("BL12I-EA-DET-02:TIF:Capture",0)

   print("moving to tomography position")
   caput ("BL12I-MO-TAB-02:X.VAL", tomopos, wait=True,timeout=300);

def doscan():
   print ("Setting TIF:NumCapture")
   caput("BL12I-EA-DET-02:TIF:NumCapture",1801)
   caput ("BL12I-EA-DET-02:TIF:Capture",1,wait=False)
   print ("TIF:Capture: 1 ")
   cothread.Sleep(2)

   for idx in range(0,1801,1):
      thetapos = 0.1 * idx
      print ("mvoing theta = ", thetapos)
      caput("BL12I-MO-TAB-02:ST1:THETA.VAL",thetapos,wait=True,timeout=300)
      print ("Acquiring CAM:Acquire, theta = ", thetapos)
      caput("BL12I-EA-DET-02:CAM:Acquire",1,wait=True,timeout=60)

   print ("TIF:Capture: 0 ")
   caput ("BL12I-EA-DET-02:TIF:Capture",0)



def doposcompscan(start=0,stop=5.0,step=0.1,exposure=0.5,fastspeed=100,slowspeed=0.1,leadin=0.1):
   global of
   print("Entering doposcompscan")

   origspeed=caget("BL12I-MO-TAB-02:ST1:THETA.VELO.RBV")
   caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True,timeout=10)
   caput("BL12I-EA-DET-02:CAM:AcquireTime",exposure,wait=True,timeout=10)
   caput("BL12I-EA-DET-02:PROC:EnableCallbacks",0,wait=True)
   caput("BL12I-EA-DET-02:STAT:EnableCallbacks",0,wait=True)
   caput("BL12I-EA-DET-02:TIF:FileNumber",0,wait=True)



   print("Setting up position compare")
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
   maxspeed=float(step)/(float(exposure) + 0.35)

   #if(maxspeed < slowspeed):
   #   slowspeed=maxspeed
   #   print("Adjusting the continuous rotation speed to",slowspeed)
   #else:
   #   print ("Using requested speed ",slowspeed)


   #spin back to the start
   before=start-leadin
   thetapos=before

   print ("moving theta quickly to = ", thetapos)
   caput("BL12I-MO-TAB-02:ST1:THETA.VELO",fastspeed,wait=True,timeout=300)
   caput("BL12I-MO-TAB-02:ST1:THETA.VAL",thetapos,wait=True,timeout=300)



   print "setting number of steps:",insteps
   print ("Setting TIF:NumCapture")
   caput("BL12I-EA-DET-02:TIF:NumCapture",insteps)
   print ("Setting TIF:Capture: 1 ")
   caput ("BL12I-EA-DET-02:TIF:Capture",1,wait=False)

   print ("Setting CAM:TriggerMode")
   caput("BL12I-EA-DET-02:CAM:TriggerMode", 2, wait=True,timeout=60)

   print ("Setting CAM:NumImages")
   caput("BL12I-EA-DET-02:CAM:NumImages",1,wait=False)

   print ("Setting CAM:ImageMode")
   caput("BL12I-EA-DET-02:CAM:ImageMode",1,wait=True,timeout=60)

   print ("Arming the camera")
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",1,wait=True,timeout=60)
   cothread.Sleep(2)


   thetapos=stop+leadin
   movetime=(float(stop)-float(start))/slowspeed 
   exptime=float(insteps) * (float(exposure)+0.35)
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
   of.write(msgstring)
   of.write("\n")

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

#MAIN part

scanname="test"

folderstr="/data/2011/cm2061-4/tmp/testpco/"

outfile="/dls/i12/data/2011/cm2061-4/processing/testpco.txt"
of=open(outfile,"a")

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
   #print("Please use a different folder or move the folder away")
   #sys.exit(0)

if not (os.access (linbasefolder, os.F_OK)):
   print ("COULD NOT CREATE %s",linbasefolder)
   sys.exit(0)

if not (os.access (linprojfolder, os.F_OK)):
   os.mkdir(linprojfolder)

if not (os.access (linprojfolder, os.F_OK)):
   print ("COULD NOT CREATE %s",linprojfolder)
   sys.exit(0)


caput("BL12I-EA-DET-02:TIF:FilePath",winprojfolder,datatype=DBR_CHAR_STR)
caput("BL12I-EA-DET-02:TIF:FileName","p_",datatype=DBR_CHAR_STR)
caput("BL12I-EA-DET-02:TIF:FileTemplate","%s%s%05d.tif",datatype=DBR_CHAR_STR)


print("setting control off")
caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",0,wait=True,timeout=300)
print("setting control auto")
caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",2,wait=True,timeout=300)
caput("BL12I-EA-DET-02:TIF:Capture",0,wait=True,timeout=10)


caput("BL12I-EA-DET-02:TIF:FileNumber",0,wait=True)

for speedstep in range(0,15):
   print("calling doposcompscan")
   tspeed=0.25 + 0.01 * speedstep
   doposcompscan(0,1,exposure=0.01,slowspeed=tspeed)
   #print("calling doposcompscan")
   #doposcompscan(0,1)

of.close()



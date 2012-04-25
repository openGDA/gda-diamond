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

tomopos=4   # tomography position centre of rotation (corrected from 1002.358)
flatpos=-100        # ss1.x position for flatfields
exp=.05             # exposure time
anglestep=.25     #angle(360/1440) 


def doflat(nflat=5):
   global flatpos
   global tomopos
   print("moving to flat position")
   caput ("BL12I-MO-TAB-02:X.VAL", flatpos, wait=True,timeout=300);

   print ("Setting CAM:NumImages")
   caput("BL12I-EA-DET-02:CAM:NumImages",1,wait=False)
   caput("BL12I-EA-DET-02:CAM:ImageMode",0,wait=True)
   caput("BL12I-EA-DET-02:CAM:TriggerMode",1,wait=True)

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

   print("moving to tomography position")
   caput ("BL12I-MO-TAB-02:X.VAL", tomopos, wait=True,timeout=300);


def doposcompscan(start=0,stop=5.0,step=0.1,exptime=0.5,fastspeed=100,slowspeed=0.1,leadin=0.1):
   print("Entering doposcompscan")

   origspeed=caget("BL12I-MO-TAB-02:ST1:THETA.VELO.RBV")
   caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True,timeout=10)
   caput("BL12I-EA-DET-02:CAM:AcquireTime",exptime,wait=True,timeout=10)
   caput("BL12I-EA-DET-02:PROC:EnableCallbacks",0,wait=True)
   caput("BL12I-EA-DET-02:STAT:EnableCallbacks",0,wait=True)
   caput("BL12I-EA-DET-02:TIF:FileNumber",0,wait=True)

   print ("setting TIF:Capture: 1 ")
   caput ("BL12I-EA-DET-02:TIF:EnableCallbacks",1,wait=True,timeout=10)



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

   if not(totalfiles == 0 ):
      msgstring="slowspeed %f: Elapsed time %f for %i images: %f seconds per image" %(slowspeed,totaltime,totalfiles,totaltime/totalfiles)
   else:
      msgstring="slowspeed %f: Elapsed time %f .. no images captured! " %(slowspeed,totaltime)

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

def do_pos_scan(nsteps=1800,exposure=0.3):
   print("setting control off")
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",0,wait=True,timeout=300)
   print("setting control auto")
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",2,wait=True,timeout=300)
   caput("BL12I-EA-DET-02:TIF:Capture",0,wait=True,timeout=10)
   tspeed=0.08
   stepsize=180.0/nsteps
   print "Calling position compare scan with stepsize %f degrees" % stepsize
   doposcompscan(0,180.0,step=stepsize,exptime=exposure,slowspeed=tspeed)

def makefolder(scanname):
   global winprojfolder
   folderstr="/data/2011/ee7076-1/processing/rawdata/"

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




def setupcam(exposure):
   #stop the camera
   caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True)

   # save the state of callback tabs
   procstate=caget("BL12I-EA-DET-02:PROC:EnableCallbacks")
   statstate=caget("BL12I-EA-DET-02:STAT:EnableCallbacks")
   roistate=caget("BL12I-EA-DET-02:ROI1:EnableCallbacks")
   modestate=caget("BL12I-EA-DET-02:CAM:ImageMode")
   expstate=caget("BL12I-EA-DET-02:CAM:AcquireTime_RBV")

   #disable the callbacks
   caput("BL12I-EA-DET-02:PROC:EnableCallbacks",0,wait=True)
   caput("BL12I-EA-DET-02:STAT:EnableCallbacks",0,wait=True)
   caput("BL12I-EA-DET-02:ROI1:EnableCallbacks",0,wait=True)





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

def setcamfolder(winprojfolder):
   caput("BL12I-EA-DET-02:TIF:FilePath",winprojfolder,datatype=DBR_CHAR_STR)
   caput("BL12I-EA-DET-02:TIF:FileName","p_",datatype=DBR_CHAR_STR)
   caput("BL12I-EA-DET-02:TIF:FileTemplate","%s%s%05d.tif",datatype=DBR_CHAR_STR)
   caput("BL12I-EA-DET-02:TIF:FileNumber",0,wait=True)

def restorecam():
   print "restoring the image mode"
   caput("BL12I-EA-DET-02:CAM:ImageMode",modestate,wait=True)
   print "restoring the exposure"
   caput("BL12I-EA-DET-02:CAM:AcquireTime",expstate,wait=True)
   print "restoring the tab callbacks"
   caput("BL12I-EA-DET-02:PROC:EnableCallbacks",procstate,wait=True)
   caput("BL12I-EA-DET-02:STAT:EnableCallbacks",statstate,wait=True)
   caput("BL12I-EA-DET-02:ROI1:EnableCallbacks",roistate,wait=True)


def do_one_scan(cur_scanname,nproj,exposure):
   global winprojfolder
   print "running do_one_scan"
   print "calling makefolder"
   makefolder(cur_scanname)
   print "Windows visible projection folder is %s" % winprojfolder

   print "calling setcamfolder %s" %  winprojfolder
   setcamfolder(winprojfolder)
   print("calling doscan")
   doscan(nproj,exposure)

def do_one_pos_scan(cur_scanname,nproj,exposure):
   global winprojfolder
   print "running do_one_pos_scan"
   print "calling makefolder"
   makefolder(cur_scanname)
   print "Windows visible projection folder is %s" % winprojfolder

   print "calling setcamfolder %s" %  winprojfolder
   setcamfolder(winprojfolder)
   print("calling doscan")
   do_pos_scan(nproj,exposure)

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
      startang=0.0
      myang = startang + ang *  (180.0 / nsteps)
      print ("moving theta = ", myang)
      #  caput("BL12I-MO-TAB-02:ST1:THETA.VAL",myang,wait=True,timeout=300)
      print ("Acquiring CAM:Acquire, theta = ", myang)
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

#I think the variable needs to have something in it at the start
winprojfolder=" "

scanname=sys.argv[1]
nproj=int(sys.argv[2])
exposure=float(sys.argv[3])

print "calling setupcam"
setupcam(exposure)


#set up a list of positions for each stage .. make sure arrays are all the same length

numscans=3
numiter=9
numflat=10
fastspeed=100

distpv="BL12I-MO-TAB-03:MOD1:Z.VAL"

caput(distpv,1295,wait=True,timeout=600)

caput("BL12I-MO-TAB-02:ST1:THETA.VELO",fastspeed,wait=True,timeout=300)

for scannum in range(0,numiter):
   this_iter=scannum
   this_scan="iter%s_%03i" % (scanname,scannum)
   this_flat="ff%s" % (this_scan)

   caput("BL12I-MO-TAB-02:X.VAL",tomopos,wait=True,timeout=300)
   print "calling do_one_scan for %s" % this_scan
   do_one_pos_scan(this_scan,nproj,exposure)

   caput("BL12I-MO-TAB-02:X.VAL",flatpos,wait=True,timeout=300)
   print "calling do_one_scan for %s" % this_flat
   do_one_scan(this_flat,numflat,exposure)

scannum=0
this_dist=395 
this_scan="%s_%04d" % (scanname,this_dist)
this_flat="ff%s" % (this_scan)

caput(distpv,this_dist,wait=True,timeout=600)
caput("BL12I-MO-TAB-02:X.VAL",tomopos,wait=True,timeout=300)
print "calling do_one_scan for %s" % this_scan
do_one_pos_scan(this_scan,nproj,exposure)

print "calling do_one_scan for %s" % this_flat
caput("BL12I-MO-TAB-02:X.VAL",flatpos,wait=True,timeout=300)
do_one_scan(this_flat,numflat,exposure)

for scannum in range(1,numscans):
   this_dist=2395.0 - 300 * scannum
   this_scan="%s_%04d" % (scanname,this_dist)
   this_flat="ff%s" % (this_scan)

   caput(distpv,this_dist,wait=True,timeout=600)

   caput("BL12I-MO-TAB-02:X.VAL",tomopos,wait=True,timeout=300)
   print "calling do_one_scan for %s" % this_scan
   do_one_pos_scan(this_scan,nproj,exposure)

   print "calling do_one_scan for %s" % this_flat
   caput("BL12I-MO-TAB-02:X.VAL",flatpos,wait=True,timeout=300)
   do_one_scan(this_flat,numflat,exposure)


#print "calling restorecam"
#restorecam()

print ("setting TIF:EnableCallbacks: 0 ")

caput ("BL12I-EA-DET-02:TIF:EnableCallbacks",0,wait=True,timeout=10)
caput("BL12I-MO-TAB-02:ST1:THETA.VELO",fastspeed,wait=True,timeout=300)

print "Closing the shutter"
caput("BL12I-PS-SHTR-02:CON",1,wait=True)

this_flat="dark" 
print "calling do_one_scan for %s" % this_flat
caput("BL12I-MO-TAB-02:X.VAL",flatpos,wait=True,timeout=300)
do_one_scan(this_flat,numflat,exposure)
print "All done!"

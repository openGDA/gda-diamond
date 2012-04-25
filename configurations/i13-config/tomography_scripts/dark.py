#!/dls_sw/prod/tools/RHEL5/bin/dls-python2.6
#
#this is a stand-alone python/epics script-- run without GDA
#
# written by Robert Atwood 
# $Id: tomo_step_scan.py 227 2012-02-29 14:10:40Z kny48981 $
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
svnstring="$Id: tomo_step_scan.py 227 2012-02-29 14:10:40Z kny48981 $"

tomopos=2.1    # tomography position centre of rotation (corrected from 1002.358)
exp=.045            # exposure time
anglestep=.25     #angle(360/1440) 
try:
   defReadout=float(os.environ["READOUT"])
except:
   defReadout=0.3

readout=defReadout #seconds allowed for readout time

#trigpv="BL12I-EA-DIO-01:OUT:00" # which digital i/o to use for triggering the camera
trigpv="BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL" # which digital i/o to use for triggering the camera
flatpv="BL12I-MO-TAB-02:X.VAL"
busypv="BL12I-EA-ADC-01:01"
exppv="BL12I-EA-ADC-01:03"
checkwritepv="BL12I-EA-DET-02:TIF:Capture_RBV"
flatpos= -100 # 

def checkwrite(messages,looptime=0):
   global checkwritepv
   tries=0
   camstat=caget(checkwritepv)
   t2=time.time()-looptime
   while (int(camstat) == 1) and (tries < 10):
      print "WARNING: tiff writer not finished!"
      print "Pushing the Snooze alarm..."
      counter=caget("BL12I-EA-DET-02:CAM:ArrayCounter_RBV")
      arrays=caget("BL12I-EA-DET-02:TIF:ArrayCounter_RBV")
      dropped=caget("BL12I-EA-DET-02:TIF:DroppedArrays_RBV")
      nextfile=caget("BL12I-EA-DET-02:TIF:FileNumber")
      ncapture=caget("BL12I-EA-DET-02:TIF:NumCaptured_RBV")
      print "tries %i time %f counter %i arrays %i dropped %i nextfile %i ncapture %i" %(tries,time.time(),counter,arrays,dropped,nextfile,ncapture)

      cothread.Sleep(0.5)
      camstat=caget(checkwritepv)

      t1=time.time()-looptime
      tel=t1-t2
      t2=t1
      messages.append("cstat: %f %f %i\n" % (t1,tel,camstat))
      tries = tries + 1


   if (tries >= 10 ):
      messages.append("Stopping file saving due to no response\n" )
      print "Stopping file saving due to no response\n" 

   print "camstat: ", camstat
   print "continuing..."

def doflat(dfolder,nflat=10,exposure=0.3,flatscanname="flat"):
   global folderstr
   global linfolder
   global winfolder
   global flatpos
   global tomopos
   global flatpv

#**********************
   dfolder.setbasefolders(flatscanname)
   dfolder.makepath()
   dfolder.printout()
   dfolder.setpathstrings()
#**********************

   tomopos=caget(flatpv)

   print("moving to flat position")
   caput (flatpv, flatpos, wait=True,timeout=300);

   caput("BL12I-MO-TAB-02:ST1:THETA.VAL",0,wait=True,timeout=300)

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

   print("moving to tomography position")
   caput (flatpv, tomopos, wait=True,timeout=300);

def doposcompscan(dfolder,nsteps=1800,exposure=0.3,scanname="scan",startangle=0,endangle=180.0,fastspeed=20,slowspeed=0.1,leadin=0.1):

   global folderstr
   global linfolder
   global winfolder
   global trigpv
   global busypv
   global exppv
   global readout
   print("Entering doposcompscan")

#**********************
   dfolder.setbasefolders(scanname)
   dfolder.makepath()
   dfolder.printout()
   dfolder.setpathstrings()
   logname="%s/scan.log" %(dfolder.linscan)

#**********************

   messages=[]
   nbusy=0
   start=startangle
   stop=endangle
   step=(float(endangle)-float(startangle))/(float(nsteps))
   origspeed=caget("BL12I-MO-TAB-02:ST1:THETA.VELO.RBV")
   print("Setting up position compare",start,stop,step)

   #set the end point to allow one more full pulse at the chosen end point
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:START",start,wait=True)
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:STOP",stop+(0.6 * step),wait=True)
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:STEP",step,wait=True)

   print("setting control off")
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",0,wait=True,timeout=300)
   print("setting control auto")
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:CTRL",2,wait=True,timeout=300)
   print("setting initial state off")
   caput("BL12I-MO-TAB-02:ST1:THETA:POSCOMP:INIT",0,wait=True)

   #calcuate inclusive endpoint number of steps
   insteps=int(nsteps)+1
   print "calculated number of steps including both end points: ",insteps

   #apply the number of images calculated to the file writer
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

   #check the requested speed/exposure ratio
   maxspeed=float(step)/(float(exposure + readout))
   if(maxspeed < slowspeed):
      print("Requested speed", slowspeed," is too fast for the requested exposure ",exposure," and readout ",readout)
      slowspeed=maxspeed
      print("Adjusting the continuous rotation speed to",slowspeed)
   else:
      print ("Using requested speed ",slowspeed," rather than maxspeed ", maxspeed)
      print("Requested speed ", slowspeed," calculated step ",step,"  requested exposure ",exposure,"  readout ",readout)


   #spin back to the start
   before=start-leadin
   thetapos=before

   print ("moving theta quickly to = ", thetapos)
   caput("BL12I-MO-TAB-02:ST1:THETA.VELO",fastspeed,wait=True,timeout=300)
   caput("BL12I-MO-TAB-02:ST1:THETA.VAL",thetapos,wait=True,timeout=300)




   print("waiting 3 seconds for camera to be ready")

   #busyv=caget(busypv)
   #tries=0

   checksleep=3.0

   #while ((busyv > 2.5) and (tries < 10)):
   #   busyv=caget(busypv)
   #   print("checking ... ")
   #   tries = tries + 1

   cothread.Sleep(checksleep)

   #if (tries > 10):
   #   print("ERROR something is wrong with the camera, it's still busy after %f seconds" % (tries * checksleep))
   #   sys.exit(0)


   #calculate the estimated time

   #choose stop position to be sure to have one complete pulse at the end
   thetapos=stop+0.9*step

   movetime=(float(stop)-float(start))/slowspeed 
   esttime=float(insteps) * (float(exposure)+0.35)
   alltime=movetime+esttime
   outtime=alltime * 2.0

   print "Estimated time", alltime, " seconds ... ", alltime/3600.0, "hours"
   print "Setting timeout",outtime


   #check the status and time before the move
   filesbefore=caget("BL12I-EA-DET-02:TIF:FileNumber")

   #set the velocity
   caput("BL12I-MO-TAB-02:ST1:THETA.VELO",slowspeed,wait=True,timeout=300)

   #actually move the stage! !
   print ("moving theta for continuous rotation = ", thetapos)
   stime=time.time()
   caput("BL12I-MO-TAB-02:ST1:THETA.VAL",thetapos,wait=True,timeout=outtime)
   etime=time.time()
   print ("theta continuous rotation finished. ", thetapos)
   #check the status and time after the move

   checkwrite(messages)

   filesafter=caget("BL12I-EA-DET-02:TIF:FileNumber")

   totaltime=etime-stime
   totalfiles=filesafter-filesbefore

   msgstring="slowspeed %f: Elapsed time %f for %i images: %f seconds per image" %(slowspeed,totaltime,totalfiles,totaltime/totalfiles)
   print msgstring


   print "Images captured: %i" % totalfiles
   if not (totalfiles == insteps):
      print"Wrong number of images! totalfiles = %i insteps = %i" % (totalfiles,insteps)
      print"filesbefore = %i filesafter = %i" % (filesbefore,filesafter)

   print ("Disarming the camera")
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",0,wait=True,timeout=60)

   print ("setting TIF:Capture: 0 ")
   caput ("BL12I-EA-DET-02:TIF:Capture",0)
   #caput("BL12I-MO-TAB-02:ST1:THETA.VELO",10,wait=True,timeout=300)
   print("Restoring theta speed",origspeed)
   caput("BL12I-MO-TAB-02:ST1:THETA.VELO",origspeed,wait=True,timeout=300)



def doscan(dfolder,nsteps=1800,exposure=0.3,scanname="scan",startangle=0.0,endangle=180.0):
   global folderstr
   global linfolder
   global winfolder
   global trigpv
   global busypv
   global exppv
   global readout
   global checkwritepv
   messages=[]
   nbusy=0

   print "Entering doscan routine"

#**********************
   dfolder.setbasefolders(scanname)
   dfolder.makepath()
   dfolder.printout()
   dfolder.setpathstrings()

   logname="%s/scan.log" %(dfolder.linscan)

#**********************

   #ensure trigger is at zero to start with

   caput(trigpv,0,wait=True)
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
   caput ("BL12I-MO-TAB-02:ST1:THETA.VELO",100,wait=True)
   caput ("BL12I-MO-TAB-02:ST1:THETA.ACCL",0.1,wait=True)

   cothread.Sleep(2)

   print("Arming the camera")
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",1,wait=True,timeout=300)

   #TRIGGER the camera with a hardware method
   #
   #thisangle=caget("BL12I-MO-TAB-02:ST1:THETA.RBV")
   #print "Acqiring first image, theta = ",thisangle
#
#   caput(trigpv,1,wait=True)
#   cothread.Sleep(exposure/2)
#   caput(trigpv,0,wait=True)
#   cothread.Sleep(exposure/2+0.55)

   print "Allowing time for camera to arm"

   camstat=caget("BL12I-EA-DET-02:CAM:ARM_MODE_RBV")

   while (camstat != 1 ):
      cothread.Sleep(0.2)
      camstat=caget("BL12I-EA-DET-02:CAM:ARM_MODE_RBV")
      cstattime=time.time()
      messages.append("camstattime: %f\n" %cstattime)
   print "continuing..."

   print ("waiting 1 second... ")
   cothread.Sleep(1.0)

   looptime=time.time()
   trigtime=looptime
   steptime=looptime
   osteptime=looptime

   t1=looptime
   t0=0
   t2=0

   messages.append("looptime: %f\n" %looptime)

   startang=startangle
   anglerange=(endangle-startang)

   print "Acquiring .... "
   for ang in range(0,nplus ,1):

      myang = startang + ang *  (anglerange / float(nsteps))

      movetime=trigtime+exposure;
      exptime=trigtime+exposure+readout;
      nowtime=time.time()
      messages.append("TimesThisLoop: %f %f %f %f %i\n" % (nowtime-looptime,trigtime-looptime,movetime-looptime,exptime-looptime,ang))

      nowtime=time.time()
      if (nowtime < movetime) :
         messages.append("movewait %f %f\n" % (nowtime-looptime,movetime-looptime))
         cothread.SleepUntil(movetime)


      t1=time.time()-looptime
      tdif=t1-t0
      tel=t1-t2
      t0=t1
      t2=t1
      busyv=caget(busypv)
      messages.append("Movetime: %f %f %f %f %f %i\n" % (t1,tel,tdif,busyv,trigtime-looptime,ang))

      #print ("moving theta = ", myang)
      #
      caput(trigpv,0,wait=True)
      #

      motortime=time.time()
      t1=motortime-looptime
      tel=t1-t2
      t2=t1
      messages.append("aftertrigdown: %f %f\n" % (t1,tel))

      caput("BL12I-MO-TAB-02:ST1:THETA.VAL",myang,wait=True,timeout=300)
      thisangle=caget("BL12I-MO-TAB-02:ST1:THETA.RBV")

      nowtime=time.time()
      motormove=nowtime-motortime
      t1=nowtime-looptime
      tel=t1-t2
      t2=t1

      messages.append("afterstep: %f %f %f %f\n" % (t1,tel,thisangle,motormove))

      #print ("Acquiring CAM:Acquire, theta = ", thisangle)
      #
      # # software trigger method -- takes 1/2 second longer
      #caput("BL12I-EA-DET-02:CAM:Acquire",1,wait=True,timeout=60)
      #

      #TRIGGER the camera with a hardware method
      nowtime=time.time()
      messages.append("checkexpwait %f %f\n" %(nowtime-looptime,exptime-looptime))
      if (nowtime < exptime) :
         messages.append("expwait %f %f\n" %(nowtime-looptime,exptime-looptime))
         cothread.SleepUntil(exptime)

      t1=time.time()-looptime
      tel=t1-t2
      t2=t1
      busyv=caget(busypv)

      osteptime=steptime
      steptime=time.time()
      stepdif=steptime-osteptime
      ohead=stepdif-motormove-exposure-readout

      messages.append("ohead: %f %f %f %f %f\n" % (stepdif,motormove,exposure,readout,ohead))
      messages.append("triggering: %f %f %f %f %f\n" % (t1,tel,busyv,stepdif,ohead))
      filenum=caget("BL12I-EA-DET-02:TIF:FileNumber")
      messages.append("angle: %i %f %i\n" % (ang,thisangle,filenum))

      #if (busyv > 3.0 ):
      #   nbusy = nbusy + 1
      #   ntries=0
      #   while ( (ntries < 10) and (busyv > 3.0)):
      #     cothread.Sleep (0.2)
      #     busyv=caget(busypv)
      #     ntries = ntries + 1
      #     nowtime=time.time()
      #     messages.append("busywait %f %f %f\n" %(nowtime-looptime,exptime-looptime,busyv))


      trigtime=time.time()
      caput(trigpv,1,wait=True)

#      t1=time.time()-looptime
#      tel=t1-t2
#      t2=t1
#      messages.append("aftertrigup: %f %f\n" % (t1,tel))
#
#      #
#      #cothread.Sleep(exposure/2)
#      #
#
#      t1=time.time()-looptime
#      tel=t1-t2
#      t2=t1
#      messages.append("aftersleep1: %f %f\n" % (t1,tel))
#
#
#      #
#      #cothread.Sleep(exposure/2+0.05)
#      #
#
#      t1=time.time()-looptime
#      tel=t1-t2
#      t2=t1
#      messages.append("aftersleep2: %f %f\n" % (t1,tel))

   camstat=caget(checkwritepv)

   t1=time.time()-looptime
   tel=t1-t2
   t2=t1
   messages.append("cstat: %f %f\n" % (t1,tel))

   cothread.Sleep(exposure)

   camstat=caget(checkwritepv)

   t1=time.time()-looptime
   tel=t1-t2
   t2=t1
   messages.append("cstat: %f %f\n" % (t1,tel))

   checkwrite(messages)



   t1=time.time()-looptime
   tel=t1-t2
   t2=t1
   messages.append("afterloop: %f %f\n" % (t1,tel))

   caput(trigpv,0,wait=True)
   t1=time.time()-looptime
   tel=t1-t2
   t2=t1
   messages.append("aftertrigdown3: %f %f\n" % (t1,tel))

   print ("waiting 1 second... ")
   cothread.Sleep(1.0)
   t1=time.time()-looptime
   messages.append("aftersleep3: %f %f\n" % (t1,tel))


   print ("setting TIF:Capture: 0 ")
   caput ("BL12I-MO-TAB-02:ST1:THETA.ACCL",1,wait=False)
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",0,wait=True,timeout=60)
   caput ("BL12I-EA-DET-02:TIF:Capture",0)
   caput ("BL12I-EA-DET-02:TIF:EnableCallbacks",0,wait=True,timeout=10)
   t1=time.time()-looptime
   messages.append("aftersleep3: %f %f\n" % (t1,tel))
   messages.append("nbusy: %i\n" % (nbusy))

   logfile=open(logname,"w")
   print ("Writing Log File")
   for i in range(len(messages)):
      logfile.write(messages[i])
   logfile.close()


class folders:


   def setpathstrings(self):
      caput("BL12I-EA-DET-02:TIF:FilePath",self.winproj,datatype=DBR_CHAR_STR)
      caput("BL12I-EA-DET-02:TIF:FileName","p_",datatype=DBR_CHAR_STR)
      caput("BL12I-EA-DET-02:TIF:FileTemplate","%s%s%05d.tif",datatype=DBR_CHAR_STR)

   def makepath(self):
      if not (os.access (self.lin, os.F_OK)):
         os.mkdir(self.lin)
      if not (os.access (self.linscan, os.F_OK)):
         os.mkdir(self.linscan)
      else:
         print("Directory %s already exists!" % self.linscan)
         print("Please use a different folder or move the folder away")
         sys.exit(0)
      if not (os.access (self.linscan, os.F_OK)):
         print ("COULD NOT CREATE %s",self.linscan)
         sys.exit(0)
      if not (os.access (self.linproj, os.F_OK)):
         os.mkdir(self.linproj)
      if not (os.access (self.linproj, os.F_OK)):
         print ("COULD NOT CREATE %s",self.linproj)
         sys.exit(0)

   def printout(self):
      print "base",self.base
      print "lin",self.lin
      print "win",self.win
      print "linscan",self.linscan
      print "winscan",self.winscan
      print "winproj",self.winproj

   def setbasefolders(self,sname):
      self.base="/data/2012/ee7447-3/processing/rawdata/"
      #self.base="/data/2012/ee7412-1/tmp/"
      self.lin="/dls/i12/%s" % self.base
      self.win="Z:/%s" % self.base
      self.linscan = "%s/%s" % (self.lin,sname)
      self.linproj = "%s/projections" % self.linscan
      self.winscan = "%s/%s" % (self.win,sname)
      self.winproj = "%s/projections" % self.winscan

class thiscam:

   #restore the camera state as it was before
   def restore(self):
      print "restoring the image mode"
      caput("BL12I-EA-DET-02:CAM:ImageMode",self.modestate,wait=True)
      print "restoring the tab callbacks"
      caput("BL12I-EA-DET-02:PRO1:EnableCallbacks",self.procstate,wait=True)
      caput("BL12I-EA-DET-02:STAT:EnableCallbacks",self.statstate,wait=True)
      caput("BL12I-EA-DET-02:ROI1:EnableCallbacks",self.roistate,wait=True)

   #setup the camera for a scan and cache the prior state
   def setup(self,exposure):
      #stop the camera
      caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True,timeout=60)
      #be sure ADC mode is correct 
      caput("BL12I-EA-DET-02:CAM:ADC_MODE", 1,wait=True,timeout=60)
      # save the state of callback tabs
      self.procstate=caget("BL12I-EA-DET-02:PRO1:EnableCallbacks")
      self.statstate=caget("BL12I-EA-DET-02:STAT:EnableCallbacks")
      self.roistate=caget("BL12I-EA-DET-02:ROI1:EnableCallbacks")
      self.modestate=caget("BL12I-EA-DET-02:CAM:ImageMode")

      #disable the callbacks
      caput("BL12I-EA-DET-02:PRO1:EnableCallbacks",0,wait=True)
      caput("BL12I-EA-DET-02:STAT:EnableCallbacks",0,wait=True)
      caput("BL12I-EA-DET-02:ROI1:EnableCallbacks",0,wait=True)


      #setup the camera modes
      caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True,timeout=60)
      caput("BL12I-EA-DET-02:CAM:NumImages",1,wait=False)
      caput("BL12I-EA-DET-02:CAM:ImageMode",0,wait=True)
      caput("BL12I-EA-DET-02:CAM:TriggerMode",2,wait=True)

      #setup and test the expousre
      caput("BL12I-EA-DET-02:CAM:AcquireTime",exposure,wait=True)
      testexp = caget("BL12I-EA-DET-02:CAM:AcquireTime_RBV")
      if not (testexp == exposure):
         print("Exposure time didn't get set properly! requested %f got %f " % (exposure,testexp) )
         sys.exit(0)

      #setup the tif
      caput("BL12I-EA-DET-02:TIF:EnableCallbacks",0,wait=True,timeout=60)
      caput("BL12I-EA-DET-02:TIF:FileWriteMode",2,wait=True,timeout=60)
      #acquire a dummy frame
      caput("BL12I-EA-DET-02:CAM:Acquire",1,wait=True,timeout=60)
      caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True,timeout=60)


      caput("BL12I-EA-DET-02:TIF:EnableCallbacks",1,wait=True,timeout=60)
      caput("BL12I-EA-DET-02:TIF:FileNumber",0,wait=True)
      #setup the counters
      caput("BL12I-EA-DET-02:CAM:ArrayCounter",0,wait=True)
      caput("BL12I-EA-DET-02:TIF:ArrayCounter",0,wait=True)
      caput("BL12I-EA-DET-02:TIF:DroppedArrays",0,wait=True)
      caput("BL12I-EA-DET-02:TIF:FileNumber",0,wait=True)


#MAIN part

if (len(sys.argv) < 4):
   print " Usage: %s <scan-name> <num-projections> <exposure-time-s> [<start-angle> <end-angle>]" % sys.argv[0]
   print " Default start-angle = 0 , end-angle = 180 degrees "
   print "CAUTION: bad scan name can crash the server"
   print "version %s" % svnstring
   sys.exit(0)


scanname=sys.argv[1]
nproj=int(sys.argv[2])
exposure=float(sys.argv[3])
startangle=0
endangle=180.0

if len(sys.argv) > 4 :
   startangle=float(sys.argv[4])

if len(sys.argv) > 5 :
   endangle=float(sys.argv[5])

print " will scan from 0 to %f degrees  in %i steps " % (endangle,nproj)

fpath=folders()
camera=thiscam()

fpath.setbasefolders(scanname)
fpath.printout()
#fpath.makepath()
#fpath.printout()
#fpath.setpathstrings()
#fpath.printout()

#set the soft accelleration
caput ("BL12I-MO-TAB-02:ST1:THETA.ACCL",1,wait=False)
caput ("BL12I-MO-TAB-02:ST1:THETA.VELO",20,wait=False)

#setup the camera
flat_exp = exposure
print "exposure is ", exposure
print "flat_exp is ", flat_exp


nflats=25


#close the shutter
print "Closing the shutter"
caput("BL12I-PS-SHTR-02:CON",1,wait=True)

print("calling doflat for dark field")
camera.setup(flat_exp)
doflat(fpath,nflats,flat_exp,"df%s"%scanname)


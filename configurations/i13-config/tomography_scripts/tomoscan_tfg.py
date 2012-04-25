#!/dls_sw/prod/tools/RHEL5/bin/dls-python2.6
#
#this is a stand-alone python/epics script-- run without GDA
#
# written by Robert Atwood 
# $Id: tomoscan_tfg.py 214 2012-02-13 15:46:36Z kny48981 $
### required libraries and modules
import sys
import os
import subprocess
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
flatpos=1000.1       # ss1.tx position for flatfields

tfgscript="tfgscript.cmd"

def setup_tfg(dfolder,exposure,nsteps):
   global tfgscript
   nplus = nsteps + 1
   tfgscript="%s/tfgscript.cmd" % dfolder.linscan 
   sys.stdout=open(tfgscript,"w")
#   print("""\
#tfg config "etfg0" tfg2
#tfg setup-groups sequence "seq0"
#1 0 %f    0 1 0 8 0 0
#1 0 10e-9  0 0 0 40 0 0
#1 0 10e-3 0 2 0 10 0 0
#1 0 10e-9  0 0  0 42 0 0
#-1
#tfg setup-groups cycles %i 
#1 seq0
#-1
#tfg start
#tfg wait ignore-pause
#""") % (exposure,nplus)
#
   print("""\
tfg config "etfg0" tfg2
tfg setup-groups sequence "seq0"
1 0 %f    0 257 0 9 0 0
1 0 10e-9  0 0 0 41 0 0
1 50e-3 10e-3 0 2 0 10 0 0
1 0 10e-9  0 2048  0 42 0 0
-1
tfg setup-groups sequence "seq1"
1 0 10e-9  0 0  0 42 0 0
-1
tfg setup-groups cycles 1 
%i seq0
-1
tfg setup-cc-mode scaler64
tfg setup-cc-chan 0 vetoed-edge
tfg setup-cc-chan 3 time-veto
tfg setup-cc-chan 4 time-veto
tfg setup-cc-chan 5 time-veto
set-func "path" "tfg open-cc"
clear %%path
enable %%path
tfg start
tfg wait ignore-pause
read 0 0 0 6 1 9 from %%path to-local-file "out.txt"
""") % (exposure,nplus)
#end of the  script text
   sys.stdout.flush()
   sys.stdout=sys.__stdout__


def doflat(dfolder,nflat=10,exposure=0.3,flatscanname="flat"):
   global folderstr
   global linfolder
   global winfolder
   global flatpos
   global tomopos

#**********************
   dfolder.setbasefolders(flatscanname)
   dfolder.makepath()
   dfolder.printout()
   dfolder.setpathstrings()
#**********************

   flatpv="BL12I-MO-TAB-02:X.VAL"
   flatrb="BL12I-MO-TAB-02:X.RBV"
   tomopos=caget(flatrb)

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

def dodark(dfolder,nflat=10,exposure=0.3,darkscanname="dark"):

      #close the shutter
   print "Closing the shutter"
   caput("BL12I-PS-SHTR-02:CON",1,wait=True)

   doflat(dfolder,nflat,exposure,darkscanname)

      #open the shutter
   print "Opening the shutter"
   caput("BL12I-PS-SHTR-02:CON",0,wait=True)

def tfgscan(dfolder,nsteps=1800,exposure=0.3,scanname="scan"):
   global trigpv
   global hightime
   print "Entering tfgscan routine"
#**********************
   print "Path setup:"
   dfolder.setbasefolders(scanname)
   dfolder.makepath()
   dfolder.printout()
   dfolder.setpathstrings()


#**********************

   setup_tfg(dfolder,nsteps,exposure)

   nplus=nsteps + 1
   print ("Setting CAM:NumImages")
   caput("BL12I-EA-DET-02:CAM:NumImages",1,wait=False)
   caput("BL12I-EA-DET-02:CAM:ImageMode",0,wait=True)
   caput("BL12I-EA-DET-02:CAM:TriggerMode",3,wait=True)

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



   #call the TFG
   print "cat %s | nc i12-tfg2-10ge 1972" % tfgscript 
   cothread.Sleep(1)
   subprocess.call("cat %s | nc i12-tfg2-10ge 1972" % tfgscript ,shell=True)


   print ("TIF:Capture: 0 ")
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",0,wait=True,timeout=60)
   caput ("BL12I-EA-DET-02:TIF:Capture",0)
   caput ("BL12I-EA-DET-02:TIF:EnableCallbacks",0,wait=True,timeout=10)
   caput("BL12I-EA-DET-02:CAM:TriggerMode",2,wait=True)

def doscan(dfolder,nsteps=1800,exposure=0.3,scanname="scan"):
   global folderstr
   global linfolder
   global winfolder

   trigpv="BL12I-EA-DIO-01:OUT:02"
   print "Entering doscan routine"

#**********************
   dfolder.setbasefolders(scanname)
   dfolder.makepath()
   dfolder.printout()

   dfolder.setpathstrings()


#**********************
   nplus=nsteps + 1
   print ("Setting CAM:NumImages")
   caput("BL12I-EA-DET-02:CAM:NumImages",1,wait=False)
   caput("BL12I-EA-DET-02:CAM:ImageMode",0,wait=True)
   caput("BL12I-EA-DET-02:CAM:TriggerMode",2,wait=True)

   print ("Setting TIF:NumCapture",nplus+2)
   caput("BL12I-EA-DET-02:TIF:NumCapture",nplus+2)
   print ("setting TIF:Capture: 1 ")

   caput ("BL12I-EA-DET-02:TIF:EnableCallbacks",1,wait=True,timeout=10)
   caput ("BL12I-EA-DET-02:TIF:FileNumber",0,wait=False)
   caput ("BL12I-EA-DET-02:TIF:Capture",1,wait=False)
   caput ("BL12I-MO-TAB-02:ST1:THETA.ACCL",0.1,wait=False)

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

   print ("waiting 1 second... ")
   cothread.Sleep(1.0)

   for ang in range(0,nplus ,1):
      startang=0.0
      myang = startang + ang *  (180.0 / nsteps)
      print ("moving theta = ", myang)
      caput("BL12I-MO-TAB-02:ST1:THETA.VAL",myang,wait=True,timeout=300)
      thisangle=caget("BL12I-MO-TAB-02:ST1:THETA.RBV")
      print ("Acquiring CAM:Acquire, theta = ", thisangle)
      #
      # # software trigger method -- takes 1/2 second longer
      #caput("BL12I-EA-DET-02:CAM:Acquire",1,wait=True,timeout=60)
      #

      #TRIGGER the camera with a hardware method
      caput(trigpv,1,wait=True)
      cothread.Sleep(exposure/2)
      caput(trigpv,0,wait=True)
      cothread.Sleep(exposure/2+0.05)


   print ("waiting 1 second... ")
   cothread.Sleep(1.0)
   print ("setting TIF:Capture: 0 ")
   caput ("BL12I-MO-TAB-02:ST1:THETA.ACCL",1,wait=False)
   caput("BL12I-EA-DET-02:CAM:ARM_MODE",0,wait=True,timeout=60)
   caput ("BL12I-EA-DET-02:TIF:Capture",0)
   caput ("BL12I-EA-DET-02:TIF:EnableCallbacks",0,wait=True,timeout=10)


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
      self.base="/data/2012/cm5706-1/tmp/"
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
      print "restoring the exposure"
      caput("BL12I-EA-DET-02:CAM:AcquireTime",self.expstate,wait=True)
      print "restoring the tab callbacks"
      caput("BL12I-EA-DET-02:PRO1:EnableCallbacks",self.procstate,wait=True)
      caput("BL12I-EA-DET-02:STAT:EnableCallbacks",self.statstate,wait=True)
      caput("BL12I-EA-DET-02:ROI1:EnableCallbacks",self.roistate,wait=True)

   #setup the camera for a scan and cache the prior state
   def setup(self,exposure):
      #stop the camera
      caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True)
      #be sure ADC mode is correct 
      caput("BL12I-EA-DET-02:CAM:ADC_MODE", 1,wait=True,timeout=60)
      # save the state of callback tabs
      self.procstate=caget("BL12I-EA-DET-02:PRO1:EnableCallbacks")
      self.statstate=caget("BL12I-EA-DET-02:STAT:EnableCallbacks")
      self.roistate=caget("BL12I-EA-DET-02:ROI1:EnableCallbacks")
      self.modestate=caget("BL12I-EA-DET-02:CAM:ImageMode")
      self.expstate=caget("BL12I-EA-DET-02:CAM:AcquireTime_RBV")

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

      caput("BL12I-EA-DET-02:TIF:EnableCallbacks",0,wait=True,timeout=60)
      #acquire a dummy frame
      caput("BL12I-EA-DET-02:CAM:Acquire",1,wait=True,timeout=60)
      caput("BL12I-EA-DET-02:CAM:Acquire",0,wait=True,timeout=60)
      caput("BL12I-EA-DET-02:TIF:FileNumber",0,wait=True)

      #setup the tif
      caput("BL12I-EA-DET-02:TIF:EnableCallbacks",1,wait=True,timeout=60)
      caput("BL12I-EA-DET-02:TIF:FileNumber",0,wait=True)




#MAIN part

if (len(sys.argv) < 4):
   print " Usage: %s <scan-name> <num-projections> <exposure-time-s> ( num-flat )" % sys.argv[0]
   print " If  (num-flat) is not present or equal to zero, flat and dark fields will not be acquired "
   print "CAUTION: bad scan name can crash the server. Don't use filnames with spaces or symbols. Don't use very long names."
   sys.exit(0)
if (len(sys.argv) >= 5):
   nflats=int(sys.argv[4])
   print "Will acquire %i flat and dark images" % nflats
else:
   nflats=0
   print "Will not acquire flat and dark images" 

scanname=sys.argv[1]
nproj=int(sys.argv[2])
exposure=float(sys.argv[3])

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


if (nflats != 0):

   camera.setup(exposure)
   print("calling dodark")
   dodark(fpath,10,exposure,"df%s"%scanname)

   camera.setup(flat_exp)
   print("calling doflat")
   doflat(fpath,10,flat_exp,"ff1%s"%scanname)

print("calling doscan")
camera.setup(exposure)

tfgscan(fpath,nproj,exposure,scanname)

if (nflats != 0):
   print("calling doflat")
   camera.setup(flat_exp)
   doflat(fpath,10,flat_exp,"ff2%s"%scanname)

#restore the callbacks
camera.restore()

#set the soft accelleration
caput ("BL12I-MO-TAB-02:ST1:THETA.ACCL",1,wait=False)






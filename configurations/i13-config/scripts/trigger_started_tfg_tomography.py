#Jython script for TFG2 controlled PCO acquisition
# for Peter Lee's Rig (taking a input pilse to start motion, and give out an output pulse when move completed)
# based on /dls_sw/i12/software/tomography-scripts/tomo-tfg.py written by Robert Atwood 
# $Id:$
### required libraries and modules
import sys
import os
import time
from gda.epics import ChannalAccessCommands
from string import Template
import string
from gda.factory import Finder
#from gda.jython.commands.ScannableCommands import pos

####end of module section 

tomopos=0       # tomography position centre of rotation (corrected from 1002.358)
flatpos=-100    # ss1.x position for flatfields
exp=.05         # exposure time
anglestep=.25   #angle(360/1440) 
trigpv="BL12I-EA-DIO-01:OUT:02"
hightime=0.15

tfg=Finder.find("tfg")
daserver=Finder.find("daserver")
cac=ChannalAccessCommands()


def config_tfg(exposure,nsteps):
    commands=Template("""
tfg config "etfg0" tfg2
tfg setup-groups sequence "seq0" 
1 0 $exp   0 257 0 9 0 0
1 0 10e-9  0 0 0 41 0 0
1 $pause 10e-3 0 2 0 10 0 0
1 0 10e-9  0 2048  0 42 0 0
-1
tfg setup-trig ttl2 start falling
tfg setup-groups ext-start
$steps seq0
-1
""")
    pausetime=0.0
    if exposure < 0.125:
        pausetime=0.125-exposure
    else:
        pausetime=0.0
    command=commands.substitute(exp=str(exposure),steps=str(nsteps), pause=str(pausetime))
    print command
    daserver.sendCommand(command) #@UndefinedVariable
    print "tfg configured."
    
def arm_tfg():
    commands="""
tfg arm
"""
    print commands
    daserver.sendCommand(commands) #@UndefinedVariable
    print "tfg2 is armed ready for P2R to start "
 

def doflat(nflat=5):
    global flatpos
    global tomopos
    global trigpv
    global cac
    print("moving to flat position")
    #pos(ss1_x, flatpos) #@UndefinedVariable
    cac.caput ("BL12I-MO-TAB-02:X.VAL", flatpos, True,300);
    
    print ("Setting CAM:NumImages")
    cac.caput("BL12I-EA-DET-02:CAM:NumImages",1,False,5)
    cac.caput("BL12I-EA-DET-02:CAM:ImageMode",0,True,5)
    cac.caput("BL12I-EA-DET-02:CAM:TriggerMode",1,True,5)
    
    print ("Setting TIF:NumCapture")
    cac.caput("BL12I-EA-DET-02:TIF:NumCapture",nflat, False, 5)
    print ("Setting capture on TIF:Capture=1")
    cac.caput ("BL12I-EA-DET-02:TIF:Capture",1,False,5)
    print ("TIF:Capture: set to 1 ")
    time.sleep(2.0)
    print("Arming the camera")
    cac.caput("BL12I-EA-DET-02:CAM:ARM_MODE",1,True,300)
    
    for idx in range(0,nflat,1):
        print ("Acquiring CAM:Acquire",idx)
        cac.caput("BL12I-EA-DET-02:CAM:Acquire",1,True, 300)
    
    print ("TIF:Capture: 0 ")
    cac.caput ("BL12I-EA-DET-02:TIF:Capture",0, False, 5)
    cac.caput("BL12I-EA-DET-02:CAM:Acquire",0,True,60)
    
    print("moving to tomography position")
    cac.caput ("BL12I-MO-TAB-02:X.VAL", tomopos, True,300);

def doscan(nsteps=1800,exposure=0.3,readout=0.4):
    global trigpv
    global hightime
    global cac
    print "Entering doscan routine"
    nplus=nsteps + 1
    print ("Setting camera acquisition parameters")
    cac.caput("BL12I-EA-DET-02:CAM:NumImages",1,False,5)
    cac.caput("BL12I-EA-DET-02:CAM:ImageMode",0,True, 5)
    cac.caput("BL12I-EA-DET-02:CAM:TriggerMode",3,True,5)
    
    print "Setting TIF:NumCapture",nplus
    cac.caput("BL12I-EA-DET-02:TIF:NumCapture",nplus, False, 5)
    print ("setting TIF:Capture: 1 ")
    cac.caput ("BL12I-EA-DET-02:TIF:EnableCallbacks",1,True,10)
    cac.caput ("BL12I-EA-DET-02:TIF:FileNumber",0,False,5)
    cac.caput ("BL12I-EA-DET-02:TIF:Capture",1,False,5)

    time.sleep(2.0)
    
    cac.caput("BL12I-EA-DET-02:CAM:ArrayCounter",0, False, 5)
    
    print("Arming the camera")
    cac.caput("BL12I-EA-DET-02:CAM:ARM_MODE",1,True,300)
    
    time.sleep(3.0)

    armed = cac.caget("BL12I-EA-DET-02:CAM:ARM_MODE")
    if not (int(armed) == 1):
        raise IOError("PCO not armed yet!!!")

    #call the TFG
    print "Arm tfg2"
    arm_tfg() 
    tfg.setShowArmed(True)
    #time.sleep(exposure*nsteps)
    status=int(tfg.getStatus())
    while (status != 0):
        status=int(tfg.getStatus())
        tfg.getProgress()
        time.sleep(10*exposure)
    
    sleep(exposure)
    print ("TIF:Capture: 0 ")
    cac.caput("BL12I-EA-DET-02:CAM:ARM_MODE",0,True,60)
    cac.caput ("BL12I-EA-DET-02:TIF:Capture",0, False, 5)
    cac.caput ("BL12I-EA-DET-02:TIF:EnableCallbacks",0,True,10)
    cac.caput("BL12I-EA-DET-02:CAM:TriggerMode",2,True,5)

#MAIN part

#cac.caput("BL12I-EA-DET-02:CAM:ADC_MODE", 1,True,60)
#if (len(sys.argv) < 4):
#    print " Usage: %s <scan-name> <num-projections> <exposure-time-s> " % sys.argv[0]
#    print "CAUTION: bad scan name can crash the server"
#    exit("")

#scanname=sys.argv[1]
#nproj=int(sys.argv[2])
#exposure=float(sys.argv[3])
    
def tfgscan(nproj, exposure):
    global cac
    from gda.data import NumTracker
    from gda.jython import InterfaceProvider
    scanNumTracker = NumTracker("i12");
    #setup file name 
    directory=InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    scanNumber=scanNumTracker.incrementNumber()
    
    folderstr=directory
    scanname=str(scanNumber)
    
    print scanname
    
    linfolder=folderstr
    winfolder=string.replace(linfolder,"/dls/i12", "Z:")
    
    linbasefolder = "%s/%s" % (linfolder,scanname)
    linprojfolder = "%s/projections" % linbasefolder
    
    winbasefolder = "%s/%s" % (winfolder,scanname)
    winprojfolder = "%s/projections" % winbasefolder
    
    print "images collected on Linux at ", linprojfolder
    print "images collected on Windows at ", winprojfolder
    #raise RuntimeError("test stopped")
    if not (os.access (linbasefolder, os.F_OK)):
        os.mkdir(linbasefolder)
    else:
        print("Directory %s already exists!" % linbasefolder)
        print("Please use a different folder or move the folder away")
        raise ValueError("Please use a different folder or move the folder away")
    
    if not (os.access (linbasefolder, os.F_OK)):
        print ("COULD NOT CREATE %s",linbasefolder)
        raise IOError("COULD NOT CREATE LINUX BASE FOLDER")
    
    if not (os.access (linprojfolder, os.F_OK)):
        os.mkdir(linprojfolder)
    
    if not (os.access (linprojfolder, os.F_OK)):
        print ("COULD NOT CREATE %s",linprojfolder)
        raise IOError("COULD NOT CREATE PROJECTION FOLDER")
    
    
    #stop the camera
    cac.caput("BL12I-EA-DET-02:CAM:Acquire",0,True, 5)
    
    # save the state of callback tabs
    #procstate=cac.caget("BL12I-EA-DET-02:PRC1:EnableCallbacks")
    statstate=int(cac.caget("BL12I-EA-DET-02:STAT:EnableCallbacks"))
    roistate=int(cac.caget("BL12I-EA-DET-02:ROI1:EnableCallbacks"))
    modestate=int(cac.caget("BL12I-EA-DET-02:CAM:ImageMode"))
    expstate=float(cac.caget("BL12I-EA-DET-02:CAM:AcquireTime_RBV"))
    
    #disable the callbacks
    #cac.caput("BL12I-EA-DET-02:PROC:EnableCallbacks",0,True)
    cac.caput("BL12I-EA-DET-02:STAT:EnableCallbacks",0,True, 5)
    cac.caput("BL12I-EA-DET-02:ROI1:EnableCallbacks",0,True, 5)
    
    
    cac.caputStringAsWaveform("BL12I-EA-DET-02:TIF:FilePath",winprojfolder)
    cac.caputStringAsWaveform("BL12I-EA-DET-02:TIF:FileName","p_")
    cac.caputStringAsWaveform("BL12I-EA-DET-02:TIF:FileTemplate","%s%s%05d.tif")
    
    
    
    print ("Setting CAM:NumImages")
    cac.caput("BL12I-EA-DET-02:TIF:EnableCallbacks",1,True,60)
    cac.caput("BL12I-EA-DET-02:CAM:Acquire",0,True,60)
    cac.caput("BL12I-EA-DET-02:CAM:NumImages",1,False, 5)
    cac.caput("BL12I-EA-DET-02:CAM:ImageMode",0,True, 5)
    cac.caput("BL12I-EA-DET-02:CAM:TriggerMode",1,True, 5)
    cac.caput("BL12I-EA-DET-02:TIF:FileNumber",0,True, 5)
    cac.caput("BL12I-EA-DET-02:CAM:AcquireTime",exposure,True, 5)
    
    testexp = cac.caget("BL12I-EA-DET-02:CAM:AcquireTime_RBV")
    
    if not (float(testexp) == float(exposure)):
        print("Exposure time didn't get set properly! requested %f got %f " % (float(exposure),float(testexp) ))
        raise IOError("Exposure time didn't get set properly!")
    

    #setup the TFG with the number of steps and exposure time
    config_tfg(exposure,nproj)
    
    print("calling doscan")
    doscan(nproj,exposure)
    #restore the callbacks
    #raise RuntimeError("scan completed!")
    
    
    
    print "restoring the image mode"
    cac.caput("BL12I-EA-DET-02:CAM:ImageMode",modestate,True, 5)
    print "restoring the exposure"
    cac.caput("BL12I-EA-DET-02:CAM:AcquireTime",expstate,True,5)
    print "restoring the tab callbacks"
    #cac.caput("BL12I-EA-DET-02:PRC1:EnableCallbacks",procstate,True)
    cac.caput("BL12I-EA-DET-02:STAT:EnableCallbacks",statstate,True,5)
    cac.caput("BL12I-EA-DET-02:ROI1:EnableCallbacks",roistate,True,5)
    print "scan completed."


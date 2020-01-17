import time
from time import sleep
import os

from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gda.jython import InterfaceProvider

#from gda.data import NumTracker
#i12NumTracker = NumTracker('i12')
#from gda.jython.commands.Input import requestInput
import os

from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gda.jython import InterfaceProvider
from epics_scripts.pv_scannable_utils import createPVScannable, caput, caget, caputStringAsWaveform

class WebCam():
    def __init__(self, pv_prefix="BL13I-DI-WEB-02:CAM"):
        self.pv_prefix = pv_prefix
        self.ca = CAClient()
        self.filename_prefix = "web2_"
        self.file_template = "%s%s%05d.tif" 	#"%s%s_%05d.tif" 
        self.outdirpath = None
        self.scan_number = None
        self.visit_path = "/dls/i13/data/2019/mg26318-1"
        
    def set_data_collection_params(self, exposure_time_sec, acq_period_sec):

        #disarm?
        #self.sanity_check(exposure_time_sec, acq_period_sec)
        caput("BL13I-DI-WEB-02:CAM:AcquirePeriod", acq_period_sec) #, timeout=10)
        caput("BL13I-DI-WEB-02:CAM:AcquireTime", exposure_time_sec) #, timeout=10)
        #sleep(1.0)
        exposure_time_sec_eff = caget("BL13I-DI-WEB-02:CAM:AcquireTime_RBV")
        acq_period_sec_eff = caget("BL13I-DI-WEB-02:CAM:AcquirePeriod_RBV")
        print "Effective exposure time: %s s" %(exposure_time_sec_eff)
        print "Effective acquisition period: %s s" %(acq_period_sec_eff)

        caput("BL13I-DI-WEB-02:CAM:ImageMode", 2)		#Continuous (2) Multiple (1) Single (0)
        caput("BL13I-DI-WEB-02:CAM:TriggerMode", 0)	#External (1) Internal (0)

        image_mode_eff = caget("BL13I-DI-WEB-02:CAM:AcquireTime_RBV")
        trigger_mode_eff = caget("BL13I-DI-WEB-02:CAM:AcquirePeriod_RBV")
        print "Effective image mode: %s s" %(image_mode_eff)
        print "Effective trigger mode: %s s" %(trigger_mode_eff)

        return exposure_time_sec_eff, acq_period_sec_eff        #order?
        
    def prepare_before_collection(self, exposure_time_sec, acq_period_sec): #, savefolderpath):
        self.set_data_collection_params(exposure_time_sec, acq_period_sec)
        #self._set_miro_hdf_path(savefolderpath)
        
    def collect_data(self, exposure_time_sec, acq_period_sec, nimages, desc=""):
        #stop acquire
        caput("BL13I-DI-WEB-02:CAM:Acquire", 0)
        #disarm
        #caput("BL13I-DI-WEB-02:CAM:ARM_MODE", 0)
        
        caput("BL13I-DI-WEB-02:CAM:ArrayCounter", 0)
        
        #self.sanity_check(exposure_time_sec, acq_period_sec)
        self.prepare_before_collection(exposure_time_sec, acq_period_sec)
        
        caput("BL13I-DI-WEB-02:CAM:NumImages", nimages)
        #self.scan_number = i12NumTracker.getCurrentFileNumber() + 1
        #i12NumTracker.incrementNumber()
        #print "scan_number = %d" %(self.scan_number)
        #t:\\i12\\data\\\\2018\\cm19662-1\\rawdata\\75136\\projections\\
        #self.outdirpath = "t:\\i12\\data\\\\2018\\cm19662-1\\rawdata\\%d\\projections\\" %(self.scan_number)
        #self.outdirpath = os.path.join(wd(), str(self.scan_number), "projections")
        tm_str = time.strftime("%d_%m_%Y-%H%M%S")
        subdir = "web2_"+desc+"_"
        subdir_tm = subdir + tm_str
        self.outdirpath = os.path.join("/dls/i13/data/2019/mg26318-1", "processing", subdir_tm)
        print "outdirpath = %s" %(self.outdirpath)
        
        self._set_tif_writer(self.outdirpath, nimages)    # remove args?
        
        self._start_acquire()
        acq_per_rbv = float(caget("BL13I-DI-WEB-02:CAM:AcquirePeriod_RBV"))
        #sleep(nimages*acq_per_rbv*(2.5))
        
        sleep(1)
        #while (int(caget("BL13I-DI-WEB-02:TIFF:Capture"))==1):	# Capture (1) Done (0)
        #while (caget("BL13I-DI-WEB-02:TIFF:Capture")=="Capture"):    # Capture (1) Done (0)
        #    sleep(max(1,acq_per_rbv))
        #self._stop_acquire()				# stop it at end?
        return

    def _start_acquire(self):
        #caput("BL12I-EA-DET-20:CAM:Acquire", 1, wait = True, timeout = None)
        caput("BL13I-DI-WEB-02:CAM:Acquire", 1) # 
        print "Started acquiring frames!"
    
    def _stop_acquire(self):
        caput("BL13I-DI-WEB-02:CAM:Acquire", 0)
        print "Acquire stopped!"

    def _make_data_folder(self,path):
        if not (os.access (path, os.F_OK)):
            os.makedirs(path)
        if not (os.access (path, os.F_OK)):
            print ("!!! Could not create folder %s",path)
            #sys.exit(0)

    def _set_tif_writer(self, outdirpath, nimages):    ## add filename_prefix_hdf and template? change to configure?
        caput("BL13I-DI-WEB-02:TIFF:Capture", 0) # Stop previous hdf streaming if the script is interrupted
        
        caput("BL13I-DI-WEB-02:TIFF:CreateDirectory",1)

        caput("BL13I-DI-WEB-02:TIFF:EnableCallbacks", 1)
        caput("BL13I-DI-WEB-02:TIFF:FileNumber", 0)#, timeout=10)    #was 0

        caputStringAsWaveform("BL13I-DI-WEB-02:TIFF:FileTemplate","%s%s%05d.tif") #, timeout=10)
        caputStringAsWaveform("BL13I-DI-WEB-02:TIFF:FileName", self.filename_prefix) #, timeout=10)
        caputStringAsWaveform("BL13I-DI-WEB-02:TIFF:FilePath", outdirpath) #, timeout=10)
        
        caput("BL13I-DI-WEB-02:TIFF:AutoIncrement", 1)
        
        caput("BL13I-DI-WEB-02:TIFF:NumCapture", nimages)
        
        sleep(1)
        caput("BL13I-DI-WEB-02:TIFF:Capture", 1)

        #return
        #print "All done - bye!"

print("Creating web2_cam object in GDA...")
web2_cam=WebCam()
print("Finished creating web2_cam object in GDA!")

#Example:
#web2_cam.collect_data(0.1,1.5,10,"ice_cream")






from time import sleep
import os
import time

from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gda.jython import InterfaceProvider

from gda.data import NumTracker
blNumTracker = NumTracker('i13-1')
from gda.jython.commands.Input import requestInput
from gda.util import VisitPath
import os

from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gda.jython import InterfaceProvider
from epics_scripts.pv_scannable_utils import createPVScannable, caput, caget, caputStringAsWaveform

from gdascripts.utils import caput_wait

from gda.device.detector.addetector.triggering import AbstractADTriggeringStrategy
from gda.device.detector import NXDetector



class ExcaliburOdinSoftwareTriggeredNXDet(NXDetector):
    def __init__(self, name, collectionStrategy, dset="entry/instrument/detector/data"):
        self.setName(name)
        self.setCollectionStrategy(collectionStrategy)
        self.afterPropertiesSet()
        #self.setExtraNames("count_time")
        self.getExtraNames()
        self.hdfpath = None
        self.dset = dset
        self.file_writer_configured = False
    
    def _readout(self):
        lastReadoutValue = super(ExcaliburOdinSoftwareTriggeredNXDet, self).readout()
        dataTree = NXDetectorData()
        #print type(dataTree)
        #print dataTree
        #output = '/dls/i13/data/2017/cm16786-5/tmp/12345.hdf'
        output = self.hdfpath
        dataTree.addScanFileLink(self.getName(), "nxfile://" + output + "#%s" %(self.dset)); #addExternaLfileLink
        #print "from readout: %s" %(output)
        #return output
        return dataTree
    
    def readout(self):
        dataTree = super(ExcaliburOdinSoftwareTriggeredNXDet, self).readout()
        #dataTree = NXDetectorData()
        #print type(dataTree)
        #print dataTree
        #output = '/dls/i13/data/2017/cm16786-5/tmp/12345.hdf'
#        output = self.hdfpath
#        dataTree.addScanFileLink(self.getName(), "nxfile://" + output + "#%s" %(self.dset)); #addExternaLfileLink
        #print "from readout: %s" %(output)
        #return output
        return dataTree
    
    def getCollectionTime(self):
        #print "@getCollectionTime!"
        #return self.getCollectionStrategy().collectionTime # instead of that getCollectionTime in DetectorBase
        return super(ExcaliburOdinSoftwareTriggeredNXDet, self).getCollectionTime()

    def set_hdfpath(self,hdfpath):
        self.hdfpath = hdfpath
        
    def createsOwnFiles(self):
        return False


class ExcaliburOdinSoftwareADTriggerringStrategy(AbstractADTriggeringStrategy):
    def __init__(self):
        #print "__init__"
        self.collectionTime = 2.0
        self.busy = False
        #print "__init__ = %.3f" %(self.collectionTime)
        #pass
        self.file_writer_configured = False
        self.filename_prefix = "excalibur"
        self.filename_template = "%s_%d"
        self.file_template = "%s%s_%d.h5"
        self.file_extension = "h5"
        self.outdirpath = None
        self.scan_number = None
        self.acq_period_rbv = None
        self.nimages = None
        self.image_idx = 0  
    
    def _set_data_collection_params(self, exposure_time_sec, acq_period_sec):

        #disarm?
        #self.sanity_check(exposure_time_sec, acq_period_sec)
        caput_wait("BL13J-EA-EXCBR-02:CAM:AcquirePeriod", acq_period_sec, timeout=10)
        caput_wait("BL13J-EA-EXCBR-02:CAM:AcquireTime", exposure_time_sec, timeout=10)
        #sleep(1.0)
        exposure_time_sec_eff = caget("BL13J-EA-EXCBR-02:CAM:AcquireTime_RBV")
        acq_period_sec_eff = caget("BL13J-EA-EXCBR-02:CAM:AcquirePeriod_RBV")
        print "\t exposure time: %s s" %(exposure_time_sec_eff)
        print "\t acquisition period: %s s" %(acq_period_sec_eff)
        self.acq_period_rbv = float(acq_period_sec_eff)

        caput_wait("BL13J-EA-EXCBR-02:CAM:ImageMode", 1)        		#0=Single, 1=Multiple
        caput_wait("BL13J-EA-EXCBR-02:CAM:TriggerMode", 0)    			#0=Internal, 1=External, 2=Sync 

        image_mode_eff = caget("BL13J-EA-EXCBR-02:CAM:ImageMode_RBV")
        trigger_mode_eff = caget("BL13J-EA-EXCBR-02:CAM:TriggerMode_RBV")
        print "\t image mode: %s" %(image_mode_eff)
        print "\t trigger mode: %s" %(trigger_mode_eff)

        return exposure_time_sec_eff, acq_period_sec_eff        #order?

    def _start_acquire(self):
        #caput("BL12I-EA-DET-20:CAM:Acquire", 1, wait = True, timeout = None)
        caput("BL13J-EA-EXCBR-02:CAM:Acquire", 1) # User may see funny image on video signal if use this option (if caput_wait? KW)
        print "\t Acquire start!"
    
    def _stop_acquire(self):
        caput("BL13J-EA-EXCBR-02:CAM:Acquire", 0)	#0=Done, 1=Acquire
        print "\t Acquire stop!"

    def _set_hdf5_writer(self, outdirpath, scan_number, nimages=1):    ## add filename_prefix_hdf and template? change to configure?
        caput_wait("BL13J-EA-EXCBR-02:OD:Capture", 0) # Stop previous writing if any | 0=Done, 1=Capture

        caputStringAsWaveform("BL13J-EA-EXCBR-02:OD:FilePath", outdirpath) #, timeout=10)	# File Directory
        fname = self.filename_template %(self.filename_prefix, scan_number)
        caputStringAsWaveform("BL13J-EA-EXCBR-02:OD:FileName", fname)        
        
        #caput("BL12I-EA-DET-02:TIF:EnableCallbacks", 1)
#        caput_wait("BL13J-EA-EXCBR-02:OD:FileNumber", scan_number, timeout=10)    #was 0

        #caputStringAsWaveform("BL12I-EA-DET-02:TIF:FileTemplate","%s%s%05d.tif") #, timeout=10)
#        caput("BL13J-EA-EXCBR-02:OD:FileNamePrefix", self.filename_prefix) #, timeout=10)    #caputStringAsWaveform produces 101 instead
#        caputStringAsWaveform("BL13J-EA-EXCBR-02:OD:FilePath", outdirpath) #, timeout=10)
        
#        caput("BL13J-EA-EXCBR-02:OD:AutoIncrement", 0) 	#0=No, 1=Yes

#        caputStringAsWaveform("BL13J-EA-EXCBR-02:OD:FileExtension", "h5")
        
        caput("BL13J-EA-EXCBR-02:OD:NumCapture", nimages)
        
        sleep(1)
        caput("BL13J-EA-EXCBR-02:OD:Capture", 1)	#0=Done, 1=Capture

        #return
        #print "All done - bye!"

    def prepare_before_collection(self, exposure_time_sec, acq_period_sec): #, savefolderpath):
        self._set_data_collection_params(exposure_time_sec, acq_period_sec)
        #self._set_miro_hdf_path(savefolderpath)
    
    def _collect_data(self, exposure_time_sec, nimages=1, primed=False):
        print("*** ExcaliburOdinSoftwareADTriggerringStrategy._collect_data called!")
        self.nimages = nimages
        print("\t nimages: %d" %(self.nimages))
        print("\t image_idx: %d" %(self.image_idx))
        #stop acquire
        caput("BL13J-EA-EXCBR-02:CAM:Acquire", 0)		#0=Done, 1=Acquire
        #disarm
        #caput("BL12I-EA-DET-02:CAM:ARM_MODE", 0)
        
        #caput("BL13J-EA-EXCBR-02:CAM:ArrayCounter", 0)		# already done by Odin
        
        #self.sanity_check(exposure_time_sec, acq_period_sec)
        self.prepare_before_collection(exposure_time_sec, exposure_time_sec)

        # handle #Exp/Image?
        
        caput("BL13J-EA-EXCBR-02:CAM:NumImages", self.nimages)
        if not self.file_writer_configured:
            self.scan_number = blNumTracker.getCurrentFileNumber() #+ 1 # appears to be already advanced by the scanning system
            #blNumTracker.incrementNumber()
            print "\t scan_number = %d" %(self.scan_number)
            #t:\\i12\\data\\\\2018\\cm19662-1\\rawdata\\75136\\projections\\
            #self.outdirpath = "t:\\i12\\data\\\\2018\\cm19662-1\\rawdata\\%d\\projections\\" %(self.scan_number)
            #self.outdirpath = os.path.join(wd(), str(self.scan_number), "projections")
            #self.outdirpath = "/dls/i13-1/data/2018/cm19663-3/tmp"
            #self.outdirpath = "/dls/i13-1/data/2019/mg21652-1/raw"
            self.outdirpath = "/dls/i13-1/data/2019/cm22975-4/raw/excalibur-odin-%d-files" %(self.scan_number)
            outdirpath = VisitPath.getVisitPath()
            print("outdirpath (pre) = %s" %(outdirpath))
            leafdir_template = "excalibur-odin-%d-files"
            leafdir = leafdir_template %(self.scan_number)
            outdirpath = os.path.join(outdirpath, leafdir) 
            print("outdirpath (post)= %s" %(outdirpath))
            if self.outdirpath is None:
                #self.outdirpath = wd()
                pass
            print "\t outdirpath = %s" %(self.outdirpath)
        
            #self._set_hdf5_writer(self.outdirpath, self.scan_number, self.nimages)    # remove args?
            self.file_writer_configured = True
        self._set_hdf5_writer(self.outdirpath, self.image_idx, self.nimages)
        
        self._start_acquire()
#        acq_per_rbv = float(caget("BL12I-EA-DET-02:CAM:AcquirePeriod_RBV"))
#        #sleep(nimages*acq_per_rbv*(2.5))
        
        #need to exit this fn somehow, so the below code is needed just in case sth goes wrong!
        sleep(5) #this sleep doesn't slow down acq but is need to give acq chance to start (but one may miss it starting so there is no point first wait for it to start and then wait for it to stop)
        #exit_test = caget("BL13J-EA-EXCBR-02:OD:Capture_RBV")=="Capturing"
        #while (exit_test):                   #0=done, 1=Capturing
        self.busy = True
        count = 0
        while (caget("BL13J-EA-EXCBR-02:OD:Capture_RBV")=="Capturing"): # change this to comparing ints
            sleep(max(1,self.acq_period_rbv*nimages))       # for hdf writing this shd be scaled by nimages
            #exit_test = caget("BL13J-EA-EXCBR-02:OD:Capture_RBV")=="Capturing"
            count += 1
            print count             # exit on count_max?
        self._stop_acquire()
        self.busy = False
        #self.generate_vds()
        print "\t Image captured!"
        self.image_idx += 1
        return                  # is it needed?

    def prepareForCollection(self, collectionTime, numImages, scanInfo):
        print("**** ExcaliburOdinSoftwareADTriggerringStrategy.prepareForCollection called!")
        #self.configureAcquireAndPeriodTimes(collectionTime) #this would call getAdBase()
        #pass
        #self.configureAcquireAndPeriodTimes(collectionTime)
        self.collectionTime = collectionTime
        self._set_data_collection_params(collectionTime, collectionTime)
        nimages = 1
        print "\t @prepareForCollection:", collectionTime, numImages, scanInfo
        caput("BL13J-EA-EXCBR-02:CAM:NumImages", nimages)
    
    def collectData(self):
        self._collect_data(self.collectionTime, 1)
    
    def stop(self):
        self._stop_acquire()
        self.file_writer_configured = False
        self.image_idx = 0
    
    def atCommandFailure(self):
        self._stop_acquire()
        self.file_writer_configured = False
        self.image_idx = 0
    
    def completeCollection(self):
        self.file_writer_configured = False
        self.image_idx = 0
        #pass
    
    def getNumberImagesPerCollection(self, collectionTime):
        return 1
    
    def waitWhileBusy(self):
        cnt_max = 5
        cnt = 0
        while self.busy and cnt<cnt_max:
            sleep(1)
            cnt += 1
        return None             #java.lang.Exception: during scan collection: DeviceException: TypeError: None required for void return
    
    def getAcquireTime(self):
        #print "@getAcquireTime!"
        print("ExcaliburOdinSoftwareADTriggerringStrategy.getAcquireTime = %.3f" %(self.collectionTime))
        #print "getAcquireTime = %.3f" %(0.11)
        return self.collectionTime


excalibur_odin_sw_cs=ExcaliburOdinSoftwareADTriggerringStrategy()
excalibur_odin_sw_det0=ExcaliburOdinSoftwareTriggeredNXDet("excalibur_odin_sw_det0", excalibur_odin_sw_cs)







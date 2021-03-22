from time import sleep
import os

from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gda.jython import InterfaceProvider

from gda.data import NumTracker
BlNumTracker = NumTracker('i13i')
from gda.jython.commands.Input import requestInput
import os

from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gda.jython import InterfaceProvider

from gdascripts.utils import caput_wait
from epics_scripts.pv_scannable_utils import caput, caget, caputStringAsWaveform

#BL12I-EA-DET-02:CAM | BL12I-EA-DET-02:HDF
#BL13I-EA-DET-01 | BL13I-EA-DET-01:HDF5

class PCOXgraph():
    def __init__(self, pv_prefix="BL13I-EA-DET-01", pv_hdf_component="HDF5", name="pco_xgraph"):	# w/out CAM?
        self.pv_prefix = pv_prefix
        self.pv_hdf_component = pv_hdf_component
        self.ca = CAClient()
        self.filename_prefix = "projections"
        self.file_template = "%s%s_%d.hdf"
        self.file_extension = "hdf"
        self.outdirpath = None
        self.scan_number = None         # int
        self.acq_period_rbv = None
        self.nimages = None
        self.name = name
        self.hdfpath = None
        self.abort_state = False
        self.visit = "mg25341-3"
        self.year = 2021
        self.subdirpath = "raw"
        
    def set_data_collection_params(self, exposure_time_sec, acq_period_sec, nimages=1):
        
        #self.sanity_check(exposure_time_sec, acq_period_sec)
        caput_wait(self.pv_prefix+":CAM:AcquireTime", exposure_time_sec, timeout=10)
        caput_wait(self.pv_prefix+":CAM:AcquirePeriod", acq_period_sec, timeout=10)
        #sleep(1.0)
        exposure_time_sec_eff = caget(self.pv_prefix+":CAM:AcquireTime_RBV")
        acq_period_sec_eff = caget(self.pv_prefix+":CAM:AcquirePeriod_RBV")
        print "Effective exposure time: %s s" %(exposure_time_sec_eff)
        print "Effective acquisition period: %s s" %(acq_period_sec_eff)
        self.exposure_time_rbv = float(exposure_time_sec_eff)
        self.acq_period_rbv = float(acq_period_sec_eff)

        caput_wait(self.pv_prefix+":CAM:ImageMode", 1)     #0=Single,1=Multiple,2=Continuous
        caput_wait(self.pv_prefix+":CAM:TriggerMode", 0)    	#0=Auto,1=Soft,2=Ext+Soft,3=Ext Pulse,4=Ext Only

        image_mode_eff = caget(self.pv_prefix+":CAM:ImageMode_RBV")
        trigger_mode_eff = caget(self.pv_prefix+":CAM:TriggerMode_RBV")
        print "Effective image mode: %s" %(image_mode_eff)
        print "Effective trigger mode: %s" %(trigger_mode_eff)

        return exposure_time_sec_eff, acq_period_sec_eff        #order?

    def sanity_check(exposure_time_sec, acq_period_sec):
        if exposure_time_sec > acq_period_sec:
            print("Exposure time %.4f is larger that acquisition period %.4f - forcing exposure time to be equal to acquisition period!")
            exposure_time_sec = acq_period_sec
        
    def prepare_before_collection(self, exposure_time_sec, acq_period_sec, nimages=1): #, savefolderpath):
        self.set_data_collection_params(exposure_time_sec, acq_period_sec, nimages)
        #self._set_miro_hdf_path(savefolderpath)
        
    def collect_data(self, exposure_time_sec, acq_period_sec, nimages, subdirpath="raw", soft_terminated=False, prepped=False):
        """
        exposure_time_sec: exposure time in sec 
        acq_period_sec: acquisition period in sec
        nimages: total number of images to be collected
        subdirpath: name of a sub-directory of the visit directory for saving output HDF5 files
            eg "rawdata", "tmp", or "rawdata/<sample-name>" (use forward-slashes only)
        soft_terminated: if True, this software script waits for HDF5 writer to finish saving the image data coming from the camera,
            and then stops acquire on the camera
        prepped: currently unused (default: False)
        """
        fn = self.collect_data.__name__
        cmd = "%s(exposure_time_sec=%.04f, acq_period_sec=%.04f, nimages=%d, subdirpath=%s, soft_terminated=%s)" %(fn, exposure_time_sec, acq_period_sec, nimages, subdirpath, soft_terminated)
    
        self.abort_state = False
        self.nimages = nimages
        #stop acquire
        caput(self.pv_prefix+":CAM:Acquire", 0)             #0=Done, 1=Acquire

        caput(self.pv_prefix+":CAM:ArrayCounter", 0)
        
        #self.sanity_check(exposure_time_sec, acq_period_sec)
        self.prepare_before_collection(exposure_time_sec, acq_period_sec, nimages)

        # handle #Exp/Image?
        
        caput(self.pv_prefix+":CAM:NumImages", nimages)
        self.scan_number = BlNumTracker.getCurrentFileNumber() + 1
        BlNumTracker.incrementNumber()
        print "scan_number = %d" %(self.scan_number)
        #t:\\i12\\data\\\\2018\\cm19662-1\\rawdata\\75136\\projections\\	#example path
        #t:\\i13\\data\\\\2018\\cm19664-3\\rawdata\\75136\\projections\\
        #self.outdirpath = "t:\\i12\\data\\\\2018\\cm19662-1\\rawdata\\%d\\projections\\" %(self.scan_number)
        #self.outdirpath = os.path.join(wd(), str(self.scan_number), "projections")
        subdirpath_sanitised = subdirpath.strip("/")
        subdirpath_sanitised_component_lst = subdirpath_sanitised.split("/")
        path_component_template = "\\%s"
        self.subdirpath = subdirpath_sanitised
        outdirpath_template = "g:\\i13\\data\\\\%i\\%s" %(self.year, self.visit)
        for c in subdirpath_sanitised_component_lst:
            outdirpath_template += path_component_template
        #self.outdirpath = "t:\\i12\\data\\\\2018\\%s\\%s" %(self.visit, self.subdirpath)
        self.outdirpath = outdirpath_template %tuple(subdirpath_sanitised_component_lst)
        #self.outdirpath = outdirpath
        print "outdirpath = %s" %(self.outdirpath)
        
        self.set_hdf5_writer(self.outdirpath, self.scan_number, nimages)    # remove args?
        
        self.start_acquire()
        
        if soft_terminated:
    #       acq_per_rbv = float(caget("BL12I-EA-DET-02:CAM:AcquirePeriod_RBV"))
    #       #sleep(nimages*acq_per_rbv*(2.5))
            
            #need to exit this fn somehow, so the below code is needed just in case sth goes wrong!
            sleep(5) #this sleep doesn't slow down acq but is needed to give acq chance to start (but one may miss it starting so there is no point first wait for it to start and then wait for it to stop)
            #exit_test = caget("BL13J-EA-EXCBR-02:OD:Capture_RBV")=="Capturing"
            #while (exit_test):                   #0=done, 1=Capturing
            pct = 0.01
            count = 0
            #sleep_interval_tot = max(1,self.acq_period_rbv*(1.0+pct)*nimages)
            sleep_interval_tot = self.acq_period_rbv*(1.0+pct)*nimages
            sleep_interval_fract = sleep_interval_tot	# could be a fraction of the total or user-specified value
            sleep_interval_fract = 1		#in sec
            #print self.abort_state
            #print caget(self.pv_prefix+":HDF:Capture_RBV")
            while ( (not self.abort_state) and caget(self.pv_prefix+":HDF5:Capture_RBV")=="1"): # change this to comparing ints? 0=Done,1=Capturing
                sleep(sleep_interval_fract)       # for hdf writing this shd be scaled by nimages
                #exit_test = caget("BL13J-EA-EXCBR-02:OD:Capture_RBV")=="Capturing"
                count += 1
                print("loop count = %d" %(count))             # exit on count_max?
            self.stop_acquire()
        #self.create_nexus_scan_file(self.name,exposure_time_sec,self.scan_number,self.hdfpath,self.outdirpath,cmd)
            print "All done - bye!"
        return                  # is this rtn necessary (or useful)?
    
    def start_acquire(self):
        #caput("BL12I-EA-DET-20:CAM:Acquire", 1, wait = True, timeout = None)
        caput(self.pv_prefix+":CAM:Acquire", 1) #(if caput_wait? KW)
        print "Acquire started!"
    
    def take_snap(self):
        self.start_acquire()
    
    def stop_acquire(self):
        caput(self.pv_prefix+":CAM:Acquire", 0)    #0=Done, 1=Acquire
        print "Acquire stopped!"

    def stop_collect_data(self):	#abort?
        self.abort_state = True		# terminate
        self.stop_acquire()
        sleep(1)
        self.stop_hdf_capture()
    
    def abort(self):
        self.stop_collect_data()
    
    def _make_data_folder(self,hdfpath):
        if not (os.access (hdfpath, os.F_OK)):
            os.makedirs(hdfpath)
        if not (os.access (hdfpath, os.F_OK)):
            print ("!!! Could not create folder %s",hdfpath)
            sys.exit(0)
    
    def set_hdf5_writer(self, outdirpath, scan_number, nimages):    ## add filename_prefix_hdf and template? change to configure?
        # wait a bit before stopping?
        caput_wait(self.pv_prefix+":HDF5:Capture", 0) # Stop previous writing if any | 0=Done, 1=Capture
        
        #caputStringAsWaveform("BL13J-EA-DET-04:HDF5:FileName", self.filename_prefix)
        
        caput(self.pv_prefix+":HDF5:EnableCallbacks", 1)
        caput_wait(self.pv_prefix+":HDF5:FileNumber", scan_number, timeout=10)    #was 0
        
        caputStringAsWaveform(self.pv_prefix+":HDF5:FileTemplate", self.file_template) #, timeout=10)
        caputStringAsWaveform(self.pv_prefix+":HDF5:FileName", self.filename_prefix) #, timeout=10)    #caput has no effect
        caputStringAsWaveform(self.pv_prefix+":HDF5:FilePath", outdirpath) #, timeout=10)
        
        self.hdfpath = self.file_template %(outdirpath+"/",self.filename_prefix,scan_number)
        print("hdfpath = %s" %(self.hdfpath))
        
        caput(self.pv_prefix+":HDF5:AutoIncrement", 0)      #0=No, 1=Yes
        caput(self.pv_prefix+":HDF5:AutoSave", 0)          #0=No, 1=Yes
        
        #caputStringAsWaveform("BL13J-EA-EXCBR-02:OD:FileExtension", "h5")
        
        caput(self.pv_prefix+":HDF5:NumCapture", nimages)
        
        caput(self.pv_prefix+":HDF5:FileWriteMode", 2)      #0=Single, 1=Capture, 3=Stream
        #blocking?
        
        sleep(1)
        caput(self.pv_prefix+":HDF5:Capture", 1)    #0=Done, 1=Capture
        
        #return

    def stop_hdf_capture(self):
        caput(self.pv_prefix+":HDF5:Capture", 0)

    def create_nexus_scan_file(self,detector_name,exptime,scan_number,hdfpath,outdirpath=None,cmd=None):
        from gda.data.scan.datawriter.DefaultDataWriterFactory import createDataWriterFromFactory
        from gda.scan.ScanInformation import ScanInformationBuilder
        from gda.scan import ScanDataPoint
        from gda.device.scannable import DummyScannable
        #from dummy_utils import dum_collstrat, dum_det
        #import sys
        #sys.path.append("/dls_sw/i12/scripts/gda-tests")
        #from dummy_utils import dum_det
    
        print("create_nexus_scan_file: outdirpath = %s" %(outdirpath))
        dw = createDataWriterFromFactory()
    
        if outdirpath is None:
            nxspath = os.path.join(gda.util.VisitPath.getVisitPath(),"%d.nxs" %(scan_number))
        else:
            nxspath = os.path.join(outdirpath,"%d.nxs" %(scan_number))
        print("nxspath = %s" %(nxspath))
        npts = 1
        si = (ScanInformationBuilder()
                .dimensions(npts)
                .scanNumber(scan_number)
                .instrument('i13')
                .filename(nxspath)
                .numberOfPoints(npts)
                .build())

        #dum_collstrat.collectionTime = exptime
        dum_det.name = detector_name
        dum_det.collectionTime = exptime
        dum_det.hdfpath = hdfpath
        #dum_det.atScanStart()
        
        dw.configureScanNumber(scan_number)
        try:
            for i in range(npts):
                #print "i = %d" %(i)
                sdp_tmp = ScanDataPoint()
                if cmd is None:
                    sdp_tmp.setCommand("undefined")
                else:
                    sdp_tmp.setCommand(cmd)
                sdp_tmp.setUniqueName("unique")
                sdp_tmp.setScanInformation(si)
                sdp_tmp.addDetector(dum_det)
                sdp_tmp.addDataFromDetector(dum_det)
                
                sdp_tmp.setCurrentPointNumber(i)
                
                dw.addData(sdp_tmp)
        except Exception, e:
            print "Error: %s" %(str(e))
        finally:
            dw.completeCollection()
        return nxspath
    
print("INFO: Creating pco_xgraph object in GDA...")
pco_xgraph=PCOXgraph()
print("INFO: Finished creating pco_xgraph object in GDA!")


#Pixel Rate?
#ADC?
#use Arm?
#record Acq Period in nexus?
#relative path to hdf data file?
#buffer monitoring?
#check for any backslashes?
#enable & disable
#timestamp


def _create_nexus_scan_file(detector_name,exptime,scan_number,hdfpath,outdirpath=None,cmd=None, xyz_before_lst=None, xyz_after_lst=None):
    from gda.data.scan.datawriter.DefaultDataWriterFactory import createDataWriterFromFactory
    from gda.scan.ScanInformation import ScanInformationBuilder
    from gda.scan import ScanDataPoint
    from gda.device.scannable import DummyScannable
    from dummy_utils import dum_collstrat, dum_det
    
    print("create_nexus_scan_file: outdirpath = %s" %(outdirpath))
    dw = createDataWriterFromFactory()
    
    dum_before_x_pos = []
    dum_before_y_pos = []
    dum_before_z_pos = []
    for i, e in enumerate(xyz_before_lst):
        dum_before_x_pos.append(xyz_before_lst[i][0])
        dum_before_y_pos.append(xyz_before_lst[i][1])
        dum_before_z_pos.append(xyz_before_lst[i][2])

    dum_after_x_pos = []
    dum_after_y_pos = []
    dum_after_z_pos = []
    for i, e in enumerate(xyz_after_lst):
        dum_after_x_pos.append(xyz_after_lst[i][0])
        dum_after_y_pos.append(xyz_after_lst[i][1])
        dum_after_z_pos.append(xyz_after_lst[i][2])
    
    npts = len(dum_before_x_pos)
    #assert(dum_x_pos.size == dum_y_pos.size and dum_y_pos.size == dum_z_pos.size)
    if outdirpath is None:
        nxspath = os.path.join(gda.util.VisitPath.getVisitPath(),"%d.nxs" %(scan_number))
    else:
        nxspath = os.path.join(outdirpath,"%d.nxs" %(scan_number))
    
    si = (ScanInformationBuilder()
            .dimensions(npts)
            .scanNumber(scan_number)
            .instrument('i13')
            .filename(nxspath)
            .numberOfPoints(npts)
            .build())

    dum_collstrat.collectionTime = exptime
    dum_det.name = detector_name
    dum_det.hdfpath = hdfpath
    dum_det.atScanStart()
    
    dum_before_x = DummyScannable("before_x")
    dum_before_x.setLowerGdaLimits(None)
    dum_before_x.setUpperGdaLimits(None)
    
    dum_before_y = DummyScannable("before_y")
    dum_before_y.setLowerGdaLimits(None)
    dum_before_y.setUpperGdaLimits(None)
    
    dum_before_z = DummyScannable("before_z")
    dum_before_z.setLowerGdaLimits(None)
    dum_before_z.setUpperGdaLimits(None)
    
    dum_after_x = DummyScannable("after_x")
    dum_after_x.setLowerGdaLimits(None)
    dum_after_x.setUpperGdaLimits(None)
    
    dum_after_y = DummyScannable("after_y")
    dum_after_y.setLowerGdaLimits(None)
    dum_after_y.setUpperGdaLimits(None)
    
    dum_after_z = DummyScannable("after_z")
    dum_after_z.setLowerGdaLimits(None)
    dum_after_z.setUpperGdaLimits(None)
    
    dw.configureScanNumber(scan_number)
    try:
        for i in range(npts):
            #print "i = %d" %(i)
            sdp_tmp = ScanDataPoint()
            if cmd is None:
                sdp_tmp.setCommand("undefined")
            else:
                sdp_tmp.setCommand(cmd)
            sdp_tmp.setUniqueName("some-unique-name-but-not-this-one")
            sdp_tmp.setScanInformation(si)
            sdp_tmp.addDetector(dum_det)
            sdp_tmp.addDataFromDetector(dum_det)
            
            sdp_tmp.addScannable(dum_before_x)
            sdp_tmp.addScannable(dum_before_y)
            sdp_tmp.addScannable(dum_before_z)
            
            sdp_tmp.addScannable(dum_after_x)
            sdp_tmp.addScannable(dum_after_y)
            sdp_tmp.addScannable(dum_after_z)
            
            sdp_tmp.setCurrentPointNumber(i)
            
            sdp_tmp.addScannablePosition(dum_before_x_pos[i], dum_before_x.getOutputFormat())
            sdp_tmp.addScannablePosition(dum_before_y_pos[i], dum_before_y.getOutputFormat())
            sdp_tmp.addScannablePosition(dum_before_z_pos[i], dum_before_z.getOutputFormat())
            
            sdp_tmp.addScannablePosition(dum_after_x_pos[i], dum_after_x.getOutputFormat())
            sdp_tmp.addScannablePosition(dum_after_y_pos[i], dum_after_y.getOutputFormat())
            sdp_tmp.addScannablePosition(dum_after_z_pos[i], dum_after_z.getOutputFormat())
            
            dw.addData(sdp_tmp)
    except Exception, e:
        print "Error: %s" %(str(e))
    finally:
        dw.completeCollection()
    return nxspath


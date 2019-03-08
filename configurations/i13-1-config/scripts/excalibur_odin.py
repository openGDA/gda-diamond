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
import os

from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gda.jython import InterfaceProvider
from epics_scripts.pv_scannable_utils import createPVScannable, caput, caget, caputStringAsWaveform

from gdascripts.utils import caput_wait

def wait_for_file(filepath, mode=os.R_OK, wait_sec=3, niter=60):
    print("wait_for_file: wait_sec = %.3f s, niter = %d" %(wait_sec,niter))
    print("filepath = %s" %(filepath))
    h, t = os.path.split(filepath)
    print("filename = %s (of %d chars)" %(t, len(t)))
    """
    Waits for file to be accessible in given access mode
    Returns True if file was successfully accessed in given mode within specified number of attempts
    
    filepath: the path to file to be accessed 
    mode: the file mode in which file is to be accessed, eg os.R_OK
    sleepdelta: time interval in seconds between two consecutive attempts to access file; default=1, 
    niter: max number of file-access attempts to be made; default=60
    """

    cnt = 0
    inaccessible = True 
    #wait for file to become accessible in given mode
    while inaccessible and (cnt < niter):
        if os.access(filepath, mode):
            inaccessible = False
            print "File %s successfully accessed on count = %i" %(filepath, cnt)
        else:
            cnt += 1
            time.sleep(wait_sec)
            #print " %i zzz..." %(cnt)
    print("@ %i/%i" %(cnt,niter))
    return (not inaccessible)


class ExcaliburOdinXgraph():
    def __init__(self, pv_prefix="BL13J-EA-EXCBR-02:CAM:"):
        self.pv_prefix = pv_prefix
        self.ca = CAClient()
        self.filename_prefix = "excalibur"
        self.filename_template = "%s_%d"
        self.file_template = "%s%s_%d.h5"
        self.file_extension = "h5"
        self.outdirpath = None
        self.scan_number = None         # int
        self.acq_period_rbv = None
        self.ndistribs = None
        self.nimages = None
        self.nnodes = 4
        #self.call_ref = {'STATE': 'BL13J-EA-EXCBR-02:CAM:DetectorState_RBV', 'IMAGE MODE': 'BL13J-EA-EXCBR-02:CAM:ImageMode', 'TRIGGER MODE': 'BL13J-EA-EXCBR-02:CAM:TriggerMode', 'MODEL': 'BL13J-EA-EXCBR-02:CAM:Model_RBV'}
        #self.call_use = ['MODEL', 'STATE', 'IMAGE MODE', 'TRIGGER MODE']
        self._init_call()
        
    def __call__(self):
        msg = ""
        for i, el in enumerate(self.call_use):
            msg += '%s: %s' %(el, caget(self.call_ref[el]))
            msg += '; ' if i < len(self.call_use)-1 else '.'
        print msg

    def _init_call(self):
        # reference
        self.call_ref = {}
        self.call_ref.update({'STATE': 'BL13J-EA-EXCBR-02:CAM:DetectorState_RBV'})
        self.call_ref.update({'IMAGE MODE': 'BL13J-EA-EXCBR-02:CAM:ImageMode'})
        self.call_ref.update({'TRIGGER MODE': 'BL13J-EA-EXCBR-02:CAM:TriggerMode'})
        self.call_ref.update({'MODEL': 'BL13J-EA-EXCBR-02:CAM:Model_RBV'})

        # use
        self.call_use = ['MODEL', 'STATE', 'IMAGE MODE', 'TRIGGER MODE']

    def _verify_model(self):
        return caget(self.call_ref['MODEL'])=='Odin [Excalibur2]'

    def set_output_dir(self, dirpath):
        self.outdirpath = dirpath
        
    def set_data_collection_params(self, exposure_time_sec, acq_period_sec):

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
        
    def prepare_before_collection(self, exposure_time_sec, acq_period_sec): #, savefolderpath):
        self.set_data_collection_params(exposure_time_sec, acq_period_sec)
        #self._set_miro_hdf_path(savefolderpath)
        
    def collect_data(self, exposure_time_sec, nimages, primed=False):
        self.nimages = nimages
        print "\t nimages: %d" %(self.nimages)
        #stop acquire
        caput("BL13J-EA-EXCBR-02:CAM:Acquire", 0)		#0=Done, 1=Acquire
        #disarm
        #caput("BL12I-EA-DET-02:CAM:ARM_MODE", 0)
        
        #caput("BL13J-EA-EXCBR-02:CAM:ArrayCounter", 0)		# already done by Odin
        
        #self.sanity_check(exposure_time_sec, acq_period_sec)
        self.prepare_before_collection(exposure_time_sec, exposure_time_sec)

        # handle #Exp/Image?
        
        caput("BL13J-EA-EXCBR-02:CAM:NumImages", nimages)
        self.scan_number = blNumTracker.getCurrentFileNumber() + 1
        blNumTracker.incrementNumber()
        print "\t scan_number = %d" %(self.scan_number)
        #t:\\i12\\data\\\\2018\\cm19662-1\\rawdata\\75136\\projections\\
        #self.outdirpath = "t:\\i12\\data\\\\2018\\cm19662-1\\rawdata\\%d\\projections\\" %(self.scan_number)
        #self.outdirpath = os.path.join(wd(), str(self.scan_number), "projections")
        #self.outdirpath = "/dls/i13-1/data/2018/cm19663-3/tmp"
        self.outdirpath = "/dls/i13-1/data/2019/cm22975-1/raw"
        if self.outdirpath is None:
            #self.outdirpath = wd()
            pass
        print "\t outdirpath = %s" %(self.outdirpath)
        
        self._set_hdf5_writer(self.outdirpath, self.scan_number, nimages)    # remove args?
        
        self._start_acquire()
#        acq_per_rbv = float(caget("BL12I-EA-DET-02:CAM:AcquirePeriod_RBV"))
#        #sleep(nimages*acq_per_rbv*(2.5))
        
        #need to exit this fn somehow, so the below code is needed just in case sth goes wrong!
        sleep(5) #this sleep doesn't slow down acq but is need to give acq chance to start (but one may miss it starting so there is no point first wait for it to start and then wait for it to stop)
        #exit_test = caget("BL13J-EA-EXCBR-02:OD:Capture_RBV")=="Capturing"
        #while (exit_test):                   #0=done, 1=Capturing
        count = 0
        while (caget("BL13J-EA-EXCBR-02:OD:Capture_RBV")=="Capturing"): # change this to comparing ints
            sleep(max(1,self.acq_period_rbv*nimages))       # for hdf writing this shd be scaled by nimages
            #exit_test = caget("BL13J-EA-EXCBR-02:OD:Capture_RBV")=="Capturing"
            count += 1
            print count             # exit on count_max?
        self._stop_acquire()
        self.generate_vds()
        print "All done - bye!"
        return                  # is it needed?

    def _start_acquire(self):
        #caput("BL12I-EA-DET-20:CAM:Acquire", 1, wait = True, timeout = None)
        caput("BL13J-EA-EXCBR-02:CAM:Acquire", 1) # User may see funny image on video signal if use this option (if caput_wait? KW)
        print "\t Acquire start!"
    
    def _stop_acquire(self):
        caput("BL13J-EA-EXCBR-02:CAM:Acquire", 0)	#0=Done, 1=Acquire
        print "\t Acquire stopped!"

    def _make_data_folder(self,hdfpath):
        if not (os.access (hdfpath, os.F_OK)):
            os.makedirs(hdfpath)
        if not (os.access (hdfpath, os.F_OK)):
            print ("!!! Could not create folder %s",hdfpath)
            sys.exit(0)

#    def _set_hdf5_writer(self, outdirpath, scan_number, nimages):    ## add filename_prefix_hdf and template? change to configure?
#        caput_wait("BL13J-EA-EXCBR-02:OD:Capture", 0) # Stop previous writing if any | 0=Done, 1=Capture#
#
#        caputStringAsWaveform("BL13J-EA-EXCBR-02:OD:FileName", "")        
#        
#        #caput("BL12I-EA-DET-02:TIF:EnableCallbacks", 1)
#        caput_wait("BL13J-EA-EXCBR-02:OD:FileNumber", scan_number, timeout=10)    #was 0##
#
#        #caputStringAsWaveform("BL12I-EA-DET-02:TIF:FileTemplate","%s%s%05d.tif") #, timeout=10)
#        caput("BL13J-EA-EXCBR-02:OD:FileNamePrefix", self.filename_prefix) #, timeout=10)    #caputStringAsWaveform produces 101 instead
#        caputStringAsWaveform("BL13J-EA-EXCBR-02:OD:FilePath", outdirpath) #, timeout=10)
#        
#        caput("BL13J-EA-EXCBR-02:OD:AutoIncrement", 0) 	#0=No, 1=Yes#
#
#        caputStringAsWaveform("BL13J-EA-EXCBR-02:OD:FileExtension", "h5")
#        
#        caput("BL13J-EA-EXCBR-02:OD:NumCapture", nimages)
#        
#        sleep(1)
#        caput("BL13J-EA-EXCBR-02:OD:Capture", 1)	#0=Done, 1=Capture
#
#        #return
#        #print "All done - bye!"
        
    def _set_hdf5_writer(self, outdirpath, scan_number, nimages):    ## add filename_prefix_hdf and template? change to configure?
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

    def generate_vds(self, scriptpath="/dls_sw/prod/tools/RHEL6-x86_64/defaults/bin/dls-vds-gen.py"):
        from gda.util import OSCommandRunner
        print "\t Running vds-gen!"
        #node_filename_template = "excalibur_%d_r%d.h5 "             # excalibur_<scan number>_r<rank>.h5
        node_filename_template = "excalibur_%d_%06d.h5 "             # excalibur_<scan number>_<0-padded rank>.h5
        interleaved_filename_template = "excalibur_%d_inter.h5 "    # excalibur_<scan number>_inter.h5
        gapfilled_filename_template = "excalibur_%d_vds.h5 "        # excalibur_<scan number>_vds.h5
        
        interleaved_filename = interleaved_filename_template %(self.scan_number)
        gapfilled_filename = gapfilled_filename_template %(self.scan_number)
        
        # create the interleaved vds
        cmd = scriptpath
        cmd += " %s -f " %(self.outdirpath)
        nfiles = self.nimages if (self.nimages < self.nnodes) else self.nnodes
        for i in range(nfiles):
            cmd += node_filename_template %(self.scan_number, i+1)	# was i
        
        counter_depth_str = caget("BL13J-EA-EXCBR-02:CAM:CounterDepth") # eg u'12 bit' # use BL13J-EA-EXCBR-02:OD:DataType?
        dtype_str = "int16"
        if counter_depth_str == "24 bit":       # replace with int compare?
            dtype_str = "int32"
        elif counter_depth_str == "12 bit":
            dtype_str = "int16"
        else:
            print("WARNING: Unexpected counter depth %s - setting VDS data type to %s!" %(counter_depth_str, dtype_str))
        cmd += "-t %s " %(dtype_str)
        cmd += "--mode interleave "
        cmd += "-o %s " %(interleaved_filename)
        
        print("Command for generating the interleaved VDS file: %s" %(cmd))
        
        
        # Check output file exists
        if os.path.isfile(interleaved_filename.strip()) == 0:
            cmd = cmd + " &"
            os.system(cmd)
        else:
            print("WARNING: interleaved VDS file %s already exists!" %(interleaved_filename))
        
        
        # create the gap-filled vds
        cmd = scriptpath
        cmd += " %s -f " %(self.outdirpath)
        cmd += interleaved_filename
        cmd += "--mode gap-fill -M 3 -s 3 -m 124 -l 2 -F -1 "
        cmd += "-o %s " %(gapfilled_filename)
        
        print("Command for generating the gap-filled VDS file: %s" %(cmd))
        
        # probably need to wait for the first command to complete before executing the next one!
        interleaved_fpath = os.path.join(self.outdirpath, interleaved_filename.strip())
        print("Waiting for the interleaved VDS file %s to appear on the file system..." %(interleaved_fpath.strip()))
        interleaved_accessible = wait_for_file(interleaved_fpath.strip())
        summary_msg = 'success' if interleaved_accessible else 'failed'
        print("Finished waiting for the interleaved VDS file %s to appear on the file system (%s)!" %(interleaved_fpath.strip(), summary_msg))
        
        if interleaved_accessible:
            # Check output file exists
            if os.path.isfile(gapfilled_filename.strip()) == 0:
                cmd = cmd + " &"
                os.system(cmd)
            else:
                print("WARNING: gap-filled VDS file %s already exists!" %(gapfilled_filename))
        
        #OSCommandRunner.runNoWait(["python /dls_sw/i13-1/software/gda/config/scripts/excalibur_odin_vds_gen.py", self.outdirpath, "-f", excalibur_<scan number>_r0.h5,... excalibur_<scan number>_r<rank>.h5, "-t", <data type>, "-s", <scan number>], OSCommandRunner.LOGOPTION.ALWAYS, None)
        

print("INFO: Creating excalibur_odin_xgraph object in GDA...")
excalibur_odin_xgraph=ExcaliburOdinXgraph()
print("INFO: Finished creating excalibur_odin_xgraph object in GDA!")

# take care of these additional PV from Alan + CreateDirectory
# run vds-gen (twice)
# use try/except
# monitor dropped frames and alert the user at scan end (on a separate thread)?
# camonitor to detect the start of acquire (or GDA observer)? 
# implement the primed functionality
# add Nexus scan file (with a link to the vds HDF file)
# implement all that in Java?
# put files in a scan sub-director?
# use BL13J-EA-EXCBR-02:OD:DataType




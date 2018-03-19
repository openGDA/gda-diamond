import time import sleep

from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gda.jython import InterfaceProvider

# in alphabetical order

CAM_ACQUIRE_START = 1
CAM_ACQUIRE_STOP = 0

HDF5_CAPTURE_START = 1
HDF5_CAPTURE_STOP = 0

# keys
CAM_ACQUIRE = "cam_acquire"
CAM_ACQUIRE_PERIOD = "cam_acquire_period"
CAM_ACQUIRE_PERIOD_RBV = "cam_acquire_period_rbv"
CAM_ACQUIRE_TIME = "cam_acquire_time"
CAM_ACQUIRE_TIME_RBV = "cam_acquire_time_rbv"

# dictionary with (key, value) pairs
PV_SUFFIX = {
		CAM_ACQUIRE: 		"Acquire",
		CAM_ACQUIRE_PERIOD: 	"AcquirePeriod",
		CAM_ACQUIRE_PERIOD_RBV:	"AcquirePeriod_RBV",
                CAM_ACQUIRE_TIME: 	"AcquireTime",
		CAM_ACQUIRE_TIME_RBV:	"AcquireTime_RBV",
                
		CAM_AUTO_BREF: 		"AutoBref",
		CAM_AUTO_RESTART: 	"AutoRestart",
		CAM_AUTO_SAVE: 		"AutoSave",
		CAM_AUX_PIN_MODE: 	"AuxPinMode",

		CAM_CINE_COUNT_RBV: 	"CineCount_RBV",
		CAM_CINE_TEMPLATE: 	"C%d"
		CAM_CSR_COUNT_RBV: 	"CSRCount_RBV",

		CAM_EXT_SYNC_TYPE: 	"ExtSyncType",
		CAM_FIRST_FRAME_RBV: 	"FirstFrame_RBV",

		CAM_LAST_FRAME_RBV: 	"LastFrame_RBV",

		CAM_MAX_FRAME_COUNT: 	"MaxFrameCount_RBV",

		CAM_PARTITION_CINES: 	"PartitionCines",
		CAM_PERFORM_CSR: 	"PerformCSR",
		CAM_POST_TRIG_FRAMES: 	"PostTrigFrames",
		CAM_PREVIEW: 		"Preview",

		CAM_READY_SIGNAL: 	"ReadySignal",
		CAM_RECORD: 		"Record",
		CAM_RECORD_COUNT_RBV:	"RecordCount_RBV",
		CAM_RECORD_END:		"RecordEnd",
		CAM_RECORD_START:	"RecordStart",

		CAM_SELECTED_CINE:	"SelectedCine",


		HDF5_AUTO_INCREMENT:	"AutoIncrement",
		HDF5_CAPTURE:		"Capture",
		HDF5_NUM_CAPTURED_RBV:	"NumCaptured_RBV",
		HDF5_FILE_NAME:		"FileName",
		HDF5_FILE_NUMBER:	"FileNumber",
		HDF5_FILE_PATH:		"FilePath",
		HDF5_FILE_TEMPLATE:	"FileTemplate",
		HDF5_FILE_WRITE_MODE:	"FileWriteMode",
		HDF5_NUM_CAPTURE:	"NumCapture",
		
		
}

def get_pvs(pv_prefix):
	pvs = {}
	for k, v in PV_SUFFIX.iteritems():
		pvs.update({k: pv_prefix + v}) 
	return pvs


class Miro():
	def __init__(self, pv_prefix="BL12I-EA-DET-20:CAM:", exposure_time_max_sec=1.0/24.0):
		self.pv_prefix = pv_prefix
		self.exposure_time_max_sec = exposure_time_max_sec
		self.pvs = get_pvs(pv_prefix)
		self.ca = CAClient()
		self.cine_num = 1
        

	def sanity_check(self, nframes_post_trigger, exposure_time_sec, acq_period_sec)
		if exposure_time_sec > self.exposure_time_max_sec:
			print "Requested exposure time of %.3f s is larger than the camera's maximum exposure time of %.3f s: forcing input exposure time to %.3f!" %(exposure_time_sec, self.exposure_time_max_sec, self.exposure_time_max_sec)
			exposure_time_sec = self.exposure_time_max_sec

		if acq_period_sec < exposure_time_sec:
			print "Requested acq period of %.3f s is smaller than the exposure time of %.3f s: forcing input acq period to %.3f!" %(acq_period_sec, exposure_time_sec, exposure_time_sec)
			acq_period_sec = exposure_time_sec

		if nframes_post_trigger < 1:
			print "Requested number of frames to record post trigger %d must not be less than 1: forcing input nframes to 1!" %(nframes_post_trigger)
			nframes_post_trigger = 1
	
	def set_data_collection_params(nframes_post_trigger, exposure_time_sec, acq_period_sec):
		pass

	def prepare_before_collection(self, nframes_post_trigger, exposure_time_sec, acq_period_sec):		
		self._set_auto_save_cine(0)
		self._set_auto_restart_acquisition(0)
		self._set_auto_back_reference(0)

		self._set_external_sync(0)
		self._set_trigger_edge(1)
		self._set_ready_signal(0)
		self._set_aux_pin_mod(1)

		self.set_data_collection_params(nframes_post_trigger, exposure_time_sec, acq_period_sec)

		self._set_partition(1)
		self._set_save_to_cine_partition(1)
		self._black_ref()
		self._set_miro_hdf_path(savefolderpath)

		
	def collect_data(self, nframes_post_trigger, exposure_time_sec, frame_rate_hz, download_option, cine_num=1, final_sleep_sec=1.):
		acq_period = 1.0/frame_rate_hz
		self.sanity_check(nframes_post_trigger, exposure_time_sec, acq_period_sec, download_option)
		self.prepare_before_collection(nframes_post_trigger, exposure_time_sec, acq_period_sec)
		
		self._start_preview()
		print "Waiting for a trigger to start recording %d frames...\n" %(nframes_post_trigger)
		self._acquire()
		self._wait_for_trigger()
		self._stop_preview()
		sleep(final_sleep_sec)

		(first_frame_idx, last_frame_idx) = self._get_frames_to_download(download_option, 1) #cine_num
		if first_frame_idx!=last_frame_idx:
    			self._download_RAM_to_hdf(1, first_frame_idx, last_frame_idx)
		else:
			print "--------------------------------------------------------"
			print "---------You chose to download data manually------------"
			print "--------------------------------------------------------"
			print "***!!! Please download before running a new scan !!!***"
			print "--------------------------------------------------------\n"

	def _get_frames_to_download(download_option, cine_num):
		cinePVbase = "BL12I-EA-DET-20:CAM:C"+str(int(cinenumpar))+":"
		max_frame_count = caget("BL12I-EA-DET-20:CAM:MaxFrameCount_RBV")
		if download_option==0:
			first_frame_idx = int(caget(cinePVbase + "FirstFrame_RBV"))
			last_frame_idx = int(caget(cinePVbase + "LastFrame_RBV"))
		if download_option==1:
			first_frame_idx = 0
			last_frame_idx = int(caget(cinePVbase + "LastFrame_RBV"))
		if download_option==-1:
			first_frame_idx = int(caget(cinePVbase + "FirstFrame_RBV"))
			last_frame_idx = 0
		if download_option==2:
			first_frame_idx = 0
			last_frame_idx = 0    
		return first_frame_idx, last_frame_idx
        

miro_test_obj=Miro()


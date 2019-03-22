from time import sleep
import os

from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gda.jython import InterfaceProvider

from i12utilities import wd
from gda.data import NumTracker
i12NumTracker = NumTracker('i12')
from gda.jython.commands.Input import requestInput

class UserHasQuit(Exception):
	pass

def test():
	user_input = requestInput('Please adjust the -Sample Y-. Is this done? (y/n)')
	if user_input == "y":
		print "got y!", user_input, repr(user_input)
	else:
		print "got not y!", user_input, repr(user_input)

def test1():
	while 1:
		user_input = requestInput('Please adjust the -Sample Y-. Is this done? (y/n)')
		if user_input == "y":
			print "got y!", user_input, repr(user_input)
			break
		elif user_input == "n":
			print "got n!", user_input, repr(user_input)
			break
	



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

CAM_AUTO_BREF = "cam_AutoBref"
CAM_AUTO_RESTART = "cam_AutoRestart"
CAM_AUTO_SAVE = "cam_AutoSave"
CAM_AUX_PIN_MODE = "cam_AuxPinMode"
		
CAM_CINE_COUNT_RBV = "cam_CineCount_RBV"
CAM_CINE_TEMPLATE = "cam_C%d"
CAM_CSR_COUNT_RBV = "cam_CSRCount_RBV"
		
CAM_EXT_SYNC_TYPE = "cam_ExtSyncType"
CAM_FIRST_FRAME_RBV = "cam_FirstFrame_RBV"
		
CAM_LAST_FRAME_RBV = "cam_LastFrame_RBV"
		
CAM_MAX_FRAME_COUNT = "cam_MaxFrameCount_RBV"
		
CAM_PARTITION_CINES = "cam_PartitionCines"
CAM_PERFORM_CSR = "cam_PerformCSR",
CAM_POST_TRIG_FRAMES = "cam_PostTrigFrames"
CAM_PREVIEW = "cam_Preview"
		
CAM_READY_SIGNAL = "cam_ReadySignal"
CAM_RECORD = "cam_Record"
CAM_RECORD_COUNT_RBV = "cam_RecordCount_RBV"
CAM_RECORD_END = "cam_RecordEnd"
CAM_RECORD_START = "cam_RecordStart"
		
CAM_SELECTED_CINE = "cam_SelectedCine"
		
		
HDF5_AUTO_INCREMENT = "hdf5_AutoIncrement"
HDF5_CAPTURE = "hdf5_Capture"
HDF5_NUM_CAPTURED_RBV = "hdf5_NumCaptured_RBV"
HDF5_FILE_NAME = "hdf5_FileName"
HDF5_FILE_NUMBER = "hdf5_FileNumber"
HDF5_FILE_PATH = "hdf5_FilePath"
HDF5_FILE_TEMPLATE = "hdf5_FileTemplate"
HDF5_FILE_WRITE_MODE = "hdf5_FileWriteMode"
HDF5_NUM_CAPTURE = "hdf5_NumCapture"

# dictionary with (key, value) pairs
PV_SUFFIX = {
		CAM_ACQUIRE: 			"Acquire",
		CAM_ACQUIRE_PERIOD: 	"AcquirePeriod",
		CAM_ACQUIRE_PERIOD_RBV:	"AcquirePeriod_RBV",
		CAM_ACQUIRE_TIME: 		"AcquireTime",
		CAM_ACQUIRE_TIME_RBV:	"AcquireTime_RBV",
		
		CAM_AUTO_BREF: 		"AutoBref",
		CAM_AUTO_RESTART: 	"AutoRestart",
		CAM_AUTO_SAVE: 		"AutoSave",
		CAM_AUX_PIN_MODE: 	"AuxPinMode",
		
		CAM_CINE_COUNT_RBV: "CineCount_RBV",
		CAM_CINE_TEMPLATE: 	"C%d",
		CAM_CSR_COUNT_RBV: 	"CSRCount_RBV",
		
		CAM_EXT_SYNC_TYPE: 		"ExtSyncType",
		CAM_FIRST_FRAME_RBV: 	"FirstFrame_RBV",
		
		CAM_LAST_FRAME_RBV: 	"LastFrame_RBV",
		
		CAM_MAX_FRAME_COUNT: 	"MaxFrameCount_RBV",
		
		CAM_PARTITION_CINES: 	"PartitionCines",
		CAM_PERFORM_CSR: 		"PerformCSR",
		CAM_POST_TRIG_FRAMES: 	"PostTrigFrames",
		CAM_PREVIEW: 			"Preview",
		
		CAM_READY_SIGNAL: 		"ReadySignal",
		CAM_RECORD: 			"Record",
		CAM_RECORD_COUNT_RBV:	"RecordCount_RBV",
		CAM_RECORD_END:			"RecordEnd",
		CAM_RECORD_START:		"RecordStart",
		
		CAM_SELECTED_CINE:		"SelectedCine",
		
		
		HDF5_AUTO_INCREMENT:	"AutoIncrement",
		HDF5_CAPTURE:			"Capture",
		HDF5_NUM_CAPTURED_RBV:	"NumCaptured_RBV",
		HDF5_FILE_NAME:			"FileName",
		HDF5_FILE_NUMBER:		"FileNumber",
		HDF5_FILE_PATH:			"FilePath",
		HDF5_FILE_TEMPLATE:		"FileTemplate",
		HDF5_FILE_WRITE_MODE:	"FileWriteMode",
		HDF5_NUM_CAPTURE:		"NumCapture",
}

def get_pvs(pv_prefix):
	pvs = {}
	for k, v in PV_SUFFIX.iteritems():
		pvs.update({k: pv_prefix + v})
	return pvs


class MiroXgraph():
	def __init__(self, pv_prefix="BL12I-EA-DET-20:CAM:", exposure_time_max_sec=1.0/24.0):
		self.pv_prefix = pv_prefix
		self.exposure_time_max_sec = exposure_time_max_sec
		self.frame_rate_hz = None
		self.pvs = get_pvs(pv_prefix)
		self.ca = CAClient()
		self.cine_num = 1
		self.filename_prefix_hdf = "miro_projections"
		self.file_template_hdf = "%s%s_%05d.hdf"
		self.hdfpath = None
		self.outdirpath = None
		self.scan_number = None
		self.download_time_max_sec = 15*60
		self.download_options_dct = {-1: "PRE-trigger frames only", 0: "PRE- & POST-trigger frames", 1: "POST-trigger frames only", 2: "MANUAL selection of frames in EPICS"}

	def sanity_check(self, nframes_post_trigger, exposure_time_sec, acq_period_sec, download_option):
		#overhead_sec = 20*10e-6 # Exposure time is less 20 microsecond of overhead
		overhead_sec = 2*10e-6
		if exposure_time_sec > self.exposure_time_max_sec:
			print("WARNING: Requested exposure time of %s s is larger than the MAX exposure time:\n\t setting the exposure time to the MAX allowable exposure time of %s s instead!" %(exposure_time_sec, self.exposure_time_max_sec))
			exposure_time_sec = self.exposure_time_max_sec
	
		exposure_time_sec_tmp = exposure_time_sec
		if acq_period_sec <= exposure_time_sec+overhead_sec:
			#print "Acquisition period of %.3f s is smaller than the exposure time (%s s) + overhead: using the value of the exposure time of %.3f instead!" %(acq_period_sec, exposure_time_sec)
			#acq_period_sec = exposure_time_sec
			exposure_time_sec = acq_period_sec - overhead_sec
			print("WARNING: Computed acquisition period of %s s is smaller or equal to the exposure time (%s s) + overhead (%s us):\n\t setting the exposure time to an adjusted value of %s to allow for the requested frame rate of %s Hz!" %(acq_period_sec, exposure_time_sec_tmp, overhead_sec, exposure_time_sec, self.frame_rate_hz))
	
		if nframes_post_trigger < 1:
			print("WARNING: Number of frames to be recorded POST trigger %d must not be less than 1:\n\t using the MIN value of 1 instead!" %(nframes_post_trigger))
			nframes_post_trigger = 1
		
		frame_count_max = int(caget("BL12I-EA-DET-20:CAM:MaxFrameCount_RBV"))
		if nframes_post_trigger > frame_count_max:
			print("WARNING: Number of frames to be recorded POST trigger %d must not exceed the MAX allowable frame count:\n\t using the current MAX allowable frame count of %d instead!" %(nframes_post_trigger, frame_count_max))
			nframes_post_trigger = frame_count_max
			
		if not download_option in (-1, 0, 1, 2):
			print "Download option %d is NOT supported!" %(download_option)
			msg = "Available download options:\n"
			msg += "-1 (automatic download of all PRE-trigger frames only)\n"
			msg += "0 (automatic download of all PRE- and POST-trigger frames)\n"
			msg += "1 (automatic download of all POST-trigger frames only)\n"
			msg += "2 (manual download of hand-picked frames directly in EPICS)"
			print msg
			#download_option = 1			#kw ???
	
	def _get_file_path_and_number(self):
		pass
		
	def set_data_collection_params(self, nframes_post_trigger, exposure_time_sec, acq_period_sec):
		#self.sanity_check(nframes_post_trigger, exposure_time_sec, acq_period_sec)
		caput_wait("BL12I-EA-DET-20:CAM:AcquirePeriod", acq_period_sec, timeout=10)
		caput_wait("BL12I-EA-DET-20:CAM:AcquireTime", exposure_time_sec, timeout=10)
		caput_wait("BL12I-EA-DET-20:CAM:PostTrigFrames", nframes_post_trigger, timeout=10)
		sleep(1.0)
		exposure_time_sec_eff = caget("BL12I-EA-DET-20:CAM:AcquireTime_RBV")
		acq_period_sec_eff = caget("BL12I-EA-DET-20:CAM:AcquirePeriod_RBV")
		print("Effective exposure time: %s s" %(exposure_time_sec_eff))
		print("Effective acquisition period: %s s (for the requested frame rate of %s Hz)" %(acq_period_sec_eff, self.frame_rate_hz))
		return nframes_post_trigger, exposure_time_sec_eff, acq_period_sec_eff		#order?
		

	def prepare_before_collection(self, nframes_post_trigger, exposure_time_sec, acq_period_sec, black_ref=True): #, savefolderpath):
		self._set_auto_save_cine(0)
		self._set_auto_restart_acquisition(0)
		self._set_auto_back_reference(0)

		self._set_external_sync(0)
		self._set_trigger_edge(1)
		self._set_ready_signal(0)
		self._set_aux_pin_mod(1)

		self.set_data_collection_params(nframes_post_trigger, exposure_time_sec, acq_period_sec)

		#self._set_partition(1)					# commented out on advice from Robert 11 Feb 2019
		#self._set_save_to_cine_partition(1)	# commented out on advice from Robert 11 Feb 2019
		
		if black_ref:
			self._perform_black_ref()
		else:
			print("User opted for NOT performing Current Session Reference (black reference)!")
		#self._set_miro_hdf_path(savefolderpath)

		
	def collect_data(self, nframes_post_trigger, exposure_time_sec, frame_rate_hz, download_option, black_ref=True, interactive_run=False, cine_num=1, pre_download_sleep_sec=1.0, nxs=False):
		"""
		nframes_post_trigger: the total number of frames to be collected after the trigger is received by the camera
		exposure_time_sec: exposure time in seconds
		frame_rate_hz: frame rate in Hz
		download_option: 
			-1 - automatic download of all PRE-trigger frames only
			0 - automatic download of all PRE- and POST-trigger frames
			1 - automatic download of all POST-trigger frames only
			2 - manual download of hand-picked frames directly in EPICS
		black_ref: True or False to indicate if a black reference image is to be collected beforehand; default=True
		interactive_run: True or False to indicate if the Miro camera should wait for a user-provided initial trigger 
			(generated by the user's equipment or by the user manually clicking on the Trigger button provided in Miro's Cam plug-in in EPICS) 
			before starting to record images; default=False
		cine_num: the integer identifier of the Cine partition from which the recorded images are to be downloaded
			at the end of the entire data-acquisition process; default=1
		pre_download_sleep_sec: default=1.0
		"""
		self.frame_rate_hz = frame_rate_hz
		acq_period_sec = 1.0/frame_rate_hz
		self.sanity_check(nframes_post_trigger, exposure_time_sec, acq_period_sec, download_option)
		self.prepare_before_collection(nframes_post_trigger, exposure_time_sec, acq_period_sec, black_ref)
		
		self.scan_number = i12NumTracker.getCurrentFileNumber() + 1
		i12NumTracker.incrementNumber()
		print "scan_number = %d" %(self.scan_number)
		self.outdirpath = wd()
		#print "outdirpath = %s" %(self.outdirpath)
		self.hdfpath = self._set_hdf_writer(self.outdirpath, self.scan_number)	# remove args?
		if nxs:
			try:
				self._create_nexus_scan_file("miro_xgraph",exposure_time_sec,self.scan_number,self.hdfpath,self.outdirpath)
			except Exception, e:
				print("Error creating Nexus scan file: %s" %(str(e)))
		else:
			print("User opted for NOT creating Nexus scan file!")
		
		self._start_preview()
		self._start_acquire()
		print("Waiting for a user trigger to record %d frames after the trigger...\n" %(nframes_post_trigger))
		self._wait_for_trigger(interactive_run=interactive_run)
		self._stop_preview()
		sleep(pre_download_sleep_sec)
		print("Finished recording the requested %d frames after the trigger!\n" %(nframes_post_trigger))

		(first_frame_idx, last_frame_idx) = self._get_frames_to_download(download_option, cine_num) #cine_num
		if first_frame_idx!=last_frame_idx:
			print("User opted for download option %d (%s) with frame indices from %d to %d:" %(download_option,self.download_options_dct[download_option], first_frame_idx, last_frame_idx))
			self._download_ram_to_hdf(cine_num, first_frame_idx, last_frame_idx)
		else:
			print("User opted for MANUAL download of frames: this task must be completed before the currently stored frames are OVERWRITTEN by any new data!")

	def _get_frames_to_download(self, download_option, cine_num):
		cinePVbase = "BL12I-EA-DET-20:CAM:C"+str(int(cine_num))+":"
		#max_frame_count = caget("BL12I-EA-DET-20:CAM:MaxFrameCount_RBV")	# not used? kw
		if download_option==0:		#ALL
			first_frame_idx = int(caget(cinePVbase + "FirstFrame_RBV"))
			last_frame_idx = int(caget(cinePVbase + "LastFrame_RBV"))
		if download_option==1:		#POST
			first_frame_idx = 0
			last_frame_idx = int(caget(cinePVbase + "LastFrame_RBV"))
		if download_option==-1:		#PRE
			first_frame_idx = int(caget(cinePVbase + "FirstFrame_RBV"))
			last_frame_idx = 0
		if download_option==2:		#MANUAL
			first_frame_idx = 0
			last_frame_idx = 0
		return first_frame_idx, last_frame_idx

	def _start_preview(self):
		caput_wait("BL12I-EA-DET-20:CAM:Preview", 1, timeout=10)
		
	def _stop_preview(self):
		caput_wait("BL12I-EA-DET-20:CAM:Preview", 0, timeout=10)
		
	def _set_auto_save_cine(self, option_num):
		caput_wait("BL12I-EA-DET-20:CAM:AutoSave", option_num, timeout=10)

	def _set_auto_restart_acquisition(self,option_num):
		caput_wait("BL12I-EA-DET-20:CAM:AutoRestart", option_num, timeout=10)

	def _set_auto_back_reference(self,option_num):
		caput_wait("BL12I-EA-DET-20:CAM:AutoBref", option_num, timeout=10)
    
	def _set_external_sync(self,option_num):
		caput_wait("BL12I-EA-DET-20:CAM:ExtSyncType", option_num, timeout=10)

	def _set_trigger_edge(self,option_num):
		caput_wait("BL12I-EA-DET-20:CAM:TriggerEdge", option_num, timeout=10)

	def _set_ready_signal(self,option_num):
		caput_wait("BL12I-EA-DET-20:CAM:ReadySignal", option_num, timeout=10)

	def _set_aux_pin_mod(self,option_num):
		caput_wait("BL12I-EA-DET-20:CAM:AuxPinMode", option_num, timeout=10)
	
	def _set_partition(self, cine_num):
		caput_wait("BL12I-EA-DET-20:CAM:PartitionCines", cine_num, timeout=10)

	def _set_save_to_cine_partition(self,cine_num):
		caput_wait("BL12I-EA-DET-20:CAM:SelectedCine", cine_num-1, timeout=10)

	def _start_acquire(self):
		#caput("BL12I-EA-DET-20:CAM:Acquire", 1, wait = True, timeout = None)
		caput("BL12I-EA-DET-20:CAM:Acquire", 1) # User may see funny image on video signal if use this option (if caput_wait? KW)
		print "Started acquiring frames before the trigger!"
	
	def _stop_acquire(self):
		caput("BL12I-EA-DET-20:CAM:Acquire", 0)
		print "Acquire stopped!"
		
	def _wait_for_trigger(self, interactive_run=False):
		
		if interactive_run:
			while 1:
				got = requestInput("Press Enter on the keyboard to send a single trigger or type q (followed by Enter) to quit...")
				#print got, repr(got)
				if eval(repr(got))=='':
					caput("BL12I-EA-DET-20:CAM:SendSoftwareTrigger", 1)
					print "Trigger sent!"
					if got=='': "This is also OK!"
					break
				elif got in ('q', 'quit'):
					print "Quitting!"
					self._stop_acquire()
					raise UserHasQuit()
		else:
			print "User opted for external or manual triggering directly in EPICS!"
		
		check = True
		i = 0
		while check:
			#sleep(1)	# kw added and then commented out, but it may be a good idea to have with 0.1 s?
			if int(caget("BL12I-EA-DET-20:CAM:Acquire"))==0:
				check = False
				print "Trigger received!"
			else:
				#if i==0: # i % 10000 and i < 10000 * 3 + 1
				#print i
				every = 500
				if (i % every == 0) and i < every * 3 + 1:
					print "...still waiting for the trigger!"
				i += 1
				if i % every == 0:
					print i
	
	def _perform_black_ref(self):
		CSRcheck = 1
		caput_wait("BL12I-EA-DET-20:CAM:PerformCSR", 1, timeout=10)
		print "Performing Current Session Reference (black reference)..."
		while (CSRcheck !=0):
			CSRcheck = int(caget("BL12I-EA-DET-20:CAM:CSRCount_RBV"))
			sleep(0.5)
		print "Finished performing Current Session Reference (black reference)!"

	def _make_data_folder(self,hdfpath):
		if not (os.access (hdfpath, os.F_OK)):
			os.makedirs(hdfpath)
		if not (os.access (hdfpath, os.F_OK)):
			print ("!!! Could not create folder %s",hdfpath)
			sys.exit(0)

	def _set_hdf_writer(self, outdirpath, filenumber):	## add filename_prefix_hdf and template? change to configure?
		caput_wait("BL12I-EA-DET-20:HDF5:Capture", 0) # Stop previous hdf streaming if the script is interrupted
		caput_wait("BL12I-EA-DET-20:HDF5:FileNumber", filenumber, timeout=10)	#was 0
		caput_wait("BL12I-EA-DET-20:HDF5:AutoIncrement", 0, timeout=10)			#was 1

		caputStringAsWaveform("BL12I-EA-DET-20:HDF5:FileTemplate","%s%s_%05d.hdf") #, timeout=10)
		caputStringAsWaveform("BL12I-EA-DET-20:HDF5:FileName", self.filename_prefix_hdf) #, timeout=10)
		caputStringAsWaveform("BL12I-EA-DET-20:HDF5:FilePath", outdirpath) #, timeout=10)
	
	#caput_wait("BL12I-EA-DET-20:HDF5:FileTemplate","%s%s_%05d.hdf", datatype = DBR_CHAR_STR, wait = True)
	#caput_wait("BL12I-EA-DET-20:HDF5:FileName", "Miro_projections", datatype = DBR_CHAR_STR, wait = True)
	#caput_wait("BL12I-EA-DET-20:HDF5:FilePath", hdfpath, datatype = DBR_CHAR_STR, wait = True) 
		return "%s%s_%05d.hdf" %(outdirpath, self.filename_prefix_hdf, filenumber)
		
	def _download_ram_to_hdf(self, cine_num, first_frame_idx, last_frame_idx):
		cinePVbase = "BL12I-EA-DET-20:CAM:C"+str(int(cine_num))+":"
		first_frame_avail = int(caget(cinePVbase + "FirstFrame_RBV"))
		last_frame_avail = int(caget(cinePVbase + "LastFrame_RBV"))
		frames_avail = range(first_frame_avail,last_frame_avail+1)
		nframes_requested = last_frame_idx - first_frame_idx + 1
		if (first_frame_idx not in frames_avail) or (last_frame_idx not in frames_avail):
			print "ERROR: download range from index %s to %s is NOT valid for the recorded range from index %s to %s" % (first_frame_idx, last_frame_idx, first_frame_avail, last_frame_avail)
			print "Try MANUAL download in EPICS!"
			return
		
		# setup hdf plugin in AreaDetector
		caput_wait("BL12I-EA-DET-20:CAM:RecordStart", first_frame_idx, timeout=10) #wait = True)
		caput_wait("BL12I-EA-DET-20:CAM:RecordEnd", last_frame_idx, timeout=10) #wait = True)
		caput_wait("BL12I-EA-DET-20:HDF5:NumCapture", nframes_requested, timeout=10) #wait = True)
		caput_wait("BL12I-EA-DET-20:HDF5:FileWriteMode",2, timeout=10) #wait = True)
		caput("BL12I-EA-DET-20:HDF5:Capture", 1)
		
		# Download
		outcome = 'UNKNOWN'
		print("\t Downloading the desired frames and saving them to HDF5 file...\n")
		print("\t *******************************************************************************")
		print("\t WARNING: Do NOT click on the Live Preview buttons when download is in progress!")
		print("\t\t\t (maximum allowable download time = %s s)" %(self.download_time_max_sec))
		print("\t *******************************************************************************\n")
		caput("BL12I-EA-DET-20:CAM:Record", 1)
		
		# monitor the progress of download process
		ndots_max = 12
		ndots = 0
		count = 0
		#wait_time_sec_max = self.download_time_max_sec # maximum download time is 15 minutes
		wait_time_delta_sec = 1.0
		wait_time_elapsed_sec = 0
		try:
			while (wait_time_elapsed_sec < self.download_time_max_sec):
				download_count = int(caget("BL12I-EA-DET-20:CAM:RecordCount_RBV"))
				nframes_captured = int(caget("BL12I-EA-DET-20:HDF5:NumCaptured_RBV"))
				if (nframes_captured==nframes_requested) and (download_count==0):
					print "\t Finished downloading the desired frames and saving them to HDF5 file %s!" %(os.path.join(self.outdirpath, (self.filename_prefix_hdf+"_%d.hdf") %(self.scan_number)))
					caput("BL12I-EA-DET-20:HDF5:Capture", 0) #wait = True)
					outcome = 'SUCCESS'
					break
				sleep(wait_time_delta_sec)
				wait_time_elapsed_sec += wait_time_delta_sec
				if (wait_time_elapsed_sec >= self.download_time_max_sec):
					print("\n\t WARNING: Download timeout - check in EPICS for any mismatch of the number of frames expected to be downloaded!")
					caput("BL12I-EA-DET-20:HDF5:Capture", 0) #wait = True)
					outcome = 'FAIL (timeout)'
				if count % 10==0:
					if ndots % ndots_max!=0:
						print "\t .",
						ndots += 1
					else:
						print "\n"
						ndots = 1
				count += 1
		except Exception, e:
			outcome = 'FAIL (%s)' %(str(e))
			print("Error in download: %s" %(str(e)))
		
		print("\t Download outcome: %s!\n" %(outcome))
		#return
		print "All done - bye!"

	def _create_nexus_scan_file(self, detector_name, exptime, scan_number, hdfpath, outdirpath=None, cmd=None, npts=1):
		from gda.data.scan.datawriter.DefaultDataWriterFactory import createDataWriterFromFactory
		from gda.scan.ScanInformation import ScanInformationBuilder
		from gda.scan import ScanDataPoint
		from gda.device.scannable import DummyScannable
		from dummy_utils import dum_collstrat, dum_det
		
		print("create_nexus_scan_file: outdirpath = %s" %(outdirpath))
		dw = createDataWriterFromFactory()
		
		if outdirpath is None:
			nxspath = os.path.join(gda.util.VisitPath.getVisitPath(),"%d.nxs" %(scan_number))
		else:
			nxspath = os.path.join(outdirpath,"%d.nxs" %(scan_number))
		
		si = (ScanInformationBuilder()
				.dimensions(npts)
				.scanNumber(scan_number)
				.instrument('i12')
				.filename(nxspath)
				.numberOfPoints(npts)
				.build())
		
		dum_collstrat.collectionTime = exptime
		dum_det.name = detector_name
		dum_det.hdfpath = hdfpath
		dum_det.atScanStart()
		
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
				
				sdp_tmp.setCurrentPointNumber(i)
				dw.addData(sdp_tmp)
		except Exception, e:
			print "Error: %s" %(str(e))
		finally:
			dw.completeCollection()
		return nxspath
	
print("Creating miro_xgraph object in GDA...")
miro_xgraph=MiroXgraph()
print("Finished creating miro_xgraph object in GDA!")

from time import sleep, strftime
import os

import tfg_commands
from epics_scripts.pv_scannable_utils import caput, caget, caputStringAsWaveform

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, e:  # Python >2.5
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class TFG2Frame(object):
    def __init__(self, duration_sec, fps, live_time_sec=0.005):
        self.duration_sec = float(duration_sec)
        self.fps = float(fps)
        self.live_time_sec = float(live_time_sec)
        self.npulses_int = None
        self.dead_time_sec = None
        self.config()
    
    def config(self):
        self.npulses_int = self.calc_npulses_int(self.duration_sec, self.fps)
        self.dead_time_sec = self.calc_dead_time_sec(self.duration_sec, self.npulses_int, self.live_time_sec)

    def calc_npulses_int(self, duration_sec, fps):
        npulses_int = int(duration_sec * fps)
        return npulses_int

    def calc_dead_time_sec(self, duration_sec, npulses_int, live_time_sec):
        dead_time_sec = duration_sec / npulses_int - live_time_sec
        assert(dead_time_sec >= 0.0)
        return dead_time_sec

    def to_string(self):
        print "duration_sec = %.5f" %(self.duration_sec)
        print "fps = %.5f" %(self.fps)
        print "live_time_sec = %.5f" %(self.live_time_sec)
        print "npulses_int = %d" %(self.npulses_int)
        print "dead_time_sec = %.5f" %(self.dead_time_sec)
        

# create individual frames
frm1 = TFG2Frame(duration_sec=10.0, fps=100)
frm2 = TFG2Frame(duration_sec=50.0, fps=40)
frm3 = TFG2Frame(duration_sec=240.0, fps=20)

# create a list of all frames
frm_lst = []
frm_lst.append(frm1)
frm_lst.append(frm2)
frm_lst.append(frm3)

for i, frm in enumerate(frm_lst):
    print "Frame %d:" %(i)
    frm.to_string()


def verify_frames(frm_lst, exposure_sec, pct=0.99):
    for i, frm in enumerate(frm_lst):
        dead_time = frm.dead_time_sec
        live_time = frm.live_time_sec
        exposure_sec_max_exc = (live_time + dead_time)*pct 
        if exposure_sec > exposure_sec_max_exc:
            msg = "Frame %d: the exposure time of %.5f s is too large for live_time = %.5f and dead_time = %.5f (pct = %.5f); it needs to be less than %.5f!" %(i, exposure_sec, live_time, dead_time, pct, exposure_sec_max_exc)
            raise Exception(msg)

# PCO CAM PVs
pco_cam_exposure_pv = "BL13I-EA-DET-01:CAM:AcquireTime"
pco_cam_acq_period_pv = "BL13I-EA-DET-01:CAM:AcquirePeriod"
pco_cam_acquire_pv = "BL13I-EA-DET-01:CAM:Acquire"		# 0 Done; 1 Acquire
pco_cam_num_images_pv = "BL13I-EA-DET-01:CAM:NumImages"
pco_cam_image_mode_pv = "BL13I-EA-DET-01:CAM:ImageMode"		# 0 Single; 1 Multiple; 2 Continuous
pco_cam_trigger_mode_pv = "BL13I-EA-DET-01:CAM:TriggerMode"	# 0 Auto; 1 Soft; 2 Ext + Soft; 3 Ext Pulse; 4 Ext Only

pco_cam_arm_pv = "BL13I-EA-DET-01:CAM:ARM_MODE" 		# 0 Disarmed; 1 Armed

pco_cam_array_counter = "BL13I-EA-DET-01:CAM:ArrayCounter"

# PCO TIFF PVs
pco_tiff_enable = "BL13I-EA-DET-01:TIFF:EnableCallbacks"	# 0 Disable; 1 Enable
pco_tiff_file_path = "BL13I-EA-DET-01:TIFF:FilePath"		# d:\\\\i13\\data\\2017\\mt15461-2\\raw\\92905-pco1-files\\
pco_tiff_file_name = "BL13I-EA-DET-01:TIFF:FileName"
pco_tiff_file_format = "BL13I-EA-DET-01:TIFF:FileTemplate"	# %s%s%05d.tif
pco_tiff_file_number = "BL13I-EA-DET-01:TIFF:FileNumber"
pco_tiff_ncapture = "BL13I-EA-DET-01:TIFF:NumCapture"
pco_tiff_capture_mode = "BL13I-EA-DET-01:TIFF:FileWriteMode"	# 0 Single; 1 Capture; 2 Stream
pco_tiff_capture = "BL13I-EA-DET-01:TIFF:Capture"		# 0 Done; 1 Capture
pco_tiff_auto_incr = "BL13I-EA-DET-01:TIFF:AutoIncrement"	# 0 No; 1 Yes
pco_tiff_auto_save = "BL13I-EA-DET-01:TIFF:AutoSave"		# 0 No; 1 Yes

#BL13I-EA-DET-01:TIFF:TempSuffix
#BL13I-EA-DET-01:CAM:NumExposures	#nexpos_per_img

visit_id = "mt17609-1"
pco_fname_prefix = "pco_"

# %.5f?
# GDA scan number?
# wait n timeout for caput?
# array port?

def config_pco_camera_gen(exposure_sec, nimages, subdir, sleep_sec=2, dry_run=False):	#prepare?
    _fname = config_pco_camera_gen.__name__
    print "Entered fn: %s\n" %(_fname)
    tm_str = time.strftime("%d_%m_%Y-%H%M%S")
    if subdir is None:
        subdir = ""
    if subdir != "":
        subdir += "_"
    subdir_bml = "raw"
    if dry_run:
        subdir_bml = "tmp"
    subdir_tm = subdir + tm_str
    #out_dirpath = "/dls/i13/data/2017/"+visit_id+"/raw/"+subdir_tm
    out_dirpath_real = os.path.join("/dls/i13/data/2017", visit_id, subdir_bml, subdir_tm)
    print("out_dirpath_real = %s" %(out_dirpath_real))
    mkdir_p(out_dirpath_real) 

    out_dirpath = "d:\\\\i13\\data\\2017\\"+visit_id+"\\"+subdir_bml+"\\"+subdir_tm+"\\"	# d:\\\\i13\\data\\2017\\mt17609-1\\raw\\93217-pco1-files\\

    # stop
    caput(pco_cam_acquire_pv, 0)		# Done
    caput(pco_tiff_capture, 0)			# Done

    # disarm
    caput(pco_cam_arm_pv, 0)			# Disarm
    sleep(sleep_sec)				# sleep needed?

    # config CAM
    caput(pco_cam_image_mode_pv, 1)		# Multiple
    #caput(pco_cam_trigger_mode_pv, 4)		# Ext Only	# specific!
    caput(pco_cam_trigger_mode_pv, 1)		# Soft
    caput(pco_cam_exposure_pv, exposure_sec)
    caput(pco_cam_acq_period_pv, 0.0)		# ends up setting the smallest possible acq period for any exposure time
    caput(pco_cam_num_images_pv, nimages)
    caput(pco_cam_array_counter, 0)

    # config TIFF
    caput(pco_tiff_enable, 1)					# Enabled		
    caputStringAsWaveform(pco_tiff_file_path, out_dirpath)	# caputStringAsWaveform
    caputStringAsWaveform(pco_tiff_file_name, pco_fname_prefix)	# caputStringAsWaveform
    caput(pco_tiff_file_number, 0)				# start counting output files from 0
    caput(pco_tiff_auto_incr, 1)				# Yes
    caputStringAsWaveform(pco_tiff_file_format, '%s%s%05d.tif')	# caputStringAsWaveform
    caput(pco_tiff_auto_save, 1)				# Yes
    caput(pco_tiff_capture_mode, 2)				# Stream

    caput(pco_tiff_ncapture, nimages)

    caput(pco_tiff_capture, 1)
    
    # arm
    #caput(pco_cam_arm_pv, 1)			# Armed 	# specific!
    #sleep(sleep_sec) 				# sleep needed?
    print "Leaving fn: %s!" %(_fname)


def config_pco_camera(exposure_sec, nimages, subdir, sleep_sec=2, dry_run=False):
    _fname = config_pco_camera.__name__
    print "Entered fn: %s\n" %(_fname)
    # gen config
    config_pco_camera_gen(exposure_sec, nimages, subdir, sleep_sec, dry_run)
    
    # specific config (CAM)
    caput(pco_cam_trigger_mode_pv, 4)		# Ext Only

    # arm (CAM)
    caput(pco_cam_arm_pv, 1)			# Armed
    sleep(sleep_sec) 				# sleep needed?
    print "Leaving fn: %s!" %(_fname)

def calc_nimages_tot(frm_lst):
    nimages_tot = 0
    for frm in frm_lst:
        npulses = frm.npulses_int
        nimages_tot += npulses
    return nimages_tot



def radio_with_triggers(frm_lst, exposure_sec, subdir="test", ncycles=1, sleep_sec=2, dry_run=True):
    _fname = radio_with_triggers.__name__
    print "Entered fn: %s\n" %(_fname)
    print "nframes = %d" %(len(frm_lst))
    print "exposure_sec = %.5f" %(exposure_sec)
    print "subdir = %s" %(subdir)
    print "ncycles = %d\n" %(ncycles)
    print "sleep_sec = %.5f" %(sleep_sec)
    print "dry_run = %s" %(dry_run)

    verify_frames(frm_lst, exposure_sec)
    nimages_tot = calc_nimages_tot(frm_lst)
    #config_pco_camera(exposure_sec, nimages_tot, subdir, sleep_sec, dry_run)
    
    ncycles_int = int(ncycles)
    tfg = tfg_commands.getTfg()
    cmd1 = "tfg init"
    if dry_run:
        print "cmd1 = %s" %(cmd1)
    else:
        tfg.getDaServer().sendCommand(cmd1)
    cmd2 = "tfg setup-groups cycles %d" %(ncycles_int)
    if dry_run:
        print "cmd2 = %s" %(cmd2)
    else:
        tfg.getDaServer().sendCommand(cmd2)
    for i, frm in enumerate(frm_lst):
        npulses = frm.npulses_int
        dead_time = frm.dead_time_sec
        live_time = frm.live_time_sec
        dead_port = 0
        live_port = 255
        dead_pause = 0
        live_pause = 0
        cmd = "%d %.5f %.5f %d %d %.5f %.5f" %(npulses, dead_time, live_time, dead_port, live_port, dead_pause, live_pause)
        if dry_run:
            print "cmd %d = %s" %(i, cmd)
        else:
            tfg.getDaServer().sendCommand(cmd)
    cmd3 = "-1 0 0 0 0 0 0"
    if dry_run:
        print "cmd3 = %s" %(cmd3)
    else:
        tfg.getDaServer().sendCommand(cmd3)
    cmd4 = "tfg start"
    if dry_run:
        print "cmd4 = %s" %(cmd4)
    else:
        tfg.getDaServer().sendCommand(cmd4)
    print "Leaving fn: %s!" %(_fname)






        


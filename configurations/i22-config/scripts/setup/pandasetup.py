from gdascripts.blueskyHandler import run_plan
from contextlib import contextmanager

from setup.tfgsetup import *
from setup.metadatatweaks import *
from gdaserver import ncddetectors
from gda.jython import InterfaceProvider
from gda.data.metadata import GDAMetadataProvider
from gda.data import NumTracker
from gdascripts.utils import caput, caget

from setup.metadatatweaks import getTitle
from time import sleep
import sys
import threading
from uk.ac.gda.server.ncd.subdetector import NcdTetrammDetector

class PandaIO(object):
    def __init__(self, fast_shutter_1, fast_shutter_2, detectors, optical_camera, fluorescence, user_trigger):
        self.fast_shutter_1=fast_shutter_1
        self.fast_shutter_2=fast_shutter_2
        self.detectors=detectors
        self.optical_camera=optical_camera
        self.fluorescence=fluorescence
        self.user_trigger=user_trigger
    
    def to_binary(self):
        return [int(bool(self.fast_shutter_1)),
                int(bool(self.fast_shutter_2)),
                int(bool(self.detectors)),
                int(bool(self.optical_camera)),
                int(bool(self.fluorescence)),
                int(bool(self.user_trigger)),
                ]

DEFAULT_WAIT_PULSE = PandaIO(fast_shutter_1=True, fast_shutter_2=True, detectors=False, optical_camera=False, fluorescence=False, user_trigger=False)
DEFAULT_RUN_PULSE = PandaIO(fast_shutter_1=True, fast_shutter_2=True, detectors=True, optical_camera=True, fluorescence=True, user_trigger=True)
DEFAULT_RUN_PAUSE = 0 #no pause
DEFAULT_WAIT_PAUSE = 0 #no pause

def pulse_to_binary(pulse):
    if isinstance(pulse, str):
        return [int(c) for c in pulse][:6]
    elif isinstance(pulse, PandaIO):
        return pulse.to_binary()


class ProfileManager():
    def __init__(self):
        self._groups = []


    def addGroup(self, 
                 numberOfFrames, 
                 exposure, 
                 waitTime, 
                 waitPulse=DEFAULT_WAIT_PULSE, 
                 runPulse=DEFAULT_RUN_PULSE, 
                 trigger="IMMEDIATE"):
        self._groups.append({"frames":numberOfFrames, 
                             "trigger": trigger, 
                             "wait_units": "MS", 
                             "run_units": "MS",
                             "wait_time": waitTime,
                             "run_time": exposure,
                             "wait_pulses": pulse_to_binary(waitPulse),
                             "run_pulses": pulse_to_binary(runPulse)
                             })

    def _to_json(self):
        return {"repeats":1, "groups": self._groups}
       
    def __str__(self):
        return_lines = []
        for group in self._groups:
            return_lines.append("  " + str(group["frames"]) + " frames with " + str(group["run_time"]) + "ms exposure, with frames taken every "+ str(group["wait_time"] + group["run_time"]) + "ms.")
        return "\n".join(return_lines)

def _get_current_scan_number():
    beamline = GDAMetadataProvider.getInstance().getMetadataValue("instrument", "gda.instrument", "base");

    runNumber = NumTracker(beamline);
    return runNumber.getCurrentFileNumber()

def _get_bluesky_detectornames_from_ncddetectors():
    
    bs_detectors = []

    for det in ncddetectors.detectors:
        det_name = str(det).lower()
        
        if 'saxs' in det_name:
            bs_detectors.append("saxs")
        if 'waxs' in det_name:
            bs_detectors.append("waxs")
        if 'i0' in det_name:
            bs_detectors.append("i0")
        if 'bsdiodes' in det_name:
            bs_detectors.append("it")
    
    return bs_detectors

@contextmanager
def pandaGroups(quiet=False):
    profile = ProfileManager()
    yield profile
    run_plan("configure_panda_triggering", profile=profile._to_json())
    if not quiet:
        print 'Panda configured to record:'
        print(profile)
        
        beamline = GDAMetadataProvider.getInstance().getMetadataValue("instrument", "gda.instrument", "base");

        scanNumber = _get_current_scan_number() + 1
        nexus_file_location = InterfaceProvider.getPathConstructor().getVisitDirectory() + "/" + beamline + "-" + str(scanNumber) + ".nxs"

        print("Writing data to file (NeXus): " + nexus_file_location)

def frame_progress_bar(): # Need to look at other tetramms depending on what added
    
    basePV = ""
    
    for det in ncddetectors.detectors:
        if isinstance(det, NcdTetrammDetector):
            basePV = det.controller.getBasePv()
            break
    
    if basePV == "":
        print("No tetramms used in detectors, giving up on monitoring the collection")
    
    def collecting():
        return int(caget(basePV + ":DRV:TriggerMode")) == 1 and int(caget(basePV + ":DRV:Acquire")) == 1
    
    while not collecting(): # Timeout
        sleep(0.1)

    while True:
        current = int(caget(basePV + ":HDF5:NumCaptured_RBV"))
        total_frames = int(caget(basePV + ":HDF5:NumCapture_RBV"))
        
        percent = float(current) / total_frames
        filled = int(percent * 50)
    
        bar = '#' * filled
        sys.stdout.write('\r[{:<50}] {:>3}% ({}/{} frames)'.format(
            bar, int(percent * 100), current, total_frames))
        sys.stdout.flush()
    
        if current >= total_frames or not collecting():
            break
    
        sleep(0.1)


def runPanda():
    detectors = _get_bluesky_detectornames_from_ncddetectors()
    run_plan("set_detectors", detectors=detectors)

    # Start the thread
    t = threading.Thread(target=frame_progress_bar)
    t.daemon = True  # optional: exits when main program exits
    t.start()

    run_plan("run_panda_triggering", metadata={"title": getTitle()})
    
    t.join()
    
    print ""
    print("Scan Complete. Scan " + str(_get_current_scan_number()) + " ended successfully")
    print ""

def do_test_compare():
    print("Running with NCD detectors")
    
    with tfgGroups():
        addGroup(4, 400, 800, '00000000', '11111111')
        addGroup(2, 200, 1500, '00000000', '11111111')
    
    staticscan(ncddetectors)
    

    print("Running with Panda")
    
    with pandaGroups() as groups:
        groups.addGroup(4, 400, 800, '0000', '1111')
        groups.addGroup(2, 200, 1500, '0000', '1111')
    runPanda()
    
    print("Done")

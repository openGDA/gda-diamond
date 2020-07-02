"""A short function to allow users to change the detector frame and exposure timings, via TFG, within a script.
numberofframes needs to be an integer, and the timings in msec
"""
from gda.configuration.properties import LocalProperties
from gda.factory import Finder
from gdaserver import operationMode
from contextlib import contextmanager

DEFAULT_RUN_PULSE = int(LocalProperties.get("gda.ncd.defaultRunPulse", "11111111"), 2)
DEFAULT_WAIT_PULSE = int(LocalProperties.get("gda.ncd.defaultWaitPulse", "00000000"), 2)
DEFAULT_RUN_PAUSE = 0 #no pause
DEFAULT_WAIT_PAUSE = 0 #no pause

INVERSION = 'Inversion'
fs_channel = 2

class State:
    LOW = 0
    HIGH = 1

MF = {'Open': State.LOW, 'Close': State.HIGH}
NORMAL = {'Open': State.HIGH, 'Close': State.LOW}

FS_MODES = {'Main Beam': NORMAL, 'Microfocus': MF, 'GISAXS': NORMAL}

timer = Finder.find('Tfg')

_bin_format = '{:08b}'.format

def _normalise_pulse(pulse):
    """Convert pulse given as '11101001' or 0b11101001 to int required by TFG"""
    if isinstance(pulse, int):
        pulse = _bin_format(pulse)
    if len(pulse) != 8:
        raise ValueError('Need 8 bit value for run or wait pulse')
    return int(pulse[::-1], 2)

@contextmanager
def tfgGroups(quiet=False):
    timer.clearFrameSets()
    yield
    timer.loadFrameSets()
    groups = timer.getFramesets()
    if not quiet:
        print 'TFG configured to record:'
        for group in groups:
            if group.frameCount < 2:
                print("  a single frame with a {0.requestedLiveTime}ms exposure and a {0.requestedDeadTime}ms wait time.".format(group))
            else:
                print("  {0.frameCount} frames with {0.requestedLiveTime}ms exposure, with frames taken every {1}ms.".format(group, group.requestedLiveTime + group.requestedDeadTime))

def addGroup(numberOfFrames, exposure, waitTime, waitPulse=DEFAULT_WAIT_PULSE, runPulse=DEFAULT_RUN_PULSE, waitPause=DEFAULT_WAIT_PAUSE, runPause=DEFAULT_RUN_PAUSE):
    """
    set number of frames and exposure times (optional arguments need keywords)

    numberOfFrames: the number of frames to collect
    exposure: the time per frame (in ms)
    waitTime: the dead time between frames (in ms)
    (optional)waitPulse: the trigger pulse for the dead time (defaults to value in properties file)
    (optional)runPulse: the trigger pulse for the live frames (defaults to value in properties file)
    (optional)waitPause: defaults to 0 (no pause)
    (optional)runPause: defaults to 0 (no pause)
    """

    runPulse = _normalise_pulse(runPulse)
    waitPulse = _normalise_pulse(waitPulse)
    timer.addFrameSet(numberOfFrames, waitTime, exposure, waitPulse, runPulse, waitPause, runPause)

def setupTfg(*a, **kw):
    """
    set number of frames and exposure times (optional arguments need keywords)

    numberOfFrames: the number of frames to collect
    exposure: the time per frame (in ms)
    waitTime: the dead time between frames (in ms)
    (optional)waitPulse: the trigger pulse for the dead time (defaults to value in properties file)
    (optional)runPulse: the trigger pulse for the live frames (defaults to value in properties file)
    (optional)waitPause: defaults to 0 (no pause)
    (optional)runPause: defaults to 0 (no pause)
    """
    with tfgGroups():
        addGroup(*a, **kw)

def fs(actionrequested=None):
    """Set the idle position of the fast shutter

    action: 'Open' or 'Close'
    """
    state_map = FS_MODES[operationMode()]
    current_inversion = timer.getAttribute(INVERSION)
    requested = state_map.get(actionrequested, None)
    if requested == State.LOW:
        timer.setAttribute(INVERSION, current_inversion & ~(1 << fs_channel))
    elif requested == State.HIGH:
        timer.setAttribute(INVERSION, current_inversion | (1 << fs_channel))
    else:
        posn = current_inversion >> fs_channel & 1
        if posn == state_map.get('Close'):
            print 'fs: Closed'
        elif posn == state_map.get('Open'):
            print 'fs: Open'

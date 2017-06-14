"""A short function to allow users to change the detector frame and exposure timings, via TFG, within a script.
numberofframes needs to be an integer, and the timings in msec
"""
from gda.configuration.properties import LocalProperties
from gda.factory import Finder

DEFAULT_RUN_PULSE = int(LocalProperties.get("gda.ncd.defaultRunPulse", "11111111"), 2)
DEFAULT_WAIT_PULSE = int(LocalProperties.get("gda.ncd.defaultWaitPulse", "00000000"), 2)
DEFAULT_RUN_PAUSE = 0 #no pause
DEFAULT_WAIT_PAUSE = 0 #no pause

INVERSION = 'Inversion'
fs_channel = 2

timer = Finder.getInstance().find('Tfg')


def setupTfg(numberOfFrames, exposure, waitTime, waitPulse=DEFAULT_WAIT_PULSE, runPulse=DEFAULT_RUN_PULSE, waitPause=DEFAULT_WAIT_PAUSE, runPause=DEFAULT_RUN_PAUSE):
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
    timer.clearFrameSets()
    timer.addFrameSet(numberOfFrames, waitTime, exposure, waitPulse, runPulse, waitPause, runPause)
    timer.loadFrameSets()

    if numberOfFrames < 2:
        print("TFG updated to record a single frame with a " + repr(exposure) + "ms exposure and a " +repr(waitTime) + "ms wait time.")
    else:
        print("TFG updated to record " + repr(numberOfFrames) + " frames of " + repr(exposure) + "ms exposures, with frames taken every " +repr(exposure+waitTime) + "ms.")


def fs(actionrequested=None):
    """Set the idle position of the fast shutter

    action: 'Open' or 'Close'
    """
    current_inversion = timer.getAttribute(INVERSION)
    if actionrequested == "Close":
        timer.setAttribute(INVERSION, current_inversion & ~(1 << fs_channel))
    elif actionrequested == "Open":
        timer.setAttribute(INVERSION, current_inversion | (1 << fs_channel))
    else:
        posn = current_inversion >> fs_channel & 1
        if posn == 0:
            print 'fs: Closed'
        if posn == 1:
            print 'fs: Open'

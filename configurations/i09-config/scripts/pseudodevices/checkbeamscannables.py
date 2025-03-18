'''
Created on 10 Apr 2018

@author: fy65
'''
###############################################################################
###                           Wait for beam device                          ###
###############################################################################
from i09shared.utils.ExceptionLogs import localStation_exception
import sys
from gdaserver import rc, topup_time, feBeamPermit, ew4000, fsi1, fsj1 #@UnresolvedImport
from gdaserver import igap, jgap #@UnresolvedImport
print("-"*100)
try:
    print("Creating checkbeam device composed of 3 conditions:")
    print(" 1. 'checkrc' - checking electron ring current (rc>190mA, 5s wait after beam back,)")
    print("    (change threshold with checkrc.minumumThreshold=12345)")
    print(" 2. 'checktopup_time' - avoid topup period, pause 5 seconds before topup starts, 5s wait after topup finished.")
    print(" 3. 'checkfe' - check Front end shutter, pause when shutter closed, resume 60s after shutter opened.")
    print(" 4. 'checkbeam' - composite scannable of above 3 scannables")
    print(" Checking is done every second!")
    print("")
    from gdascripts.scannable.beamokay import WaitWhileScannableBelowThreshold
    from gda.device.scannable.scannablegroup import ScannableGroup
    from i09shared.pseudodevices.pauseDetectorWhileMonitorBelowThreshold import WaitForScannableState2

    checkrc = WaitWhileScannableBelowThreshold('checkrc', rc, 190, secondsBetweenChecks=1.0, secondsToWaitAfterBeamBackUp=5.0, id1gap=igap, id2gap=jgap)
    checktopup_time = WaitWhileScannableBelowThreshold('checktopup_time', topup_time, 5, secondsBetweenChecks=1.0, secondsToWaitAfterBeamBackUp=5.0)
    checkfe = WaitForScannableState2('checkfe', feBeamPermit, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5.0)
    checkbeam = ScannableGroup('checkbeam', [checkrc, checkfe, checktopup_time])
    checkbeam.configure()

except:
    localStation_exception(sys.exc_info(), "creating checkbeam objects")

try:
    print("Creating checkbeamdetector which monitors:")
    print(" 1. 'topup_time' : 'SR-CS-FILL-01:COUNTDOWN'")
    print(" 2. 'ring_current'  : 'SR-DI-DCCT-01:SIGNAL'")
    print(" 3. 'FE_beam_permit'  : 'FE09I-CS-BEAM-01:STA'")
    print("")
    from pseudodevices.checkBeamDetector import PauseDetectorScannable, PV_MonitorListener_Dictionary
    checkbeamdetector=PauseDetectorScannable("checkbeamdetector", "BL09I-EA-DET-01:CAM:", ew4000, monitoredPvs=PV_MonitorListener_Dictionary)

except:
    localStation_exception(sys.exc_info(), "creating checkbeamdetector object")

try:
    print("Creating 'checkdetector' scannable to be used to pause or resume detector acquisition based on states of:")
    print(" 'checkrc', 'checkfe', and 'checktopup_time'")
    print(" Users can set the times between checks in seconds if required, it is default to 1.0 second.")
    print("")

    from i09shared.pseudodevices.pauseDetectorWhileMonitorBelowThreshold import PauseableDetector, PauseResumeDetectorScannable
    detectorpausecontrol=PauseableDetector("detectorpausecontrol", "BL09I-EA-DET-01:CAM:", fastshutters=[fsi1, fsj1], secondsBetweenFastShutterDetector=2.0)
    checkdetector = PauseResumeDetectorScannable('checkdetector', detectorpausecontrol, checkedDevices={'Electron_Beam':checkrc, 'Front_End_Permit':checkfe, 'Top_up':checktopup_time})

except:
    localStation_exception(sys.exc_info(), "creating checkdetector objects")

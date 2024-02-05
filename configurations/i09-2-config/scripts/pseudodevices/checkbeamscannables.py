'''
Created on 10 Apr 2018

@author: fy65
'''
###############################################################################
###                           Wait for beam device                          ###
###############################################################################
from i09shared.utils.ExceptionLogs import localStation_exception
import sys
from gdaserver import rc, topup_time, feBeamPermit  # @UnresolvedImport

print("-"*100)
try:
    print("Creating checkbeam device composed of 3 conditions:")
    print(" 1. 'checkrc' - checking electron ring current (rc>190mA, 5s wait after beam back,)")
    print("    (change threshold with checkrc.minumumThreshold=12345)")
    print(" 2. 'checktopup_time' - avoid topup period, pause 5 seconds before topup starts, 5s wait after topup finished.")
    print(" 3. 'checkfe' - check Front end shutter, pause when shutter closed, resume 60s after shutter opened.")
    print(" 4. 'checkbeam' - composite scannable of above 3 scannables")
    print(" Checking is done every second!")

    from gdascripts.scannable.beamokay import WaitWhileScannableBelowThreshold, WaitForScannableState
    from gda.device.scannable.scannablegroup import ScannableGroup
    
    checkrc = WaitWhileScannableBelowThreshold('checkrc', rc, 190, secondsBetweenChecks=1.0, secondsToWaitAfterBeamBackUp=5.0) 
    checktopup_time = WaitWhileScannableBelowThreshold('checktopup_time', topup_time, 5, secondsBetweenChecks=1.0, secondsToWaitAfterBeamBackUp=5.0) 
    checkfe = WaitForScannableState('checkfe', feBeamPermit, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5.0) 
    checkbeam = ScannableGroup('checkbeam', [checkrc, checkfe, checktopup_time])
    checkbeam.configure()
    
except:
    localStation_exception(sys.exc_info(), "creating checkbeam objects")


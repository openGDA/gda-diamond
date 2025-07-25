'''
add ID gap scannables to capture and restore ID gaps when beam dump occurrs.

Created on 10 Apr 2018

@author: fy65
'''
###############################################################################
###                           Wait for beam device                          ###
###############################################################################
from utils.ExceptionLogs import localStation_exception
import sys

from gdaserver import ringcurrent, topup_time, feBeamPermit, idgap, idblena, idaccesscontrol  # @UnresolvedImport
print("-"*100)
try:
    print("Creating checkbeam and checkbeamcv devices composed of 3 conditions:")
    print(" 1. 'checkrc', 'checkrc_cv' - checking electron ring current (rc>190mA, 5s wait after beam back,)")
    print("    (change threshold with checkrc.minumumThreshold=12345)")
    print(" 2. 'checktopup_time', 'checktopup_time_cv' - avoid topup period, pause 5 seconds before topup starts, 5s wait after topup finished.")
    print(" 3. 'checkfe', 'checkfe_cv' - check Front end shutter, pause when shutter closed, resume 60s after shutter opened.")
    print(" 4. 'checkid' scannable to be used to pause or resume scan based on ID access control given by main control room")
    print(" 5. 'checkbeam', 'checkbeam_cv'- composite scannable of above 3 scannables")
    print(" Checking is done every second!")
       
    from gdascripts.scannable.beamokay import WaitWhileScannableBelowThreshold, WaitForScannableState
    from gda.device.scannable.scannablegroup import ScannableGroup

    checkrc = WaitWhileScannableBelowThreshold('checkrc', ringcurrent, 190, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5, id1gap = idgap, accesscontrol4id1 = idblena)
    checktopup_time = WaitWhileScannableBelowThreshold('checktopup_time', topup_time, 5, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5)
    checkfe = WaitForScannableState('checkfe', feBeamPermit, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=60)
    checkid = WaitForScannableState('checkid', idaccesscontrol, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5.0, readyStates=['ENABLED'])
    checkbeam = ScannableGroup('checkbeam', [checkrc, checkfe, checktopup_time, checkid])
    checkbeam.configure()

    #beam monitors used for continuous scan
    checkrc_cv = WaitWhileScannableBelowThreshold('checkrc_cv', ringcurrent, 190, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5, id1gap = idgap, accesscontrol4id1 = idblena)
    checkrc_cv.setOperatingContinuously(True)
    checktopup_time_cv = WaitWhileScannableBelowThreshold('checktopup_time_cv', topup_time, 5, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5)
    checktopup_time_cv.setOperatingContinuously(True)
    checkfe_cv = WaitForScannableState('checkfe_cv', feBeamPermit, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=60)
    checkfe_cv.setOperatingContinuously(True)
    checkid_cv = WaitForScannableState('checkid_cv', idaccesscontrol, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5.0, readyStates=['ENABLED'])
    checkid_cv.setOperatingContinuously(True)
    checkbeam_cv = ScannableGroup('checkbeam_cv', [checkrc_cv, checkfe_cv, checktopup_time_cv, checkid_cv])
    checkbeam_cv.configure()
except:
    localStation_exception(sys.exc_info(), "creating checkbeam objects")

try:
    print("Adding checkbeamcv device (add to cvscan to get checkbeam functionality)")

    from gda.device.scannable import PassthroughScannableDecorator
    
    class ZiePassthroughScannableDecorator(PassthroughScannableDecorator):

        def __init__(self, delegate):
            PassthroughScannableDecorator.__init__(self, delegate)  # @UndefinedVariable
    
        def getInputNames(self): 
            return []
    
        def getExtraNames(self): 
            return []
    
        def getOutputFormat(self):
            return []
    
        def getPosition(self):
            return None

    checkbeamcv = ZiePassthroughScannableDecorator(checkbeam_cv)
except:
    localStation_exception(sys.exc_info(), "creating checkbeamcv object")
   
    
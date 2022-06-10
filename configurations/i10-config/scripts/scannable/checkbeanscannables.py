'''
Created on 10 Apr 2018

@author: fy65
'''
###############################################################################
###                           Wait for beam device                          ###
###############################################################################
from utils.ExceptionLogs import localStation_exception
import sys
from gdaserver import rc, topup_time, frontend  # @UnresolvedImport
print("-"*100)
try:
    print("Creating checkbeam and checkbeamcv devices composed of 3 conditions:")
    print(" 1. 'checkrc', 'checkrc_cv' - checking electron ring current (rc>190mA, 5s wait after beam back,)")
    print("    (change threshold with checkrc.minumumThreshold=12345)")
    print(" 2. 'checktopup_time', 'checktopup_time_cv' - avoid topup period, pause 5 seconds before topup starts, 5s wait after topup finished.")
    print(" 3. 'checkfe', 'checkfe_cv' - check Front end shutter, pause when shutter closed, resume 60s after shutter opened.")
    print(" 4. 'checkbeam', 'checkbeam_cv'- composite scannable of above 3 scannables")
    print(" Checking is done every second!")
    
    from gdascripts.scannable.beamokay import WaitWhileScannableBelowThreshold, WaitForScannableState
    from gda.device.scannable.scannablegroup import ScannableGroup
    
    checkrc = WaitWhileScannableBelowThreshold('checkrc', rc, 190, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5) 
    checktopup_time = WaitWhileScannableBelowThreshold('checktopup_time', topup_time, 5, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5) 
    checkfe = WaitForScannableState('checkfe', frontend, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=60) 
    checkbeam = ScannableGroup('checkbeam', [checkrc, checkfe, checktopup_time])
    checkbeam.configure()
    
    #beam monitors used for continuous scan
    checkrc_cv = WaitWhileScannableBelowThreshold('checkrc_cv', rc, 190, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5) 
    checkrc_cv.setOperatingContinuously(True)
    checktopup_time_cv = WaitWhileScannableBelowThreshold('checktopup_time_cv', topup_time, 5, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5) 
    checktopup_time_cv.setOperatingContinuously(True)
    checkfe_cv = WaitForScannableState('checkfe_cv', frontend, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=60)
    checkfe_cv.setOperatingContinuously(True)
    checkbeam_cv = ScannableGroup('checkbeam_cv', [checkrc_cv, checkfe_cv, checktopup_time_cv])
    checkbeam_cv.configure()
except:
    localStation_exception(sys.exc_info(), "creating checkbeam objects")
    
try:    
    print "Adding checkbeamcv device (add to cvscan to get checkbeam functionality)"

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
    
def checkbeam4scan():
    from gda.jython.commands.ScannableCommands import add_default, remove_default
    try:
        remove_default(checkbeamcv)
    except:
        pass
    add_default(checkbeam)

def checkbeam4cvscan():
    from gda.jython.commands.ScannableCommands import add_default, remove_default
    try:
        remove_default(checkbeam)
    except:
        pass
    add_default(checkbeamcv)
    
from gda.jython.commands.GeneralCommands import alias
alias("checkbeam4scan")
alias("checkbeam4cvscan")
    
from i09shared.pseudodevices.pauseDetectorWhileMonitorBelowThreshold import WaitForScannableStateAndHandleShutter

from gda.configuration.properties import LocalProperties
BEAMLINE = LocalProperties.get("gda.beamline.name")

print("-"*100)
shutters = []

if BEAMLINE == "i09":
    from gdaserver import fsi1, fsj1 #@UnresolvedImport
    shutters = shutters + [fsi1, fsj1]
elif BEAMLINE == "i09-1":
    from gdaserver import psi1 #@UnresolvedImport
    shutters = shutters + [psi1]
elif BEAMLINE == "i09-2":
    from gdaserver import fsk1, psk1 #@UnresolvedImport
    shutters = shutters + [fsk1, psk1]

if BEAMLINE == "i09-2" or BEAMLINE == "i09":
    from gdaserver import  jidaccesscontrol #@UnresolvedImport
    print "Creating 'checkjid' scannable to be used to pause or resume detector acquisition based on ID control"
    checkjid = WaitForScannableStateAndHandleShutter('checkjid', shutters, jidaccesscontrol, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5.0, readyStates=['ENABLED'])

if BEAMLINE == "i09-1" or BEAMLINE == "i09":
    from gdaserver import  iidaccesscontrol #@UnresolvedImport
    print "Creating 'checkiid' scannable to be used to pause or resume detector acquisition based on ID control"
    checkiid = WaitForScannableStateAndHandleShutter('checkiid', shutters, iidaccesscontrol, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5.0, readyStates=['ENABLED'])

print("")
## this file can be customised to include everything that is needed

beamlinescriptsloc = "/dls_sw/i22/scripts/BeamlineScripts/"

print "Creating beamline specific devices...";
execfile(beamlinescriptsloc + "energy.py")
execfile(beamlinescriptsloc + "ExafsScannable.py")
execfile(beamlinescriptsloc + "DiodeAverage.py")
execfile(beamlinescriptsloc + "feedback.py")

execfile(beamlinescriptsloc + "CalibratedDiode.py")
execfile(beamlinescriptsloc + "DiodeSleep.py")

# those need "run" as it includes gda syntax
# run("commissioning/Marc/shutdown/hotwaxs.py")
#run("/BeamlineScripts/i22.py")

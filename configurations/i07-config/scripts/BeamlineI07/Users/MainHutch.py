
#    MainHutch.py
#
#    For user specific initialisation code on I07 Main Hutch.

from commands import getoutput
from os import path
from os import system

try_execfile("BeamlineI07/Users/pvMonitors.py")

print "Creating aliases to control shutter (shopen, shclose, shop, shcl)"
try_execfile("BeamlineI07/Users/ShutterControl2.py")



# TODO do we need checkdcm for the new DCM?
# print "Setting up checkdcm to pause scans when t17 gets too hot: add 'checkdcm' to scan line"
try_execfile("BeamlineI07/Users/waitAbove.py")
#checkdcm = WaitAbove('checkdcm', dcm1t17, maximumThreshold=120, maximumToResume=90, secondsBetweenChecks=1,secondsToWaitAfterOK=5)

print "Setting up checkbeam to pause scans when beam is down: add 'checkbeam' to scan line"
try_execfile("BeamlineI07/Users/waitBelowAndShutter.py")
checkbeam = WaitBelowAndShutter('checkbeam', scannableToMonitor=rc, minimumThreshold=20, shutterScannable=portshutter, shutterValue="Open", secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=15, idgap=idgap)

# add automatic peak finding commands: peak, com, cen
try_execfile("BeamlineI07/Users/gotopeak.py")

# find the root data directory for the visit
# this replaces PathConstructor.createFromDefaultProperty()
#visitRoot = "/".join(i07.getDataPath().split("/",6)[0:6])

# set operation link to be the same as current data directory
# but not if the directory starts with /tmp (indicating a local GDA client)
#if not visitRoot.startswith("/tmp"):
#    system("rm -f /dls/i07/data/operation")
#    system("ln -s "+visitRoot+" /dls/i07/data/operation")

#print "*******************************************************************\n"
#print "Current data directory: " + i07.getDataPath()
#print "Operation link (for legacy apps): " + getoutput("readlink /dls/i07/data/operation") + "\n"
#print "EH1 p100k path: " + pil1.getFullFileName()
#print "EH1 p2m   path: " + pil2.getFullFileName()
#print "EH2 p100k path: " + pil3.getFullFileName()
#print "\n*******************************************************************"

# add diffcalc headers
try_execfile("BeamlineI07/Users/DiffcalcHeaders.py")

# add pilNumRestore to restore Pilatus image number after fastpil use
# Charles 19-01-16 - want to remove pilNumRestore as it may cause problems with fastpil with soft trigger
# ignores pil3 for now
try_execfile("BeamlineI07/Users/PilNumRestore.py")

# add createUserSetup(), setPilPaths(), etc.
try_execfile("BeamlineI07/Users/FileDirFunctions.py")

# add AutoMonitor and CountNormaliser classes
try_execfile("BeamlineI07/Users/AutoMonitor.py")

# add per-point fast shutter support (fs1 and fs2)
try_execfile("BeamlineI07/Users/FastShutter3.py")

# add setpos command
try_execfile("BeamlineI07/Users/setpos.py")

# add hex1axes
try_execfile("BeamlineI07/Users/hexutils.py")

# add plot choosing commands yplot, yshow, yreset, xplot, xreset
try_execfile("BeamlineI07/Users/plotchoose.py")

# add restorerois command
try_execfile("BeamlineI07/Users/restorerois.py")

# set ion chamber output to more useful format
ionc1.setOutputFormat([u'%20.12e'])

# set diffractometer motor GDA limits to +/- 1000
for m in DIFF.getGroupMembers():
    try:
        m.setUpperGdaLimits(1000)
        m.setLowerGdaLimits(-1000)
    except AttributeError:
        pass

# set permissions for i07user on all available visits this year
try_execfile("BeamlineI07/Users/i07userperms_all.py")

# override setVisit and setvisit to set permissions as well
try_execfile("BeamlineI07/Users/setVisitAndPerm.py")

# add checkvalve for when running in EH2
try_execfile("BeamlineI07/Users/checkValve.py")

# add troughReset
try_execfile("BeamlineI07/Users/troughReset.py")

# add ct command
try_execfile("BeamlineI07/Users/ct.py")

# run the local setup file for this experiment
# now finds this at the location returned by getDir()
visitRoot = "/".join(i07.getDataPath().split("/",6)[0:6])
if path.isfile("../../.."+visitRoot+"/UserSetup.py"):
    print "Running UserSetup.py"
    run("../../.."+visitRoot+"/UserSetup.py")
else:
    print "No UserSetup.py script found"

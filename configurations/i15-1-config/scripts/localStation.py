import java, sys

from gdascripts.messages.handle_messages import simpleLog, log
from gdascripts.pd.time_pds import waittimeClass2
global run

localStation_exceptions = []

def localStation_exception(exc_info, msg):
    typ, exception, traceback = exc_info
    simpleLog("! Failure %s !" % msg)
    localStation_exceptions.append("    %s" % msg)
    log(None, "Error %s -  " % msg , typ, exception, traceback, False)

try:
    simpleLog("================ INITIALISING I15-1 GDA ================")
    w = waittimeClass2('w')

except:
    localStation_exception(sys.exc_info(), "in localStation")

print "*"*80
print "Attempting to run localStationStaff.py from users script directory"
try:
    run("localStationStaff")
    print "localStationStaff.py completed."
except java.io.FileNotFoundException, e:
    print "No localStationStaff.py found in user scripts directory"
except:
    localStation_exception(sys.exc_info(), "running localStationStaff user script")

print "*"*80
print "Attempting to run localStationUser.py from users script directory"
try:
    run("localStationUser")
    print "localStationUser.py completed."
except java.io.FileNotFoundException, e:
    print "No localStationUser.py found in user scripts directory"
except:
    localStation_exception(sys.exc_info(), "running localStationUser user script")

if len(localStation_exceptions) > 0:
    simpleLog("=============== %r ERRORS DURING STARTUP ================" % len(localStation_exceptions))

for localStationException in localStation_exceptions:
    simpleLog(localStationException)

simpleLog("===================== GDA ONLINE =====================")
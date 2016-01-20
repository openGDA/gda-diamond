import java, sys
import installation
import gdascripts.scan.concurrentScanWrapper

from gdascripts.messages.handle_messages import simpleLog, log
from gdascripts.scannable.dummy import SingleInputDummy
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
from gda.device.scannable.scannablegroup import ScannableGroup

from gdascripts.degas.degas import Degas

global run

scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()

print "Adding dummy devices x,y and z"
dummies = ScannableGroup()
dummies.setName("dummies")
dummies.setGroupMembers([SingleInputDummy("x"), SingleInputDummy("y"), SingleInputDummy("z")])

print "Adding timer devices t, dt, and w, clock"
from gdascripts.scannable.timerelated import timerelated #@UnusedImport

if installation.isLive():
    print "Running in live mode"
else:
    print "Running in dummy mode"

simpleLog("================ INITIALISING I21 GDA ================")

print "*"*80
print "Attempting to run localStationUser.py from users script directory"

run("localStationUser")
print "localStationUser.py completed."

simpleLog("===================== GDA ONLINE =====================")

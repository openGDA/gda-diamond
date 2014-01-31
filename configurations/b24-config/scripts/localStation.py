from gdascripts.scannable.dummy import SingleInputDummy #@UnusedImport

from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
import gdascripts.scan.concurrentScanWrapper
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()

print "Adding dummy devices x,y and z"
x=SingleInputDummy("x")
y=SingleInputDummy("y")
z=SingleInputDummy("z")

print "Adding timer devices t, dt, and w, clock"
from gdascripts.scannable.timerelated import t, dt, w, clock, epoch #@UnusedImport
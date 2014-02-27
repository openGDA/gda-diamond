from gdascripts.scannable.dummy import SingleInputDummy #@UnusedImport

from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
import gdascripts.scan.concurrentScanWrapper
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()

print "Adding dummy devices x,y and z"
x=SingleInputDummy("x")
y=SingleInputDummy("y")
z=SingleInputDummy("z")
xyz = gda.device.scannable.scannablegroup.ScannableGroup( 'xyz', [x, y, z] )

import nexusMetadata
NMD = nexusMetadata.NexusMetaData()
xyzMetaPaths = [ 'instrument:NXinstrument/XYZ:NXcollection/x',
                'instrument:NXinstrument/XYZ:NXcollection/y',
                'instrument:NXinstrument/XYZ:NXcollection/z' ]
xyzUnits = [ 'mm', 'mm', 'mm' ]
NMD.addScannablePaths( xyz, xyzMetaPaths, xyzUnits )

print "Adding timer devices t, dt, and w, clock"
from gdascripts.scannable.timerelated import t, dt, w, clock, epoch #@UnusedImport

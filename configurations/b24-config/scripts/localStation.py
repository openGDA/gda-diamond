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

from gda.configuration.properties import LocalProperties


#New "standard" nexus metadata stuff
#move to mt-config?
from gdascripts.metadata.metadata_commands import setTitle, getTitle, meta_add, meta_ll, meta_ls, meta_rm
alias("setTitle")
alias("getTitle")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")

from gda.data.scan.datawriter import NexusDataWriter
LocalProperties.set( NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME, "metashop" )


from gdascripts.scannable.installStandardScannableMetadataCollection import *
meta.rootNamespaceDict=globals()
note.rootNamespaceDict=globals()

print "Adding timer devices t, dt, and w, clock"
from gdascripts.scannable.timerelated import t, dt, w, clock, epoch #@UnusedImport

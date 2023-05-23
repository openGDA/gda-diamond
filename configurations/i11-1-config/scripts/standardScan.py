
print "=================================================================================================================";
print "installing standard scan.";
print

from gdascripts.scan import gdascans
from gda.scan import SortedScanDataPointCache
from gdascripts.analysis.datasetprocessor.oned.GaussianPeakAndBackground import GaussianPeakAndBackground
from gdascripts.scan.process.ScanDataProcessor import ScanDataProcessor
from gda.jython import InterfaceProvider

sdp_cache = SortedScanDataPointCache()
_sdpp = InterfaceProvider.getScanDataPointProvider()
_sdpp.addIObserver(sdp_cache)
add_reset_hook(lambda x=_sdpp, o=sdp_cache: x.deleteIObserver(o))

gpab = GaussianPeakAndBackground(plotPanel='Peak Fitting')
scan_processor = ScanDataProcessor([gpab], globals(), sdp_cache)
rscan = gdascans.Rscan([scan_processor])
alias('rscan')

cscan = gdascans.Cscan([scan_processor])
alias('cscan')

go = scan_processor.go
alias('go')


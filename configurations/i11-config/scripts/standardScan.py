
print "=================================================================================================================";
print "installing standard scan.";
print

from gdascripts.scan import gdascans
from gdascripts.analysis.datasetprocessor.oned.GaussianPeakAndBackground import GaussianPeakAndBackground
from gdascripts.scan.process.ScanDataProcessor import ScanDataProcessor
from gdaserver import dataPointCache

gpab = GaussianPeakAndBackground(plotPanel='Peak Fitting')
scan_processor = ScanDataProcessor([gpab], globals(), dataPointCache)
rscan = gdascans.Rscan([scan_processor])
alias('rscan')

cscan = gdascans.Cscan([scan_processor])
alias('cscan')

go = scan_processor.go
alias('go')


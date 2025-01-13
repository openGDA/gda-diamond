
print "=================================================================================================================";
print "installing standard scan.";
print

#from gda.jython import InterfaceProvider
from gdascripts.scan import gdascans
from gdascripts.analysis.datasetprocessor.oned.GaussianPeakAndBackground import GaussianPeakAndBackground
from gdascripts.scan.process.ScanDataProcessor import ScanDataProcessor
from gdaserver import dataPointCache

#InterfaceProvider.getScanDataPointProvider().addIScanDataPointObserver(dataPointCache)

gpab = GaussianPeakAndBackground(plotPanel='Peak Fitting')
scan_processor = ScanDataProcessor([gpab], globals(), dataPointCache)
rscan = gdascans.Rscan([scan_processor])
alias('rscan')

cscan = gdascans.Cscan([scan_processor])
alias('cscan')

go = scan_processor.go
alias('go')

#peak_scan = gdascans.Scan([scan_processor])
#alias('peak_scan')

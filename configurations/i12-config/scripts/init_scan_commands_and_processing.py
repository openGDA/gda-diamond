from gdascripts.analysis.datasetprocessor.oned.MaxPositionAndValue import MaxPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.MinPositionAndValue import MinPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.CentreOfMass import CentreOfMass
from gdascripts.analysis.datasetprocessor.oned.GaussianPeakAndBackground import  GaussianPeakAndBackground
from gdascripts.scan.process.ScanDataProcessor import ScanDataProcessor
#from gdascripts.scan.process.ScanDataProcessorResult import go
#from gdascripts.scan import specscans
from gdascripts.scan import gdascans

from gda.jython.commands.GeneralCommands import alias

print "Setting up scan data processor, scan_processor"
scan_processor = ScanDataProcessor( [MaxPositionAndValue(),MinPositionAndValue(),CentreOfMass(), GaussianPeakAndBackground() ], globals() )
#alias("go")

print "Creating scan commands:"

#scan=gdascans.Scan()
rscan=gdascans.Rscan()
scanp=gdascans.Scan([scan_processor])
rscanp=gdascans.Rscan([scan_processor])

#alias('scan')
alias('rscan')
alias('scanp')
alias('rscanp')
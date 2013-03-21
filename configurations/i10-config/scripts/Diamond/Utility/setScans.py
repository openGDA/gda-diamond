#init_scan_commands_and_processing.py
from gdascripts.analysis.datasetprocessor.oned.MaxPositionAndValue import MaxPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.MinPositionAndValue import MinPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.CentreOfMass import CentreOfMass
from gdascripts.analysis.datasetprocessor.oned.GaussianPeakAndBackground import  GaussianPeakAndBackground
from gdascripts.scan.process.ScanDataProcessor import ScanDataProcessor

from gdascripts.scan.process.ScanDataProcessorResult import go

from gdascripts.scan import specscans
from Diamond.Objects.Scans import NormalScan, RelativeScan;

from gda.jython.commands.GeneralCommands import alias

print "Setting up scan data processor, scan_processor"
scan_processor = ScanDataProcessor( [MaxPositionAndValue(),MinPositionAndValue(),CentreOfMass(), GaussianPeakAndBackground() ], globals() )
alias("go")

print "Creating scan commands:"
nscan=NormalScan([scan_processor])
rscan=RelativeScan([scan_processor])

ascan  = specscans.Ascan([scan_processor]);
a2scan = specscans.A2scan([scan_processor]);
a3scan = specscans.A3scan([scan_processor]);
mesh   = specscans.Mesh([scan_processor]);
dscan  = specscans.Dscan([scan_processor]);
d2scan = specscans.D2scan([scan_processor]);
d3scan = specscans.D3scan([scan_processor]);


alias('nscan');  #print nscan.__doc__.split('\nUSAGE:\t\t\t\n')[1];
alias('rscan');

alias('ascan');  print ascan.__doc__.split('\nUSAGE:\n\t\n  ')[1];
alias('a2scan'); print a2scan.__doc__.split('\nUSAGE:\n\t\n  ')[1];
alias('a3scan'); print a3scan.__doc__.split('\nUSAGE:\n\t\n  ')[1];
alias('mesh');   print mesh.__doc__.split('\nUSAGE:\n\t\n  ')[1];
alias('dscan');  print dscan.__doc__.split('\nUSAGE:\n\t\n  ')[1];
alias('d2scan'); print d2scan.__doc__.split('\nUSAGE:\n\t\n  ')[1];
alias('d3scan'); print d3scan.__doc__.split('\nUSAGE:\n\t\n  ')[1];

for s in nscan, rscan, ascan, a2scan, a3scan, mesh, dscan, d2scan, d3scan:
	s.dataVectorPlotNameForSecondaryScans =  "Secondary Plot"

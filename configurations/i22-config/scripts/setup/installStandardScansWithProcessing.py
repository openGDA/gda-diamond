# To use this module (from LocalStation.py for example):
# >>> from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
# >>> scan_processor.rootNamespaceDict=globals()
#
# To modify the processor called at the end of each scan, modify scan_processor.


from gdascripts.analysis.datasetprocessor.oned.MaxPositionAndValue import MaxPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.MinPositionAndValue import MinPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.CentreOfMass import CentreOfMass
from gdascripts.analysis.datasetprocessor.oned.GaussianPeakAndBackground import  GaussianPeakAndBackground
from gdascripts.analysis.datasetprocessor.oned.GaussianEdge import  GaussianEdge
from gdascripts.analysis.datasetprocessor.oned.TwoGaussianEdges import TwoGaussianEdges
from gdascripts.scan.process.ScanDataProcessor import ScanDataProcessor
from gdascripts.scan import specscans
from gdascripts.scan import gdascans

from gda.jython.commands.GeneralCommands import alias

print "Setting up scan data processor, scan_processor"
ge=GaussianEdge()
ge.smoothwidth=5
ge.plotPanel = "Edge Fit Plot"
ge.formatString = 'Edge at %-14.6gslope: %.6g, fwhm: %.6g, residual: %.6g'

tge = TwoGaussianEdges(smoothwidth=3,
		labelList=('centre','upos','dpos', 'width'),
		keyxlabel='centre',
		plotPanel='Two Edge Plot',
		formatString='Centre at %-12.6gupos: %.6g, dpos: %.6g, width: %.6g')

gpab = GaussianPeakAndBackground()
gpab.plotPanel = "Peak Fit Plot"
gpab.formatString = 'Peak at %-14.6goffset: %.6g, top: %.6g, fwhm: %.6g, residual: %.6g'

mxpav = MaxPositionAndValue()
mxpav.formatString = 'maxval at %-12.6gmaxval = %.6g'

mnpav = MinPositionAndValue()
mnpav.formatString = 'minval at %-12.6gminval = %.6g'

scan_processor = ScanDataProcessor([mnpav, mxpav, gpab, ge, tge], globals())

go = scan_processor.go
alias("go")

print "Creating spec-like commands:"
ascan  = specscans.Ascan([scan_processor])
#a2scan = specscans.A2scan([scan_processor])
#a3scan = specscans.A3scan([scan_processor])
#mesh   = specscans.Mesh([scan_processor])
#dscan  = specscans.Dscan([scan_processor])
#d2scan = specscans.D2scan([scan_processor])
#d3scan = specscans.D3scan([scan_processor])
alias('ascan');print ascan.__doc__.split('\n')[3]
#alias('a2scan');print a2scan.__doc__.split('\n')[3]
#alias('a3scan');print a3scan.__doc__.split('\n')[3]
#alias('mesh');print mesh.__doc__.split('\n')[3]
#alias('dscan');print dscan.__doc__.split('\n')[3]
#alias('d2scan');print d2scan.__doc__.split('\n')[3]
#alias('d3scan');print d3scan.__doc__.split('\n')[3]

print "Creating gda scan commands:"
scan=gdascans.Scan([scan_processor])
rscan=gdascans.Rscan([scan_processor])
cscan=gdascans.Cscan([scan_processor])
alias('scan');print scan.__doc__.split('\n')[2]
alias('rscan');print rscan.__doc__.split('\n')[2]
alias('cscan');print cscan.__doc__.split('\n')[2]

#for s in ascan, a2scan, a3scan, mesh, dscan, d2scan, d3scan, scan, rscan:
for s in ascan, scan, rscan:
	s.dataVectorPlotNameForSecondaryScans =  "Secondary Plot"

#example/focus_with_wire
print "12345"
from gdascripts.scan.SecondaryConcurrentScan import SecondaryConcurrentScan
from gdascripts.scan.process.ScannableScan import ScannableScan
from gdascripts.analysis.datasetprocessor.oned.GaussianEdge import GaussianEdge
from gdascripts.analysis.datasetprocessor.oned.TwoGaussianEdges import TwoGaussianEdges
from gdascripts.analysis.datasetprocessor.oned.MinPositionAndValue import MinPositionAndValue
from gdascripts.scan.process.tuner import Tuner
from gdascripts.scan.gdascans import Scan, Rscan



import installation

if not installation.isLive():
	from testjy.gdascripts_test.analysis_test.datasetprocessor_test.oned_test.files.files import WIRESCANFILE, WIRESCANFILE2 
	from gdascripts.scannable.ScanFileHolderScannable import ScanFileHolderScannable
	from gda.analysis import ScanFileHolder
	from gda.analysis.io import SRSLoader
	sfh = ScanFileHolder()
	sfh.load(SRSLoader(WIRESCANFILE))
	data_10040 = ScanFileHolderScannable('data_10040',sfh, ('tbdiagZcoarse', 'tbdiagY'), ('rc', 'pips2'),{'tbdiagZcoarse':1, 'tbdiagY':.0005} )
	tbdiagZcoarse = data_10040.scannableFactory('tbdiagZcoarse', ['tbdiagZcoarse'])
	tbdiagY = data_10040.scannableFactory('tbdiagY', ['tbdiagY'])
	rc = data_10040.scannableFactory('rc', ['rc'])
	pips2 = data_10040.scannableFactory('pips2', ['pips2'])
	

# 1. Setup the wirescanner scannable
#    Choose either Scan or Rscan (must begin with a capital) and follow with standard
#    scan arguments. Include the detector whose output is to be processed last:


wirescanner = ScannableScan('wirescanner', TwoGaussianEdges(), 	Scan, tbdiagY, -3.8500, -3.999500, 0.0005, tbdiagZcoarse, rc, pips2, .2)
print "1/0 = ", 1/0

# 2. Use the wirescanner scannable to determine the current focus:
pos(wirescanner) # (it takes no position)

# 3. Determine focus as a parameter is scanned:

scan(tbdiagZcoarse, 148, 188, 1, wirescanner)

1/0
# 4. Got to the best focus:

#go minval

## Or use an automatic tuner

# The tuner simply performs a scan and goes to a feature
# 1. To create the tuner, embed the scan arguments from section 3 above. i.e.:
wiretuner = Tuner('wiretuner', MinPositionAndValue(), Scan,tbdiagZcoarse, 148, 188, 1, wirescanner)

# 2. And to tune:
wiretuner.tune()



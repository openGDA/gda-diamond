print("Running xes_peak_fit.py")

from uk.ac.gda.beamline.i20.scannable import ScannableGaussian
xesSignalGaussian = ScannableGaussian("xesSignalGaussian", XESEnergyLower.getPosition(), 5, 1)
xesSignalGaussian.setNoiseLevel(0.01)
xesSignalGaussian.setParams(2001.23, 5, 1)
xesSignalGaussian.setScannableToMonitorForPosition(XESEnergyUpper)# position of braggoffset determines value returned by scannable

# Setup curve fitting scan runner to run XES scans
from uk.ac.gda.server.exafs.scan.preparers import CurveFitScanRunner
scanRunner = CurveFitScanRunner()
scanRunner.setScannableToMove(XESEnergyLower)
if LocalProperties.isDummyModeEnabled() :
    scanRunner.setDetectorArgs([xesSignalGaussian])
    scanRunner.setFitDataName("value")
else :
    scanRunner.setDetectorArgs([medipix1, 1.0])
    scanRunner.setFitDataName("roi1_total")

xesEnergyUpperPeakScan = CurveFitScanRunner()
xesEnergyUpperPeakScan.setScannableToMove(XESEnergyUpper)
xesEnergyUpperPeakScan.setDetectorArgs([I1, 1, medipix1])
xesEnergyUpperPeakScan.setFitDataName("FFI1_medipix1")

xesEnergyLowerPeakScan = CurveFitScanRunner()
xesEnergyLowerPeakScan.setScannableToMove(XESEnergyLower)
xesEnergyLowerPeakScan.setDetectorArgs([I1, 1, medipix2])
xesEnergyLowerPeakScan.setFitDataName("FFI1_medipix2")

xesEnergyBothPeakScan = CurveFitScanRunner()
xesEnergyBothPeakScan.setScannableToMove(XESEnergyBoth)
xesEnergyBothPeakScan.setDetectorArgs([I1, 1, medipix2])
xesEnergyBothPeakScan.setFitDataName("FFI1_medipix2")

if LocalProperties.isDummyModeEnabled() :
    xesEnergyUpperPeakScan.setDetectorArgs([xesSignalGaussian])
    xesEnergyUpperPeakScan.setFitDataName("value")

def set_scan_runner_range(scan_runner, start, end, step):
    scan_runner.setRelativeStart(start)
    scan_runner.setRelativeEnd(end)
    scan_runner.setStepSize(step)   

def set_scan_runner_fit(scan_runner, range=5, fit_to_peak_only=True) :
    fitter = scan_runner.getCurveFitter() 
    fitter.setPeakPointRange(range)
    fitter.setFitToPeakPointsOnly(fit_to_peak_only)

def setup_defaults(curve_fit_runner) :
    set_scan_runner_range(curve_fit_runner, -2, 2, 0.2)
    set_scan_runner_fit(curve_fit_runner, 5, True)

for f in [xesEnergyUpperPeakScan, xesEnergyLowerPeakScan, xesEnergyBothPeakScan] :
    setup_defaults(f)


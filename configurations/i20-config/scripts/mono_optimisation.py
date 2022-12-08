# Create mono optimiser object - this will also need sending into one of the preparers... imh 31/8/2016

print "Setting up monoOptimiser to do bragg offset optimisation scans"

from uk.ac.gda.beamline.i20.scannable import MonoOptimisation

if LocalProperties.get("gda.mode") == "live":
    monoOptimiser = MonoOptimisation( braggoffset, ionchambers )
else :
    #Setup gaussian used to provide signal when optimising mono
    from uk.ac.gda.beamline.i20.scannable import ScannableGaussian
    scannableGaussian = ScannableGaussian("scannableGaussian", 0.1, 5, 1)
    scannableGaussian.setScannableToMonitorForPosition(braggoffset) # position of braggoffset determines value returned by scannable
    monoOptimiser = MonoOptimisation( braggoffset, scannableGaussian )

monoOptimiser.setBraggScannable(bragg1WithOffset)
monoOptimiser.setDaServer(DAServer)
monoOptimiser.setPhotonShutter(photonshutter)
bragg1WithOffset.setMonoOptimiser(monoOptimiser)

#Set up monoOptimiser for bragg offset adjustment
monoOptimiser.setAllowOptimisation(True)
monoOptimiser.setOffsetStart(-2.0)
monoOptimiser.setOffsetEnd(2.0)
monoOptimiser.setOffsetNumPoints(21)
monoOptimiser.setSelectNewScansInPlotView(False) # False = don't select new bragg offset scans in Plot view

monoOptimiser.setFitToPeakPointsOnly(True)
monoOptimiser.setPeakPointRange(4)

# set these back to zero, in case fitting went wrong. 23/1/2019
bragg1WithOffset.setOffsetStartValue(0)
bragg1WithOffset.setOffsetGradient(0)
bragg1WithOffset.setAdjustBraggOffset(True) # True = Adjust bragg offset when moving to new energy

import gda.scan.ScanBase
from gda.jython.commands import Input
import java
import math
from cendac import CentreDAC


def centre(axis, scanRange,scanStep,rockAngle,diode, peak=False, centre=58.):
	"""
	centre(scanRange, scanStep, rockAngle, diode)
	
	Centers the sample (DAC) on the beam and the diffractometer center.
	Firstly finds the sample position about dkphi=-58 deg scan around the current position 
	in dx and dz +/- scanRange (mm) with a step size scanStep (mm). 
	Then the DAC is rotated +/- rockAngle (deg) about 58 degrees, the
	centre is found again and the drift of the centre is used to correct the dy axis.

	Example: centre58(0.4, 0.02, 10, d4)
	
	"""
	
	print "Axis = ", axis
	cn = CentreDAC(axis, scanRange,scanStep,rockAngle,diode, peak, centre)
	cn.cendy()
	if peak:
		centrePeak(scanRange,scanStep,rockAngle,diode, axis, centre)
	return

def centrePeak(scanRange,scanStep,rockAngle,diode, axis, centre):
	
	"""
	centrePeak(scanRange, scanStep, rockAngle, diode)
	
	Same as centre(...), but instead of scan, scanPeak is used to fit a
	step function and automatically find the centre. 

	Example: centrePeak(0.4, 0.02, 10, d4)
	
	"""
	cn = CentreDAC(axis, scanRange,scanStep,rockAngle,diode,True, centre)
	cn.cendy()
	return
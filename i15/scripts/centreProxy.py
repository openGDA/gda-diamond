from gdascripts.parameters import beamline_parameters
from cendac import CentreDAC

def centre(rotation_axis, scanRange, scanStep, rockAngle, diode,
		auto_fit=False, rotation_centre=58.):
	"""
	Centers the sample (DAC) on the beam and the diffractometer center.
	
	Example: centre(dkphi, 0.4, 0.02, 10, d4)
	
	For axis=dkphi, finds the sample position about dkphi=-58 deg scan around
	the current position in dx and dz +/- scanRange (mm) with a step size
	scanStep (mm). Then the DAC is rotated +/- rockAngle (deg) about 58 degrees,
	the centre is found again and the drift of the centre is used to correct
	the dy axis.
	"""
	
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	beamline= jythonNameMap.beamline

	if   rotation_axis == jythonNameMap.dkphi:
		perp2rot_axis	= jythonNameMap.dx
		focus_axis		= jythonNameMap.dy
	elif rotation_axis == jythonNameMap.dktheta:
		perp2rot_axis	= jythonNameMap.dv
		focus_axis		= jythonNameMap.dy
	elif rotation_axis == jythonNameMap.cryorot:
		perp2rot_axis	= jythonNameMap.cryox
		focus_axis		= jythonNameMap.cryoz
	else:
		print "Axis %s not supported by centre()" % rotation_axis.name
		print "Please specify dkphi, dktheta or cryorot."
		return
	
	print "Axis = ", rotation_axis
	cn = CentreDAC(rotation_axis, perp2rot_axis, focus_axis, beamline,
		scanRange, scanStep, rockAngle, diode, auto_fit, rotation_centre)
	cn.cendy()
	if auto_fit:
		centrePeak(rotation_axis, perp2rot_axis, focus_axis, beamline,
			scanRange, scanStep, rockAngle, diode, rotation_centre)
	return

def centrePeak(rotation_axis, perp2rot_axis, focus_axis, beamline,
		scanRange, scanStep, rockAngle, diode, rotation_centre):
	
	cn = CentreDAC(rotation_axis, perp2rot_axis, focus_axis, beamline,
		scanRange, scanStep, rockAngle, diode, True, rotation_centre)
	cn.cendy()
	return
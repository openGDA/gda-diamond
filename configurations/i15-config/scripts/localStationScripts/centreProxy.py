from gdascripts.parameters import beamline_parameters
from localStationScripts.centreDac import CentreDAC

def centre(rotation_axis, scanRange, scanStep, rockAngle, diode,
		auto_fit=False, rotation_centre=None):
	"""
	
	Centers the sample (DAC) on the beam and the diffractometer center.
	
	For rotation_axis=dkphi, finds the sample position about dkphi=-58 deg scan
	around the current position in dx and dz +/- scanRange (mm) with a step size
	scanStep (mm). Then the DAC is rotated +/- rockAngle (deg) about 58 degrees,
	the centre is found again and the drift of the centre is used to correct
	the dy axis.
	
	For rotation_axis=dktheta, sphi or cryorot the rotation_centre must be specified
	but the centre() routine uses the relevant axes.
	
	Example: centre(dkphi, 0.4, 0.02, 10, d4)
	         centre(dkphi, 0.4, 0.02, 10, d4, False, 57)
	         centre(cryorot, 0.4, 0.02, 10, d4, False, 11)
	         centre(cryorot, 0.4, 0.02, 10, d4, rotation_centre=11)
	         centre(sphi, 0.1, 0.005, 3, d8, rotation_centre=0)
	"""
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	beamline= jythonNameMap.beamline

	focus_axis_inverted = False
	print "Axis %s" % rotation_axis.name,
	
	if   rotation_axis == jythonNameMap.dkphi:
		perp2rot_axis	= jythonNameMap.dx
		focus_axis		= jythonNameMap.dy
		default_rotcen=58.
		if  rotation_centre==None:
			rotation_centre=default_rotcen
		if (default_rotcen-90 > rotation_centre or
								rotation_centre > default_rotcen+90 ):
			print "!!! Inverting focus axis because sample is rotated !!!"
			focus_axis_inverted = True
			print "NOTE: This function is unverified, if your focus diverges"
			print "      you should call your GDA representative to debug it."
	
	elif rotation_axis == jythonNameMap.dktheta:
		perp2rot_axis	= jythonNameMap.dv
		focus_axis		= jythonNameMap.dy

	elif rotation_axis == jythonNameMap.cryorot:
		perp2rot_axis	= jythonNameMap.cryox
		focus_axis		= jythonNameMap.cryoz
		focus_axis_inverted = True
	
	elif rotation_axis == jythonNameMap.sphi:
		perp2rot_axis	= jythonNameMap.ssx
		focus_axis		= jythonNameMap.ssz
		if  rotation_centre==None:
			rotation_centre=0
			print "No rotation_centre specified, assuming 0."
		#focus_axis_inverted = True
	else:
		print "not supported by centre()"
		print "Please specify rotation_axis as dkphi, dktheta or cryorot."
		return
	if rotation_centre==None:
		print "has no default rotation_centre."
		print "Please specify rotation_centre for this axis. See 'help centre'"
		return

	print "focus_axis %s, perp2rot_axis %s" % (
		focus_axis.name, perp2rot_axis.name)
	print "  rotation_centre=%.4f & focus_axis_inverted = %r" % (
			 rotation_centre, 		focus_axis_inverted)
	
	cn = CentreDAC(rotation_axis, perp2rot_axis, focus_axis, beamline,
				   scanRange, scanStep, rockAngle, diode, auto_fit,
				   rotation_centre, focus_axis_inverted)
	cn.cendy()
	if auto_fit:
		centrePeak(rotation_axis, perp2rot_axis, focus_axis, beamline,
				   scanRange, scanStep, rockAngle, diode, rotation_centre,
				   focus_axis_inverted)
	return

def centrePeak(rotation_axis, perp2rot_axis, focus_axis, beamline,
		scanRange, scanStep, rockAngle, diode, rotation_centre,
		focus_axis_inverted):
	
	cn = CentreDAC(rotation_axis, perp2rot_axis, focus_axis, beamline,
				   scanRange, scanStep, rockAngle, diode, True,
				   rotation_centre, focus_axis_inverted)
	cn.cendy()
	return

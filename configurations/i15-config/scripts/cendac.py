from gda.jython.commands import InputCommands
from math import pi, tan
from GeneralScan import GeneralScan
from operationalControl import genericScanChecks
#from scanPeak import fitStepFunction

class CentreDAC(GeneralScan):
	"""
	CentreDAC(rotation_axis, perp2rot_axis, focus_axis,
			  scanRange, scanStep, rockAngle, diode, autoFit, rotation_centre)
	
	Centers the sample (DAC) on the beam and the diffractometer center.
	
	Example: CentreDAC(dkphi, dx, dy, 0.4, 0.02, 10, d4, False, 58.)
	
	Firstly finds the sample position about axis=-10 deg scan around the
	current position in dx +/- scanRange (mm) with a step size
	scanStep (mm). Then the DAC is rotated +/- rockAngle (deg) about 10 degrees
	and the drift of the centre is used to correct the dy axis.
	"""
	def __init__(self, rotation_axis, perp2rot_axis, focus_axis, beamline,
			scanRange, scanStep, rockAngle, diode, autoFit, rotation_centre,
			focus_axis_inverted):
		"""
		Example: CentreDAC(dkphi, dx, dy, 0.4, 0.02, 10, d4, False, 58.)
		"""
		self.beamline= beamline
		
		self.rotation_axis	= rotation_axis
		# Axis perpendicular to axis of rotation
		self.perp2rot_axis	= perp2rot_axis 
		self.focus_axis		= focus_axis
		#self.dz = jythonNameMap.dz
		self.scanRange	= scanRange
		self.scanStep	= scanStep
		self.rockAngle	= rockAngle
		self.diode		= diode
		self.autoFit	= autoFit
		self.rotation_centre = rotation_centre
		self.focus_axis_inverted = focus_axis_inverted
		
		self.perp2rot_axis_ref = self.perp2rot_axis()
		self.focus_axis_ref = self.focus_axis()
		#self.dz_ref = self.dz()
		#self.ref_axis = self.rotation_axis
		self.rotation_axis(self.rotation_centre)

#	def centre(self):
#		self.cendzdx()
#		self.cendy()
#		self.cendzdx()

#	def cendzdx(self):
#		print "Centre DAC in the x and z axes..."
#		print "==================== dz ====================="
#		peakdz = self.cendz()
#		if peakdz=="":
#			print "No peak selected. Exiting..."
#			self.dz(self.dz_ref)
#			return
#		else:
#			print "You have entered ", `peakdz`," as the peak value of the z-axis scan."
#			self.dz(peakdz)
#			print "dz now at: ", `self.dz()`
#		
#		print "==================== "+self.perp2rot_axis.name+" ====================="
#		peakdx = self.centre_perp()
#		if peakdx=="":
#			print "No peak selected. Exiting..."
#			self.perp2rot_axis(self.perp2rot_axis_ref)
#			return
#		else:
#			print "You have entered ", `peakdx`," as the peak value of the x-axis scan."
#			self.perp2rot_axis(peakdx)
#			print self.perp2rot_axis.name+" now at: ", `self.perp2rot_axis()`
#		print "============================================="

	def cendy(self):
		self.perp2rot_axis_ref = self.perp2rot_axis.getPosition()
		#self.dz_ref = self.dz.getPosition()
		print "Focal Alignment."
		print "=============== "+self.focus_axis.name+" positive ================="
		print "Rotate axis by +%f and perform %s scan." % (
			self.rockAngle, self.perp2rot_axis.name)
		yposx = self.ypos()
		if yposx=="":
			print "No peak selected. Exiting..."
			self.rotation_axis(self.rotation_centre)
			print self.rotation_axis.name+" reset to: ", `self.rotation_axis()`
			self.perp2rot_axis(self.perp2rot_axis_ref)
			print self.perp2rot_axis.name+" reset to: ", `self.perp2rot_axis()`
			return
		else:
			print "You have entered a peak centre of ", `yposx`, \
				" for the positive "+self.perp2rot_axis.name+" x-axis scan."
		
		self.perp2rot_axis(self.perp2rot_axis_ref)
		#self.dz(self.dz_ref)
		print "=============== "+self.focus_axis.name+" negative ================="
		print "Centre & rotate axis by -%f and perform %s scan." % (
			self.rockAngle, self.perp2rot_axis.name)
		ynegx = self.yneg()
		if ynegx=="":
			print "No peak selected. Exiting..."
			self.rotation_axis(self.rotation_centre)
			print self.rotation_axis.name+" reset to: ", `self.rotation_axis()`
			self.perp2rot_axis(self.perp2rot_axis_ref)
			print self.perp2rot_axis.name+" reset to: ", `self.perp2rot_axis()`
			return
		else:
			print "You have entered a peak centre of ", `ynegx`, \
				" for the negative "+self.focus_axis.name+" x-axis scan."
		
		corrected_focus = self.calcdy(yposx,ynegx)
		self.applydycorrection(corrected_focus)
		print self.focus_axis.name+" now at corrected focal position: ", \
			`self.focus_axis()`
		self.rotation_axis(self.rotation_centre)
		print self.rotation_axis.name+" reset to: ", `self.rotation_axis()`
		self.perp2rot_axis(self.perp2rot_axis_ref)
		print self.perp2rot_axis.name+" reset to: ", `self.perp2rot_axis()`
		#self.dz(self.dz_ref)
		#print "dz reset to: ", `self.dz()`

#	def centre(self,scanRange,scanStep,rockAngle,diode):
#		self.scanRange  = scanRange
#		self.scanStep   = scanStep
#		self.rockAngle  = rockAngle
#		self.diode      = diode
#		self.perp2rot_axis_ref = self.perp2rot_axis()
#		self.dz_ref = self.dz()
#		self.focus_axis_ref = self.focus_axis()
#		self.ref_axis = self.rotation_axis() 
#		self.rotation_centre     = 58.0
#		self.rotation_axis(self.rotation_centre) #Start at 58.
#		self.perp2rot_axis_ref = self.perp2rot_axis()
#		self.dz_ref = self.dz()
#		print "Focal Alignment."
#		print "=============== "+self.focus_axis.name+" positive ================="
#		print "Rotate axis by +",`self.rockAngle`," and perform "+self.perp2rot_axis.name+" scan."
#		yposx = self.ypos()
#		if yposx=="":
#			print "No peak selected. Exiting..."
#			self.perp2rot_axis(self.perp2rot_axis_ref)
#			return
#		else:
#			print "You have entered a peak centre of ", `yposx`," for the positive "+self.focus_axis.name+" x-axis scan."
#
#		self.perp2rot_axis(self.perp2rot_axis_ref)
#		self.dz(self.dz_ref)
#		print "=============== "+self.focus_axis.name+" negative ================="
#		print "Centre & rotate axis by -",`self.rockAngle`," and perform "+self.perp2rot_axis.name+" scan."
#		ynegx = self.yneg()
#		if ynegx=="":
#			print "No peak selected. Exiting..."
#			self.perp2rot_axis(self.perp2rot_axis_ref)
#			return
#		else:
#			print "You have entered a peak centre of ", `ynegx`," for the negative "+self.focus_axis.name+" x-axis scan."
#		
#		corrected_focus = self.calcdy(yposx,ynegx)
#		self.applydycorrection(corrected_focus)
#		print self.focus_axis.name+" now at corrected focal position: ", `self.focus_axis()`
#		self.rotation_axis(self.rotation_centre)
#		print "axis reset to: ", `self.rotation_axis()`
#		self.perp2rot_axis(self.perp2rot_axis_ref)
#		print self.perp2rot_axis.name+" reset to: ", `self.perp2rot_axis()`
#		self.dz(self.dz_ref)
#		print "dz reset to: ",`self.dz()`

#	def cendz(self):
#		self.diode
#		scan([self.dz, 1, 2, 0.2, w, 0.2, self.diode])
#		#scanPeak(dz, 1, 2, 0.2, w, 0.2, self.diode)
#		print "Centring the DAC in height (dz), currently |axis =",`self.rotation_axis()`," deg| and |dz =",`self.dz()`, " mm|."
#		print "Scanning dz: ",str(self.dz_ref-self.scanRange),"->", str(self.dz_ref+self.scanRange)
#		
#		return self.scanAndGetCentre(self.dz, self.dz_ref-self.scanRange, self.dz_ref+self.scanRange, self.scanStep, w, 0.2, self.diode)

	def centre_perp(self):
		print "Centring the DAC in horizontal direction, "+ \
			self.rotation_axis.name+" =", `self.rotation_axis()`, "deg and "+ \
			self.perp2rot_axis.name+" =", `self.perp2rot_axis()`, "mm."
		print "Scanning "+self.perp2rot_axis.name+": ", \
			str(self.perp2rot_axis_ref+self.scanRange),"->", \
			str(self.perp2rot_axis_ref-self.scanRange)
		
		return self.scanAndGetCentre(self.perp2rot_axis,
			self.perp2rot_axis_ref+self.scanRange,
			self.perp2rot_axis_ref-self.scanRange, self.scanStep, self.diode)

	def scanAndGetCentre(self, motor, start, stop, step, param1, param2=-1, param3=-1):
		genericScanChecks(False, False, motor, start, stop, step, param1, param2, param3)
		if (self.autoFit):
			centre = fitStepFunction(0)
			userValue = InputCommands.requestInput("Type y to use peak centre"+
				" %f, or enter a different value (enter to quit)" % centre)
			if (userValue == "y"):
				return centre
			else:
				return userValue
		else:
			return InputCommands.requestInput("Please enter the peak centre or press enter to exit:")

	def ypos(self):
		if self.focus_axis_inverted:
			self.rotation_axis(self.rotation_centre-self.rockAngle)
		else:
			self.rotation_axis(self.rotation_centre+self.rockAngle)
		self.perp2rot_axis(self.perp2rot_axis_ref)
		yposx = self.centre_perp()
		return yposx

	def yneg(self):
		if self.focus_axis_inverted:
			self.rotation_axis(self.rotation_centre+self.rockAngle)
		else:
			self.rotation_axis(self.rotation_centre-self.rockAngle)
		self.perp2rot_axis(self.perp2rot_axis_ref)
		ynegx = self.centre_perp()
		return ynegx

	def calcdy(self,yposx,ynegx):
		self.rotation_axis(self.rotation_centre)
		delta_focus=(float(yposx)-float(ynegx))/(2*tan(self.rockAngle*pi/180))
		corrected_focus = self.focus_axis_ref+delta_focus
		print "Initial value of %s: %f" % (
			self.focus_axis.name, self.focus_axis_ref)
		print "Focal correction of: ",delta_focus
		return corrected_focus

	def applydycorrection(self,corrected_focus):
		corrected_focus = float(corrected_focus)
		lowLimit = float(self.beamline.getValue(None,"Top","-MO-DIFF-01:SAMPLE:Y.LLM"))
		highLimit = float(self.beamline.getValue(None,"Top","-MO-DIFF-01:SAMPLE:Y.HLM"))
		if self.focus_axis.name == "cryoz":
			lowLimit = self.focus_axis.lowerMotorLimit
			highLimit = self.focus_axis.upperMotorLimit
		if (corrected_focus >= lowLimit):
			if (corrected_focus <= highLimit):
				print "focus correction (" + `corrected_focus` + \
					") is within the upper (" + `highLimit` + \
					") and lower (" + `lowLimit` + ") limits."
				ans = InputCommands.requestInput("Apply this correction [y/n]:")
				if (ans == 'y'):
					print "Correcting focus axis to ", `corrected_focus`
					self.focus_axis(corrected_focus)
					print "%s now at corrected focal position: %f" % (
						self.focus_axis.name, self.focus_axis())
				elif (ans == 'n'):
					print self.focus_axis.name+" still at: ", `self.focus_axis()`
					print "Exiting script..."
				else:
					print "Use 'y' to indicate yes, and 'n' to indiciate no."
					ans = InputCommands.requestInput("Apply this correction [y/n]:")
					if (ans == 'y'):
						print "Correcting focus axis to ", `corrected_focus`
						self.focus_axis(corrected_focus)
						print "%s now at corrected focal position: %f" % (
							self.focus_axis.name, self.focus_axis())
					elif (ans == 'n'):
						print self.focus_axis.name+" still at: ", `self.focus_axis()`
						print "Exiting script..."
			else:
				print "Cannot correct %s (%f) above the the upper limit (%f)."\
					% (self.focus_axis.name, corrected_focus, highLimit)
		else:
			print "Cannot correct %s (%f) below the the lower limit (%f)."\
				% (self.focus_axis.name, corrected_focus, lowLimit)

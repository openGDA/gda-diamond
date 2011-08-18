import gda.scan.ScanBase
from gda.jython.commands import InputCommands
import java
from math import *
from GeneralScan import GeneralScan
from gdascripts.parameters import beamline_parameters
from scan_commands import scan
from operationalControl import genericScanChecks
from scanPeak import fitStepFunction

class CentreDAC(GeneralScan):
	"""
	CentreDAC(scanRange, scanStep, rockAngle, diode)
	
	Centers the sample (DAC) on the beam and the diffractometer center.
	Firstly finds the sample position about axis=-122 deg scan around the current position 
	in dx and dz +/- scanRange (mm) with a step size scanStep (mm). 
	Then the DAC is rotated +/- rockAngle (deg) about -122 degrees
	and the drift of the centre is used to correct the dy axis.

	Example: CentreDAC(dkphi, 0.4, 0.02, 10, d4)
	
	"""
	def __init__(self,axis,scanRange,scanStep,rockAngle,diode,autoFit, centre):
		print "Axis = ", axis
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		self.beamline= jythonNameMap.beamline
		self.axis = axis
		self.dx = jythonNameMap.dx
		self.dy = jythonNameMap.dy
		self.dz = jythonNameMap.dz
		self.scanRange  = scanRange
		self.scanStep   = scanStep
		self.rockAngle  = rockAngle
		self.diode      = diode
		self.ref_dx = self.dx()
		self.ref_dy = self.dy()
		self.ref_dz = self.dz()
		self.ref_axis = self.axis
		self.centre = centre
		self.autoFit = autoFit
		
		self.axis(self.centre)

	def centre(self):
		self.cendzdx()
		self.cendy()
		self.cendzdx()

	def cendzdx(self):
		print "Centre DAC in the x and z axes..."
		print "==================== dz ====================="
		peakdz = self.cendz()
		if peakdz=="":
			print "No peak selected. Exiting..."
			self.dz(self.ref_dz)
			return
		else:
			print "You have entered ", `peakdz`," as the peak value of the z-axis scan."
			self.dz(peakdz)
			print "dz now at: ", `self.dz()`

		print "==================== dx ====================="
		peakdx = self.cendx()
		if peakdx=="":
			print "No peak selected. Exiting..."
			self.dx(self.ref_dx)
			return
		else:
			print "You have entered ", `peakdx`," as the peak value of the x-axis scan."
			self.dx(peakdx)
			print "dx now at: ", `self.dx()`
		print "============================================="
   
	def cendy(self):
		self.ref_dx = self.dx.getPosition()
		self.ref_dz = self.dz.getPosition()
		print "Focal Alignment."
		print "=============== dy positive ================="
		print "Rotate axis by +",str(self.rockAngle)," and perform dx scan."
		yposx = self.ypos()
		if yposx=="":
			print "No peak selected. Exiting..."
			self.axis(self.centre)
			print "axis reset to: ", `self.axis()`
			self.dx(self.ref_dx)
			print "dx reset to: ", `self.dx()`
			return
		else:
			print "You have entered a peak centre of ", `yposx`," for the positive dy x-axis scan."

		self.dx(self.ref_dx)
		self.dz(self.ref_dz)
		print "=============== dy negative ================="
		print "Centre & rotate axis by -",`self.rockAngle`," and perform dx scan."
		ynegx = self.yneg()
		if ynegx=="":
			print "No peak selected. Exiting..."
			self.axis(self.centre)
			print "axis reset to: ", `self.axis()`
			self.dx(self.ref_dx)
			print "dx reset to: ", `self.dx()`
			return
		else:
			print "You have entered a peak centre of ", `ynegx`," for the negative dy x-axis scan."
		
		corrected_y = self.calcdy(yposx,ynegx)
		self.applydycorrection(corrected_y)
		print "dy now at corrected focal position: ", `self.dy()`
		self.axis(self.centre)
		print "axis reset to: ", `self.axis()`
		self.dx(self.ref_dx)
		print "dx reset to: ", `self.dx()`
		self.dz(self.ref_dz)
		print "dz reset to: ", `self.dz()`


	def centre(self,scanRange,scanStep,rockAngle,diode):
		self.scanRange  = scanRange
		self.scanStep   = scanStep
		self.rockAngle  = rockAngle
		self.diode      = diode
		self.ref_dx = self.dx()
		self.ref_dz = self.dz()
		self.ref_dy = self.dy()
		self.ref_axis = self.axis() 
		self.centre     = 58.0
		self.axis(self.centre) #Start at 58.
		self.ref_dx = self.dx()
		self.ref_dz = self.dz()
		print "Focal Alignment."
		print "=============== dy positive ================="
		print "Rotate axis by +",`self.rockAngle`," and perform dx scan."
		yposx = self.ypos()
		if yposx=="":
			print "No peak selected. Exiting..."
			self.dx(self.ref_dx)
			return
		else:
			print "You have entered a peak centre of ", `yposx`," for the positive dy x-axis scan."

		self.dx(self.ref_dx)
		self.dz(self.ref_dz)
		print "=============== dy negative ================="
		print "Centre & rotate axis by -",`self.rockAngle`," and perform dx scan."
		ynegx = self.yneg()
		if ynegx=="":
			print "No peak selected. Exiting..."
			self.dx(self.ref_dx)
			return
		else:
			print "You have entered a peak centre of ", `ynegx`," for the negative dy x-axis scan."
		
		corrected_y = self.calcdy(yposx,ynegx)
		self.applydycorrection(corrected_y)
		print "dy now at corrected focal position: ", `self.dy()`
		self.axis(self.centre)
		print "axis reset to: ", `self.axis()`
		self.dx(self.ref_dx)
		print "dx reset to: ", `self.dx()`
		self.dz(self.ref_dz)
		print "dz reset to: ",`self.dz()`

	def cendz(self):
		self.diode
		scan([self.dz, 1, 2, 0.2, w, 0.2, self.diode])
		#scanPeak(dz, 1, 2, 0.2, w, 0.2, self.diode)
		print "Centring the DAC in height (dz), currently |axis =",`self.axis()`," deg| and |dz =",`self.dz()`, " mm|."
		print "Scanning dz: ",str(self.ref_dz-self.scanRange),"->", str(self.ref_dz+self.scanRange)
		
		return self.scanAndGetCentre(self.dz, self.ref_dz-self.scanRange, self.ref_dz+self.scanRange, self.scanStep, w, 0.2, self.diode)


	def cendx(self):
		print "Centring the DAC in horizontal direction (dx), currently |axis =",`self.axis()`,"deg| and |dx =",`self.dx()`, "mm|."
		print "Scanning dx: ",str(self.ref_dx+self.scanRange),"->", str(self.ref_dx-self.scanRange)
		
		return self.scanAndGetCentre(self.dx, self.ref_dx+self.scanRange, self.ref_dx-self.scanRange, self.scanStep, self.diode)

	
	def scanAndGetCentre(self, motor, start, stop, step, param1, param2=-1, param3=-1):
		
		genericScanChecks(False, False, motor, start, stop, step, param1, param2, param3)
		if (self.autoFit):
			centre = fitStepFunction(0)
			userValue = InputCommands.requestInput("Type y to use peak centre " + str(centre) + ", or enter a different value (enter to quit)")
			if (userValue == "y"):
				return centre
			else:
				return userValue
		else:
			return InputCommands.requestInput("Please enter the peak centre or press enter to exit:")
			
	def ypos(self):
		self.axis(self.centre+self.rockAngle)
		self.dx(self.ref_dx)
		yposx = self.cendx()
		return yposx

	def yneg(self):
		self.axis(self.centre-self.rockAngle)
		self.dx(self.ref_dx)
		ynegx = self.cendx()
		return ynegx

	def calcdy(self,yposx,ynegx):
		self.axis(self.centre)
		delta_dy=(float(yposx)-float(ynegx))/(2*tan(self.rockAngle*pi/180))
		corrected_y = self.ref_dy+delta_dy
		print "Initial value of y: ",str(self.ref_dy)
		print "Focal correction of: ",delta_dy
		return corrected_y

	def applydycorrection(self,corrected_y):
		corrected_y = float(corrected_y)
		lowLimit = float(self.beamline.getValue(None,"Top","-MO-DIFF-01:SAMPLE:Y.LLM"))
		highLimit = float(self.beamline.getValue(None,"Top","-MO-DIFF-01:SAMPLE:Y.HLM"))
		if (corrected_y >= lowLimit):
			if (corrected_y <= highLimit):
				print "y correction (" + `corrected_y` + ") is within the upper (" + `highLimit` + ") and lower (" + `lowLimit` + ") limits."
				ans = InputCommands.requestInput("Apply this correction [y/n]:")
				if (ans == 'y'):
					print "Correcting y axis to ", `corrected_y`
					self.dy(corrected_y)
					print "dy now at corrected focal position: ", `self.dy()`
				elif (ans == 'n'):
					print "dy still at: ", `self.dy()`
					print "Exiting script..."
				else:
					print "Use 'y' to indicate yes, and 'n' to indiciate no."
					ans = InputCommands.requestInput("Apply this correction [y/n]:")
					if (ans == 'y'):
						print "Correcting y axis to ", `corrected_y`
						self.dy(corrected_y)
						print "dy now at corrected focal position: ", `self.dy()`
					elif (ans == 'n'):
						print "dy still at: ", `self.dy()`
						print "Exiting script..."
			else:
				print "Cannot correct dy (" + `corrected_y` + ") above the the upper limit (" + `highLimit` + ")."
		else:
			print "Cannot correct dy (" + `corrected_y` + ") below the lower limit (" + `lowLimit` + ")."

from gda.epics import CAClient
import java
from time import sleep
ca = CAClient()

#The questar microscope has a mirror to look at the sample position and a 
#diode (4) to measure the transmission through the sample. To move the 
#diode/mirror in/out of beam, the questar motors are used. There is also 
#a pneumatic to be opened/closed. 

class questar:

	def __init__(self):
	#The positions will change if the beam changes position."
		self.inBeamX = -11.978
		self.outBeamX = 19.90
		self.mirror = 7.92
		self.diode = 25.5
		self.SHUTTER_Record  = "-DI-PHDGN-03:CON"
		self.SHUTTER_Status  = "-DI-PHDGN-03:STA"
		self.SHUTTER_OPEN  = 0
		self.SHUTTER_CLOSE = 1
		self.SHUTTER_RESET = 2

#This D4 pneumatic is actuated in the epics by D3 (although the diode attached is D4!).

#Move the questar mirror in beam.
	def mirror(self):
#print "pos DR1CX -11.978"
#print "pos DR1CY 7.92"
		DR1CX(self.inBeamX)
		DR1CY(self.mirror)
		beamline.setValue("Top",self.SHUTTER_Record, self.SHUTTER_CLOSE)
		print "Mirror in beam. Close Pneumatic."

#Move the questar diode in beam
	def diode(self):
		DR1CX(self.inBeamX)
		DR1CY(self.diode)
		beamline.setValue("Top",self.SHUTTER_Record, self.SHUTTER_CLOSE)
		print "Diode in Beam. Close Pneumatic."

#Once aligned and wish to take data. 
#Put both mirror and diode out of beam to measure experimental diffraction data.
	def out(self):
#pos DR1CX 19.90
#		Microscope.DR1CX(self.outBeamX)
		DR1CX(self.outBeamX)
		beamline.setValue("Top",self.SHUTTER_Record, self.SHUTTER_OPEN)
		print "Mirror & Diode out of beam. Open Pneumatic."	





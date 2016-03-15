import java
import gda.device.scannable.ScannableBase
from math import sin, cos, asin, acos, sqrt, exp, degrees
from gdascripts.pd.time_pds import tictoc
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from gda.device import DeviceException

class BraggInkeV(gda.device.scannable.PseudoDevice,gda.observable.IObserver):

	"""
	    Purpose:       To enable energy in keV to be supplied instead of Bragg
                           This script controls all the necessary motors including id gap, bragg, perp
	"""

	def __init__(self, name, bragg):
		self.name = name
		self.setInputNames([name])
		self.bragg = bragg
		'''
		self.slope = 1.0006                # April 2013, coefficient changed to slope
		self.intercept = -0.0383            # April 2013, intercept added
		self.slope = 0.9990536                # November 2013
		self.intercept = -0.0083482            # November 2013
		self.slope = 1.0002945               # September 2014 - Direct calibration of EXAFS features in Bragg angle
		self.intercept = -0.02577            # September 2014 - Direct calibration of EXAFS features in Bragg angle
		self.slope = 1.0013725				# Jun 2015 - Direct calibration of EXAFS in Bragg
		self.intercept = -0.03556			# Jun 2015 - Direct calibration of EXAFS in Bragg
		'''
		self.slope = 1.00
		self.intercept = 0.0
		self.bragg.addIObserver(self)

	def update(self, observed, change):
		self.notifyIObservers(self, change)

	def isBusy(self):
		return self.bragg.isBusy()

	def getPosition(self):
		""" Return the keV value"""
		X=float(self.bragg.getPosition())
		exp = (X-self.intercept) / self.slope 
		return 12.3985/(6.2695*sin(exp*3.14159265/180)) 

	def asynchronousMoveTo(self,X):
		""" Moves to the keV value supplied """
		theta = 180/3.14159265*asin(12.3985/(X*6.2695))
		thetaExp = self.slope*theta+self.intercept
		self.bragg.asynchronousMoveTo(thetaExp)
		
class Harmonic:
	""" Constructor method give the initial values
	Harmonic peak positions from undulator spectra are fitted with a cubic function
	a = cubic term
	b = quadratic term
	c = linear term
	d = constant term
	"""
	
	def __init__(self, order, energyStart, energyEnd, a, b, c, d):
		self.name = "Harmonic "+str(order)
		self.energyStart = energyStart
		self.energyEnd = energyEnd
		self.EPSILON = 0.0005
		# y = a x*x + bx + c
		self.a = a
		self.b = b
		self.c = c
		self.d = d

	def getEnergy(self, position):
		c = self.c - position
		b = self.b
		a = self.a 
		delta = b*b - 4.0 * a*c
		if ( delta ) < 0:
			raise DeviceException("No real solution for the energy")

		x1 = ( - b + sqrt( delta ) ) / ( 2.0 * a )
		x2 = ( - b - sqrt( delta ) ) / ( 2.0 * a )
		if ( x1 >= (self.energyStart-self.EPSILON) and x1 < self.energyEnd ):			
			return x1 
		if ( x2 >= (self.energyStart-self.EPSILON) and x2 < self.energyEnd ):			
			return x2 
		raise DeviceException("Energy out of range for the "+self.name+". The 2 solutions for an ID gap of "+str(position)+"mm are "+str(x1)+" or "+str(x2))

	def getPosition(self, X):
		return self.a*X*X*X + self.b*X*X + self.c*X + self.d

	def getName(self):
		return self.name
	
	def isSelected(self, X):
		selected = False
#		print str(X)+" "+str(self.energyEnd)+" "+str(X<self.energyEnd)
		if ( X >= self.energyStart and X < self.energyEnd ):
			selected = True
		return selected	

class CalibratedID(gda.device.scannable.PseudoDevice):
	"""
	    Purpose:       To change the ID gap to the right energy value.It is assumed the DCM has been commissioned first.
	"""

	def __init__(self, name, id):
		""" Constructor method give the device a name - in this case CalibratedID"""
		self.name = name
		self.setInputNames([name])
		self.id = id
		self.selectedHarmonic = 3 
		harmonics =[]
		#                            fit y = ax^3 + bx^2 + cx +d
		#                            n: harmonic order
		#                            E1, E2: Energy range
		#                          n,   E1,   E2,       a,        b,       c,        d
		harmonics.append(Harmonic( 3,  3.6,  5.0, 0.0165500, -0.25328, 2.81477, -1.54599) )
		harmonics.append(Harmonic( 5,  5.0,  7.0, 0.0047000, -0.11913, 1.91751, -2.16431) )
		harmonics.append(Harmonic( 7,  7.0,  9.0, 0.0016000, -0.05737, 1.33471, -2.04875) )
		harmonics.append(Harmonic( 9,  9.0, 11.0, 0.0007599, -0.03490, 1.04028, -2.05728) )
		harmonics.append(Harmonic(11, 11.0, 13.5, 0.0004090, -0.02303, 0.84579, -2.02706) ) # extended range of 11th harmonic for Mascotto experiment
		harmonics.append(Harmonic(13, 13.5, 15.0, 0.0003369, -0.02115, 0.79635, -2.48642) )
		harmonics.append(Harmonic(15, 15.0, 17.0, 0.0001630, -0.01305, 0.64662, -2.27659) )
		harmonics.append(Harmonic(17, 17.0, 19.0,         0, -0.00379, 0.44713, -1.46301) )
		harmonics.append(Harmonic(19, 19.0, 23.5,         0, -0.00237, 0.37332, -1.19618) )
		self.harmonics = harmonics

	def isBusy(self):
		return self.id.isBusy()

	def getPosition(self):
		return float(self.id.getPosition())

	def asynchronousMoveTo(self,X):
		self.id.asynchronousMoveTo(self.calculateposition(X)-0.005)

	def getSelectedHarmonic(self, X):
		n = len(self.harmonics)
		for i in range (n):
			if ( self.harmonics[i].isSelected(X) ):
				return i
 		raise DeviceException("No harmonics found for the selected energy")

	def calculateposition(self, X):
		self.selectedHarmonic = self.getSelectedHarmonic(X)
		return self.harmonics[self.selectedHarmonic].getPosition(X)

	def test(self , start, end , step):
		energy_position = start 
		while ( energy_position <= end ):
			position = self.position( energy_position )
			selectedHarmonic = self.getSelectedHarmonic(energy_position)
			e = self.harmonics[selectedHarmonic].getEnergy(position)

			if ( position < 26.00 ):
				print str(energy_position) + " , " + str(position) +" , "+ str(e)
			energy_position = energy_position + step
		print "Done"

class CalibratedPerp(gda.device.scannable.PseudoDevice):
	"""
	    Purpose: To move perp at the right value when changing the energy. THE DCM needs to be calibrated first with foils.
	"""
	
	'''
	Values from prior to Feb '14
	intercept = -1.8628
	slope = 14.7664
	
	Values from prior to Nov '14
	intercept = -0.4829
	slope = 12.9295
	'''

	def __init__(self, name, perp):
		self.name = name
		self.setInputNames([name])
		self.perp = perp
		self.intercept = -0.32111
		self.slope = 12.78805
		
	def isBusy(self):
		""" This device is busy if perp is moving """
		return self.perp.isBusy()

	def getPosition(self):
		""" Return the perp value"""
		perp_position = float(self.perp.getPosition())
		return perp_position
	
	def asynchronousMoveTo(self,X):
		""" Moves to the perp value according to the energy supplied """
		
		costheta = cos(asin(12.3985/(X*6.2712)))
		self.perp.asynchronousMoveTo(self.slope/costheta+self.intercept)
		
		
class CalibratedPitch(gda.device.scannable.PseudoDevice):
	"""
	    Purpose: To move pitch at the right value when changing the energy. THE DCM needs to be calibrated first with foils.
	"""

	def __init__(self, name, pitch):
		self.name = name
		self.setInputNames([name])
		self.pitch = pitch
		self.intercept = 186.1418
		self.coefficient = 17.0967
		
	def isBusy(self):
		""" This device is busy if pitch is moving """
		return self.pitch.isBusy()

	def getPosition(self):
		""" Return the pitch value"""
		pitch_position = float(self.pitch.getPosition())
		energy = exp((-pitch_position - self.intercept)/self.coefficient)
		return energy 

	def asynchronousMoveTo(self,X):
		""" Moves to the perp value according to the energy supplied """
		#self.pitch.moveTo(self.pitch.getPosition()-20)
		self.pitch.moveTo(-1*(self.coefficient*log(X)+self.intercept)+20)
		sleep(2)
		self.pitch.asynchronousMoveTo(-1*(self.coefficient*log(X)+self.intercept))


class PilatusThreshold(ScannableMotionBase):
	def __init__(self, name, pvbase):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames([])
		self.Units=['keV']
		self.setOutputFormat(['%4.2f'])
		self.setLevel(7)
		self.timer=tictoc()
		self.waitUntilTime = 0
		self.demand = 0.0
		self.gain = CAClient(pvbase+":GainMenu")
		self.thres = CAClient(pvbase+":ThresholdEnergy")
		self.gain.configure()
		self.thres.configure()
		self.gainranges = { 0 : [6.5, 19.7], 1 : [4.4, 14.0], 2 : [3.8, 11.4] }
		self.thresholdtolerance = 0.1
		self.waittime = 3

	def rawGetPosition(self):
		return float(self.thres.caget()) * 2.0

	def rawAsynchronousMoveTo(self,newpos):
		# gain
		gain = int(self.gain.caget())
		if newpos >= self.gainranges[gain][0] and newpos <= self.gainranges[gain][1]:
			# gain ok
			pass
		else:
			for i in self.gainranges.keys():
				if newpos >= self.gainranges[i][0] and newpos <= self.gainranges[i][1]:
					self.gain.caput(i)	
					self.timer.reset()
					break
			# raise exception, value out of range
		# threshold
		thres = float(self.thres.caget())
		if abs((thres * 2.0) - newpos) < newpos * self.thresholdtolerance:
			# threshold ok
			pass
		else:
			self.thres.caput(newpos / 2.0)
			self.timer.reset()
	
	def rawIsBusy(self):
		return (self.timer()<self.waittime)

pilthres = PilatusThreshold("pilthres", "BL22I-EA-PILAT-01:cam1")
pilthresWAXS_L = PilatusThreshold("pilthresWAXS_L", "BL22I-EA-PILAT-03:cam1")
calibrated_perp = CalibratedPerp("calibrated_perp", dcm_perp)
calibrated_ID = CalibratedID("calibrated_ID", idgap_mm)
bkeV = BraggInkeV("bkeV", dcm_bragg)
bkeV.setProtectionLevel(3)
energy.setBragg(bkeV)
energy.clearScannables()
for i in [calibrated_ID, calibrated_perp, pilthres, pilthresWAXS_L]:
	energy.addScannable(i)

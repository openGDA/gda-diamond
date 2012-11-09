import java
import gda.device.scannable.ScannableBase
from math import sin, cos, asin, acos, sqrt
from gdascripts.pd.time_pds import tictoc
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class Energy(gda.device.scannable.PseudoDevice):
	"""
	    Purpose:       To change the bragg angle and all other energy setting devices to a common energy
	"""

	def __init__(self, name, mono, aux):
		""" Constructor method give the device a name - in this case energy"""
		self.name = name
		self.devices = aux
		self.setInputNames([name])
		self.setExtraNames([a.getInputNames()[0] for a in aux])
		self.devices.insert(0, mono)
		self.setOutputFormat(["%5.3f" for i in range(len(self.devices))])

	def isBusy(self):
		""" This device is busy if Bragg, perp or id gap is moving"""
		for device in self.devices:
			if device.isBusy():
				return True
		return False

	def getPosition(self):
		""" Return the energy value"""
		return [ device.getPosition() for device in self.devices ] 

	def asynchronousMoveTo(self,X):
		""" Moves to the energy value supplied """
		for device in self.devices:
			device.asynchronousMoveTo(float(X))

class BraggInkeV(gda.device.scannable.PseudoDevice):
	"""
	    Purpose:       To enable raw keV to be supplied instead of Bragg i.e. no additional mono motor moves
	"""

	def __init__(self, name, bragg):
		self.name = name
		self.setInputNames([name])
		self.bragg = bragg

	def isBusy(self):
		return self.bragg.isBusy()

	def getPosition(self):
		""" Return the keV value"""
		X=float(self.bragg.getPosition())
		return 12.3985/(6.2712*sin(X*3.14159265/180)) 

	def asynchronousMoveTo(self,X):
		""" Moves to the keV value supplied """
		self.bragg.asynchronousMoveTo(180/3.14159265*asin(12.3985/(X*6.2712)))

class Harmonic:
	""" Constructor method give the initial values"""
	def __init__(self, order, energyStart, energyEnd, a, b, c):
		self.name = "Harmonic "+str(order)
		self.energyStart = energyStart
		self.energyEnd = energyEnd
		self.EPSILON = 0.0005
		# y = a x*x + bx + c
		self.a = a
		self.b = b
		self.c = c

	def getEnergy(self, position):
		c = self.c - position
		b = self.b
		a = self.a 
		delta = b*b - 4.0 * a*c
		if ( delta ) < 0:
			raise DeviceException("No real solution for the energy")

		x1 = ( - b + sqrt( delta ) ) / ( 2.0 * a )
		x2 = ( - b - sqrt( delta ) ) / ( 2.0 * a )
#		print x1
#		print self.energyStart
#		print self.energyEnd
#		print self.energyEnd-self.EPSILON
		if ( x1 >= (self.energyStart-self.EPSILON) and x1 < self.energyEnd ):			
			return x1 
		if ( x2 >= (self.energyStart-self.EPSILON) and x2 < self.energyEnd ):			
			return x2 
		raise DeviceException("Energy out of range for the "+self.name+". The 2 solutions for an ID gap of "+str(position)+"mm are "+str(x1)+" or "+str(x2))

	def getPosition(self, X):
		return self.a*X*X + self.b*X + self.c

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
		""" Constructor method give the device a name - in this case bkeV"""
		self.name = name
		self.setInputNames([name])
		self.id = id
		self.selectedHarmonic = 3 
		harmonics =[]
		#                            fit y = a x*x + bx + c
		#                            n: harmonic order
		#                            E1, E2: Energy range
		#                              n,    E1  ,   E2 ,    a   ,   b   ,   c
		harmonics.append(Harmonic( 3,  3.70,  5.95, -0.0154, 1.6875,  0.2278) )
		harmonics.append(Harmonic( 5,  5.95,  8.29, -0.0110, 1.0901, -0.0450) )
		harmonics.append(Harmonic( 7,  8.29, 10.66, -0.0115, 0.8957, -0.6364) )
		harmonics.append(Harmonic( 9, 10.66, 13.05, -0.0075, 0.7111, -0.7234) )
		harmonics.append(Harmonic(11, 13.05, 15.44, -0.0058, 0.6035, -0.8664) )
		harmonics.append(Harmonic(13, 15.44, 17.81, -0.0043, 0.5170, -0.9191) )
		harmonics.append(Harmonic(15, 17.81, 23.11, -0.0032, 0.4478, -0.9143) )
		self.harmonics = harmonics

	def isBusy(self):
		return self.id.isBusy()

	def getPosition(self):
		X = float(bkeV.getPosition())
		id_position = self.id.getPosition()
		if (id_position < 5.9):
			raise DeviceException("ID gap out of range (<6mm)")
		if (id_position > 10.0):
			raise DeviceException("ID gap out of range (>10mm)")
#		selectedHarmonic = self.getSelectedHarmonic(X)
#		print "position at harmonic "+self.harmonics[self.selectedHarmonic].getName()
		return self.harmonics[self.selectedHarmonic].getEnergy(id_position)

	def asynchronousMoveTo(self,X):
		self.id.asynchronousMoveTo(self.position(X))

	def getSelectedHarmonic(self, X):
		n = len(self.harmonics)
		for i in range (n):
			if ( self.harmonics[i].isSelected(X) ):
				return i
 		raise DeviceException("No harmonics found for the selected energy")

	def position(self, X):
		self.selectedHarmonic = self.getSelectedHarmonic(X)
#		print "moveto harmonic "+self.harmonics[self.selectedHarmonic].getName()
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
	    Purpose:       To move perp at the right value when changing the energy. THE DCM needs to be calibrated first with foils.
	"""

	def __init__(self, name, perp):
		self.name = name
		self.setInputNames([name])
		self.perp = perp
		self.intercept = 0.
		self.slope = 13.035

	def isBusy(self):
		""" This device is busy if perp is moving """
		return self.perp.isBusy()

	def getPosition(self):
		""" Return the perp value"""
		perp_position = float(self.perp.getPosition())
		cosTheta = self.slope / ( perp_position - self.intercept )
		if (cosTheta > 1):
			raise DeviceException("position for %s out of reasonable range"%self.perp.getName())
		theta = acos(cosTheta)
		energy = (12.3985/6.2712) / ( sin(theta) )
		return energy 

	def asynchronousMoveTo(self,X):
		""" Moves to the perp value according to the energy supplied """
		costheta = cos(asin(12.3985/(X*6.2712)))
		self.perp.asynchronousMoveTo( self.slope/costheta+self.intercept)

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
		self.waittime = 30

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
calibrated_perp = CalibratedPerp("calibrated_perp", perp)
calibrated_ID = CalibratedID("calibrated_ID", idgap_mm)
bkeV = BraggInkeV("bkeV", bragg)
#energy = Energy("energy", bkeV, [pilthres])
energy = Energy("energy", bkeV, [calibrated_ID, calibrated_perp, pilthres])

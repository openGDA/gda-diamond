from java.lang import Double
from gda.device.enumpositioner import EpicsSimpleMbbinary

THRESHOLD_ERROR = 'Cannot access %s: check detector is connected and run ' +\
		'%s.configure()'

class PilatusThreshold(ScannableMotionBase):
	def __init__(self, name, pvbase):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames([])
		self.Units=['keV']
		self.setOutputFormat(['%4.2f'])
		self.setLevel(7)
		self.timer=tictoc()
		self.waittime = 3
		self.thresholdtolerance = 0.1
		self.pvbase = pvbase
		self.configure()

	def configure(self):
		try:
			self.thres = CAClient(self.pvbase+":ThresholdEnergy")
			self.thres.configure()
			self.thres.caget()
		except:
			print THRESHOLD_ERROR % (self.name, self.name)
			self.thres = DummyThreshold(self.name)

	def rawGetPosition(self):
		try:
			return float(self.thres.caget()) * 2.0
		except:
			self.thres.clearup()
			self.thres = DummyThreshold(self.name)
			return self.thres.caget()

	def rawAsynchronousMoveTo(self,newpos):
		thres = float(self.thres.caget())
		if abs((thres * 2.0) - newpos) < newpos * self.thresholdtolerance:
			# threshold ok
			pass
		else:
			self.thres.caput(newpos / 2.0)
			self.timer.reset()

	def rawIsBusy(self):
		return (self.timer()<self.waittime)

class DummyThreshold:
	def __init__(self, name):
		self.name = name
	def caget(self):
		#when position cannot be accessed return NaN
		return Double.NaN
	def caput(self, newVal):
		print THRESHOLD_ERROR %(self.name, self.name)
		return

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

	def __init__(self, name, id_gap, check):
		""" Constructor method give the device a name - in this case CalibratedID"""
		self.name = name
		self.setInputNames([name])
		self.id_gap = id_gap
		self.selectedHarmonic = 3
		self.check = check
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
		return self.check() == 'ENABLED' and self.id_gap.isBusy()

	def getPosition(self):
		return float(self.id_gap.getPosition())

	def asynchronousMoveTo(self,X):
		if self.check() == 'ENABLED':
			self.id_gap.asynchronousMoveTo(self.calculateposition(X)-0.005)
		else:
			print 'Not moving ID gap - access is disabled'

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


class CalibratedOffset(gda.device.scannable.PseudoDevice):
	"""Set offset to 25 every time"""

	def __init__(self, name, offset):
		self.name = name
		self.setInputNames([name])
		self.offset_motor = offset

	def isBusy(self):
		""" This device is busy if offset is moving """
		return self.offset_motor.isBusy()

	def getPosition(self):
		""" Return the offset value"""
		offset_position = float(self.offset_motor.getPosition())
		return offset_position
	
	def asynchronousMoveTo(self,X):
		"""set to 25 offset compound motor need to be calibrated"""
		
		self.offset_motor.asynchronousMoveTo(25)


pilthres = PilatusThreshold("pilthres", "BL22I-EA-PILAT-01:CAM")
pilthresWAXS_L = PilatusThreshold("pilthresWAXS_L", "BL22I-EA-PILAT-03:CAM")
calibrated_offset = CalibratedOffset("calibrated_offset", dcm_offset)
id_enabled = EpicsSimpleMbbinary()
id_enabled.name = 'id_enabled'
id_enabled.recordName = 'SR22I-MO-SERVC-01:IDBLENA'
id_enabled.configure()
calibrated_ID = CalibratedID("calibrated_ID", idgap_mm, check=id_enabled)
energy.clearScannables()
for i in [calibrated_ID, calibrated_offset, pilthres, pilthresWAXS_L]:
	energy.addScannable(i)

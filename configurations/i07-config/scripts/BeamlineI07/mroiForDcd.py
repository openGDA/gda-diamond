import math
from gda.device.scannable import DummyScannable

class mroiAngleDevice(ScannableBase):

	def __init__(self, name, motorOmega, motorLambda, func):
		self.name = name
		self.baseMotor = motorOmega
		self.lamMotor = motorLambda
		self.func = func
		self.inputNames = []
		self.extraNames = ['out']
		self.outputFormat = ['%5.5g']

	def getPosition(self):
		return self.func( self.baseMotor.getPosition(), self.lamMotor.getPosition() )

def thetaFunc( omega, lam ):
	dth = math.asin(lam / (2 * 3.740652))
	sth = math.sin(math.radians(omega)) * math.sin(2 * dth )
	return math.degrees(math.asin(sth))

def gammaFunc( omega, lam ):
	dth = math.asin(lam / (2 * 3.740652))
	sgam = math.sin(math.pi / 2 - math.radians(omega)) * math.sin(2 * dth)
	return math.degrees(math.asin(sgam))

thetaAngleDevice = mroiAngleDevice('thetaAngleDevice', dcdomega, dcm1lambda, thetaFunc)
gammaAngleDevice = mroiAngleDevice('gammaAngleDevice', dcdomega, dcm1lambda, gammaFunc)

def configureMroiForDcd(beamX=600, beamY=600, sizeX=20, sizeY=20, distance=3,
		thetaDevice=thetaAngleDevice, gammaDevice=gammaAngleDevice):
	mroi.clearRois()
	mroi.setAngleDevice(thetaDevice, gammaDevice)
	mroi.setGammaZero(gammaDevice.func(0, gammaDevice.lamMotor.getPosition()))
	mroi.setDistance(distance)
	mroi.setBeamRoiByCentre(beamX, beamY, sizeX, sizeY)

configureMroiForDcd()

dummy_dcd_omega = DummyScannable('dummy_dcd_omega')
dummy_dcd_lambda = DummyScannable('dummy_dcd_lambda')

dummyThetaDevice = mroiAngleDevice('dummyThetaDevice', dummy_dcd_omega, dummy_dcd_lambda, thetaFunc)
dummyGammaDevice = mroiAngleDevice('dummyGammaDevice', dummy_dcd_omega, dummy_dcd_lambda, gammaFunc)

pos dummy_dcd_omega dcdomega()
pos dummy_dcd_lambda dcm1lambda()


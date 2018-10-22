
#from i06Magnet import *
import math

def sph2cartesian(rho, theta, phi):
	# NB. Units used in GDA are DEGREE for PHI and THETA
	# print "sph2cartesian, rho: %f, theta: %f, phi: %f" % (rho, theta, phi) 
	x = rho * math.cos(deg2rad(phi)) * math.sin(deg2rad(theta))
	y = rho * math.sin(deg2rad(phi)) * math.sin(deg2rad(theta))
	z = rho * math.cos(deg2rad(theta))
	# rho2 = math.sqrt(x*x + y*y + z*z)
	# transform "standard" axes to beamline axes (x->z, y->x, z->y)
	xBL = y
	yBL = z
	zBL = x
	return (xBL, yBL, zBL)
	
def cartesian2sph(x, y, z):
	xBL = y
	yBL = z
	zBL = x
	rootSumSquares = math.sqrt(x*x + y*y + z*z)
	if (rootSumSquares == 0):
		return (0, 0, 0)
	rho = rootSumSquares
	# phi = rad2deg(math.atan2(y, x))
	phi = rad2deg(math.atan2(x, z))
	# theta = rad2deg(math.acos(z/rootSumSquares))
	theta = rad2deg(math.acos(y/rootSumSquares))
	return (rho, theta, phi)


def sph2cartesianBL(rho, theta, phi):
	"""
	Convert BL spherical coordinates to cartesian coordinates (x,y,z)
	using the beamline geometry
	"""
	# NB. Units used in GDA are DEGREE for PHI and THETA

	z = rho * math.sin(deg2rad(theta)) * math.cos(deg2rad(phi))
	x = rho * math.sin(deg2rad(theta)) * math.sin(deg2rad(phi))
	y = rho * math.cos(deg2rad(theta))
	return (x, y, z)
	
def cartesian2sphBL(x, y, z):
	"""
	Convert BL cartesian coordinates (x,y,z) to spherical coordinates (r, th, phi),
	using the beamline geometry
	"""
	rootSumSquares = math.sqrt(x*x + y*y + z*z)
	if (rootSumSquares == 0):
		return (0, 0, 0)
	rho = rootSumSquares
	phi = rad2deg(math.atan2(x, z))
	theta = rad2deg(math.acos(y/rho))
	return (rho, theta, phi)

def sph2cartesianBL2(rho, theta, phi):
	"""
	Convert BL spherical coordinates to cartesian coordinates (x,y,z)
	using the beamline geometry
	
	theta and phi swapped (i06 convention)
	theta: 0-360
	phi: 0-180
	"""
	# NB. Units used in GDA are DEGREE for PHI and THETA

	z = rho * math.sin(deg2rad(phi)) * math.cos(deg2rad(theta))
	x = rho * math.sin(deg2rad(phi)) * math.sin(deg2rad(theta))
	y = rho * math.cos(deg2rad(phi))
	return (x, y, z)
	
def cartesian2sphBL2(x, y, z):
	"""
	Convert BL cartesian coordinates (x,y,z) to spherical coordinates (r, th, phi),
	using the beamline geometry
	"""
	rootSumSquares = math.sqrt(x*x + y*y + z*z)
	if (rootSumSquares == 0):
		return (0, 0, 0)
	rho = rootSumSquares
	theta = rad2deg(math.atan2(x, z))
	phi = rad2deg(math.acos(y/rho))
	return (rho, theta, phi)
	
def deg2rad(degrees):
	return degrees * math.pi / 180
	
def rad2deg(radians):
	return radians * 180 / math.pi	

class MagnetTester():
	magnetScanabbles = ["XDMD", "YDMD", "ZDMD", "XRBV", "YRBV", "ZRBV", "RAMPSTATUS", "LIMITSTATUS", "MODE", "START"]
	
	def __init__(self):
		pass
		#self.magnet = I06Magnet("magnet")
		#print "magnet: " + str(self.magnet) + ", name: " + self.magnet.name
	
	def test(self):
		print "\n** magnetTester.test()"
		self.testGettersSetters()
		self.testTransformations()
		
		
	def testGettersSetters(self):
		print "\n** testGettersSetters()"
		
		
	def testTransformations(self):
		print "\n** testTransformations()"
		#self.testCartesian2Sph()
		self.testSph2Cartesian()
		
		
	def testCartesian2Sph(self):
		print "\n** testCartesian2Sph()"
		startCoordValue = -1
		endCoordValue = 1
		coordIncr = 0.5
		x = startCoordValue
		while x <= endCoordValue:
			y = startCoordValue
			while y <= endCoordValue:
				z = startCoordValue
				while z <= endCoordValue:
					(rho, theta, phi) = cartesian2sphBL2(x, y, z)
					(x2, y2, z2) = sph2cartesianBL2(rho, theta, phi)
					print "xyz: [%4.1f,%4.1f,%4.1f], r: %4.2f, t: %6.2f, p: %7.2f, xyz_2: [%4.1f,%4.1f,%4.1f]" % (x, y, z, rho, theta, phi, x2, y2, z2)
					z += coordIncr
				y += coordIncr
			x += coordIncr
		print "end of testCartesian2Sph()"
		
		
	def testSph2Cartesian(self):
		'''
		convention: 
		theta: 0-360
		phi: 0-180 
		'''
		print "\n** testSph2Cartesian(), rho constant = 1"
		self.testTheta()
		self.testPhi()
		self.testPhiTheta()
		
		
	def testTheta(self):
		print "\n** testTheta(0-360), phi = 0 (y=0), sweep in the x-z plane"
		phi = 90;
		thetaStart = 0; thetaEnd = 360; thetaIncr = 45
		theta = thetaStart
		while theta <= thetaEnd:
			rho = 1
			(x, y, z) = sph2cartesianBL2(rho, theta, phi)
			(rho2, theta2, phi2) = cartesian2sphBL2(x, y, z)
			print "th: %5.1f, ph: %5.1f, xyz: [%5.2f, %5.2f, %5.2f], rtp_2: %7.1f %7.1f %7.1f" % (theta, phi, x, y, z, rho2, theta2, phi2)
			theta += thetaIncr			

		
	def testPhi(self):
		print "\n** testPhi(0-180), theta = 0 (rotate rho about the x-axis from +y (phi=0) to -y (phi=180) in the positive z half-plane)"
		rho = 1
		theta = 0;
		phiStart = 0; phiEnd = 180; phiIncr = 45
		phi = phiStart
		while phi <= phiEnd:
			(x, y, z) = sph2cartesianBL2(rho, theta, phi)
			(rho2, theta2, phi2) = cartesian2sphBL2(x, y, z)
			print "th: %5.1f, ph: %6.1f, xyz: [%5.2f, %5.2f, %5.2f], rtp_2: %7.1f %7.1f %7.1f" % (theta, phi, x, y, z, rho2, theta2, phi2)
			phi += phiIncr

		
	def testPhiTheta(self):
		print "\n** testPhiTheta, rho constant = 1"
		# angles in degrees (GDA convention)
		thetaStart = -180; thetaEnd = 180; thetaIncr = 45
		phiStart = 0; phiEnd = 180; phiIncr = 45
		theta = thetaStart
		while theta <= thetaEnd:
			phi = phiStart
			while phi <= phiEnd:
				rho = 1
				(x, y, z) = sph2cartesianBL2(rho, theta, phi)
				(rho2, theta2, phi2) = cartesian2sphBL2(x, y, z)
				print "th: %6.1f, ph: %6.1f, xyz: [%5.2f,%5.2f,%5.2f], t2: %6.1f, p2: %6.1f, r2: %3.1f" % (theta, phi, x, y, z, theta2, phi2, rho2)
				phi += phiIncr
			theta += thetaIncr
		print "end of testSph2Cartesian()"
	
		
	def testArraysEqual(self, a1, a2):
		print "a1: " + str(a1) + ", a2: " + str(a2)
		for i in range(len(a1)):
			if (a1[i] != a2[i]):
				return False
		return True
		

def testMagnet():
	magnetTester = MagnetTester()	
	magnetTester.test()
	
	
if __name__ == '__main__':
	testMagnet()
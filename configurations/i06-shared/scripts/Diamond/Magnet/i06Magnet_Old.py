import math

class I06Magnet:
	modes = ["UNIAXIAL_X", "UNIAXIAL_Y", "UNIAXIAL_Z", "SPHERICAL", "PLANAR_XZ"]
	# PVs
	pvMap = {"XDMD": "BL06J-EA-MAG-01:X:DMD", 
			"YDMD": "BL06J-EA-MAG-01:Y:DMD", 
			"ZDMD": "BL06J-EA-MAG-01:Z:DMD", 
			"XRBV": "BL06J-EA-MAG-01:X:RBV", 
			"YRBV": "BL06J-EA-MAG-01:Y:RBV",
			"ZRBV": "BL06J-EA-MAG-01:Z:RBV",
			"RAMPSTATUS": "BL06J-EA-MAG-01:RAMPSTATUS", 
			"LIMITSTATUS": "BL06J-EA-MAG-01:LIMITSTATUS", 
			"MODE": "BL06J-EA-MAG-01:MODE", 
			"START": "BL06J-EA-MAG-01:STARTRAMP"}
	# descriptions, element: description, type, read only
	pvDesc = {"XDMD": "X field demand, pv, false",
			"YDMD":	"Y field demand, pv, false",
			"ZDMD":	"Z field demand, pv, false",
			"XRBV":	"X field readback, pv, true",
			"YRBV":	"Y field readback, pv, true",
			"ZRBV":	"Z field readback, pv, true",
			"RAMPSTATUS": "Ramp status, binary, true",
			"LIMITSTATUS": "Limit violation status, binary, true",
			"MODE":	"Operational mode, mbbinary, false",
			"START": "Request to start ramp, pv, false"} 
	
	def __init__(self, name):
		self.name = name
		
	# print object
		
	def printModes(self):
		print "\nmodes:"
		for i in range(len(self.modes)):
			print "%d: %s" % (i, self.modes[i])
		
	def printPvMap(self):
		print "\nPV map:"
		sortedKeys = sorted(self.pvMap.keys())
		for key in sortedKeys:
			value = self.pvMap[key]
			print key + ": " + value
			
	def printDesc(self):
		print "\nPV description:"
		print "keys: " + str(self.pvDesc.keys())
		sortedKeys = sorted(self.pvDesc.keys())
		print "sortedKeys: " + str(sortedKeys)
		for key in sortedKeys:
			value = self.pvDesc[key]
			print key + ": " + value
			#(desc, type, ro) = value.split(', ')
			#print "desc: " + desc + ", type: " + type + ", ro: " + ro
			
	# validate the ranges for a given mode
	def validateMode(self):
		# is validation of field values done already by EPICS?
		pass
	
	def sph2cartesian(self, rho, phi, theta):
		# NB. Units used in GDA are DEGREE for PHI and THETA
		x = rho * math.sin(self.degrees2radians(phi)) * math.sin(self.degrees2radians(theta))
		y = rho * math.cos(self.degrees2radians(phi))
		z = rho * math.sin(self.degrees2radians(phi)) * math.cos(self.degrees2radians(theta))
		rho2 = math.sqrt(x*x + y*y + z*z)
		return (x, y, z, rho2)
	
	def cartesian2sph(self, rho, x, y, z):
		rootSumSquares = math.sqrt(x*x + y*y + z*z)
		if (rootSumSquares == 0):
			return (0, 0, 0)
		rho = rootSumSquares
		phi = self.radians2degrees(math.atan2(y, x))
		theta = self.radians2degrees(math.acos(z/rootSumSquares))
		return (rho, phi, theta)
	
	def degrees2radians(self, degrees):
		return degrees * math.pi / 180
	
	def radians2degrees(self, radians):
		return radians * 180 / math.pi	
	
	def testTransformations(self):
		self.testSph2Cartesian()
		self.testCartesian2sph()
		
	def testSph2Cartesian(self):
		print "testSph2Cartesian"
		
	def testCartesian2sph(self):
		print "testCartesian2Sph"
	
	
def testI06Magnet():
	magnet = I06Magnet("i06Magnet")
	magnet.printModes()
	magnet.printPvMap()
	magnet.printDesc()
	magnet.testTransformations()
	
if __name__ == '__main__':
	testI06Magnet()

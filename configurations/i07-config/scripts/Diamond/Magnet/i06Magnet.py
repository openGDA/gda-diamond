from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
import random
import math

#from i06Magnet import *

"""
Dummy PDs to simulate operation of the magnet, without connecting to PVs
"""

# PDs to simulate
# magmode
# magx, magy, magz
# magrho, magphi, magtheta, magspherical (rho, theta, phi together)
# magtemp1, magtemp2
# magposx, magpsy, magrot

# PVs to access:
# magnetBasePVName = "BL06J-EA-MAG-01:"
# xFieldSetPVName = magnetBasePVName + "X:DMD"
# xFieldGetPVName = magnetBasePVName + "X:RBV"
# yFieldSetPVName = magnetBasePVName + "Y:DMD"
# yFieldGetPVName = magnetBasePVName + "Y:RBV"
# zFieldSetPVName = magnetBasePVName + "Z:DMD"
# zFieldGetPVName = magnetBasePVName + "Z:RBV"
# rampStatusPVName = magnetBasePVName + "RAMPSTATUS"
# limitStatusPVName = magnetBasePVName + "LIMITSTATUS"
# modePVName = magnetBasePVName + "MODE"
# startRampPVName = magnetBasePVName + "STARTRAMP"

class i06Magnet:
	"""
	The i06Magnet class is a wrapper for the i06 SCM PVs.
	It also defines several "real" and "virtual" scannables.
	
	Usage:
	
	To make a new magnet object:
	>>> mag = i06Magnet()
	
	To list the GDA magnet components:
	>>> mag.__dict__ 
	"""
	magnetBasePVName = "BL06J-EA-MAG-01:"
	
	def __init__(self, name):
		print "new magnet, name:" + name
		self.initMagnetValues()
		self.initPVs()
		self.initOtherMagnetPVs()
		self.initScannables()
		
	def initPVs(self):
		# make a hashtable of key:CAClient pairs for setting directional field strengths
		i06MagnetPvRoot = "BL06J-EA-MAG-01:"
		i06MagnetPvNames = ["X:DMD", "X:RBV", "Y:DMD", "Y:RBV", "Z:DMD", "Z:RBV", "RAMPSTATUS", "LIMITSTATUS", "MODE", "STARTRAMP.PROC"]
		self.pvs = {}
		for pvKey in i06MagnetPvNames:
			pvName = i06MagnetPvRoot + pvKey
			#print "pvName: " + pvName
			pv = CAClient(pvName)
			pv.configure()
			self.pvs[pvKey] = pv
		print "pvs: " + str(self.pvs)

	def initOtherMagnetPVs(self):
		# make a hashtable of key:CAClient pairs for other magnet-related detectors
		otherMagnetPvsData = [["Magnet temperature 1", "TMON.T1", "BL06J-EA-TMON-01:T1", "true"],
							  ["Magnet temperature 2", "TMON.T2", "BL06J-EA-TMON-01:T2", "true"],
							  ["Magnet temperature 3", "TMON.T3", "BL06J-EA-TMON-01:T3", "true"],
							  ["Nitrogen Level", "TMON.NL", "BL06J-EA-TMON-01:NL", "true"],
							  ["Cryostat temp", "TCTRL.T1", "BL06J-EA-TCTRL-01:STS:T1", "true"],
							  ["VTI setpoint demand", "VTI.SETPOINT-DMD", "BL06J-EA-TCTRL-01:DMD:LOOP1:SETPOINT", "false"],
							  ["VTI setpoint readback", "VTI.SETPOINT-RBV", "BL06J-EA-TCTRL-01:STS:LOOP1:SETPOINT", "true"],
							  ["Needle valve manual control demand", "NVALV.MANUAL-DMD", "BL06J-EA-TCTRL-01:DMD:LOOP2:MANUAL", "false"],
							  ["Needle valve manual control readback", "NVALV.MANUAL-RBV", "BL06J-EA-TCTRL-01:STS:LOOP2:MANUAL", "true"],
							  ["Helium Depth Indicator current level (mm)", "HDI.LEVEL", "BL06J-EA-HDI-01:LEVEL", "true"],
							  ["Helium Depth Indicator pump control", "HDI.PUMP", "BL06J-EA-HDI-01:PUMP", "false"],
							  ]
		self.otherPvs = {}
		for otherMagnetPv in otherMagnetPvsData:
			pvKey = otherMagnetPv[1]
			pvValue = otherMagnetPv[2];
			pv = CAClient(pvValue)
			pv.configure()
			self.otherPvs[pvKey] = pv		
		print "otherPvs: " + str(self.otherPvs)

	def initScannables(self):
		print "init magnet scannables"
		print "scannables: magmode, magx, magy, magz, magrho, magth, magphi, magspherical"
		
		# real scannables
		self.magmode = magMode(self)
		self.magx = magX(self)
		self.magy = magY(self)
		self.magz = magZ(self)
		
		# virtual scannables
		self.magxyz = magXYZ(self)
		self.magrho = magRho(self)
		self.magtheta = magTheta(self)
		self.magphi = magPhi(self)
		self.magrtp = magRTP(self)
		
		# other pseudodevices, e.g. temperature monitors
		self.tmonT1 = tmonT1(self)
		self.tmonT2 = tmonT2(self)
		self.tmonT3 = tmonT3(self)
		self.tmonNL = tmonNL(self)
		self.tcntrlT1 = tcntrlT1(self)
		self.vtiDmd = vtiDmd(self)
		self.vtiRbv = vtiRbv(self)
		self.nvalvDmd = nvalvDmd(self)
		self.nvalvRbv = nvalvRbv(self)
		self.hdiLevel = hdiLevel(self)
		self.hdiPump = hdiPump(self)
		
	def setPsuTolerance(self, psuTolerance):
		self.psuTolerance = psuTolerance
		self.x.psuTolerance = psuTolerance
		self.y.psuTolerance = psuTolerance
		self.z.psuTolerance = psuTolerance
		
	def initMagnetValues(self):
		# what should default PSU tolerance be?
		# n.b. tolerance will be replaced by implementing a listener for the ramp callback
		# to monitor when the correct field strength has been reached
		self.psuTolerance = 0.005 # future versions might query the scan parameters, to set the tolerance to 0.1 * scan step size
		self.x = 0
		self.y = 0
		self.z = 0
		self.magmode = "uniaxialz"
		self.rho = 0
		self.phi = 90
		self.theta = 0
		
	def printMagnetValues(self):
		print "magnet values, xyz: [%.3f,%.3f,%.3f], rtp: [%.3f,%.3f,%.3f]" % (self.x, self.y, self.z, self.rho, self.theta, self.phi)
		

# implement the callback listener for STARTRAMP.PROC PV

# cf Eric's implementation in i07-config/scripts/Diamond/PseudoDevices/EpicsCamera.py

#class StartRampCallbackListener(PutListener):
#	
#	def __init__(self, magnet):
#		self.magnet = magnet
#		
#	def putCompleted(self, event):
#		if event.getStatus() != CAStatus.NORMAL:
#			print "callback, CAStatus ! NORMAL
#		else:
#			print "callback, CAStatus is NORMAL
#			
##	def getStatus(self):
##		return self.camera.cameraStatus

class magX(ScannableMotionBase):
	
	def __init__(self, magnet, name="magX", unitstring="T", formatstring="%.4f"):
		print "magX.__init__"
		self.magnet = magnet
		self.setName(name);
		self.setInputNames([name])
		self.Units = [unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.currentposition = random.random()
		self.setterPv = magnet.pvs['X:DMD']
		self.getterPv = magnet.pvs['X:RBV']
		self.rampPv = magnet.pvs['STARTRAMP.PROC']
		self.rampStatusPv = magnet.pvs['RAMPSTATUS']
		self.target = 0
		self.psuTolerance = magnet.psuTolerance
		print "magx.tolerance: " + str(self.psuTolerance) 
		
	def getPosition(self):
		print "magx get Pos: " + str(self.getterPv.caget())
		return float(self.getterPv.caget())
		
	def asynchronousMoveTo(self, new_position):
		print "magx asynch moveto, new_position: " + str(new_position)
		print "actual magnet value: " + str(self.getterPv.caget())
		return
		# don't change x or y fields while in development: 20090908
#		self.target=new_position
#		self.setterPv.caput(new_position)
#		# start ramp
#		self.rampPv.caput(1)
	
	def isBusy(self):
		if (abs(float(self.getterPv.caget()) - float(self.target)) < self.psuTolerance):
			return 0
		return 1


class magY(ScannableMotionBase):
	
	def __init__(self, magnet, name="magY", unitstring="T", formatstring="%.4f"):
		print "magY.__init__"
		self.magnet = magnet
		self.setName(name);
		self.setInputNames([name])
		self.Units = [unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.currentposition = random.random()
		self.setterPv = magnet.pvs['Y:DMD']
		self.getterPv = magnet.pvs['Y:RBV']
		self.rampPv = magnet.pvs['STARTRAMP.PROC']
		self.rampStatusPv = magnet.pvs['RAMPSTATUS']
		self.target = 0
		self.psuTolerance = magnet.psuTolerance
		print "magy.tolerance: " + str(self.psuTolerance) 
		
	def getPosition(self):
		print "magy get Pos: " + str(self.getterPv.caget())
		return float(self.getterPv.caget())
		
	def asynchronousMoveTo(self, new_position):
		print "magy asynch moveto, new_position: " + str(new_position)
		print "actual magnet value: " + str(self.getterPv.caget())
		self.target = new_position
		# don't change x or y fields while in development: 20090908
#		self.setterPv.caput(new_position)
#		# start ramp
#		self.rampPv.caput(1)
	
	def isBusy(self):
		if (abs(float(self.getterPv.caget()) - float(self.target)) < self.psuTolerance):
			return 0
		return 1


class magZ(ScannableMotionBase):
	
	def __init__(self, magnet, name="magZ", unitstring="T", formatstring="%.4f"):
		print "magZ.__init__"
		self.magnet = magnet
		self.setName(name);
		self.setInputNames([name])
		self.Units = [unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.currentposition = random.random()
		self.setterPv = magnet.pvs['Z:DMD']
		self.getterPv = magnet.pvs['Z:RBV']
		self.rampPv = magnet.pvs['STARTRAMP.PROC']
		self.rampStatusPv = magnet.pvs['RAMPSTATUS']
		self.target = 0
		self.psuTolerance = magnet.psuTolerance
		print "magz.tolerance: " + str(self.psuTolerance) 
		
	def getPosition(self):
		print "magz get Pos: " + str(self.getterPv.caget())
		return float(self.getterPv.caget())
	
	def asynchronousMoveTo(self, new_position):
		print "magz asynch moveto, new_position: " + str(new_position)
		print "actual magnet value: " + str(self.getterPv.caget())
		self.target = new_position
		self.setterPv.caput(new_position)
		# start ramp
		self.rampPv.caput(1)
		# try with a default timeout to allow ramp to complete
		# units of timout? s? ms? look at CAClient
		# self.rampPv.caput(1, 60)

	def isBusy(self):
		if (abs(float(self.getterPv.caget()) - float(self.target)) < self.psuTolerance):
			return 0
		return 1

	
# combined x, y, z pseudodevice

class magXYZ(ScannableMotionBase):
	
	def __init__(self, magnet, name="magXYZ", unitstring="T", formatstring="[%.4f][%.4f][%.4f]"):
		print "magXYZ.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["X", "Y", "Z"])
		self.Units = ["T", "T", "T"]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.x = random.random()
		self.y = random.random()
		self.z = random.random()
	
	def getPosition(self):
		return [self.x, self.y, self.z]

	def asynchronousMoveTo(self, new_position):
		# self.currentposition = new_position
		self.x = new_position[0]
		self.y = new_position[1]
		self.z = new_position[2]
		# set actual magnet scannables
		# wn: correct?
		#self.magnet.magx.asynchronousMoveTo(self.x)
		#self.magnet.magy.asynchronousMoveTo(self.y)
		#self.magnet.magz.asynchronousMoveTo(self.z)

	def isBusy(self):
		return 0	
		
class magMode(ScannableMotionBase):
	
	def __init__(self, magnet, name="magMode", mode="uniaxialx"):
		print "magMode.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["Mode"])
		self.setLevel(3)
		self.mode = mode
		self.setOutputFormat(["%s"])
		#self.checkRho(mode)
		#checkMagnetModeRho(mode)
		#self.allowedModes = ["uniaxialx", "uniaxialy", "uniaxialz", "spherical", "quadrantxy", "planarxz", "cubic"]
		self.allowedModes = ["uniaxialx", "uniaxialy", "uniaxialz", "spherical", "planarxz"]
		self.pv = magnet.pvs['MODE']
	
	def getPosition(self):
		print "get mode: " + self.pv.caget()
		index = int(self.pv.caget())
		modeName = self.allowedModes[index]
		print "index: %d, %s " % (index, modeName) 
		return modeName
		#return self.mode

	def asynchronousMoveTo(self, new_mode):
		# self.currentposition = new_position
		if not new_mode in self.allowedModes:
			self.mode = "Unknown mode: " + new_mode
		else:
			# self.checkRho(new_mode)
			# checkMagnetModeRho(new_mode)
			self.mode = new_mode
			self.magnet.mode = new_mode
			index = self.allowedModes.index(new_mode)
			print "set mode: %s, index: %d" % (new_mode, index)
			self.pv.caput(index)
	
	def isBusy(self):
		return 0	
	
class magRho(ScannableMotionBase):
	
	def __init__(self, magnet, name="magRho", rho=1.0, formatstring="[%.4f]"):
		print "magRho.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["rho"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.rho = rho
		
	def getPosition(self):
		return self.rho
	
	def asynchronousMoveTo(self, new_position):
		self.rho = new_position
		
	def isBusy(self):
		return 0	
		
class magTheta(ScannableMotionBase):
	'''
	theta in Diamond is 0-360 about the y axis
	'''
	
	def __init__(self, magnet, name="magTheta", formatstring="[%.4f]"):
		print "magTheta.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["theta"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.rho = magnet.rho
		self.theta = magnet.theta
		self.phi = magnet.phi
		# for testing scanning in xz plane (e.g. scan magnet.magtheta 0 360 30), 
		# set rho to 0.1, and phi to 90
		self.rho = 0.1
		self.phi = 90
		
	def getPosition(self):
		print "theta, getPosition: " + str(self.theta)
		print "rho: %.3f, theta: %f, phi: %.3f" % (self.rho, self.theta, self.phi)
		#(self.x, self.y, self.z) = sph2cartesian(self.rho, self.theta, self.phi)
		#print "xyz: [%.2f][%.2f][%.2f]" % (self.x, self.y, self.z)
		return self.theta
	
	def asynchronousMoveTo(self, new_position):
		print "theta, asynMoveTo: " + str(new_position)
		(x, y, z) = sph2cartesian(rho, theta, phi)
		self.theta = new_position
		
	def isBusy(self):
		return 0	
		
class magPhi(ScannableMotionBase):
	'''
	phi in Diamond is 0-180 from the positive y axis
	'''
	
	def __init__(self, magnet, name="magPhi", phi=0, formatstring="[%.4f]"):
		print "magPhi.__init__"
		self.magnet = magnet
		self.phi = phi
		self.setName(name)
		self.setInputNames(["phi"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		
	def getPosition(self):
		return self.phi
	
	def asynchronousMoveTo(self, new_position):
		self.phi = new_position
		
	def isBusy(self):
		return 0	
	
class magRTP(ScannableMotionBase):
	
	def __init__(self, magnet, name="magRTP", rho=1, theta=90, phi=0, formatstring="[%.4f][%.4f][%.4f]"):
		print "magRTP.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["rho", "theta", "phi"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.rho = rho
		self.theta = theta
		self.phi = phi
	
	def getPosition(self):
		(self.x, self.y, self.z) = self.sph2cartesian(self.rho, self.theta, self.phi)
		print "\nmagRTP.getPosition()"
		print "rho: %.3f, theta: %f, phi: %.3f" % (self.rho, self.theta, self.phi)
		print "x: %.2f, y: %.2f, z: %.2f" % (self.x, self.y, self.z)
		return [self.x, self.y, self.z]

	def asynchronousMoveTo(self, new_position):
		# self.currentposition = new_position
		self.rho = new_position[0]
		self.theta = new_position[1]
		self.phi = new_position[2]
		print "\nmagRTP.asynmoveto(), rho: %.3f, theta: %.3f, phi: %.3f" % (self.rho, self.theta, self.phi)
		(self.x, self.y, self.z) = self.sph2cartesian(self.rho, self.theta, self.phi)
		print "for rho: %.3f, theta: %.3f, phi: %.3f" % (self.rho, self.theta, self.phi)
		print "set x, y, z fields to:[%5.2f,%5.2f,%5.2f]" % (self.x, self.y, self.z)
		
		# 

	def isBusy(self):
		return 0	
	
	# transformation routines
	
	def sph2cartesian(self, rho, theta, phi):
		# NB. Units used in GDA are DEGREE for PHI and THETA
		# print "sph2cartesian, rho: %f, theta: %f, phi: %f" % (rho, theta, phi) 
		x = rho * math.cos(self.deg2rad(phi)) * math.sin(self.deg2rad(theta))
		y = rho * math.sin(self.deg2rad(phi)) * math.sin(self.deg2rad(theta))
		z = rho * math.cos(self.deg2rad(theta))
		# test calculated rho == input rho
		rho2 = math.sqrt(x * x + y * y + z * z)
		# transform "standard" axes to beamline axes (x->z, y->x, z->y)
		xBL = y
		yBL = z
		zBL = x
		return (xBL, yBL, zBL)
	
	def cartesian2sph(self, rho, x, y, z):
		rootSumSquares = math.sqrt(x * x + y * y + z * z)
		if (rootSumSquares == 0):
			return (0, 0, 0)
		rho = rootSumSquares
		theta = rad2deg(math.acos(z / rootSumSquares))
		phi = rad2deg(math.atan2(y, x))
		return (rho, theta, phi)
	
	'''
	Modified transformations for BL geometry:
	Standard	BL
	x			z
	y			x
	z			y
	'''
	
	def sph2cartesianBL(self, rho, theta, phi):
		"""
		Convert BL spherical coordinates (rho, theta, phi) to cartesian coordinates (x,y,z)
		using the beamline geometry
		"""
		# NB. Units used in GDA are DEGREE for PHI and THETA
		z = rho * math.sin(deg2rad(theta)) * math.cos(deg2rad(phi))
		x = rho * math.sin(deg2rad(theta)) * math.sin(deg2rad(phi))
		y = rho * math.cos(deg2rad(theta))
		return (x, y, z)
	
	def cartesian2sphBL(self, x, y, z):
		"""
		Convert BL cartesian coordinates (x,y,z) to spherical coordinates (rho, theta, phi)
		using the beamline geometry
		"""
		rootSumSquares = math.sqrt(x * x + y * y + z * z)
		if (rootSumSquares == 0):
			return (0, 0, 0)
		rho = rootSumSquares
		phi = rad2deg(math.atan2(x, z))
		theta = rad2deg(math.acos(y / rho))
		return (rho, theta, phi)
	
	def sph2cartesianBL2(self, rho, theta, phi):
		"""
		Convert BL spherical coordinates (rho, theta, phi) to cartesian coordinates (x,y,z)
		using the beamline geometry
		
		theta and phi are swapped (i06 convention)
		"""
		# NB. Units used in GDA are DEGREE for PHI and THETA
		z = rho * math.sin(deg2rad(phi)) * math.cos(deg2rad(theta))
		x = rho * math.sin(deg2rad(phi)) * math.sin(deg2rad(theta))
		y = rho * math.cos(deg2rad(phi))
		return (x, y, z)
	
	def cartesian2sphBL2(self, x, y, z):
		"""
		Convert BL cartesian coordinates (x,y,z) to spherical coordinates (rho, theta, phi)
		using the beamline geometry
		
		theta and phi are swapped (i06 convention)
		"""
		rootSumSquares = math.sqrt(x * x + y * y + z * z)
		if (rootSumSquares == 0):
			return (0, 0, 0)
		rho = rootSumSquares
		theta = rad2deg(math.atan2(x, z))
		phi = rad2deg(math.acos(y / rho))
		return (rho, theta, phi)
	
	def deg2rad(self, degrees):
		return degrees * math.pi / 180
	
	def rad2deg(self, radians):
		return radians * 180 / math.pi	
	
	
	
def checkMagnetModeRho(mode):
	'''
	NOT USED; EPICS does the directional magnitude checks for a given mode and requested directional (x,y,z) field strength values
	The status of the combined x,y,z field magnitude is returned by the 'LIMITSTATUS' EPICS PV 
	'''
	print "checkMagnetModeRho(): check magnitude of field for given mode: %s" % mode
	if mode == "uniaxialx":
		print "mode: uniaxialx"
		print "\tx <= +-2T"
		print "\ty = 0 and locked"
		print "\tz = 0 and locked"
	elif mode == "uniaxialy":
		print "mode: uniaxialy"
		print "\tx = 0 and locked"
		print "\ty <= +-2T"
		print "\tz = 0 and locked"
	elif mode == "uniaxialz":
		print "mode: uniaxialz"
		print "\tx = 0 and locked"
		print "\ty = 0 and locked"
		print "\tz <= +-6T"
	elif mode == "spherical":
		print "mode: spherical"
		print "sqrt(x*x + y*y + z*z) <= +-1.75T"
	elif mode == "quadrantxy":
		print "mode: quadrantxy"
		print "\tsqrt(x*x + y*y) <= +-2T"
		print "\tx > 0"
		print "\ty > 0"
		print "\tz <= 0.05T"
		print "\tdx/dt = 0.5"
		print "\tdy/dt = 0.2"
	elif mode == "planarxz":
		print "mode: planarxz"
		print "\tsqrt(x*x + z*z) <= +-2T"
		print "\ty = 0 and locked"
	elif mode == "cubic":
		print "mode: cubic"
		print "\tx <= +-1.5T"
		print "\ty <= +-1.5T"
		print "\tz <= +-1.5T"

#
#
# other magnet pseudodevices: temperature monitors etc.
#
# ["Magnet temperature 1", "TMON.T1", "BL06J-EA-TMON-01:T1", "true"],
# ["Magnet temperature 2", "TMON.T2", "BL06J-EA-TMON-01:T2", "true"],
# ["Magnet temperature 3", "TMON.T3", "BL06J-EA-TMON-01:T3", "true"],
# ["Nitrogen Level", "TMON.NL", "BL06J-EA-TMON-01:NL", "true"],
# ["Cryostat temp", "TCTRL.T1", "BL06J-EA-TCTRL-01:STS:T1", "true"],
# ["VTI setpoint demand", "VTI.SETPOINT-DMD", "BL06J-EA-TCTRL-01:DMD:LOOP1:SETPOINT", "false"],
# ["VTI setpoint readback", "VTI.SETPOINT-RBV", "BL06J-EA-TCTRL-01:STS:LOOP1:SETPOINT", "true"],
# ["Needle valve manual control demand", "NVALV.MANUAL-DMD", "BL06J-EA-TCTRL-01:DMD:LOOP2:MANUAL", "false"],
# ["Needle valve manual control readback", "NVALV.MANUAL-RBV", "BL06J-EA-TCTRL-01:STS:LOOP2:MANUAL", "true"],
# ["Helium Depth Indicator current level (mm)", "HDI.LEVEL", "BL06J-EA-HDI-01:LEVEL", "true"],
# ["Helium Depth Indicator pump control", "HDI.PUMP", "BL06J-EA-HDI-01:PUMP", "false"],
# 
# tmonT1, tmonT2, tmonT3, tmonNL, tcntrlT1, vtiDmd, vtiRbv, nvalvDmd, nvalvRbv, hdiLevel, hdiPump
#
#

class tmonT1(ScannableMotionBase):
	def __init__(self, magnet, name="tmonT1", formatstring="[%.4f]"):
		print "tmonT1.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["tmonT1"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.pv = magnet.otherPvs['TMON.T1']
		self.readonly = True
		
	def getPosition(self):
		return float(self.pv.caget())
	
	def asynchronousMoveTo(self, new_position):
		if (self.readonly):
			pass
		else:
			self.pv.caput(new_position)
		
	def isBusy(self):
		return 0	
	
class tmonT2(ScannableMotionBase):
	def __init__(self, magnet, name="tmonT2", formatstring="[%.4f]"):
		print "tmonT2.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["tmonT2"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.pv = magnet.otherPvs['TMON.T2']
		self.readonly = True
		
	def getPosition(self):
		return float(self.pv.caget())
	
	def asynchronousMoveTo(self, new_position):
		if (self.readonly):
			pass
		else:
			self.pv.caput(new_position)
		
	def isBusy(self):
		return 0	
	
class tmonT3(ScannableMotionBase):
	def __init__(self, magnet, name="tmonT3", formatstring="[%.4f]"):
		print "tmonT3.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["tmonT3"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.pv = magnet.otherPvs['TMON.T3']
		self.readonly = True
		
	def getPosition(self):
		return float(self.pv.caget())
	
	def asynchronousMoveTo(self, new_position):
		if (self.readonly):
			pass
		else:
			self.pv.caput(new_position)
		
	def isBusy(self):
		return 0
	
class tmonNL(ScannableMotionBase):
	def __init__(self, magnet, name="tmonNL", formatstring="[%.4f]"):
		print "tmonNL.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["tmonNL"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.pv = magnet.otherPvs['TMON.NL']
		self.readonly = True
		
	def getPosition(self):
		return float(self.pv.caget())
	
	def asynchronousMoveTo(self, new_position):
		if (self.readonly):
			pass
		else:
			self.pv.caput(new_position)
		
	def isBusy(self):
		return 0
	
class tcntrlT1(ScannableMotionBase):
	def __init__(self, magnet, name="tcntrlT1", formatstring="[%.4f]"):
		print "tcntrlT1.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["tcntrlT1"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.pv = magnet.otherPvs['TCTRL.T1']
		self.readonly = True
		
	def getPosition(self):
		return float(self.pv.caget())
	
	def asynchronousMoveTo(self, new_position):
		if (self.readonly):
			pass
		else:
			self.pv.caput(new_position)
		
	def isBusy(self):
		return 0
	
class vtiDmd(ScannableMotionBase):
	def __init__(self, magnet, name="vtiDmd", formatstring="[%.4f]"):
		print "vtiDmd.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["vtiDmd"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.pv = magnet.otherPvs['VTI.SETPOINT-DMD']
		self.readonly = True
		
	def getPosition(self):
		return float(self.pv.caget())
	
	def asynchronousMoveTo(self, new_position):
		if (self.readonly):
			pass
		else:
			self.pv.caput(new_position)
		
	def isBusy(self):
		return 0
	
class vtiRbv(ScannableMotionBase):
	def __init__(self, magnet, name="vtiRbv", formatstring="[%.4f]"):
		print "vtiRbv.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["vtiRbv"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.pv = magnet.otherPvs['VTI.SETPOINT-RBV']
		self.readonly = True
		
	def getPosition(self):
		return float(self.pv.caget())
	
	def asynchronousMoveTo(self, new_position):
		if (self.readonly):
			pass
		else:
			self.pv.caput(new_position)
		
	def isBusy(self):
		return 0

class nvalvDmd(ScannableMotionBase):
	def __init__(self, magnet, name="nvalvDmd", formatstring="[%.4f]"):
		print "nvalvDmd.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["nvalvDmd"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.pv = magnet.otherPvs['NVALV.MANUAL-DMD']
		self.readonly = True
		
	def getPosition(self):
		return float(self.pv.caget())
	
	def asynchronousMoveTo(self, new_position):
		if (self.readonly):
			pass
		else:
			self.pv.caput(new_position)
		
	def isBusy(self):
		return 0
	
class nvalvRbv(ScannableMotionBase):
	def __init__(self, magnet, name="nvalvRbv", formatstring="[%.4f]"):
		print "nvalvRbv.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["nvalvRbv"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.pv = magnet.otherPvs['NVALV.MANUAL-RBV']
		self.readonly = True
		
	def getPosition(self):
		return float(self.pv.caget())
	
	def asynchronousMoveTo(self, new_position):
		if (self.readonly):
			pass
		else:
			self.pv.caput(new_position)
		
	def isBusy(self):
		return 0	
	
class hdiLevel(ScannableMotionBase):
	def __init__(self, magnet, name="hdiLevel", formatstring="[%.4f]"):
		print "hdiLevel.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["hdiLevel"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.pv = magnet.otherPvs['HDI.LEVEL']
		self.readonly = True
		
	def getPosition(self):
		return float(self.pv.caget())
	
	def asynchronousMoveTo(self, new_position):
		if (self.readonly):
			pass
		else:
			self.pv.caput(new_position)
		
	def isBusy(self):
		return 0	
	
class hdiPump(ScannableMotionBase):
	def __init__(self, magnet, name="hdiPump", formatstring="[%.4f]"):
		print "hdiPump.__init__"
		self.magnet = magnet
		self.setName(name)
		self.setInputNames(["hdiPump"])
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.pv = magnet.otherPvs['HDI.PUMP']
		self.readonly = True
		
	def getPosition(self):
		return float(self.pv.caget())
	
	def asynchronousMoveTo(self, new_position):
		if (self.readonly):
			pass
		else:
			self.pv.caput(new_position)
		
	def isBusy(self):
		return 0	

	
# global transformation functions
# these functions have been tested in i06MagnetTester.py, 
# functions sph2cartesianBL2 and cartesian2sphBL2.
# These functions are renamed here to 
# sph2cartesian and cartesian2sph


def sph2cartesian(self, rho, theta, phi):
		"""
		Convert BL spherical coordinates (rho, theta, phi) to cartesian coordinates (x,y,z)
		using 1. beamline geometry and 2. angle naming convention
		
		1. Modified transformations for BL geometry:
		Standard	BL
		x			z
		y			x
		z			y
		
		2. theta and phi are swapped (i06 convention)
		theta: 0-360
		phi: 0-180
		"""
		# NB. Units used in GDA are DEGREE for PHI and THETA
		z = rho * math.sin(deg2rad(phi)) * math.cos(deg2rad(theta))
		x = rho * math.sin(deg2rad(phi)) * math.sin(deg2rad(theta))
		y = rho * math.cos(deg2rad(phi))
		return (x, y, z)

	
def cartesian2sph(self, x, y, z):
	"""
	Convert BL cartesian coordinates (x,y,z) to spherical coordinates (rho, theta, phi)
	using 1. beamline geometry and 2. angle naming convention
	
	1. Modified transformations for BL geometry:
		Standard	BL
		x			z
		y			x
		z			y
		
	2. theta and phi are swapped (i06 convention)
	theta: 0-360
	phi: 0-180
	"""
	rootSumSquares = math.sqrt(x * x + y * y + z * z)
	if (rootSumSquares == 0):
		return (0, 0, 0)
	rho = rootSumSquares
	theta = rad2deg(math.atan2(x, z))
	phi = rad2deg(math.acos(y / rho))
	return (rho, theta, phi)
	
def deg2rad(self, degrees):
	return degrees * math.pi / 180
	
def rad2deg(self, radians):
	return radians * 180 / math.pi	
	

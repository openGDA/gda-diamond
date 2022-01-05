#A GDA Pseudo Device that controls the I06 Superconducting Magnet

from time import sleep
import math


from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient;

#import cPickle as pickle
#import threading;
#import synchronize;

import __main__ as gdamain

from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();

#For magnet mode settings
#uniaxialx, uniaxialy, uniaxialz, spherical, phanarxz, quadrantxy, cubic = range(7);

#The Class for creating a socket-based Psuedo Device to control the magnet
class SuperconductingMagnetClass(object):
	SCM_MODE_UNIAXIAL_X, SCM_MODE_UNIAXIAL_Y, SCM_MODE_UNIAXIAL_Z, SCM_MODE_SPHERICAL, SCM_MODE_QUADRANT_XY, SCM_MODE_PLANAR_XZ, SCM_MODE_CUBIC, SCM_MODE_UNDEFINED = range(8);
	SCM_STATUS_RAMPING, SCM_STATUS_DONE,  = range(2);
	SCM_LIMIT_VIOLATION, SCM_LIMIT_OK = range(2);

	SCM_MODES = (SCM_MODE_UNIAXIAL_X, SCM_MODE_UNIAXIAL_Y, SCM_MODE_UNIAXIAL_Z, SCM_MODE_SPHERICAL, SCM_MODE_QUADRANT_XY, SCM_MODE_PLANAR_XZ, SCM_MODE_CUBIC, SCM_MODE_UNDEFINED);
	SCM_MODE_STRINGS = ('uniaxialx', 'uniaxialy', 'uniaxialz', 'spherical', 'planar_xz', 'quadrant_xy', 'cubic', 'undefined');
	
	def __init__(self, name, rootPV):
		self.name = name;
#        self.setInputNames(['field', 'theta', 'phi']);
#        self.setOutputFormat(["%10.4f", "%10.2f", "%10.2f"]);
#		self.setExtraNames(['field']);
#        self.Units=['Telsa','Deg','Deg'];
#        self.setLevel(7);
		self.magnetRootPV = rootPV;
		self.timeoutLimit = 300;
		self._delay = 5;
		self._tolerance = 0;

		self.mode = None;
		self.modeString = ['uniaxialx', 'uniaxialy', 'uniaxialz', 'spherical', 'planar_xz', 'quadrant_xy', 'cubic', 'undefined'];
		
		self.rampStatus = None ;
		self.limitStatus = None ;
		self.rampString = ['RAMPING', 'RAMP MADE'];
		self.limitString = ['VIOLATION', 'OK'];
		
		self.x = None;
		self.y = None;
		self.z = None;
		
		self.rho=None;
		self.theta=None;
		self.phi=None;

		self.setup();
		self.getMagnetMode();
		self.getMagnetStatus();
		self.getMagnetPosition(raw=True);

		self.verbose=False

	def __del__(self):
		self.cleanChannel(self.chXi);
		self.cleanChannel(self.chYi);
		self.cleanChannel(self.chZi);
		self.cleanChannel(self.chXo);
		self.cleanChannel(self.chYo);
		self.cleanChannel(self.chZo);
		
		self.cleanChannel(self.chMode);
		self.cleanChannel(self.chStatus);
		self.cleanChannel(self.chLimit);
		self.cleanChannel(self.chGo);

	def setup(self):
#		Epics PVs for changing the magnet X, Y, Z field value:
		self.chXi=CAClient(self.magnetRootPV+':X:DMD'); self.configChannel(self.chXi);
		self.chYi=CAClient(self.magnetRootPV+':Y:DMD'); self.configChannel(self.chYi);
		self.chZi=CAClient(self.magnetRootPV+':Z:DMD'); self.configChannel(self.chZi);

#		Epics PVs for getting the magnet field values:
		self.chXo=CAClient(self.magnetRootPV+':X:RBV'); self.configChannel(self.chXo);
		self.chYo=CAClient(self.magnetRootPV+':Y:RBV'); self.configChannel(self.chYo);
		self.chZo=CAClient(self.magnetRootPV+':Z:RBV'); self.configChannel(self.chZo);
		
#		Epics PV for Changing the magnet mode. Possible values: UNIAXIAL_X, UNIAXIAL_Y, UNIAXIAL_Z, SPHERICAL, QUADRANT_XY, PLANAR_XZ, CUBIC. Note QUADRANT_XY and CUBIC won't be implemented yet:
		self.chMode=CAClient(self.magnetRootPV+':MODE'); self.configChannel(self.chMode);

#		Epics PV for getting  the magnet status. Possible values: 'RAMPING', 'RAMP MADE'
		self.chStatus=CAClient(self.magnetRootPV+':RAMPSTATUS'); self.configChannel(self.chStatus);

#		Epics PV for getting  the magnet status. Possible values: 'VIOLATION', 'OK'
		self.chLimit=CAClient(self.magnetRootPV+':LIMITSTATUS'); self.configChannel(self.chLimit);

#		Epics PV for requesting magnet to start ramping, will call-back when done or if there is an error
		self.chGo=CAClient(self.magnetRootPV+':STARTRAMP.PROC'); self.configChannel(self.chGo);

	def setTimeout(self, newTimeout):
		self.timeoutLimit =  newTimeout;

	def setDelay(self, newDelay=None):
		self._delay = newDelay;

	def getDelay(self):
		return self._delay;

	def delay(self, newDelay=None):
		""" Set or display the magnet delay.
		"""
		if newDelay == None:
			print "Current magnet delay is %r,  plus Epics axis delay" % self._delay
			
		else:
			self.setDelay(newDelay)

	def tolerance(self, newTolerance=None):
		""" Set or display the magnet readback tolerance. If zero, already return the readback, if large always return demand position
		"""
		if newTolerance == None:
			print "Current magnet tolerance is %r" % self._tolerance
		else:
			self._tolerance = newTolerance

	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();

	def setMagnetMode(self, newMode):
		if newMode not in SuperconductingMagnetClass.SCM_MODES:
			print "Please use the right mode";
			return;
		self.mode = newMode;
		self.chMode.caput(self.timeoutLimit, newMode);

#		To check the mode changing result:
		self.getMagnetStatus();
		self.checkMagnetStatus();

		return SuperconductingMagnetClass.SCM_MODE_STRINGS[self.mode];

	def getMagnetMode(self):
		self.mode = int( float(self.chMode.caget() ) );
		return SuperconductingMagnetClass.SCM_MODE_STRINGS[self.mode];

	def getMagnetModeIndex(self):
		self.mode = int( float(self.chMode.caget() ) );
		return self.mode;

	def getMagnetStatus(self):
		self.rampStatus = int( float(self.chStatus.caget() ) );
		self.limitStatus = int( float(self.chLimit.caget() ) );
		return 'Ramp Status: ' + self.rampString[self.rampStatus] + '; Limit Status: ' + self.limitString[self.limitStatus];

	def getMagnetRampStatus(self):
		self.rampStatus = int( float(self.chStatus.caget() ) );
		return self.rampString[self.rampStatus];

	def getMagnetLimitStatus(self):
		self.limitStatus = int( float(self.chLimit.caget() ) );
		return self.limitString[self.limitStatus];

	def checkMagnetStatus(self):
		self.getMagnetStatus();
		if self.rampStatus == SuperconductingMagnetClass.SCM_STATUS_DONE and self.limitStatus == SuperconductingMagnetClass.SCM_LIMIT_OK:
			if self.verbose:
				print "The Magnet Ramping is done and the Limit is OK";
			return True;
		else:
			if self.rampStatus == SuperconductingMagnetClass.SCM_STATUS_RAMPING:
				if self.verbose:
					print "The Magnet is still ramping.";
			if self.limitStatus == SuperconductingMagnetClass.SCM_LIMIT_VIOLATION:
				if self.verbose:
					print "Limit violation error!";
			return False;

	def getMagnetPosition(self, raw=False):
		'''Get the magnetic field in Cartesian coordinate '''
		#get XYZ value from Epics
		self.x = float( self.chXo.caget() );
		self.y = float( self.chYo.caget() );
		self.z = float( self.chZo.caget() );
		
		#Calculate the Spherical value in Degree
		[self.rho, self.theta, self.phi] = self.getSphericalCoordinate(self.x, self.y, self.z);
		pos=[self.x, self.y, self.z]
		if not raw:
			dmd=self.getDemandPosition()
		
			for i in range(3):
				if abs(dmd[i]-pos[i]) < self._tolerance:
					pos[i]=dmd[i]
					logger.logger.info("Axis %r is at %r, within %r, returning %r" % (i, pos[i], self._tolerance, dmd[i]))
				else:
					logger.logger.info("Axis %r is at %r, more than +-%r of %r" % (i, pos[i], self._tolerance, dmd[i]))
		
		return pos

	def getDemandPosition(self):
		'''Get the demanded magnetic field in Cartesian coordinate '''
		#get XYZ value from Epics
		x = float( self.chXi.caget() );
		y = float( self.chYi.caget() );
		z = float( self.chZi.caget() );
		
		return [x, y, z];

	def getMagnetCartesianPosition(self, newX, newY, newZ):
		'''Get the magnetic field in Cartesian coordinate '''
		return self.getMagnetPosition();

	def setMagnetPosition(self, newX, newY, newZ):
		return self.setMagnetPositionWithinBoundary(newX, newY, newZ);
#		return self.setMagnetPositionWithoutBoundary(newX, newY, newZ);

	def setMagnetPositionWithinBoundary(self, newX, newY, newZ):
		'''Set the magnetic field in Cartesian coordinate '''
		#For keeping the magnitude constrained to avoid quench, always do the decreasing before increasing motors
		[x0, y0, z0]=self.getMagnetPosition(raw=True); #Starting point
		[x1, y1, z1]=[newX, newY, newZ];
		dx=abs(x1)-abs(x0);
		dy=abs(y1)-abs(y0);
		dz=abs(z1)-abs(z0);
		
		if dz<0: #decrease z first if it is the case
			if self.verbose:
				print "Move Z from " + str(z0) + " to " + str(z1);
			self.chZi.caput(newZ);
			self.chGo.caput(self.timeoutLimit, 1);
			
		if dx <0: #decrease x second if it is the case
			if self.verbose:
				print "Move X from " + str(x0) + " to " + str(x1);
			self.chXi.caput(newX);
			self.chGo.caput(self.timeoutLimit, 1);
			
		if dy <0: #decrease y last if it is the case
			if self.verbose:
				print "Move Y from " + str(y0) + " to " + str(y1);
			self.chYi.caput(newY);
			self.chGo.caput(self.timeoutLimit, 1);
			
		# Increase only if one or more need it.
		if dx > 0 or dy > 0 or dz > 0:
			if self.verbose:
				[x0, y0, z0]=self.getMagnetPosition(raw=True); #New starting point
				print "Move X, Y, Z from " + str([x0, y0, z0]) + " to " + str([x1, y1, z1]);
			self.chYi.caput(newY);
			self.chXi.caput(newX);
			self.chZi.caput(newZ);
			self.chGo.caput(self.timeoutLimit, 1);

		if self.verbose:
			print "Waiting for magnet readback to settle down..."
		
		#Due to EPICS flaw, after the callback, still need to wait for a few second for the magnet settle down
		if self._delay is not None:
			sleep(self._delay);
		
		if self.verbose:
			print "Wait completed, checking status..."
		
		self.checkMagnetStatus();
		
	def setMagnetPositionWithoutBoundary(self, newX, newY, newZ):
		'''Set the magnetic field in Cartesian coordinate '''
		#For keeping the magnitude constrained to avoid quench, always follows Y, X, Z order to move 
		self.chYi.caput(newY);
		self.chXi.caput(newX);
		self.chZi.caput(newZ);
		
		self.chGo.caput(self.timeoutLimit, 1);
		
		#Due to EPICS flaw, after the callback, still need to wait for a few second for the magnet settle down
		sleep(self._delay);
		
		self.checkMagnetStatus();

	def setMagnet(self, newRho, newTheta, newPhi):
		'''Set the magnetic field in Spherical coordinate '''
		[newX, newY, newZ] = self.getCartesianCoordinate(newRho, newTheta, newPhi);
		self.setMagnetPosition(newX, newY, newZ);

	def getMagnet(self):
		'''Get the magnetic field in Spherical coordinate '''
		self.getMagnetPosition();
		return [self.rho, self.theta, self.phi];

	def getMagnetSphericalPosition(self):
		'''Get the magnetic field in Spherical coordinate '''
		return self.getMagnet();

	def isBusy(self):
		return not self.checkMagnetStatus();

	def getSphericalCoordinate(self, x, y, z):
		rho = math.sqrt(x**2 + y**2 + z**2);

#		theta = math.atan2(x,z);
		theta = self.getTheta(x,z);

		#phi = math.degrees( math.acos(y/rho));
		phi = math.degrees( math.atan2(math.sqrt(x*x + z*z), y) );
		return [rho, theta, phi];
		
	def getCartesianCoordinate(self, rho, dTheta, dPhi):
		theta = math.radians(dTheta);
		phi = math.radians(dPhi);
		
		x=rho*math.sin(phi)*-1.0*math.sin(theta);
		y=rho*math.cos(phi);
		z=rho*math.sin(phi)*math.cos(theta);
	
		return [x, y, z];
	
	def getTheta(self, x, z):
#		return theta = math.atan2(x,z);
		if str( x ) == "0" or str( x ) == "0.0": #assume 0 or 0.0 are -0.0
			x=-1.0*x;
			
		theta = math.degrees( math.atan2(-1.0*x,z) );
		
		if theta < 0:
			theta += 360;
		elif str(theta) == "-0.0":
			theta = 360;
			
		return theta;


	def degrees(self, radians):
		'Converts angle x from radians to degrees.'
		return radians * 180.0 / math.pi	

	def radians(self, degrees):
		'Converts angle x from degrees to radians.'
		return degrees * math.pi / 180.0


#The Class for creating a magnet pseudo class in the Cartesian coordinate
class CartesianMagnetClass(ScannableMotionBase):
	def __init__(self, name, nameMagnet):
		self.setName(name);
		self.setInputNames(['Bx', 'By', 'Bz']);
		self.setExtraNames([]);
		self.setOutputFormat(["%6.4f", "%6.4f", "%6.4f"]);
		self.setLevel(7);
		self.magnet = vars(gdamain)[nameMagnet];

	#ScannableMotionBase Implementation
	def toString(self):
		ss=self.getName() + ": [Bx, By, Bz]: " + str(self.getPosition());
		return ss;

	def getPosition(self):
		return self.magnet.getMagnetPosition();

	def asynchronousMoveTo(self,newPos):
		self.magnet.setMagnetPosition(newPos[0], newPos[1], newPos[2]);
		return;

	def isBusy(self):
		return self.magnet.isBusy();

#The Class for creating a magnet pseudo class in the Spherical coordinate
class SphericalMagnetClass(ScannableMotionBase):
	def __init__(self, name, nameMagnet):
		self.setName(name);
		self.setInputNames(['Rho', 'Theta', 'Phi']);
		self.setExtraNames([]);
		self.setOutputFormat(["%6.4f", "%6.4f", "%6.4f"]);
		self.setLevel(7);
		self.magnet = vars(gdamain)[nameMagnet];

	#ScannableMotionBase Implementation
	def toString(self):
		ss=self.getName() + ": [Rho, Theta, Phi]: " + str(self.getPosition());
		return ss;

	def getPosition(self):
		return self.magnet.getMagnet();

	def asynchronousMoveTo(self,newPos):
		self.magnet.setMagnet(newPos[0], newPos[1], newPos[2]);
		return;

	def isBusy(self):
		return self.magnet.isBusy();

#The Class of Pseudo device for changing the magnet mode
class ModeMagnetClass(ScannableMotionBase):
	def __init__(self, name, nameMagnet):
		self.setName(name);
		self.setInputNames(['MagnetMode']);
		self.setExtraNames([]);
		self.setOutputFormat(["%6.4f"]);
		self.setLevel(7);
		self.magnet = vars(gdamain)[nameMagnet];

	#ScannableMotionBase Implementation
	def toString(self):
		ss=self.getName() + ": Current Magnet Mode: " + self.magnet.getMagnetMode();
		return ss;

	def getPosition(self):
		return self.magnet.getMagnetModeIndex();

	def asynchronousMoveTo(self,newPos):
		self.magnet.setMagnetMode(newPos);
		return;

	def isBusy(self):
		return self.magnet.isBusy();


#The Class for creating a pseudo class in the direction of a uniaxial x, y, or z
class SingleAxisMagnetClass(ScannableMotionBase):
	X, Y, Z, RHO, THETA, PHI  = range(6);

	def __init__(self, name, nameMagnet, axialIndex):
		self.setName(name);
		self.axialIndex = axialIndex;
		
		self.axisName = ['Bx', 'By', 'Bz', 'Rho', 'Theta', 'Phi'][self.axialIndex];
		self.setInputNames([ self.axisName ]);
		self.setExtraNames([]);
		self.setOutputFormat(["%6.4f"]);
		self.setLevel(7);
		self.magnet = vars(gdamain)[nameMagnet];
		
	#ScannableMotionBase Implementation
	def toString(self):
		ss=self.getName() + ': ' + self.axisName + ': ' + str(self.getPosition());
		return ss;

	def getPosition(self):
		if self.axialIndex < 3:
			return self.magnet.getMagnetPosition()[self.axialIndex];
		else:
			return self.magnet.getMagnet()[self.axialIndex-3];
		
	def asynchronousMoveTo(self,newPos):
		if self.axialIndex < 3:
			currentPosition = self.magnet.getMagnetPosition();
			currentPosition[self.axialIndex]=newPos;
			self.magnet.setMagnetPosition(currentPosition[0], currentPosition[1], currentPosition[2]);
		else:
			currentPosition = self.magnet.getMagnet();
			currentPosition[self.axialIndex-3]=newPos;
			self.magnet.setMagnet(currentPosition[0], currentPosition[1], currentPosition[2]);
		return;
	
	def isBusy(self):
		return self.magnet.isBusy();


#Usage:
#The root EPICS PV for the Super Conductiong Magnet
#magRootPV = 'BL06J-EA-MAG-01';

#print "Note: Use object name 'scm' for the Super Conducting Magenet control";
#scm = SuperconductingMagnetClass('scm', magRootPV);

#print "Note: Use Pseudo device name 'magmode' for the Super Conducting Magenet mode control";
#magmode = ModeMagnetClass('magmode', 'scm');

#print "Note: Use Pseudo device name 'magcartesina' for the Super Conducting Magenet control in Cartesian coordinate";
#magcartesian = CartesianMagnetClass('magcartesian', 'scm');

#print "Note: Use Pseudo device name 'magspherical' for the Super Conducting Magenet control in Spherical coordinate";
#magspherical = SphericalMagnetClass('magspherical', 'scm');

#print "Note: Use Pseudo device name 'magx, magy, magz, magrho, magth, magphi' for the Super Conducting Magenet single axis control";
#magx = SingleAxisMagnetClass('magx', 'scm', SingleAxisMagnetClass.X);
#magy = SingleAxisMagnetClass('magy', 'scm', SingleAxisMagnetClass.Y);
#magz = SingleAxisMagnetClass('magz', 'scm', SingleAxisMagnetClass.Z);
#magrho = SingleAxisMagnetClass('magrho', 'scm', SingleAxisMagnetClass.RHO);
#magth  = SingleAxisMagnetClass('magth',  'scm', SingleAxisMagnetClass.THETA);
#magphi = SingleAxisMagnetClass('magphi', 'scm', SingleAxisMagnetClass.PHI);

import sys
from datetime import datetime, timedelta
from threading import Timer
from time import sleep
from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import ScannableBase
#from gda.device.scannable import ScannableMotor
#from gda.device.scannable.component import MotorLimitsComponent

from gda.epics import CAClient
from gov.aps.jca.event import MonitorListener
from org.slf4j import LoggerFactory

#The Class for changing the underline EPICS motor at different ID polarisation conditions so that the same energy device name is used
class CombinedIDEnergyClass(ScannableBase):
	def __init__(self, name, denergy, uenergy, pgmenergy):
		self.logger = LoggerFactory.getLogger("CombinedIDEnergyClass:%s" % name)
		self.verbose = True

		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.Units=['eV'];
		self.setLevel(5);
		self.setOutputFormat(["%11.7f"]);
		
		self.denergy = denergy;
		self.uenergy = uenergy;
		self.pgmenergy = pgmenergy;
	
	#Scannable Implementations
	def getPosition(self):
		return self.pgmenergy.getPosition();
	
	def asynchronousMoveTo(self,newPos):
		if self.verbose: self.logger.info("asynchronousMoveTo(%r)..."%newPos)
		self.denergy.asynchronousMoveTo(newPos);
		self.uenergy.asynchronousMoveTo(newPos);
		self.pgmenergy.asynchronousMoveTo(newPos);
		if self.verbose: self.logger.info("...asynchronousMoveTo()")

	def isBusy(self):
		busyStatus= self.denergy.isBusy() or self.uenergy.isBusy() or self.pgmenergy.isBusy();
		return busyStatus;


#The Class for changing the underline EPICS motor at different ID polarisation conditions so that the same energy device name is used
class EnergyConsolidationClass(ScannableMotionBase):
	def __init__(self, name, pol, energy0, energy1, inPositionTolerance = None):
		self.logger = LoggerFactory.getLogger("EnergyConsolidationClass:%s" % name)
		self.verbose = True

		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.Units=['eV'];
		self.setLevel(5);
		self.setOutputFormat(["%11.7f"]);
		
		self.idpol = pol;
		self.energy0 = energy0;
		self.energy1 = energy1;
		self.energy = energy0;
		
		self.switchMotor();
		self.delayedSwitchAndMoveEnergyTimer = None
		self.energymovelog_time = datetime.now()
		self.idpolmovelog_time = datetime.now()
		
# 		self.skipDuplicateMoveOptimisation=True
		self.inPositionTolerance = inPositionTolerance

	def switchMotor(self):
		# Note that idpolPosition is only valid if it isn't moving
		pol=self.idpol.getPosition()
		if self.verbose: self.logger.info("switchMotor() energy=%r (pol=%r)" % (self.energy, pol))
		if pol != ID_PolarisationClass.READBACK_POSITIONS[5]: # None LA mode
			if self.energy.getMotor() != self.energy0.getMotor(): # motor is not correct
				self.energy = self.energy0;
# 				self.skipDuplicateMoveOptimisation=True
				if self.verbose: self.logger.info("switchMotor() energy now %r (non LA)" % self.energy)
		else: # LA mode
			if self.energy.getMotor() != self.energy1.getMotor(): # motor is not correct
				self.energy = self.energy1;
# 				self.skipDuplicateMoveOptimisation=True
				if self.verbose: self.logger.info("switchMotor() energy now %r (LA)" % self.energy)

	#Scannable Implementations
	def atScanStart(self):
		if self.verbose: self.logger.info("atScanStart()...")
		self.switchMotor();
# 		self.skipDuplicateMoveOptimisation=True
		if self.verbose: self.logger.info("...atScanStart()")

	def getPosition(self):
		self.switchMotor();
		return self.energy.getPosition();
	
	def asynchronousMoveTo(self,newPos):
		if self.verbose: self.logger.info("asynchronousMoveTo(%r)..."%newPos)
		# Since energy and polarisation could come very close together, delay until we can be
		# sure that polarisation has been set before we decide which energy to use and set.
		self.delayedSwitchAndMoveEnergyTimer = Timer(0.1, self.delayedSwitchAndMoveEnergy, [newPos])
		self.delayedSwitchAndMoveEnergyTimer.start()
		if self.verbose: self.logger.info("...asynchronousMoveTo(%r)"%newPos)

	def delayedSwitchAndMoveEnergy(self, newPos):
		# Delay any energy move until after any polarisation move has completed.
		if self.verbose: self.logger.info('delayedSwitchAndMoveEnergy(%r)... %s.isBusy()=%r' % (newPos, self.idpol.name, self.idpol.isBusy()))
		while self.idpol.isBusy():
			sleep(0.1)
			if self.verbose and (datetime.now() - self.idpolmovelog_time) > timedelta(seconds=1):
				self.logger.info('delayedSwitchAndMoveEnergy(): %s.isBusy()=%r' % (self.idpol.name, self.idpol.isBusy()))
				self.idpolmovelog_time = datetime.now()
		self.switchMotor();
# 		currentPos = self.getPosition()
# 		if self.skipDuplicateMoveOptimisation or not self.inPositionTolerance or (abs(newPos-currentPos) > self.inPositionTolerance):
		if self.energy.isBusy(): #ID218
			raise "Hardware is busy, so could not be moved at the moment!"
		self.energy.asynchronousMoveTo(newPos);
# 			self.skipDuplicateMoveOptimisation=False
# 		else:
# 			msg = "Skipping setting the energy as %r is closer to %r than the tolerance of %r" % (newPos, currentPos, self.inPositionTolerance)
# 			self.logger.info("asynchronousMoveTo() %s" % msg)
# 			if self.verbose: print "%s: %s" % (self.name, msg)
		if self.verbose: self.logger.info("...delayedSwitchAndMoveEnergy()")

	def isBusy(self):
		energy_busy = self.energy.isBusy()
		idpol_busy = self.idpol.isBusy()
		timer_busy = self.delayedSwitchAndMoveEnergyTimer and not self.delayedSwitchAndMoveEnergyTimer.finished.isSet()
		busy = energy_busy or idpol_busy or timer_busy
		if busy == None:
			self.logger.error('isBusy() = %r (%s=%r %s=%r Timer=%r!!!) assuming True' % (busy, self.energy.name, energy_busy, self.idpol.name, idpol_busy, timer_busy))
			busy=True
		if self.verbose and (datetime.now() - self.energymovelog_time) > timedelta(seconds=1):
			self.logger.info('isBusy() = %r (%s=%r %s=%r Timer=%r)' % (busy, self.energy.name, energy_busy, self.idpol.name, idpol_busy, timer_busy))
			self.energymovelog_time = datetime.now()
		return busy

"""
class NewEnergyConsolidationClass(ScannableMotor):
	def __init__(self, name, pol, energy0, energy1):
		self.logger = LoggerFactory.getLogger("NewEnergyConsolidationClass:%s" % name)
		self.verbose = True

		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.Units=['eV'];
		self.setLevel(5);
		self.setOutputFormat(["%11.7f"]);

		self.idpol = pol;
		self.energy0 = energy0;
		self.energy1 = energy1;
		
		self.setMotor(self.energy0.getMotor());
		self.configure();
	
	def getMode(self):
		return self.idpol.getPos();

	def updateMode(self):
		idpolmode = self.idpol.getPosition();	
		if self.verbose: self.logger.info("updateMode() idpolmode=%r" % idpolmode)

		if  idpolmode != ID_PolarisationClass.READBACK_POSITIONS[5]: # None LA mode
			newMotor = self.energy0.getMotor();
#			newLimitComponent = self.axis0.getMotorLimitsComponent();
		else: # LA mode
			newMotor = self.energy1.getMotor();
#			newLimitComponent = self.axis1.getMotorLimitsComponent();
			
		if self.getMotor() != newMotor: # motor is not correct
			if self.verbose: self.logger.info("updateMode() motor was %r now %r" % (self.getMotor(), newMotor))
			self.setMotor( newMotor );
			self.getAdditionalPositionValidators().clear();#A hack to clear the old limit component
			self.setMotorLimitsComponent(MotorLimitsComponent(newMotor));
#			self.setMotorLimitsComponent(newLimitComponent);

			self.configure();

		if self.verbose: self.logger.info("...updateMode()")

	def setMode(self, newMode):
		self.logger.info("setMode(%r)=%r" % (newMode, ID_PolarisationClass.READBACK_POSITIONS[newMode]))
		print "Changing " + self.getName() + " to " + ID_PolarisationClass.READBACK_POSITIONS[newMode] + " mode";
		
		self.idpol.setPol(newMode);
		self.updateMode();
		
		if self.verbose: self.logger.info("...setMode()")


	#Scannable Implementations
	def setAttribute(self, attributeName, value):
		if self.verbose: self.logger.info("setAttribute(self, attributeName=%r, value=%r)" % (attributeName, value))
		if attributeName == 'mode':
			self.setMode(value);
		else:
			super.setAttribute(attributeName, value);
	
	def atScanStart(self):
		if self.verbose: self.logger.info("atScanStart()...")
		self.updateMode();
		if self.verbose: self.logger.info("...atScanStart()")

	def getPosition(self):
		self.updateMode();
		return ScannableMotor.getPosition(self);
	
	def asynchronousMoveTo(self,newPos):
		if self.verbose: self.logger.info("asynchronousMoveTo(%r)..."%newPos)
		self.updateMode();
		ScannableMotor.asynchronousMoveTo(self, newPos);
		if self.verbose: self.logger.info("...asynchronousMoveTo()")
"""


#The Class for changing the ID polarisation
class ID_PolarisationClass(ScannableMotionBase):
	READBACK_POSITIONS = ['None', 'PosCirc', 'NegCirc', 'Horizontal', 'Vertical', 'LinArb', 'ERROR']
	POLARISATIONS = { 0:'None', 
					  1:'PosCirc', 
					  2:'NegCirc',
					  3:'Horizontal',
					  4:'Vertical',
					  5:'LinArb',
					  6:'ERROR' }
	
	def __init__(self, name, strSetPV, strGetPV, strStatusPV, strEnablePV):
		self.logger = LoggerFactory.getLogger("ID_PolarisationClass:%s" % name)
		self.verbose = True

		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
#		self.Units=[strUnit];
		self.setLevel(7);
#		self.setOutputFormat(["%20.12f"]);
		self.enable = ['Beamline', 'Machine Control Room'];
		self.positions = ['PosCirc', 'NegCirc', 'Horizontal', 'Vertical', 'LinArb'];
		
		self.chSetPol=CAClient(strSetPV);
		self.chSetPol.configure();
		self.chGetPol=CAClient(strGetPV);
		self.chGetPol.configure();
		self.chStatus=CAClient(strStatusPV);
		self.chStatus.configure();
		self.chEnable=CAClient(strEnablePV);
		self.chEnable.configure();
		self.currentPol='Unknown';
		self.demandPol='Unknown';
		self.strStatus='unknown';
		self.strEnable=self.enable[1]
		
# 		self.skipDuplicateMoveOptimisation=True

	def __repr__(self):
		format = "ID_PolarisationClass(name=%r, strSetPV=%r, strGetPV=%r, strStatusPV=%r, strEnablePV=%r)"
		return format % (self.name, self.chSetPol.getPvName(), self.chGetPol.getPvName(), self.chStatus.getPvName(), self.chEnable.getPvName())

	def getPositioner(self, channel, dict):
		value = int( self.caget(channel) );
		return dict[value];

	def setPositioner(self, channel, dict, newValue):
		if self.verbose: self.logger.info("setPositioner(channel=%r, dict=%r, newValue=%r)..."%(channel, dict, newValue))
		keys = dict.keys();
		values=dict.values();

		if newValue in keys:
			out=newValue;
		elif newValue in values:
			out=values.index(newValue);
		else:
			self.logger.info("setPositioner(): %s" %
				 ('Wrong parameter, please use one of ' + str(keys) + ' or ' + str(values)))
			print 'Wrong parameter, please use one of ' + str(keys) + ' or ' + str(values);
			return;
		
		self.caput(channel, out);
		if self.verbose: self.logger.info("...setPositioner()")


	#Scannable Implementations
	def atScanStart(self):
		if self.verbose: self.logger.info("atScanStart()...")
		if not self.chSetPol.isConfigured():
			self.chSetPol.configure()
		if not self.chGetPol.isConfigured():
			self.chGetPol.configure()
		if not self.chStatus.isConfigured():
			self.chStatus.configure()
		if not self.chEnable.isConfigured():
			self.chEnable.configure()
# 		self.skipDuplicateMoveOptimisation=True

	def getPosition(self):
		return self.getPol();
	
	def asynchronousMoveTo(self,newPos):
		if self.verbose: self.logger.info("asynchronousMoveTo(%r)..."%newPos)
		# Set the pol for the first point in a scan and every time the pol subsequently changes
		if newPos <> self.getPol(): #or self.skipDuplicateMoveOptimisation:
			self.demandPol = newPos
			self.setPol(self.demandPol)
# 			self.skipDuplicateMoveOptimisation=False
		else:
			self.logger.info("asynchronousMoveTo() skipping setting the polarisation to same value to save time %r=%r" % (newPos, self.currentPol))
		if self.verbose: self.logger.info("...asynchronousMoveTo()")

	def isBusy(self):
		result = True;
		try:
			self.checkReady();
		except:
			self.logger.error("isbusy() self.checkReady() raised an exception, returning True.", sys.exc_info())
			return True
		if  self.strStatus == "Ready":
			result = False;
		elif self.strStatus == "Failed, control of ID required.":
			self.logger.warn("isBusy(): strStatus Failed, attempting the move again...")
			self.setPol(self.demandPol);
		elif self.strStatus == "Failed, ID already moving":
			self.logger.warn("isBusy(): strStatus Failed, ID already moving")
		elif not self.strStatus in ("Resetting energy for polarisation",
									"Resetting energy for polarisation (la)",
									"Setting Row Phase to Linear Arbitrary",
									"Setting Row Phase to Linear Vertical",
									"Setting Row Phase to Linear Horizontal",
									"Setting Row Phase to Positive Circular",
									"Setting Row Phase to Negative Circular"):
			self.logger.warn("isBusy(): strStatus neither Ready, Failed nor (re)setting: %s" % self.strStatus)
		return result;

	def checkReady(self):
		if self.chStatus.isConfigured():
			self.strStatus=self.chStatus.caget()
		else:
			self.chStatus.configure()
			self.strStatus=self.chStatus.caget()
			self.chStatus.clearup()
		return self.strStatus;

	def checkEnable(self):
		if self.chEnable.isConfigured():
			e=self.chEnable.caget()
		else:
			self.chEnable.configure()
			e=self.chEnable.caget()
			self.chEnable.clearup()
		ne=int(float(e));
		self.strEnable=self.enable[ne];
		if ne ==0:
			return True;
		else:
			return False;

	def atScanEnd(self):
		if self.verbose: self.logger.info("atScanEnd()...")
		if self.chSetPol.isConfigured():
			self.chSetPol.clearup()
		if self.chGetPol.isConfigured():
			self.chGetPol.clearup()
		if self.chStatus.isConfigured():
			self.chStatus.clearup()
		if self.chEnable.isConfigured():
			self.chEnable.clearup()

	def getPol(self):
		if self.chGetPol.isConfigured():
			p=self.chGetPol.caget()
		else:
			self.chGetPol.configure()
			p=self.chGetPol.caget()
			self.chGetPol.clearup()

		np=int(float(p));
		self.currentPol=ID_PolarisationClass.READBACK_POSITIONS[np]
		return self.currentPol;

	def setPol(self, x):
		if self.verbose: self.logger.info("setPol(x=%r)..."%x)
		
		while not self.checkEnable():
			self.logger.info("setPol(): %s" %
				  "ID is currently under Machine Control")
			print "ID is currently under Machine Control"
			sleep(10);
		
		if not (x in self.positions):
			self.logger.warn("setPol(): %r not in %r" % (x, ", ".join(self.positions)))
			self.logger.info("setPol(): %s" %
				  "Wrong parameter, must be one of this: 'PosCirc', 'NegCirc', 'Horizontal', 'Vertical', 'LinArb'")
			msg="Wrong parameter, must be one of this: 'PosCirc', 'NegCirc', 'Horizontal', 'Vertical', 'LinArb'"
			raise Exception(msg)
		xx=self.positions.index(x);
		if self.chSetPol.isConfigured():
			self.chSetPol.caput(xx)
		else:
			self.chSetPol.configure()
			self.chSetPol.caput(xx)
			self.chSetPol.clearup()
		
		if self.verbose: self.logger.info("...setPol()")

	def toString(self):
		ss=self.getName() + ": Current Polarisation is " + self.getPol() + ". (Total five polarisation settings are: 'PosCirc', 'NegCirc', 'Horizontal', 'Vertical', 'LA')";
		return ss;

"""
#The Class for changing the ID poslarisation
class ID_PolarisationWithMonitorClass(ID_PolarisationClass, MonitorListener):
	
	def __init__(self, name, strSetPV, strGetPV, strStatusPV, strEnablePV):
		self.logger = LoggerFactory.getLogger("ID_PolarisationWithMonitorClass:%s" % name)
		self.verbose = True

		try:
			ID_PolarisationClass.__init__(self, name, strSetPV, strGetPV, strStatusPV, strEnablePV);
#			super(EpicsMotorClass, self).__init__(name, pvRootMotor, strUnit, strFormat);
		except AttributeError, err:
			self.logger.error("Trying to call superclass constructor: ", err)

		# The call to the parent class constructor will overwrite the logger.
		self.logger = LoggerFactory.getLogger("ID_PolarisationWithMonitorClass:%s" % name)

		self.idenabled=False;
		self.monitor=self.chEnable.camonitor(self)

	def monitorChanged(self, mevent):
		idenabled=self.idenabled
		if int(mevent.getDBR().getIntValue()[0]) is 0:
			self.idenabled = True;
		else:
			self.idenabled = False;
		if self.verbose and idenabled <> self.idenabled:
			self.logger.info("monitorChanged(%r) idenabled was %r now %r" % (mevent, idenabled, self.idenabled))

	def checkEnable(self):
		return self.idenabled;
"""
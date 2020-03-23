"""
A Controller for Continuous Energy moving of both PGM energy and ID gap motors at Constant Velocity

@author: Fajin Yuan 
@since: 12 August 2019
"""

from datetime import datetime, timedelta
from gda.device import DeviceBase, DeviceException
from gda.device.continuouscontroller import ConstantVelocityMoveController
from gdascripts.scannable.epics.PvManager import PvManager
from java.util.concurrent import Callable
from org.slf4j import LoggerFactory
import threading, time
import installation
from time import sleep

ID_GAP_END_OFFSET=0.00 # value used to make sure ID gap stops at the same time as PGM Energy

class ContinuousPgmEnergyIDGapMoveController(ConstantVelocityMoveController, DeviceBase):
    '''Controller for constant velocity scan moving both PGM Energy and ID Gap at same time at constant speed respectively.
        It works for both Live and Dummy mode.
    '''
    def __init__(self, name, energy, idpvroot, move_pgm=True, move_id=True, detune=None): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("ContinuousPgmEnergyIDGapMoveController:%s" % name)
        self.verbose = False
        self.setName(name)
        self._start_event = threading.Event()
        self._movelog_time = datetime.now()
        self._energy = energy
        #PGM
        self._pgm_energy=self._energy.scannables.getGroupMemberByName("pgmenergy")
        self._pgm_energy_speed_orig = None
        self._pgm_runupdown_time = None
        #ID
        self._id_gap=self._energy.scannables.getGroupMemberByName("jgap")
        self._id_gap_speed_orig=None
        self._id_runupdown_time = None
        self.idpvs = PvManager({'vel':'BLGSETVEL',
                                'acc':'IDGSETACC'}, idpvroot)
        if installation.isLive():
            self.idpvs.configure()
            
        self.pgm_energy_positions=[]
        self.id_gap_positions=[]
        self._start_time = None
        
        #behaviour properties
        self._move_pgm = move_pgm
        self._move_id  = move_id
        self.detune=detune
        self.idspeedfactor=1.0
        self.pgmspeedfactor=1.0
        self.idstartdelaytime=0.0

    # Implement: public interface ConstantVelocityMoveController extends ContinuousMoveController
    def setStart(self, start): # double
        self._move_start = start
        if self.verbose: self.logger.info('setStart(%r)' % start)
    
    def setEnd(self, end): # double
        self._move_end = end
        if self.verbose: self.logger.info('setEnd(%r)' % end)
    
    def setStep(self, step): # double
        self._move_step = step 
        if self.verbose: self.logger.info('setStep(%r)' % step)

    # Implement: public interface ContinuousMoveController extends HardwareTriggerProvider
    def PreparePGMForMove(self):
        
        self._pgm_energy_speed_orig = self._pgm_energy.speed #current speed in EPICS
   
        ### Calculate main cruise moves & speeds from start/end/step in eV
        self._pgm_energy_speed = (abs(self._move_end - self._move_start) * 1000.0/ self.getTotalTime())*self.getPGMSpeedFactor()
        
        ### Calculate ramp distance from required speed and ramp times
        #check speed within limits
        if self._pgm_energy_speed<=0.000 or self._pgm_energy_speed>10.0: #eV/sec
            print ("Calculated PGM energy speed %f is outside limits [%f, %f]!" % (self._pgm_energy_speed, 0.000, 10.0))
            raise DeviceException("Calculated PGM energy speed %f is outside limits [%f, %f]!" % (self._pgm_energy_speed, 0.000, 10.0))
        
        # Set the speed before we read out ramp times in case it is dependent
        self._pgm_energy.speed = self._pgm_energy_speed 
        # Should really be / | | | | | \ not /| | | | |\
        self._pgm_runupdown_time = self._pgm_energy.timeToVelocity
        self._pgm_runupdown = self._pgm_energy_speed / 2 * self._pgm_runupdown_time
        ### Move motor at full speed to start position
        self._pgm_energy.speed = self._pgm_energy_speed_orig
        if self.getEnergyMoveDirectionPositive():
            if self.verbose:
                self.logger.info('preparePGMForMove:_pgm_energy.asynchronousMoveTo(%r) @ %r (+ve)' % ((self._move_start * 1000.0 - self._pgm_runupdown), self._pgm_energy_speed_orig))
            self._pgm_energy.asynchronousMoveTo((self._move_start*1000.0 - self._pgm_runupdown))
        else:
            if self.verbose:
                self.logger.info('preparePGMForMove:_pgm_energy.asynchronousMoveTo(%r) @ %r (-ve)' % ((self._energy_start * 1000.0 + self._pgm_runupdown), self._pgm_energy_speed_orig))
            self._pgm_energy.asynchronousMoveTo((self._move_start * 1000.0 + self._pgm_runupdown))

    def PrepareIDForMove(self):

        if installation.isLive():
            #get JID gap speed from EPICS
            self._id_gap_speed_orig = float(self.idpvs['vel'].caget())
        else:
            self._id_gap_speed_orig = self._id_gap.speed
            
        #assume no rowphase motors need to move during continuous energy move
        
        # Calculate grating angles for given grating density, energy, mirror angle and offsets
        self._id_gap_start = self._energy.idgap(self._move_start, 1) #idgap calculation using energy in keV
        self._id_gap_end = self._energy.idgap(self._move_end, 1)
        
        if self.detune:
            self._id_gap_start = self._id_gap_start + float(self.detune.getPosition())
            self._id_gap_end = self._id_gap_end + float(self.detune.getPosition())
            
            ### Calculate main cruise moves & speeds from start/end/step
        self._id_gap_speed = abs(self._id_gap_end - self._id_gap_start) / self.getTotalTime()*self.idspeedfactor
        
        ### Calculate ramp distance from required speed and ramp times
        #check speed within limits
        if self._id_gap_speed<0.01 or self._id_gap_speed>1.0:
            print ("Calculated ID gap speed %f is outside limits [%f, %f]!" % (self._id_gap_speed, 0.01, 1.0))
            raise DeviceException("Calculated ID gap speed %f is outside limits [%f, %f]!" % (self._id_gap_speed, 0.01, 1.0))
        if installation.isLive():
            #Cannot set id_gap.speed through soft motor which in EPICS is read-only 
            self.idpvs['vel'].caput(self._id_gap_speed)
        else:
            self._id_gap.speed = self._id_gap_speed
                        
        #acceleration time per axis
        self._id_axis_speed=self._id_gap_speed/2
        self._id_runupdown_time_per_axis=self._id_axis_speed*4
        # Should really be / | | | | | \ not /| | | | |\
        self._id_runupdown_per_axis = self._id_axis_speed / 2 * self._id_runupdown_time_per_axis
        self._id_gap_runupdown = self._id_runupdown_per_axis * 2
        
        if installation.isLive():
            self.idpvs['vel'].caput(self._id_gap_speed_orig)
        else:
            self._id_gap.speed = self._id_gap_speed_orig 
            
        if self.getIDGapMoveDirectionPositive():
            if self.verbose:
                self.logger.info('prepareIDForMove:_id_gap.asynchronousMoveTo(%r) @ %r (+ve)' % ((self._id_gap_start - self._id_gap_runupdown), self._id_gap_speed_orig))
            self._id_gap.asynchronousMoveTo((self._id_gap_start - self._id_gap_runupdown))
        else:
            if self.verbose:
                self.logger.info('prepareIDForMove:_id_gap.asynchronousMoveTo(%r) @ %r (-ve)' % ((self._id_gap_start + self._id_gap_runupdown), self._id_gap_speed_orig))
            self._id_gap.asynchronousMoveTo((self._id_gap_start + self._id_gap_runupdown))

    def prepareForMove(self):
        if self.verbose: self.logger.info('prepareForMove()...')
        if self.isPGMMoveEnabled():
            self.PreparePGMForMove()
        else:
            if self.verbose:
                self.logger.info('PGM move is disabled in %r' % (self.getName()))

        if self.isIDMoveEnabled():
            self.PrepareIDForMove()
        else:
            if self.verbose:
                self.logger.info('ID move is disabled in %r' % (self.getName()))
            
        if not self.isPGMMoveEnabled() and not self.isIDMoveEnabled():
            print ("Both PGM and ID moves are disabled so no scan will occur!")
            raise DeviceException("Both PGM and ID moves are disabled so no scan will occur!")
        
        self.waitWhileMoving()
        ### Calculate trigger delays
        if self.verbose:
            self.logger.info('...prepareForMove')

    def startMove(self):
        if self.verbose: self.logger.info('startMove()...')
        
        # Notify all position callables to start waiting for their time
        self._start_time = datetime.now()
        self._start_event.set()
        # Start threads to start ID & PGM and at the correct times
        if self.isPGMMoveEnabled():
            self._pgm_energy.speed = self._pgm_energy_speed
        
        if self.isIDMoveEnabled():
            if installation.isLive():
                self.idpvs['vel'].caput(self._id_gap_speed)
            else:
                self._id_gap.speed = self._id_gap_speed 
        
        if self.isPGMMoveEnabled():
            if self.getEnergyMoveDirectionPositive():
                if self.verbose: self.logger.info('startMove PGM Energy: _pgm_energy.asynchronousMoveTo(%r) @ %r (+ve)' % (
                                                        (self._move_end * 1000.0 + self._pgm_runupdown), self._pgm_energy_speed))
                self._pgm_energy.asynchronousMoveTo((self._move_end * 1000.0 + self._pgm_runupdown))
            else:
                if self.verbose: self.logger.info('startMove PGM Energy: _pgm_energy.asynchronousMoveTo(%r) @ %r (-ve)' % (
                                                        (self._move_end * 1000.0 - self._pgm_runupdown), self._pgm_energy_speed))
                self._pgm_energy.asynchronousMoveTo((self._move_end * 1000.0 - self._pgm_runupdown))
                
        if self.isIDMoveEnabled():
            sleep(self.getIDStartDelayTime())
            if self.getIDGapMoveDirectionPositive():
                if self.verbose: self.logger.info('startMove ID Gap: _id_gap.asynchronousMoveTo(%r) @ %r (+ve)' % (
                                                        (self._id_gap_end + ID_GAP_END_OFFSET + self._id_gap_runupdown), self._id_gap_speed))
                self._id_gap.asynchronousMoveTo((self._id_gap_end + ID_GAP_END_OFFSET + self._id_gap_runupdown))
            else:
                if self.verbose: self.logger.info('startMove ID Gap: _id_gap.asynchronousMoveTo(%r) @ %r (-ve)' % (
                                                        (self._id_gap_end - ID_GAP_END_OFFSET - self._id_gap_runupdown), self._id_gap_speed))
                self._id_gap.asynchronousMoveTo((self._id_gap_end - ID_GAP_END_OFFSET - self._id_gap_runupdown))
        # How do we trigger the detectors, since they are 'HardwareTriggerable'?
        if self.verbose: self.logger.info('...startMove')

    def isMoving(self):
        if self.verbose and (datetime.now() - self._movelog_time) > timedelta(seconds=1):
            self.logger.info('isMoving() _pgm_energy=%r @ %r, _id_gap=%r @ %r' % (
                self._pgm_energy.isBusy(), self._pgm_energy(),
                self._id_gap.isBusy(), self._id_gap()))
            self._movelog_time = datetime.now()
        return self._pgm_energy.isBusy() or self._id_gap.isBusy()

    def waitWhileMoving(self):
        if self.verbose: self.logger.info('waitWhileMoving()...')
        while self.isMoving():
            time.sleep(1)
        if self.verbose: self.logger.info('...waitWhileMoving()')

    def stopAndReset(self):
        if self.verbose: self.logger.info('stopAndReset()')
        self._start_time = None
        self._start_event.clear()
        if self.isPGMMoveEnabled():
            self._pgm_energy.stop()
        if self.isIDMoveEnabled():
            self._id_gap.stop()
        self._restore_orig_speed()

    # Implement: public interface HardwareTriggerProvider extends Device
    def setTriggerPeriod(self, seconds): # double
        self._triggerPeriod = seconds
        if self.verbose: self.logger.info('setTriggerPeriod(%r)' % seconds)

    def getNumberTriggers(self):
        triggers = self.getTotalMove() / abs(self._move_step)
        if self.verbose: self.logger.info('getNumberTriggers()=%r (%r)' % (int(triggers), triggers))
        return int(triggers)

    def getTotalTime(self):
        totalTime = self.getNumberTriggers() * self._triggerPeriod
        if self.verbose: self.logger.info('getTotalTime()=%r' % totalTime)
        return totalTime

    def getTimeToVelocity(self):
        return self._pgm_runupdown_time

    # Override: public abstract class DeviceBase implements Device, ConditionallyConfigurable, Localizable
        # None needed

    # Other functions
    def getTotalMove(self):
        totalMove = abs(self._move_end - self._move_start)
        if self.verbose: self.logger.info('getTotalMove()=%r' % totalMove)
        return totalMove

    def getEnergyMoveDirectionPositive(self):
        return (self._move_end - self._move_start) > 0

    def getIDGapMoveDirectionPositive(self):
        return (self._id_gap_end - self._id_gap_start) > 0
    
    class DelayableCallable(Callable):
    
        def __init__(self, controller, demand_position):
            #self.start_event = threading.Event()
            self.start_event = controller._start_event
            self._controller, self._demand_position = controller, demand_position
            self.logger = LoggerFactory.getLogger("ContinuousPgmEnergyIDGapMoveController:%s:DelayableCallable[%r]" % (controller.name, demand_position))
            if self._controller.verbose:
                self.logger.info('__init__(%r, %r)...' % (controller.name, demand_position))
    
        def call(self):
            if self._controller.verbose: self.logger.info('call...')
            # Wait for controller to start all motors moving and set start time
            if self._controller._start_time:
                if self._controller.verbose: self.logger.info('start_time=%r' % (self._controller._start_time))
            else:
                if self._controller.verbose: self.logger.info('wait()...')
                timeout=60
                self.start_event.wait(timeout)
                if not self.start_event.isSet():
                    raise Exception("%rs timeout waiting for startMove() to be called on %s at position %r." % (timeout, self._controller.name, self._demand_position))
                if self._controller.verbose: self.logger.info('...wait()')
            # Wait for delay before actually move start and then a time given by
            # how far through the scan this point is
            
            complete = abs( (self._demand_position - self._controller._move_start) /
                            (self._controller._move_end - self._controller._move_start) )
            sleeptime_s = (self._controller._pgm_runupdown_time + (complete * self._controller.getTotalTime()))
            
            delta = datetime.now() - self._controller._start_time
            delta_s = delta.seconds + delta.microseconds/1000000.
            if delta_s > sleeptime_s:
                self.logger.warn('Sleep time already past!!! sleeptime_s=%r, delta_s=%r, sleeptime_s-delta_s=%r' % (sleeptime_s, delta_s, sleeptime_s-delta_s))
            else:
                if self._controller.verbose:
                    self.logger.info('sleeping... sleeptime_s=%r, delta_s=%r, sleeptime_s-delta_s=%r' % (sleeptime_s, delta_s, sleeptime_s-delta_s))
                time.sleep(sleeptime_s-delta_s)
            
            energy = self._controller._pgm_energy()

            if self._controller.verbose:
                self.logger.info('...DelayableCallable:call returning %r, %r' % (self._demand_position, energy))
            return self._demand_position, energy

    def getPositionCallableExtraNames(self):
        return ['readback']

    def getPositionCallableFormat(self):
        return ['%f', '%f']

    # public Callable<T> getPositionCallable() throws DeviceException;
    def getPositionCallableFor(self, position):
        if self.verbose: self.logger.info('getPositionCallableFor(%r)...' % position)
        return self.DelayableCallable(self, position)
    
    def _restore_orig_speed(self):
        if self.isPGMMoveEnabled():
            if self._pgm_energy_speed_orig:
                if self.verbose: self.logger.info('Restoring original PGM Energy speed %r, was %r' % (self._pgm_energy_speed_orig, self._pgm_energy.speed))
                self._pgm_energy.speed = self._pgm_energy_speed_orig
                self._pgm_energy_speed_orig = None
        if self.isIDMoveEnabled():
            if self._id_gap_speed_orig:
                if installation.isLive():
                    if self.verbose: self.logger.info('Restoring original ID gap speed %r, was %r' % (self._id_gap_speed_orig, self.idpvs['vel'].caget()))
                    self.idpvs['vel'].caput(self._id_gap_speed_orig)
                else:
                    if self.verbose: self.logger.info('Restoring original ID gap speed %r, was %r' % (self._id_gap_speed_orig, self._id_gap.speed))
                    self._id_gap.speed = self._id_gap_speed_orig 
                self._id_gap_speed_orig = None

    def atScanEnd(self):
        if self.verbose: self.logger.info('atScanEnd()...')
        self._restore_orig_speed()
        # Should we also move the pgm_energy to a known value too, such as the midpoint?
       
    def setIDStartDelayTime(self, t):
        self.idstartdelaytime=t
        
    def getIDStartDelayTime(self):
        return self.idstartdelaytime
     
    def setIDSpeedFactor(self, val):
        self.idspeedfactor=val
    
    def getIDSpeedFactor(self):
        return self.idspeedfactor
    
    def setPGMSpeedFactor(self, val):
        self.pgmspeedfactor=val
    
    def getPGMSpeedFactor(self):
        return self.pgmspeedfactor
        
    #https://jira.diamond.ac.uk/browse/I10-301
    def enableIDMove(self):
        self._move_id=True
    
    def disableIDMove(self):
        self._move_id=False
        
    def isIDMoveEnabled(self):
        return self._move_id

    def enablePGMMove(self):
        self._move_pgm=True
    
    def disablePGMMove(self):
        self._move_pgm=False
        
    def isPGMMoveEnabled(self):
        return self._move_pgm

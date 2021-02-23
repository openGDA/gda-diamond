"""
A Controller for Continuous Energy moving of both PGM or DCM energy and Hard X-ray or Soft X-ray ID gap motors at Constant Velocity.

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

ID_GAP_END_OFFSET = 0.00 # value used to make sure ID gap stops at the same time as PGM Energy
IID_GAP_SPEED_LOWER_LIMIT = 0.002
IID_GAP_SPEED_UPPER_LIMIT = 1.0
JID_GAP_SPEED_LOWER_LIMIT = 0.010
JID_GAP_SPEED_UPPER_LIMIT = 1.0

class ContinuousEnergyMoveController(ConstantVelocityMoveController, DeviceBase):
    '''Controller for constant velocity scan moving both PGM Energy and JID Gap, or DCM energy and IID gap at same time at constant speed respectively.
        It works for both Live and Dummy mode.
    '''
    def __init__(self, name, energy, idgap, idpvroot, move_mono=True, move_id=True): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("ContinuousEnergyMoveController:%s" % name)
        self.verbose = False
        self.setName(name)
        self._start_event = threading.Event()
        self._movelog_time = datetime.now()
        self._energy = energy
        #PGM
        self._mono_energy = energy.mono_energy
        self._mono_energy_speed_orig = None
        self._mono_runupdown_time = None
        #ID
        self._id_gap = idgap
        self._id_gap_speed_orig = None
        self._id_runupdown_time = None
        self.idpvs = PvManager({'vel':'BLGSETVEL',
                                'acc':'IDGSETACC'}, idpvroot)
        if installation.isLive():
            self.idpvs.configure()
            
        self.mono_energy_positions=[]
        self.id_gap_positions=[]
        self._start_time = None
        
        #behaviour properties
        self._move_mono = move_mono
        self._move_id  = move_id
        self.idspeedfactor=1.0
        self.monospeedfactor=1.0
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
    def PrepareMonoForMove(self):
        
        if self._mono_energy.getName() == "pgmenergy" :
            self.energy_scale = 1000.0 #convert energy from keV to eV
        else:
            self.energy_scale = 1.0
        
        self._mono_energy_speed_orig = self._mono_energy.speed #current speed in EPICS
   
        ### Calculate main cruise moves & speeds from start/end/step in eV
        self._mono_energy_speed = (abs(self._move_end - self._move_start) * self.energy_scale/ self.getTotalTime())*self.getMonoSpeedFactor()
        
        #check speed within limits
        if self._mono_energy_speed<=0.000 or self._mono_energy_speed>10.0: #eV/sec
            raise DeviceException("Calculated %s speed %f is outside limits [%f, %f]!" % (self._mono_energy.getName(), self._mono_energy_speed, 0.000, 10.0))
        
        ### Calculate ramp distance from required speed and ramp times
        # Set the speed before we read out ramp times in case it is dependent
        self._mono_energy.speed = self._mono_energy_speed 
        # Should really be / | | | | | \ not /| | | | |\
        self._mono_runupdown_time = self._mono_energy.timeToVelocity
        self._mono_runupdown = self._mono_energy_speed / 2 * self._mono_runupdown_time
        ### Move motor at full speed to start position
        self._mono_energy.speed = self._mono_energy_speed_orig
        if self.isEnergyMoveDirectionPositive():
            if self.verbose:
                self.logger.info('prepareMonoForMove: %s.asynchronousMoveTo(%r) @ %r (+ve)' % (self._mono_energy.getName(), (self._move_start * self.energy_scale - self._mono_runupdown), self._mono_energy_speed_orig))
            self._mono_energy.asynchronousMoveTo((self._move_start * self.energy_scale - self._mono_runupdown))
        else:
            if self.verbose:
                self.logger.info('prepareMonoForMove: %s.asynchronousMoveTo(%r) @ %r (-ve)' % (self._mono_energy.getName(), (self._energy_start * self.energy_scale + self._mono_runupdown), self._mono_energy_speed_orig))
            self._mono_energy.asynchronousMoveTo((self._move_start * self.energy_scale + self._mono_runupdown))
    
    def id_speed_limits(self):
        if self._id_gap.getName() == 'jgap':
            return JID_GAP_SPEED_LOWER_LIMIT, JID_GAP_SPEED_UPPER_LIMIT
        else:
            return IID_GAP_SPEED_LOWER_LIMIT, IID_GAP_SPEED_UPPER_LIMIT        

    def PrepareIDForMove(self):
        GAP_SPEED_LOWER_LIMIT, GAP_SPEED_UPPER_LIMIT = self.id_speed_limits()

        if installation.isLive():
            #get ID gap speed from EPICS PV
            self._id_gap_speed_orig = float(self.idpvs['vel'].caget())
        else:
            self._id_gap_speed_orig = self._id_gap.speed
            
        #assume no row phase motors need to move during continuous energy move
        
        self._id_gap_start = self._energy.idgap(self._move_start) #idgap calculation using energy in keV
        self._id_gap_end = self._energy.idgap(self._move_end)
        
        ### Calculate main cruise moves & speeds from start/end/step
        self._id_gap_speed = abs(self._id_gap_end - self._id_gap_start) / self.getTotalTime()*self.idspeedfactor
        
        #check speed within limits
        if self._id_gap_speed < GAP_SPEED_LOWER_LIMIT or self._id_gap_speed > GAP_SPEED_UPPER_LIMIT:
            raise DeviceException("Calculated ID gap speed %f is outside limits [%f, %f]!" % (self._id_gap_speed, GAP_SPEED_LOWER_LIMIT, GAP_SPEED_UPPER_LIMIT))

        if installation.isLive():
            #Cannot set id_gap.speed through soft motor which in EPICS is read-only 
            self.idpvs['vel'].caput(self._id_gap_speed)
        else:
            self._id_gap.speed = self._id_gap_speed
                        
        ### Calculate ramp distance from required speed and ramp times
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
            
        if self.isIDGapMoveDirectionPositive():
            if self.verbose:
                self.logger.info('prepareIDForMove: _id_gap.asynchronousMoveTo(%r) @ %r (+ve)' % ((self._id_gap_start - self._id_gap_runupdown), self._id_gap_speed_orig))
            self._id_gap.asynchronousMoveTo(self._id_gap_start - self._id_gap_runupdown)
        else:
            if self.verbose:
                self.logger.info('prepareIDForMove: _id_gap.asynchronousMoveTo(%r) @ %r (-ve)' % ((self._id_gap_start + self._id_gap_runupdown), self._id_gap_speed_orig))
            self._id_gap.asynchronousMoveTo(self._id_gap_start + self._id_gap_runupdown)

    def prepareForMove(self):
        if self.verbose: self.logger.info('prepareForMove()...')
        if self.isMonoMoveEnabled():
            self.PrepareMonoForMove()
        else:
            if self.verbose:
                self.logger.info('%s move is disabled in %r' % (self._mono_energy.getName(), self.getName()))

        if self.isIDMoveEnabled():
            self.PrepareIDForMove()
        else:
            if self.verbose:
                self.logger.info('ID %s move is disabled in %r' % (self._id_gap.getName(), self.getName()))
            
        if not self.isMonoMoveEnabled() and not self.isIDMoveEnabled():
            print ("Both PGM and ID moves are disabled so no scan will occur!")
            raise DeviceException("Both PGM and ID moves are disabled so no scan will occur!")
        
        self.waitWhileMoving()
        if self.verbose:
            self.logger.info('...prepareForMove')

    def startMove(self):
        if self.verbose: self.logger.info('startMove()...')
        
        # Notify all position callables to start waiting for their time
        self._start_time = datetime.now()
        self._start_event.set()
        # Start threads to start ID & PGM and at the correct times
        if self.isMonoMoveEnabled():
            self._mono_energy.speed = self._mono_energy_speed
        
        if self.isIDMoveEnabled():
            if installation.isLive():
                self.idpvs['vel'].caput(self._id_gap_speed)
            else:
                self._id_gap.speed = self._id_gap_speed 
        
        if self.isMonoMoveEnabled():
            if self.isEnergyMoveDirectionPositive():
                if self.verbose: self.logger.info('startMove Mono Energy: _mono_energy.asynchronousMoveTo(%r) @ %r (+ve)' % (
                                                        (self._move_end * self.energy_scale + self._mono_runupdown), self._mono_energy_speed))
                self._mono_energy.asynchronousMoveTo((self._move_end * self.energy_scale + self._mono_runupdown))
            else:
                if self.verbose: self.logger.info('startMove Mono Energy: _mono_energy.asynchronousMoveTo(%r) @ %r (-ve)' % (
                                                        (self._move_end * self.energy_scale - self._mono_runupdown), self._mono_energy_speed))
                self._mono_energy.asynchronousMoveTo((self._move_end * self.energy_scale - self._mono_runupdown))
                
        if self.isIDMoveEnabled():
            sleep(self.getIDStartDelayTime())
            if self.isIDGapMoveDirectionPositive():
                if self.verbose: self.logger.info('startMove ID Gap: _id_gap.asynchronousMoveTo(%r) @ %r (+ve)' % (
                                                        (self._id_gap_end + ID_GAP_END_OFFSET + self._id_gap_runupdown), self._id_gap_speed))
                self._id_gap.asynchronousMoveTo((self._id_gap_end + ID_GAP_END_OFFSET + self._id_gap_runupdown))
            else:
                if self.verbose: self.logger.info('startMove ID Gap: _id_gap.asynchronousMoveTo(%r) @ %r (-ve)' % (
                                                        (self._id_gap_end - ID_GAP_END_OFFSET - self._id_gap_runupdown), self._id_gap_speed))
                self._id_gap.asynchronousMoveTo((self._id_gap_end - ID_GAP_END_OFFSET - self._id_gap_runupdown))

        if self.verbose: self.logger.info('...startMove')

    def isMoving(self):
        if self.verbose and (datetime.now() - self._movelog_time) > timedelta(seconds=1):
            self.logger.info('isMoving() _mono_energy=%r @ %r, _id_gap=%r @ %r' % (
                self._mono_energy.isBusy(), self._mono_energy(), self._id_gap.isBusy(), self._id_gap()))
            self._movelog_time = datetime.now()
        return self._mono_energy.isBusy() or self._id_gap.isBusy()

    def waitWhileMoving(self):
        if self.verbose: self.logger.info('waitWhileMoving()...')
        while self.isMoving():
            time.sleep(1)
        if self.verbose: self.logger.info('...waitWhileMoving()')

    def stopAndReset(self):
        if self.verbose: self.logger.info('stopAndReset()')
        self._start_time = None
        self._start_event.clear()
        if self.isMonoMoveEnabled():
            self._mono_energy.stop()
        if self.isIDMoveEnabled():
            if installation.isLive():
                print("ID gap motion stop is not supported according to ID-Group instruction. Please wait for the Gap motion to complete!")
            else:
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
        total_time = self.getNumberTriggers() * self._triggerPeriod
        if self.verbose: self.logger.info('getTotalTime()=%r' % total_time)
        return total_time

    def getTimeToVelocity(self):
        return self._mono_runupdown_time

    # Override: public abstract class DeviceBase implements Device, ConditionallyConfigurable, Localizable
        # None needed

    # Other functions
    def getTotalMove(self):
        total_move = abs(self._move_end - self._move_start)
        if self.verbose: self.logger.info('getTotalMove()=%r' % total_move)
        return total_move

    def isEnergyMoveDirectionPositive(self):
        return (self._move_end - self._move_start) > 0

    def isIDGapMoveDirectionPositive(self):
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
                    raise RuntimeError("%rs timeout waiting for startMove() to be called on %s at position %r." % (timeout, self._controller.name, self._demand_position))
                if self._controller.verbose: self.logger.info('...wait()')
            # Wait for delay before actually move start and then a time given by
            # how far through the scan this point is
            
            complete = abs( (self._demand_position - self._controller._move_start) /
                            (self._controller._move_end - self._controller._move_start) )
            sleeptime_s = (self._controller._mono_runupdown_time + (complete * self._controller.getTotalTime()))
            
            delta = datetime.now() - self._controller._start_time
            delta_s = delta.seconds + delta.microseconds/1000000.
            if delta_s > sleeptime_s:
                self.logger.warn('Sleep time already past!!! sleeptime_s=%r, delta_s=%r, sleeptime_s-delta_s=%r' % (sleeptime_s, delta_s, sleeptime_s-delta_s))
            else:
                if self._controller.verbose:
                    self.logger.info('sleeping... sleeptime_s=%r, delta_s=%r, sleeptime_s-delta_s=%r' % (sleeptime_s, delta_s, sleeptime_s-delta_s))
                time.sleep(sleeptime_s-delta_s)
            
            energy = self._controller._mono_energy()

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
        if self.isMonoMoveEnabled() and self._mono_energy_speed_orig:
            if self.verbose: self.logger.info('Restoring original PGM Energy speed %r, was %r' % (self._mono_energy_speed_orig, self._mono_energy.speed))
            self._mono_energy.speed = self._mono_energy_speed_orig
            self._mono_energy_speed_orig = None
        if self.isIDMoveEnabled() and self._id_gap_speed_orig:
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
    
    def setMonoSpeedFactor(self, val):
        self.monospeedfactor=val
    
    def getMonoSpeedFactor(self):
        return self.monospeedfactor
        
    #https://jira.diamond.ac.uk/browse/I10-301
    def enableIDMove(self):
        self._move_id=True
    
    def disableIDMove(self):
        self._move_id=False
        
    def isIDMoveEnabled(self):
        return self._move_id

    def enableMonoMove(self):
        self._move_mono=True
    
    def disableMonoMove(self):
        self._move_mono=False
        
    def isMonoMoveEnabled(self):
        return self._move_mono

from gda.jython.commands.GeneralCommands import add_reset_hook
from gda.epics import CachedLazyPVFactory
from gda.device.scannable import ScannableBase
from gda.scan import ScanPositionProviderFactory
from uk.ac.diamond.daq.concurrent import Async
from java.lang import ThreadLocal

import logging
from time import sleep
from setup import rate

from gdascripts.pd.time_pds import showtimeClass

CTRL_TO_NAME = ['Manual', 'Auto']
NAME_TO_CTRL = {'manual': 0, 'auto': 1}

ERROR_MASK = 1
AT_SETPOINT_MASK = 1 << 1
HEATER_ON_MASK = 1 << 2
PUMP_ON_MASK = 1 << 3
PUMP_AUTO_MASK = 1 << 4

DSC_MASK = 1 << 1

class Linkam(ScannableBase):
    '''
    Linkam 3 scannable

    Can be used either as a normal scannable (ie for step scans)

        >>> scan linkam3 20 100 5 ncddetectors

    or by setting up ramps to run automatically and then collect data at regular
    intervals.

        >>> scan linkam3.intervals(6) linkam3.ramps((50, 10), (50, 25), (45, 5)) ncddetectors

    where:
        - the 6 in 'intervals(6)' determines the interval between data collections
        - the ramps are a list of (temp, rate) pairs. If two consecutive pairs specify the same temperature,
            the second is treated as a hold with its second value being the duration (second ramp above is hold
            for 25 seconds).

    The temperature can be set using the pos command

        >>> # set the linkam3 temp to 25 'C
        >>> pos linkam3 25

    The ramp rate used for step scans and pos commands can be set via linkam3.ramp_rate

        >>> # get rate in C/min
        >>> linkam3.ramp_rate
        10
        >>> # Set the rate to 5 C/min
        >>> linkam3.ramp_rate = 5
        >>>

    Configuration should use the PV up to and including the final ':' in the common
    base PV, eg

        >>> linkam3 = Linkam('linkam3', 'BL22I-EA-TEMPC-05:')
    '''
    TEMP = 'TEMP'
    DSC = 'DSC'
    START = 'STARTHEAT'
    RATE = 'RAMPRATE:SET'
    RATE_RBV = 'RAMPRATE'
    RAMP_TIME = 'RAMPTIME'
    SETPOINT = 'SETPOINT:SET'
    SETPOINT_RBV = 'SETPOINT:SET'
    PUMP_CTRL = 'LNP_MODE:SET'
    PUMP_SPEED = 'LNP_SPEED:SET'
    PUMP_SPEED_RBV = 'LNP_SPEED'
    POWER = 'POWER'
    STATUS = 'STATUS'
    CONFIG = 'STAGE:CONFIG'

    def __init__(self, name, pv, fmt='%.2f', tolerance=0.2):
        self._ramping_thread = ThreadLocal()
        self._logger = logging.getLogger('gda.i22.linkam.' + name)
        self.name = name
        self.tolerance = tolerance
        self.pv = pv
        self._fmt= fmt
        self._pv = CachedLazyPVFactory(pv)
        self._shutdown_hooks = []
        self._add_listeners()
        add_reset_hook(self.shutdown)

        self.interval = 6
        self._ramp_future = None

        self.inputNames = ['temp']
        self._config_update() # Set dsc input/extranames

    def shutdown(self):
        '''Run shutdown hooks to remove monitors etc'''
        for hook in self._shutdown_hooks:
            try:
                hook()
            except:
                # we tried
                self._logger.error('Error running shutdown hook', exc_info=True)

    @property
    def temp(self):
        return self._pv.getDouble(self.TEMP)
    
    @property
    def dsc(self):
        return self._pv.getDouble(self.DSC)

    @property
    def setpoint(self):
        return self._pv.getDouble(self.SETPOINT_RBV)

    @setpoint.setter
    def setpoint(self, target):
        self._logger.debug('Setting setpoint to %s', target)
        if abs(self.temp - target) > self.tolerance and not self.running:
            self.running = True
        self._pv.set(self.SETPOINT, target)
        sleep(0.2)

    @property
    def ramp_time(self):
        return self._pv.getDouble(self.RAMP_TIME)

    @property
    def ramp_rate(self):
        return self._pv.getDouble(self.RATE_RBV)

    @ramp_rate.setter
    def ramp_rate(self, rate):
        self._logger.debug('Setting ramp rate to %s', rate)
        self._pv.set(self.RATE, rate)

    @property
    def pump_control(self):
        val = self._pv.getInteger(self.PUMP_CTRL)
        return CTRL_TO_NAME[val]

    @pump_control.setter
    def pump_control(self, value):
        if isinstance(value, str):
            value = NAME_TO_CTRL[value.lower()]
        self._logger.debug('Setting pump control to %s', CTRL_TO_NAME[value])
        self._pv.set(self.PUMP_CTRL, value)

    @property
    def pump_speed(self):
        return self._pv.getDouble(self.PUMP_SPEED_RBV)

    @pump_speed.setter
    def pump_speed(self, speed):
        if self.pump_control == 'Auto':
            raise ValueError("Can't set the pump speed in auto mode")
        self._logger.debug('Setting pump speed to %s', speed)
        self._pv.set(self.PUMP_SPEED, speed)
        
    @property
    def _config(self):
        return self._pv.getInteger(self.CONFIG)
    
    @property
    def dsc_enabled(self):
        return self._config & DSC_MASK > 0

    @property
    def _status(self):
        return self._pv.getInteger(self.STATUS)

    def _status_mask(self, mask):
        return self._status & mask > 0

    @property
    def at_setpoint(self):
        return self._status_mask(AT_SETPOINT_MASK)

    @property
    def heater_on(self):
        return self._status_mask(HEATER_ON_MASK)

    @property
    def pump_on(self):
        return self._status_mask(PUMP_ON_MASK)

    @property
    def pump_auto(self):
        return self._status_mask(PUMP_AUTO_MASK)

    @property
    def error(self):
        return self._status_mask(ERROR_MASK)

    @property
    def power(self):
        return self._pv.getDouble(self.POWER)

    @property
    def running(self):
        return self._pv.getInteger(self.START) == 1

    @running.setter
    def running(self, run_state):
        if isinstance(run_state, str):
            run_state = 1 if run_state.lower() == 'on' else 0
        self._logger.debug('Setting running state to %s', run_state)
        self._pv.set(self.START, 1 if run_state else 0)

    def start(self):
        self.running = True

    def stop(self):
        # self.running = False
        self.setpoint = self.temp
        if self._ramp_future is not None:
            self._ramp_future.cancel(True)
            self._ramp_future = None

    def atCommandFailure(self):
        self._logger.info('Stopping linkam after command failure')
        self.stop()

    def rawAsynchronousMoveTo(self, posn):
        self.setpoint = posn

    def rawGetPosition(self):
        if self.dsc_enabled:
            return self.temp, self.dsc
        else:
            return self.temp,

    def isBusy(self):
        return (not self._ramping_thread.get() and self._ramp_future is not None and not self._ramp_future.isDone()) or self.moving
    
    @property
    def moving(self):
        return abs(self.temp - self.setpoint) > self.tolerance and self.running

    def _temp_update(self, src, temp):
        pass

    def _state_update(self, src, state):
        pass

    def _setpoint_update(self, src, setpoint):
        pass
    
    def _config_update(self, *args):
        if self.dsc_enabled:
            self.extraNames = ['dsc']
            self.outputFormat = [self._fmt, self._fmt]
        else:
            self.extraNames = []
            self.outputFormat = [self._fmt]

    def _add_listeners(self):
        self._add_listener(self._pv.getPVInteger(self.CONFIG), self._config_update)
        # self._add_listener(self._pv.getPVDouble(self.TEMP), self._temp_update)
        # self._add_listener(self._pv.getPVDouble(self.STARTHEAT), self._state_update)
        # self._add_listener(self._pv.getPVDouble(self.SETPOINT_RBV), self._setpoint_update)

    def _add_listener(self, pv, listener):
        '''Add a listener to a pv and setup shutdown hook to remove it'''
        pv.addObserver(listener)
        self._shutdown_hooks.append(lambda: pv.removeObserver(listener))

    def ramps(self, *ramps):
        ramps = ((self.temp,),) + ramps
        self._logger.info('Running ramps: %s', ramps)
        time = 0
        for prev, curr in zip(ramps, ramps[1:]):
            if abs(curr[0] - prev[0]) < self.tolerance: # hold
                time += curr[1]
            else: # ramp
                time += float(abs(curr[0] - prev[0])) * 60/curr[1]
        print('Expected run time ~%f' %time)
        steps = int(time // self.interval) + 2 # +1 to counter truncating to int, +1 to include end point
        self._ramp_future = Async.submit(lambda: self.run_ramps(*ramps[1:]))
        return ScanPositionProviderFactory.create([i*self.interval for i in range(steps)])

    def run_ramps(self, *ramps):
        self._logger.info("Starting to run %d ramps", len(ramps))
        self._ramping_thread.set(True) # override the isBusy check if we're the ones being busy
        ramps = ((self.temp,),) + ramps
        try:
            if self.moving:
                raise ValueError('Linkam is already busy')
            for prev, curr in zip(ramps, ramps[1:]):
                self._logger.info('Starting ramp %s', curr)
                if abs(curr[0] - prev[0]) < self.tolerance: # hold
                    self._logger.info("Holding at current temp for %f", curr[1])
                    sleep(curr[1])
                else: # ramp
                    self._logger.info('Moving to %f at %f C/s', curr[0], curr[1])
                    self.ramp_rate = curr[1]
                    self(curr[0])
        except:
            self._logger.error("Failed to run ramps", exc_info=True)

    def intervals(self, s):
        self.interval = s
        return ShowtimeProxy(self)

    @property
    def readout(self):
        return ReadOnlyScannable(self.name, self)

class ShowtimeProxy(showtimeClass):
    def __init__(self, source):
        super(ShowtimeProxy, self).__init__(source.name)
        self._source = source
        self.inputNames = ['time']
        self.extraNames = list(source.inputNames) + list(source.extraNames)
        self.outputFormat = ['%.1f'] + list(source.outputFormat)

    def rawGetPosition(self):
        return [showtimeClass.rawGetPosition(self)] + list(self._source.rawGetPosition())
    

class ReadOnlyScannable(ScannableBase):
    def __init__(self, name, source):
        self.name = name
        self.inputNames = []
        self.extraNames = list(source.inputNames) + list(source.extraNames)
        self.outputFormat = source.outputFormat[:]
        self.source = source

    def rawAsynchronousMoveTo(self, posn):
        pass

    def rawGetPosition(self):
        return self.source.getPosition()

    def isBusy(self):
        return False

class Ramp(object):
    def __init__(self, start, target=None, duration=None, interval=None):
        self._start = start
        self._target = target
        self._duration = duration
        self._interval = interval

        self._rate = float(self._target - self._start) / self.duration

    @property
    def points(self):
        return self
    

class RampRunner(object):
    def __init__(self, linkam, *ramps):
        pass

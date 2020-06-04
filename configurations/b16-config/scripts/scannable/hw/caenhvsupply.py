from scannable.moveToCore import DynamicPvManager
from gda.device.scannable import ScannableMotionBase
import time       

PUT_TIMEOUT = 5

VERBOSE = False

def _log(msg):
    if VERBOSE:
        print '* ' + msg

FAULT_MSG = """
** EPICS is reporting an error status for CH%i of CAEN high voltage supply. **

RESOLUTION: If the channel has tripped make sure the current set value (ISET) is
            set appropriately. 
            
            After resolving this, the channel may need to be manually enabled
            from the EPICS screen to clear the fault status register.
            This *MUST* be done if the channel has tripped.
"""

class CaenHvSupply(ScannableMotionBase):

    def __init__(self, name, pv_prefix, channel):
        self.name = name
        self.inputNames = ['ch%i_vset' % channel]
        self.extraNames = ['ch%i_vmon' % channel, 'ch%i_enabled' % channel]
        self.outputFormat = ['%.2f', '%.2f', '%i']
        self._pvs = DynamicPvManager(pv_prefix)
        self._ch = int(channel)
        self.deadband = 1.
        self.deadband_for_zero = 2.
        self.required_seconds_at_target = 3.
        self.seconds_after_disable = 3.
        
    def rawAsynchronousMoveTo(self, t):
        """Block while moving to the target voltage. Always enable of target is >0.
        If target is 0 then allow the ramp to drop the voltage to 0 and *then* disable.
        """
        
        t = float(t)
        if t < 0:
            raise Exception('Target temperature must be +ve (it was: %f).' % t)

        self._check_for_fault()
        self._set_target(t)
        # TODO: assert it has been set

        if t != 0:
            self.enable(1)
        
        # The ramp status returns too soon so cannot be used. We must use the monitored value.
        # The thing overshoots so we need to make sure we are stable within the deadband
        number_of_times_at_target = 0
        while number_of_times_at_target < self.required_seconds_at_target:
            while not(self._is_at_temp(self._get_target())):
                time.sleep(.2)
            number_of_times_at_target += 1
            time.sleep(1)
            _log('Time remaining at target:' + str(self.required_seconds_at_target - number_of_times_at_target))
        
        # disable after reached 0
        if t == 0:
            self.enable(0)
            time
        self._check_for_fault()


    def rawIsBusy(self):
        return False  #  asynchMoveto blocks

    def rawGetPosition(self):
        return self._get_target(), self._get_monitored(), int(self._get_status_dict()['on'])

    def enable(self, b):
        b = bool(b)
        
        # Return if already in required state
        if b == self._get_status_dict()['on']:
            _log("Already " + ('enabled' if b else 'disabled'))
            return
        
        self._pvs['ON%i' % self._ch].caput(PUT_TIMEOUT, int(b))
        # The thing takes its sweet time to turn off, so wait
        while self._get_status_dict()['on'] != b:
            _log('enabling' if b else 'disabling')
            time.sleep(1)
        if not b:
            # takes a while to reach 0. Maybe okay with a cable attached, but for safety:
            _log('waiting for %fs' % self.seconds_after_disable)
            time.sleep(self.seconds_after_disable)

    def _set_target(self, t):
        self._pvs['VSET%i' % self._ch].caput(PUT_TIMEOUT, t)
    
    def _get_target(self):
        return float(self._pvs['VSET%i:RBV' % self._ch].caget())
    
    def _get_monitored(self):
        return float(self._pvs['VMON%i:RBV' % self._ch].caget())
    

    def _is_at_temp(self, t):
        # The thing got stuck around 1.8v when moving to zero
        deadband = self.deadband_for_zero if t == 0 else self.deadband
        return abs(self._get_monitored() - t) <= deadband
    
    def _get_status_dict(self):
        status = int(self._pvs['STAT%i:RBV' % self._ch].caget())
        
        return {
                'on': bool((2 ** 0) & status),
                'chan_tripped': bool((2 ** 7) & status)
               }
    def _check_for_fault(self):
        # include errors from the right hand batch of status flags, i.e. 'Chan Tripped' ... 'Calibration err'
        fault_mask =  sum([2 ** bit for bit in 7, 8, 9, 10, 11, 12, 13])# 0b11111110000000
        status = int(self._pvs['STAT%i:RBV' % self._ch].caget())
        if fault_mask & status:
            raise Exception(FAULT_MSG % self._ch)
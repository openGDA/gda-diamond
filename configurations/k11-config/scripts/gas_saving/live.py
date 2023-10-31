from gas_saving.valve import ValveController, Valve
from gda.device import DeviceException  # @UnresolvedImport
from gda.device import EnumPositionerStatus # @UnresolvedImport
from threading import Thread, Event


class EpicsValveController(ValveController):
    
    STATE_OPEN = "Open"
    STATE_CLOSE = "Closed"
   
    def __init__(self, pv_prefix):
        self.pv_prefix = pv_prefix if pv_prefix.endswith(":") else pv_prefix + ":"
   
    def configure(self):
        from gda.epics import LazyPVFactory  # @UnresolvedImport
        
        self.control_pv = LazyPVFactory.newStringPV(self.get_pv_name("ACTION"))
        self.rb_open_pv = LazyPVFactory.newBooleanFromIntegerPV(self.get_pv_name("OPEN_STATE"))
        self.rb_closed_pv = LazyPVFactory.newBooleanFromIntegerPV(self.get_pv_name("CLOSE_STATE"))
        
        self.state_tracker = ValveStateTracker(self.rb_open_pv, self.rb_closed_pv)
        
        self.gas_saving_enabled_pv = LazyPVFactory.newBooleanFromEnumPV(self.get_pv_name("ENABLED"))
        self.setConfigured(True)
       
    def move(self, position):

        allowed_position = [Valve.OPEN, Valve.CLOSE]
        if position in allowed_position:
            if self.control_pv.get() != position:
                self.state_tracker.set_moving()
                self.control_pv.putNoWait(position)
        else:
            raise DeviceException("Allowed positions: " + str(allowed_position))
       
    def read(self):
        if self.is_closed():
            return EpicsValveController.STATE_CLOSE
        elif self.is_open():
            return EpicsValveController.STATE_OPEN
        elif not self.state_tracker.steady_state.is_set():
            command = self.control_pv.get()
            if command == Valve.CLOSE:
                return "Closing"
            elif command == Valve.OPEN:
                return "Opening"
        
        # probably error
        return self.state_tracker.status().toString()
       
    def is_closed(self):
        return self.rb_closed_pv.get()
   
    def is_open(self):
        return self.rb_open_pv.get()
    
    def status(self):
        return self.state_tracker.status()
   
    def get_pv_name(self, name):
        return self.pv_prefix + name
    
    def auto_save_gas(self):
        return self.gas_saving_enabled_pv.get()



class ValveStateTracker:
    
    """
    We evaluate the state from two boolean PVs ('open' and 'closed').
    The state is recalculated whenever either PV changes value.
    """
    
    MOVE_TIMEOUT = 3
    
    def __init__(self, open_pv, closed_pv):
        """
        PV objects please (not Strings)
        """
        self.open_pv = open_pv
        self.closed_pv = closed_pv

        self.steady_state = Event()

        self.open_pv.addMonitorListener(lambda event: self.recalculate())
        self.closed_pv.addMonitorListener(lambda event: self.recalculate())
        
        # resolve initial state
        self.recalculate()
    
    def recalculate(self):
        
        """
        OPEN xor CLOSED => IDLE
        OPEN and CLOSED => ERROR
        Neither => MOVING until IDLE or timed out, in which case ERROR
        """
        open_rb = self.open_pv.get()
        closed_rb = self.closed_pv.get()
        
        if open_rb and closed_rb:
            self.steady_state.set()
            self.state = EnumPositionerStatus.ERROR
        elif open_rb or closed_rb:
            self.steady_state.set()
            self.state = EnumPositionerStatus.IDLE
        elif self.steady_state.is_set(): # and neither OPEN or CLOSED (implicitly)
            self.state = EnumPositionerStatus.MOVING
            self.steady_state.clear()
            Thread(target=self.wait_for_steady_state).start()
        # neither OPEN or CLOSED but we are MOVING and within the timeout, no need to change the state
        
    def wait_for_steady_state(self):
        if not self.steady_state.wait(ValveStateTracker.MOVE_TIMEOUT):
            self.state = EnumPositionerStatus.ERROR
            self.steady_state.set()
    
    def status(self):
        return self.state

    def set_moving(self):
        """
        Called by controller before moving to avoid race conditions when isBusy() is invoked
        """
        self.state = EnumPositionerStatus.MOVING

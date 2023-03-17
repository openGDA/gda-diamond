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


from java.time import Instant, Duration # @UnresolvedImport
from org.slf4j import LoggerFactory # @UnresolvedImport
from java.net import NoRouteToHostException  # @UnresolvedImport


class WaitForGas:
    """ 
    It is not always appropriate to open a gas valve and reset the interlock (allowing shutter to open) immediately.
    This class is responsible for delaying the interlock reset according to some configuration.

    The strategy is to see whether the valve has been on for an accumulative amount of time specified
    within a search window. If it has not, we block for that specified time.
    """
    
    LOGGER = LoggerFactory.getLogger("gas_saving.live.WaitForGas")
    
    def __init__(self, pv, target_value, search_window_pv, delay_pv):

        """
        pv: pv whose history we are searching in the archiver
        target_value: the 'desirable' value
        search_window_pv: in minutes
        delay_pv: in minutes. we want to see the PV having target_value for this amount of time
                  or more in total within the search window; otherwise we wait by this amount
        """
        from gda.epics import LazyPVFactory  # @UnresolvedImport
        self.pv = pv
        livepv = LazyPVFactory.newDoublePV(pv)
        self.current_value = lambda: livepv.get()
        self.target = target_value
        self.window = LazyPVFactory.newDoublePV(search_window_pv)
        self.delay = LazyPVFactory.newDoublePV(delay_pv)
        
        from uk.ac.gda.epics.archiverclient import EpicsArchiverClient  # @UnresolvedImport
        self.archiver = EpicsArchiverClient("http://archappl.diamond.ac.uk/retrieval/data/")
        self.backup_archiver = EpicsArchiverClient("http://sbarchappl.diamond.ac.uk/retrieval/data/")
        
        # we use a threading.Event to wait, so that it can be interrupted (set) by a different thread
        self.gas_ready = Event()
    
    def wait(self):
        try:
            if self.should_wait():
                wait_min = self.delay.get()
                WaitForGas.LOGGER.info("Waiting %d min for gas to fill" % wait_min)
                wait_time = self.delay.get() * 60
                self.gas_ready.wait(wait_time)
                self.gas_ready.clear()
                WaitForGas.LOGGER.info("Finished waiting.")
        except:
            raise DeviceException("Error accessing archiver. Open gas & shutter manually.")
    
    def stop(self):
        self.gas_ready.set()
    
    def should_wait(self):
        records = self.retrieve_records()
        if records.isEmpty() and self.current_value() != self.target:
            return True

        # we iterate from earliest to newest events
        laston = None
        ontime = 0

        for record in records.get().getData():
            # if first 'Open' event since last duration increment,
            # cache the time
            if record.getVal() == self.target and not laston:
                laston = Instant.ofEpochSecond(record.getSecs(), record.getNanos())

            # if 'Close' event and we have seen an 'Open' event earlier,
            # increment the on time by the duration between these two.
            elif record.getVal() != self.target and laston:
                ontime += Duration.between(laston, Instant.ofEpochSecond(record.getSecs(), record.getNanos())).toMinutes()
                laston = None

        WaitForGas.LOGGER.debug("Valve was open for a total of %d minutes within the specified window" % ontime)
        return ontime < self.delay.get()

    def retrieve_records(self):
        from java.time import LocalDateTime # @UnresolvedImport
        try:
            return self.archiver.getRecordForPv(self.pv, LocalDateTime.now().minusMinutes(int(self.window.get())))
        except NoRouteToHostException, e:
            WaitForGas.LOGGER.warn("Primary EPICS archiver unreachable; trying Standby Archiver", e)
            return self.backup_archiver.getRecordForPv(self.pv, LocalDateTime.now().minusMinutes(int(self.window.get())))

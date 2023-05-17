from gda.device import DeviceException, EnumPositionerStatus  # @UnresolvedImport
from gda.device.enumpositioner import EnumPositionerBase # @UnresolvedImport
from gda.factory import ConfigurableBase  # @UnresolvedImport
from org.slf4j import LoggerFactory # @UnresolvedImport
from threading import Event


class ValveController(ConfigurableBase):
    def move(self, position):
        raise NotImplementedError
   
    def read(self):
        raise NotImplementedError

    def auto_save_gas(self):
        raise NotImplementedError
    
    def status(self):  # -> EnumPositionerStatus
        raise NotImplementedError



class Valve(EnumPositionerBase):
   
    OPEN = "Open"
    CLOSE = "Close"
   
    def __init__(self, name, controller):
        self.setName(name)
        self.setPositionsInternal([Valve.OPEN, Valve.CLOSE])
        self.controller = controller

    def rawAsynchronousMoveTo(self, position):       
        self.controller.move(position)

    def rawGetPosition(self):
        return self.controller.read()
    
    def gas_saving_enabled(self):
        return self.controller.auto_save_gas()
    
    def getStatus(self):
        return self.controller.status()


class InterlockedValves():
    
    LOGGER = LoggerFactory.getLogger("gas_saving.valve.InterlockedValves")
    
    def __init__(self, valves, interlock, waiter):
        self.valves = valves
        self.interlock = interlock
        self.waiter = waiter
        
        self.stopping = Event()
    
    def stop(self):
        InterlockedValves.LOGGER.info("Stopping...")
        self.stopping.set()
        self.waiter.stop()
    
    def toggle_valves(self, position):
        valves_toggled = []
        self.stopping.clear()
        
        for valve in self.valves:
            if valve.gas_saving_enabled():
                InterlockedValves.LOGGER.info("Moving %s to %s" % (valve.getName(), position))
                valve.asynchronousMoveTo(position)
                valves_toggled.append(valve)
                self.check_stopped()
        
        for valve in valves_toggled:
            valve.waitWhileBusy()
            self.check_stopped()
            
        for valve in valves_toggled:
            self.check_status(valve)
        
        if position == Valve.OPEN and len(valves_toggled) > 0:
            InterlockedValves.LOGGER.info("Resetting interlock...")
            self.waiter.wait()
            self.check_stopped()
            self.interlock.reset([valve.getName() for valve in valves_toggled])
    
        # because the auto save gas could have been disabled,
        # we still check here that the interlock is cleared
        if position == Valve.OPEN and not self.interlock.getPosition():
            raise DeviceException("%s interlock not cleared!" % self.interlock.getName())
        
    def check_stopped(self):
        if self.stopping.is_set():
            self.stopping.clear()
            raise DeviceException("Operation cancelled by user")
    
    def check_status(self, positioner):
        """
        Throw a DeviceException if positioner status is ERROR
        """
        if positioner.getStatus() == EnumPositionerStatus.ERROR:
            raise DeviceException("%s is in ERROR state" % positioner.getName())
 
    

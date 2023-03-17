from gda.commandqueue import SimpleCommandProgress  # @UnresolvedImport
from gda.device import DeviceException, EnumPositionerStatus  # @UnresolvedImport
from gda.device.enumpositioner import EnumPositionerBase # @UnresolvedImport
from gas_saving.valve import Valve
from uk.ac.diamond.daq.concurrent import Async # @UnresolvedImport
        
from org.slf4j import LoggerFactory # @UnresolvedImport

class GasSavingShutter(EnumPositionerBase):
    
    """
    This will simply be a wrapper around EH shutter
    which controls the appropriate gas valves
    if their 'save gas' option is enabled
    """
    
    LOGGER = LoggerFactory.getLogger("gas_saving.gas_saving_shutter.GasSavingShutter")
    
    def __init__(self, name, shutter, searched_and_locked_interlock, interlocked_valves):
        
        self.setName(name)
        self.shutter = shutter
        self.searched_and_locked_interlock = searched_and_locked_interlock
        self.valves = interlocked_valves
        self.setPositionsInternal([Valve.OPEN, Valve.CLOSE])
        
        from threading import Event
        self.moving = Event()
        self.stopping = Event()
        
        self.shutter.addIObserver(lambda source, argument: self.notifyIObservers(self, argument))

        
    def isBusy(self):
        return self.moving.is_set()
    
    def rawGetPosition(self):
        return self.shutter.getPosition()
    
    def rawAsynchronousMoveTo(self, position):
        if self.searched_and_locked_interlock.getPosition():
            self.stopping.clear()
            self.moving.set()
            Async.execute(lambda: self.move(position))
        else:
            GasSavingShutter.LOGGER.error("Cannot move shutter: not SEARCHED AND LOCKED!")
            self.set_status_and_notify(EnumPositionerStatus.ERROR)
        
    def move_shutter(self, position):
        self.notifyIObservers(self, SimpleCommandProgress(0, "Moving shutter"))
        if position == Valve.OPEN:
            self.check_stopping()
            self.shutter.asynchronousMoveTo("Reset")
            self.shutter.waitWhileBusy()

        self.check_stopping()
        self.shutter.asynchronousMoveTo(position)
        self.shutter.waitWhileBusy()
        self.check_status(self.shutter)
    
    def toggle_valves(self, position):
        self.notifyIObservers(self, SimpleCommandProgress(0, "Toggling gas valves (if gas saving enabled)"))
        self.check_stopping()
        self.valves.toggle_valves(position)
    
    def check_status(self, positioner):
        """
        Throw a DeviceException if positioner status is ERROR
        """
        if positioner.getStatus() == EnumPositionerStatus.ERROR:
            raise DeviceException("%s is in ERROR state" % positioner.getName())
    
    def check_stopping(self):
        if self.stopping.is_set():
            self.stopping.clear()
            raise DeviceException("%s stopped by user" % self.getName())
            
    def move(self, position):
        try:
            self.set_status_and_notify(EnumPositionerStatus.MOVING)
            
            if position == Valve.OPEN:
                self.toggle_valves(position)
                self.move_shutter(position)
            elif position == Valve.CLOSE:
                self.move_shutter(position)
                self.toggle_valves(position)
                
            self.set_status_and_notify(EnumPositionerStatus.IDLE)
        except DeviceException as e:
            GasSavingShutter.LOGGER.error("Error moving to %s" % position, e)
            self.set_status_and_notify(EnumPositionerStatus.ERROR)
        finally:
            self.moving.clear()
            
    def set_status_and_notify(self, status):
        self.setPositionerStatus(status)
        self.notifyIObservers(self, status)
        
    def stop(self):
        if self.getStatus() == EnumPositionerStatus.MOVING:
            self.stopping.set()
            self.valves.stop()
            self.shutter.stop()
            
        else: raise DeviceException("Stop called but not moving")
